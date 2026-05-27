# Gemini Models Reference — Don't Ask Me skill

Last updated: 2026-05-27. **Whitelist reduced to 2 models** — `gemini-3.5-flash` (primary for all tasks) and `gemini-3.1-pro-preview` (fallback for pure-math reasoning where Flash falls short).

## Whitelisted Models

| Model | Role | Cost (in/out $/1M) | Best For |
|-------|------|-------------------|----------|
| `gemini-3.5-flash` | **PRIMARY** (default for all `gemini.py` commands) | $1.50 / $9.00 | Adversarial critique, deep reasoning, web-grounded research, quick questions, data extraction, multimodal — everything |
| `gemini-3.1-pro-preview` | **FALLBACK** (via `-m` flag) | $2.00–$4.00 / $12.00–$18.00 (tiered by length) | Pure-math reasoning, ARC-AGI-style problems where Flash falls short |

### Why one model for everything (post-audit 2026-05-20 + 2026-05-27 simplification)

Live A/B test on a real adversarial-critique task (5 design docs, ~80KB context):
- **3.1 Pro:** 13 findings, 26,270 tokens, 54s, 1 factual error
- **3.5 Flash:** 16 findings (5 new architectural concerns Pro missed), 27,509 tokens, 42s, 0 factual errors
- 22% faster, 33% cheaper, MORE findings, BETTER architectural depth

Flash 3.5 also handles:
- Web grounding (`--grounded`) — supports Google Search as tool, same as Pro
- High thinking (`thinking_level=HIGH`) — matches Pro reasoning depth on most tasks
- Multimodal (`--image`, `--video`) — natively
- JSON mode (`--json-mode`) — structured extraction
- All 4 thinking levels (MINIMAL/LOW/MEDIUM/HIGH) — full control

The only cases where 3.1 Pro wins: ARC-AGI-2 (77.1% vs not benchmarked), GPQA Diamond (94.3%), pure-math reasoning where every percentage point matters. For those — use `-m gemini-3.1-pro-preview` explicitly. Default everything else to 3.5 Flash.

### Benchmarks (May 2026)

