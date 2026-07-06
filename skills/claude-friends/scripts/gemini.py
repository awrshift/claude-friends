#!/usr/bin/env python3
"""
Gemini SDK CLI — direct Google GenAI calls via Python subprocess.

Models (whitelist — 2 only):
  3.5 Flash ($1.50/$9)         — PRIMARY, default for all commands (agentic + coding + critique)
  3.1 Pro Preview ($2-4/$12-18) — FALLBACK via -m, pure-math reasoning (ARC-AGI-style)

Usage:
  python3 gemini.py ask "prompt"
  python3 gemini.py second-opinion "question" --context "context"
  python3 gemini.py ask "prompt" --grounded          # web-grounded answer
  python3 gemini.py ask "prompt" --save output.md
  python3 gemini.py ask "prompt" --grounded  # research mode (Google Search tool)
  python3 gemini.py second-opinion @prompt.txt --image site.png --image ref.png  # visual review
  python3 gemini.py ask @prompt.txt --video https://www.youtube.com/watch?v=ID  # YouTube video analysis
  python3 gemini.py ask @prompt.txt --video path/to/clip.mp4 -m gemini-3.1-pro-preview  # local video

Video notes (Gemini 3.x):
  - YouTube URL: public/unlisted only, 1 URL per request
  - Local video: inline if <20MB, else auto-upload via File API (up to 2GB)
  - Tokens: ~300/sec at default media_resolution, ~100/sec at low
  - --image and --video are mutually exclusive (one media type per request)

Audit history:
  2026-05-20: removed `analyze` + `review` commands, removed `--seed` + `--focus` flags,
              removed `gemini-3-flash-preview`, added `gemini-3.5-flash` (new default),
              trimmed whitelist to 2 models.

Key resolution (in order): the GOOGLE_API_KEY env var, else the global key file
~/.gemini/api_key (plain text, key only). The env var wins when set, so a per-project
`export` still overrides. NOTE: no `.env` is auto-loaded — a plain `GOOGLE_API_KEY=... in
~/.env` does NOT reach a fresh non-interactive shell (the shell never sources it). Write
the key once to ~/.gemini/api_key, or `export` it. This is the fix for the old
"GOOGLE_API_KEY not set" failure that hit every shell without the export.
"""

import argparse
import json
import os
import re
import sys
import time

try:
  from google import genai
  from google.genai import types
except ImportError:
  print("ERROR: google-genai not installed. Run: pip install google-genai", file=sys.stderr)
  sys.exit(1)

# --- Config ---

MODELS = {
  "gemini-3.5-flash",         # PRIMARY: $1.50/$9 per 1M. Frontier agentic + coding. Default for all tasks.
  "gemini-3.1-pro-preview",   # FALLBACK: $2-4/$12-18. Pure-math reasoning where Flash falls short (ARC-AGI-style).
}
GEMINI_3 = MODELS  # All current models are Gemini 3 series
# Gemini 3.1 Pro: LOW, MEDIUM, HIGH. No MINIMAL (thinking can't be off).
# Gemini 3.5 Flash: all 4 levels (MINIMAL, LOW, MEDIUM, HIGH).
GEMINI_3_FLASH = {"gemini-3.5-flash"}
THINKING_LEVELS = {"minimal", "low", "medium", "high"}
THINKING_LEVELS_PRO = {"low", "medium", "high"}

DEFAULT_MODEL = "gemini-3.5-flash"
RESEARCH_MODEL = "gemini-3.5-flash"
SECOND_OPINION_MODEL = "gemini-3.5-flash"
PRO_FALLBACK_MODEL = "gemini-3.1-pro-preview"

# Video support (Gemini 3.x, April 2026)
YOUTUBE_URL_RE = re.compile(
  r"^https?://(?:www\.)?(?:youtube\.com/watch\?|youtu\.be/|youtube\.com/shorts/|youtube\.com/live/|youtube\.com/embed/)",
  re.IGNORECASE,
)
VIDEO_MIME_MAP = {
  ".mp4": "video/mp4",
  ".mov": "video/quicktime",
  ".mpeg": "video/mpeg",
  ".mpg": "video/mpeg",
  ".avi": "video/x-msvideo",
  ".webm": "video/webm",
  ".wmv": "video/x-ms-wmv",
  ".3gp": "video/3gpp",
  ".3gpp": "video/3gpp",
  ".flv": "video/x-flv",
  ".mkv": "video/x-matroska",
}
INLINE_VIDEO_MAX_BYTES = 20 * 1024 * 1024  # 20MB — above this use File API
FILE_API_POLL_INTERVAL = 2  # seconds between file state polls
FILE_API_MAX_WAIT = 300  # 5 min max wait for video processing


def _is_youtube_url(s: str) -> bool:
  """True if s looks like a YouTube watch/shorts/live/embed URL."""
  return bool(YOUTUBE_URL_RE.match(s))


