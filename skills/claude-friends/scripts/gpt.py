#!/usr/bin/env python3
"""
OpenAI SDK CLI — direct OpenAI Responses-API calls via Python subprocess.

The OPTIONAL third reviewer family for the Claude Friends skill (Gemini + isolated Opus + GPT).
Sibling of gemini.py — same `second-opinion` contract, same `@file` + `--save` flags, same
key-from-global-file discipline so a fresh non-interactive agent shell works with NO env prefix.

This is an OPT-IN upgrade, not part of the default two-family flow: it needs a paid OpenAI key
(no free tier like Gemini's). See `references/third-family-gpt.md` for when a third family earns
its cost. If you only run the free two-family setup, you never need this file.

Models (verified 2026-07 against the current API):
  GPT-5.4 ($2.50/$15)       — previous flagship. DEFAULT for second-opinion/think (cost: a
                              third-reviewer leg whose marginal value over Gemini is modest,
                              so the half-price 5.4 is the sensible default).
  GPT-5.5 ($5/$30 per 1M)   — current GA flagship. ESCALATION via -m gpt-5.5 for the
                              highest-stakes / one-way-door reviews.
  (GPT-5.6 is limited-preview / select-partners only as of 2026-07 → NOT whitelisted, same
   discipline as Gemini: no preview models in the second-opinion whitelist.)

NOTE: this file is named gpt.py, NOT openai.py — a module named openai.py shadows the
installed `openai` package (its own dir leads sys.path), so `from openai import OpenAI`
would import this file and fail. Keep the name gpt.py.

Usage:
  python3 gpt.py second-opinion "question" --context "context"
  python3 gpt.py second-opinion @prompt.txt --save out.md
  python3 gpt.py ask "prompt"
  python3 gpt.py think "Design a caching strategy for 10M users"
  python3 gpt.py second-opinion @prompt.txt -m gpt-5.4 -t medium   # cheaper, less reasoning

Reasoning (GPT-5.x are reasoning models): effort is none/low/medium/high/xhigh
(Responses API `reasoning.effort`). NOTE: gpt-5.5 rejects 'minimal' (live-verified 400);
the API generic type lists it but the flagship's supported set is none/low/medium/high/xhigh
— so 'minimal' is OUT of our whitelist. second-opinion + think default to HIGH (matches the
gemini.py second-opinion HIGH-thinking choice). Temperature is NOT sent — reasoning models
ignore/penalize it; leave the model at its default like our Gemini-3 adapter does.

Key resolution (in order): OPENAI_API_KEY env var, else the global key file
~/.openai/api_key (plain text, key only, chmod 600). The env var always wins, so a
per-project `export` overrides. No `.env` is auto-loaded — write the key to ~/.openai/api_key
once (this is the exact gemini.py lesson: a fresh agent Bash shell never sourced your project
.env, so the wrapper must self-resolve a key).
"""

import argparse
import json
import os
import sys
import time
from typing import Any

try:
  from openai import OpenAI
except ImportError:
  print("ERROR: openai SDK not installed. Run: pip install -U openai", file=sys.stderr)
  sys.exit(1)

# --- Config ---

MODELS = {
  "gpt-5.4",   # PRIMARY (default): $2.50/$15. Previous flagship, half-price.
  "gpt-5.5",   # ESCALATION: $5/$30 per 1M. Current GA flagship, for highest-stakes reviews via -m.
}
# Responses-API reasoning effort levels supported by the gpt-5.5 flagship (live-verified:
# 'minimal' → 400 on gpt-5.5, so it is excluded). 'none' disables reasoning.
EFFORT_LEVELS = {"none", "low", "medium", "high", "xhigh"}

DEFAULT_MODEL = "gpt-5.4"
SECOND_OPINION_MODEL = "gpt-5.4"

GLOBAL_KEY_FILE = os.path.expanduser("~/.openai/api_key")


def _resolve_api_key() -> str | None:
  """Resolve the OpenAI API key. Env var wins (lets a project `export` override);
  otherwise fall back to the global key file ~/.openai/api_key (plain text). Mirrors
  gemini.py — the durable fix for "OPENAI_API_KEY not set" in fresh non-interactive
  shells that never sourced a project .env."""
  env_key = os.environ.get("OPENAI_API_KEY")
  if env_key and env_key.strip():
    return env_key.strip()
  try:
    with open(GLOBAL_KEY_FILE, encoding="utf-8") as fh:
      file_key = fh.read().strip()
    return file_key or None
  except OSError:
    return None


def _usage_field(usage, *names) -> int:
  """Read the first present token field across Responses-API naming variants
  (input_tokens/output_tokens/total_tokens). Defensive against SDK version drift."""
  for n in names:
    v = getattr(usage, n, None)
    if isinstance(v, int):
      return v
  return 0


