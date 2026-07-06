# Third Reviewer Family (OpenAI GPT) — OPTIONAL upgrade

> Read on demand. The default skill is **two families** (Gemini + isolated Opus) and is complete
> without this. A third family is an opt-in for the highest-stakes work — it costs a **paid** OpenAI
> key (no free tier like Gemini's), so it is deliberately NOT wired into the default flow.

## Why a third family at all

Boardroom Debate's whole value is *independent* blind spots: Gemini (Google) + an isolated Opus
subagent (Anthropic, no parent context) already give two distinct lineages. A third distinct family
(OpenAI) widens tail coverage on one-way-door / security / architecture-lock decisions where being
wrong is expensive.

**But it is tail coverage, not a vote.** Never count votes across three models — always adjudicate.
The Opus subagent *reads your actual code*; the brief-only reviewers do not, so on code facts Opus
outranks them. GPT earns its permanent slot only by surfacing findings the other two miss — measure
that (same A/B discipline that keeps the Gemini whitelist at 2 models), don't assume it.

## When it's worth the extra key

Turn it on only for: ADRs / architecture locks, security-surface changes, anything with meaningful
rollback cost, or a genuinely close call the two-family review left split. For routine sanity checks,
the free two-family setup is the right tool — adding a paid third leg there just burns money.

## Setup (one-time)

```bash
pip install -U openai

# Store the key so any shell finds it (mirrors the Gemini key discipline):
mkdir -p ~/.openai && printf '%s' 'your_openai_key' > ~/.openai/api_key && chmod 600 ~/.openai/api_key
```

`gpt.py` resolves `OPENAI_API_KEY` first, then `~/.openai/api_key`. If you rotate the key, update
that file too.

## Models (whitelist — 2, verified 2026-07)

| Model | Role | Cost (in/out $/1M) |
|---|---|---|
| `gpt-5.4` | **PRIMARY / default** for `second-opinion` + `think` | $2.50 / $15.00 |
| `gpt-5.5` | **ESCALATION** via `-m gpt-5.5` — current GA flagship, highest-stakes only | $5.00 / $30.00 |

Default is the half-price `gpt-5.4`: the third leg's marginal value over Gemini is usually modest, so
reserve the flagship for reviews that truly warrant it. `gpt-5.6` is preview-only → not whitelisted
(same "no preview models" rule as Gemini).

GPT-5.x are reasoning models: the only knob is `reasoning.effort` (`none/low/medium/high/xhigh` —
`minimal` is rejected by gpt-5.5). `second-opinion`/`think` default to `high`. Temperature is not sent.

## Using it in a Boardroom Debate (three families, one message)

Same non-negotiable rule as the two-family flow: **one message, all reviewers in parallel** — never
sequential (the later reviewer would see the earlier one's framing and echo it). Add the third call
alongside the existing two:

```python
Bash("python3 ~/.claude/skills/dont-ask-me/scripts/gemini.py second-opinion @prompt.txt --save gemini-out.md")
Bash("python3 ~/.claude/skills/dont-ask-me/scripts/gpt.py    second-opinion @prompt.txt --save gpt-out.md")
Agent(subagent_type="idea-validator", prompt="<same artifact pasted inline>")
```

Then build the acceptance ledger with a third column (Gemini / Opus / GPT), adjudicate row by row,
and present it critically — the [Critical Evaluation Rule](../SKILL.md#critical-evaluation-rule)
applies unchanged. Three opinions are input, still not a majority rule.

## Text-only in v1

`gpt.py` has no `--image` / `--video` / `--grounded`. For a currency web-check, lean on Gemini
`--grounded` + the Opus idea-validator's WebSearch; GPT contributes pure-reasoning critique. Add the
OpenAI web-search / vision tools only if a review actually needs them (simplicity default).