def _build_video_part(video: str, client) -> tuple[object | None, str | None]:
  """Build a single video content Part from YouTube URL or local file path.

  Returns (part, error). Exactly one is non-None.
    - YouTube URL → FileData with file_uri (no upload, no bytes)
    - Local file < 20MB → inline bytes via Part.from_bytes
    - Local file ≥ 20MB → upload via File API, poll until ACTIVE, then Part.from_uri
  """
  # YouTube URL branch
  if _is_youtube_url(video):
    part = types.Part(file_data=types.FileData(file_uri=video))
    return part, None

  # Local file branch
  if not os.path.isfile(video):
    return None, f"Video not found (not a YouTube URL and no such file): {video}"

  ext = os.path.splitext(video)[1].lower()
  mime = VIDEO_MIME_MAP.get(ext)
  if not mime:
    return None, f"Unsupported video extension: {ext}. Supported: {', '.join(sorted(VIDEO_MIME_MAP))}"

  size = os.path.getsize(video)
  if size <= INLINE_VIDEO_MAX_BYTES:
    with open(video, "rb") as f:
      data = f.read()
    return types.Part.from_bytes(data=data, mime_type=mime), None

  # Large file: File API upload + polling until ACTIVE
  try:
    uploaded = client.files.upload(file=video)
    waited = 0
    while getattr(uploaded, "state", None) and getattr(uploaded.state, "name", None) == "PROCESSING":
      if waited >= FILE_API_MAX_WAIT:
        return None, f"File API processing timeout after {FILE_API_MAX_WAIT}s"
      time.sleep(FILE_API_POLL_INTERVAL)
      waited += FILE_API_POLL_INTERVAL
      uploaded = client.files.get(name=uploaded.name)
    if getattr(uploaded.state, "name", None) == "FAILED":
      return None, "File API reported FAILED state for uploaded video"
    part = types.Part.from_uri(file_uri=uploaded.uri, mime_type=uploaded.mime_type or mime)
    return part, None
  except Exception as e:
    return None, f"File API upload failed: {type(e).__name__}: {e}"


GLOBAL_KEY_FILE = os.path.expanduser("~/.gemini/api_key")


def _resolve_api_key() -> str | None:
  """Resolve the Gemini API key. The env var wins (a project `export` overrides);
  otherwise fall back to the global key file ~/.gemini/api_key (plain text). This is
  the durable fix for "GOOGLE_API_KEY not set" in fresh non-interactive shells that
  never sourced a project .env — fix the wrapper once, not every caller."""
  env_key = os.environ.get("GOOGLE_API_KEY")
  if env_key and env_key.strip():
    return env_key.strip()
  try:
    with open(GLOBAL_KEY_FILE, encoding="utf-8") as fh:
      file_key = fh.read().strip()
    return file_key or None
  except OSError:
    return None


def call_gemini(
  prompt: str,
  model: str = DEFAULT_MODEL,
  system_instruction: str | None = None,
  thinking_level: str | None = None,
  grounded: bool = False,
  temperature: float | None = None,
  top_p: float | None = None,
  top_k: int | None = None,
  max_output_tokens: int | None = None,
  json_mode: bool = False,
  images: list[str] | None = None,
  video: str | None = None,
) -> dict:
  """Call Gemini SDK and return response + usage. Supports multimodal (text + images OR text + video)."""
  api_key = _resolve_api_key()
  if not api_key:
    return {
      "error": "GOOGLE_API_KEY not set (env empty and ~/.gemini/api_key missing/empty). "
      "Fix: mkdir -p ~/.gemini && printf '%s' YOUR_KEY > ~/.gemini/api_key && chmod 600 ~/.gemini/api_key"
    }

  if model not in MODELS:
    return {"error": f"Invalid model: {model}. Valid: {', '.join(sorted(MODELS))}"}

  try:
    client = genai.Client(api_key=api_key)
    start = time.time()

    config_kwargs = {}
    if system_instruction:
      config_kwargs["system_instruction"] = system_instruction

    # Sampling parameters (Gemini 3 default: temp=1.0, top_p=0.95)
    if temperature is not None:
      config_kwargs["temperature"] = temperature
    if top_p is not None:
      config_kwargs["top_p"] = top_p
    if top_k is not None:
      config_kwargs["top_k"] = top_k
    if max_output_tokens is not None:
      config_kwargs["max_output_tokens"] = max_output_tokens

    # JSON structured output
    if json_mode:
      config_kwargs["response_mime_type"] = "application/json"

    # Google Search grounding
    if grounded:
      config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]

    # Thinking configuration — all models are Gemini 3.x, use thinkingLevel
    is_flash = model in GEMINI_3_FLASH
    if is_flash:
      level = thinking_level or "medium"
      valid = THINKING_LEVELS
    else:
      # Pro: LOW, MEDIUM (new in 3.1), HIGH. No MINIMAL.
      level = thinking_level or "high"
      valid = THINKING_LEVELS_PRO
      if level not in valid:
        level = "high"  # fallback for Pro
    if level in valid:
      config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level=level)

    config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

    # Build multimodal contents — images OR video, not both
    if images and video:
      return {"error": "--image and --video are mutually exclusive (Gemini: one media type per request)"}

    contents = prompt
    if images:
      parts = [types.Part.from_text(text=prompt)]
      for img_path in images:
        if not os.path.isfile(img_path):
          return {"error": f"Image file not found: {img_path}"}
        with open(img_path, "rb") as f:
          img_data = f.read()
        ext = os.path.splitext(img_path)[1].lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}
        mime = mime_map.get(ext, "image/png")
        parts.append(types.Part.from_bytes(data=img_data, mime_type=mime))
      contents = parts
    elif video:
      video_part, err = _build_video_part(video, client)
      if err:
        return {"error": err}
      # Video best practice: one video + text in a single turn.
      contents = [video_part, types.Part.from_text(text=prompt)]

    response = client.models.generate_content(
      model=model, contents=contents, config=config,
    )

    elapsed_ms = int((time.time() - start) * 1000)

    usage = {"model": model, "latency_ms": elapsed_ms}
    if response.usage_metadata:
      um = response.usage_metadata
      usage.update({
        "input_tokens": um.prompt_token_count or 0,
        "output_tokens": um.candidates_token_count or 0,
        "total_tokens": um.total_token_count or 0,
      })
      if hasattr(um, "thoughts_token_count") and um.thoughts_token_count:
        usage["thinking_tokens"] = um.thoughts_token_count

    return {"response": response.text or "", "usage": usage}

  except Exception as e:
    return {"error": f"{type(e).__name__}: {e}"}