def call_openai(
  prompt: str,
  model: str = DEFAULT_MODEL,
  system_instruction: str | None = None,
  effort: str | None = None,
  max_output_tokens: int | None = None,
) -> dict:
  """Call the OpenAI Responses API and return response + usage."""
  api_key = _resolve_api_key()
  if not api_key:
    return {"error": "OPENAI_API_KEY not set (env empty and ~/.openai/api_key missing/empty)"}

  if model not in MODELS:
    return {"error": f"Invalid model: {model}. Valid: {', '.join(sorted(MODELS))}"}

  if effort is not None and effort not in EFFORT_LEVELS:
    return {"error": f"Invalid reasoning effort: {effort}. Valid: {', '.join(sorted(EFFORT_LEVELS))}"}

  try:
    client = OpenAI(api_key=api_key)
    start = time.time()

    kwargs: dict[str, Any] = {"model": model, "input": prompt}
    if system_instruction:
      kwargs["instructions"] = system_instruction
    if effort:
      kwargs["reasoning"] = {"effort": effort}
    if max_output_tokens is not None:
      kwargs["max_output_tokens"] = max_output_tokens

    response = client.responses.create(**kwargs)
    elapsed_ms = int((time.time() - start) * 1000)

    text = getattr(response, "output_text", None) or ""

    usage = {"model": model, "latency_ms": elapsed_ms}
    um = getattr(response, "usage", None)
    if um:
      usage["input_tokens"] = _usage_field(um, "input_tokens", "prompt_tokens")
      usage["output_tokens"] = _usage_field(um, "output_tokens", "completion_tokens")
      usage["total_tokens"] = _usage_field(um, "total_tokens")
      details = getattr(um, "output_tokens_details", None)
      reasoning_tokens = getattr(details, "reasoning_tokens", 0) if details else 0
      if reasoning_tokens:
        usage["reasoning_tokens"] = reasoning_tokens

    if not text:
      return {"error": f"Empty response (status={getattr(response, 'status', '?')}). Usage: {usage}"}

    return {"response": text, "usage": usage}

  except Exception as e:
    return {"error": f"{type(e).__name__}: {e}"}


def format_output(result: dict) -> str:
  """Format response with usage footer (mirrors gemini.py)."""
  if "error" in result:
    return f"ERROR: {result['error']}"

  usage = result.get("usage", {})
  model = usage.get("model", "?")
  tokens = usage.get("total_tokens", "?")
  latency = usage.get("latency_ms", "?")
  reasoning = f" | {usage['reasoning_tokens']} reasoning" if usage.get("reasoning_tokens") else ""

  return f"{result['response']}\n\n---\n*[OpenAI {model} | {tokens} tokens{reasoning} | {latency}ms]*"


# --- Commands ---

COMMANDS = {
  "ask": {
    "system": None,
    "model": DEFAULT_MODEL,
    "effort": None,  # model default reasoning
  },
  "second-opinion": {
    "system": "Provide a critical second opinion. Identify blind spots, errors, unconsidered alternatives, and missing context. Challenge assumptions. Be thorough but structured.",
    "model": SECOND_OPINION_MODEL,
    "effort": "high",
  },
  "think": {
    "system": None,
    "model": SECOND_OPINION_MODEL,
    "effort": "high",
  },
}


def main():
  parser = argparse.ArgumentParser(
    description="OpenAI SDK CLI (Responses API) — optional third reviewer family for Claude Friends",
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  parser.add_argument("command", choices=COMMANDS.keys(), help="Command to run")
  parser.add_argument("prompt", help="Prompt text (or @file to read from file)")
  parser.add_argument("--context", "-c", help="Additional context (for second-opinion)")
  parser.add_argument("--model", "-m", help="Override model (gpt-5.5 | gpt-5.4)")
  parser.add_argument("--thinking", "-t", help="Reasoning effort: none/low/medium/high/xhigh (gpt-5.5 rejects 'minimal')")
  parser.add_argument("--system", "-s", help="Override system instruction")
  parser.add_argument("--save", help="Save response to file")
  parser.add_argument("--json", action="store_true", help="Output raw JSON (for piping)")
  parser.add_argument("--max-tokens", type=int, help="Max output tokens (incl. reasoning tokens)")

  args = parser.parse_args()
  cmd = COMMANDS[args.command]

  # Read prompt from file if @file syntax
  prompt = args.prompt
  if prompt.startswith("@"):
    filepath = prompt[1:]
    try:
      with open(filepath, "r") as f:
        prompt = f.read()
    except FileNotFoundError:
      print(f"ERROR: File not found: {filepath}", file=sys.stderr)
      sys.exit(1)

  # Build final prompt
  if args.command == "second-opinion" and args.context:
    prompt = f"{prompt}\n\nContext:\n{args.context}"

  result = call_openai(
    prompt=prompt,
    model=args.model or cmd["model"],
    system_instruction=args.system or cmd["system"],
    effort=args.thinking or cmd["effort"],
    max_output_tokens=args.max_tokens,
  )

  # Output
  if args.json:
    print(json.dumps(result, ensure_ascii=False, indent=2))
  else:
    print(format_output(result))

  # Save to file
  if args.save and "error" not in result:
    output = format_output(result)
    os.makedirs(os.path.dirname(args.save) or ".", exist_ok=True)
    with open(args.save, "w") as f:
      f.write(output)
    print(f"\n>> Saved to {args.save}", file=sys.stderr)

  sys.exit(1 if "error" in result else 0)


if __name__ == "__main__":
  main()