| Benchmark | 3.5 Flash | 3.1 Pro |
|-----------|-----------|---------|
| MCP Atlas (multi-step agentic) | **83.6%** | 78.2% |
| MMMU-Pro | **83.6%** | — |
| Finance Agent v2 | 57.9% | — |
| Terminal-bench 2.1 | 76.2% | — |
| AI Intelligence Index | — | **57** (#1 tied) |
| GPQA Diamond | — | **94.3%** |
| ARC-AGI-2 | — | **77.1%** |

3.5 Flash wins on agentic/coding/multi-step. 3.1 Pro wins on pure reasoning benchmarks.

## Thinking Level Compatibility

All Gemini 3 models use `thinking_level` (string). Legacy `thinking_budget` (int) is for 2.5 only — do NOT mix.

| Model | MINIMAL | LOW | MEDIUM | HIGH |
|-------|---------|-----|--------|------|
| `gemini-3.5-flash` | YES | YES | YES (default) | YES |
| `gemini-3.1-pro-preview` | NO | YES | YES | YES (default, dynamic) |

- **MINIMAL** (Flash only): near-zero thinking tokens. Simple classification, extraction
- **LOW**: fewer tokens. Simple tasks where reasoning is not critical
- **MEDIUM**: balanced depth vs speed for moderate complexity
- **HIGH**: maximum reasoning depth. May increase latency significantly

Pro does not support MINIMAL (thinking can't be turned off). Auto-fallback to HIGH if unsupported level requested.

## Temperature (CRITICAL — Google's explicit recommendation)

> *"When using Gemini 3 models, we strongly recommend keeping the temperature at its default value of 1.0."*

Lower temperature may cause **looping or degraded performance**, especially for reasoning/math tasks. Range: 0.0-2.0. Only adjust with a specific, tested reason.

## Thought Signatures

Gemini 3 returns encrypted thought signatures. SDK handles them automatically. If using raw API: must pass signatures back in multi-turn conversations (400 error otherwise).

## Function Call IDs (2026 breaking change)

Gemini 3 models generate a unique `id` per function call. When returning function results, you **must** echo the matching `id` in `function_response`. Required for multi-turn + tool chaining. Older patterns without `id` are deprecated.

## Task-to-Command Matrix

| Task | Command | Thinking | Why |
|------|---------|----------|-----|
| **Adversarial critique / second opinion** | `gemini.py second-opinion` | HIGH | A/B-verified winner on critique tasks |
| **Complex reasoning** | `gemini.py think` | HIGH | High thinking, no system prompt framing |
| **Quick factual questions** | `gemini.py ask` | (default) | Fast response with optional `--grounded` |
| **Research with web grounding** | `gemini.py ask --grounded` | (default) | Google Search as tool |
| **Data extraction / structured** | `gemini.py extract --json-mode` | MINIMAL | High throughput, structured output |
| **Visual review** | `gemini.py second-opinion --image` | HIGH | Multimodal native, design QA |
| **Pure-math / ARC-AGI** | `gemini.py think -m gemini-3.1-pro-preview` | HIGH | Pro reasoning benchmarks |

## Skill-to-Style Matrix

| Style | Model | Thinking | Notes |
|-------|-------|----------|-------|
| Quick Web Check | `gemini-3.5-flash` + `--grounded` | (default) | Google Search tool enabled |
| Devil's Advocate (Gemini) | `gemini-3.5-flash` | HIGH | Adversarial reviewer system prompt |
| Devil's Advocate (Opus) | `idea-validator` subagent | — | Isolated Claude Opus, no parent context |
| Boardroom Debate | Both above in parallel | HIGH (Gemini) | Same message, two tool calls |
| Round-Table Discussion | `gemini-3.5-flash` (all phases) | HIGH (reasoning), default (grounded research) | Phase 0.5 + 3.5 use `--grounded` |

## Removed from Whitelist (2026-05-27)

Previously supported, now removed for simplicity and cost discipline:

| Model | Status | Replacement |
|-------|--------|-------------|
| `gemini-3.1-flash-lite` | Removed | `gemini-3.5-flash` (handles all same use cases including grounded research) |
| `gemini-3.1-flash-lite-preview` | Removed | `gemini-3.5-flash` |
| `gemini-3-flash-preview` | Removed (2026-05-20 audit) | `gemini-3.5-flash` |
| `gemini-3-pro-preview` | SHUT DOWN (March 9, 2026) | `gemini-3.1-pro-preview` |
| `gemini-2.5-pro` / `gemini-2.5-flash` / `gemini-2.5-flash-lite` | Superseded | `gemini-3.5-flash` |
| `gemini-2.0-flash` / `gemini-2.0-flash-lite` | Retiring | `gemini-3.5-flash` |

## Google Search Grounding

`gemini-3.5-flash` supports `--grounded` / Google Search tool. Used for factual research (Quick Web Check, Round-Table Phase 0.5 + 3.5).

**Billing** (2026 update): Gemini 3 models — per **unique search query executed** (not per prompt). 5,000 free queries/month, then $14 per 1,000 queries.

## Cost Optimization Features

- **Batch API**: 50% discount on input + output
- **Implicit context caching**: enabled by default for Gemini 3.x models
- **Explicit cache control**: `cache_control = CacheControlEphemerality(ephemeralMinutes=60)` for high-volume repeated queries
- **Minimum cacheable tokens**: 1,024 (3.5 Flash), 4,096 (3.1 Pro)
- **Priority mode**: ~1.8× pricing for guaranteed throughput

## Image / Video / Other Modalities

This skill is **CLI-only** (no MCP). Image generation is NOT supported via this skill — for that use other tools.

Image / video INPUT (multimodal vision — sending media to Gemini for analysis) IS supported:
- `--image PATH` (repeatable) — send PNG/JPEG/WebP/GIF for visual review
- `--video PATH` or `--video URL` — send local video file or YouTube URL for analysis

Supported via `gemini-3.5-flash` natively.
