# Dual Validation — Opus Subagent + Gemini in Parallel

For non-trivial design decisions, get two independent second opinions in parallel: the `idea-validator` sub-agent (isolated Claude Opus, no parent context) and Gemini 3.5 Flash (different model family — post-audit 2026-05-20, replaced 3.1 Pro as default for adversarial critique). Two independent angles catch more blind spots than one.

## When to apply

Elevate from standard single Gemini second-opinion to dual validation for:

- Architecture decisions before locking in
- Multi-step plans with ≥3 dependent stages
- New patterns/conventions before codifying
- Hypothesis falsification (ICF-Research phases)
- Prompt design for core logic

For single-file code review or fact-checking a number — single opinion suffices. Dual validation is for high-stakes design moments.

## How to call (parallel — single message, two tool uses)

Both calls MUST go in the same response. If one sees the other's output first, independence is destroyed.

```python
# Tool call 1: isolated Opus sub-agent
Agent(
    subagent_type="idea-validator",
    description="Validate <design name>",
    prompt="<self-contained design/idea/plan as artifact>"
)

# Tool call 2: Gemini (in the SAME message — runs in parallel)
Bash(
    command='python3 ~/.claude/skills/gemini/gemini.py second-opinion @prompt.txt --save tmp/gemini-out.md'
)
```

Alternative shell-only pattern (for non-Agent contexts):

```bash
# Run both in background, wait for both
(claude-code-subagent idea-validator < prompt.txt > opus-out.md &)
(python3 ~/.claude/skills/gemini/gemini.py second-opinion @prompt.txt --save gemini-out.md &)
wait
```

## Output: single acceptance ledger

After both return, build ONE table:

| # | Concern | Opus says | Gemini says | My evaluation | Action |
|---|---|---|---|---|---|

Three outcome classes per concern:

- **Both agree** → high-signal, must address
- **One raises, other silent** → medium-signal, evaluate whether the silent one had enough context to notice
- **They disagree** → highest-value finding. Different model perspectives surfaced different things — investigate which is right (and why)

## Anti-patterns

- **Sequential calls** — destroys independence (the second agent sees the first one's framing)
- **Merging into a single summary without the ledger** — loses disagreement signal, which is the most valuable output
- **Accepting any output as-is** — same critical-evaluation rule as for single Gemini (see main SKILL.md § Critical Evaluation Rule). Output is INPUT for decisions, not the decision itself
- **Using dual validation for routine checks** — overkill burns context and time. Save it for genuinely high-stakes design moments

## Why this pattern

- **Opus sub-agent** — same model family as parent, but isolated context. Gives deep reasoning without inherited blind spots from the parent's framing.
- **Gemini Pro** — different model family entirely. Catches what Anthropic-family models don't see.

Combining both = two independent angles, not two echoes.
