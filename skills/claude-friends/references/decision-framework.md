# When to Use Gemini vs Claude Subagents

**Principle:** Claude subagents (Task tool) = DEFAULT. Gemini only where unique value.

## Claude Subagents WIN (use Task tool)

- Code review (can READ files, follow imports)
- Codebase exploration (has Grep, Glob, Read)
- Deep reasoning (`Task(model="opus")` > `gemini think`)
- Any task needing file I/O or project context

## Gemini WINS (use CLI skill)

- **Independent second opinion** — different model family = different biases
- **Quick stateless questions** — `ask` (<3s, cheap)
- **Fact-check verification** — cross-validate Claude's analysis with Gemini 3.5 Flash
- **Parallel batch calls** — 4+ background processes via `&` + `wait`
- **Dual validation (advanced)** — `idea-validator` sub-agent (Opus, isolated) + `gemini.py second-opinion` (3.5 Flash) in parallel for high-stakes design decisions. See `references/dual-validation.md`

## Model Selection Quick Reference

| Need | Best option | Fallback |
|------|------------|----------|
| Parallel file-aware work | `Task(model="sonnet")` | — |
| Deep reasoning | `Task(model="opus")` | `gemini.py think` (3.5 Flash, HIGH) |
| **Second opinion** | **`gemini.py second-opinion` (3.5 Flash)** | `gemini.py second-opinion -m gemini-3.1-pro-preview` for pure-math |
| Dual validation (high-stakes) | `idea-validator` Agent + `gemini.py second-opinion` in parallel | single second-opinion |
| Quick question | `gemini.py ask` (Flash default) | — |
| Research / fact-check | `gemini.py ask --grounded` (Flash default) | — |
| Data extraction | `gemini.py extract` (Flash, LOW) | — |
| Visual review (image input) | `gemini.py second-opinion --image` (multimodal CLI) | — |

## DO NOT Use Gemini For

- File operations (Claude Code has direct access)
- Neo4j queries (use neo4j driver)
- Tasks requiring conversation history (Gemini calls are stateless)
- Sensitive data that shouldn't leave local machine (Gemini sends to Google API)
- Tasks where Claude subagent can do the same thing WITH file access