def format_output(result: dict) -> str:
  """Format response with usage footer."""
  if "error" in result:
    return f"ERROR: {result['error']}"

  usage = result.get("usage", {})
  model = usage.get("model", "?")
  tokens = usage.get("total_tokens", "?")
  latency = usage.get("latency_ms", "?")
  thinking = f" | {usage['thinking_tokens']} thinking" if usage.get("thinking_tokens") else ""

  return f"{result['response']}\n\n---\n*[Gemini {model} | {tokens} tokens{thinking} | {latency}ms]*"


# --- Commands ---

COMMANDS = {
  "ask": {
    "system": None,
    "model": DEFAULT_MODEL,
    "thinking": None,
  },
  "second-opinion": {
    "system": "Provide a critical second opinion. Identify blind spots, errors, unconsidered alternatives, and missing context. Challenge assumptions. Be thorough but structured.",
    "model": SECOND_OPINION_MODEL,
    "thinking": "high",
  },
  "extract": {
    "system": "Extract structured data. Return ONLY valid JSON.",
    "model": RESEARCH_MODEL,
    "thinking": "minimal",
  },
  "think": {
    "system": None,
    "model": SECOND_OPINION_MODEL,
    "thinking": "high",
  },
}


def main():
  parser = argparse.ArgumentParser(
    description="Gemini SDK CLI",
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  parser.add_argument("command", choices=COMMANDS.keys(), help="Command to run")
  parser.add_argument("prompt", help="Prompt text (or @file to read from file)")
  parser.add_argument("--context", "-c", help="Additional context (for second-opinion)")
  parser.add_argument("--model", "-m", help="Override model")
  parser.add_argument("--thinking", "-t", help="Thinking level: minimal/low/medium/high")
  parser.add_argument("--system", "-s", help="Override system instruction")
  parser.add_argument("--save", help="Save response to file")
  parser.add_argument("--json", action="store_true", help="Output raw JSON (for piping)")
  parser.add_argument("--grounded", "-g", action="store_true", help="Enable Google Search grounding (Gemini searches web before answering)")
  parser.add_argument("--temp", type=float, help="Temperature: 0.0-2.0 (default 1.0, keep default for Gemini 3)")
  parser.add_argument("--top-p", type=float, help="Top-p nucleus sampling: 0.0-1.0 (default 0.95)")
  parser.add_argument("--top-k", type=int, help="Top-k sampling (default ~40)")
  parser.add_argument("--max-tokens", type=int, help="Max output tokens: 1-65536 (default model max)")
  parser.add_argument("--json-mode", action="store_true", help="Force JSON output (sets response_mime_type=application/json)")
  parser.add_argument("--image", "-i", action="append", dest="images", help="Image file path (repeatable, for multimodal input)")
  parser.add_argument("--video", help="Video input: YouTube URL (public/unlisted) or local file path (inline <20MB, File API otherwise). Mutually exclusive with --image.")

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

  # Call Gemini
  result = call_gemini(
    prompt=prompt,
    model=args.model or cmd["model"],
    system_instruction=args.system or cmd["system"],
    thinking_level=args.thinking or cmd["thinking"],
    grounded=args.grounded,
    temperature=args.temp,
    top_p=args.top_p,
    top_k=args.top_k,
    max_output_tokens=args.max_tokens,
    json_mode=args.json_mode,
    images=args.images,
    video=args.video,
  )

  # Output
  if args.json:
    print(json.dumps(result, ensure_ascii=False, indent=2))
  else:
    output = format_output(result)
    print(output)

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
