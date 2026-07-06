# Critical Evaluation Rule — Why Reviewer Output ≠ Decision

> Reviewer responses (Gemini second-opinion, idea-validator Opus, Round-Table outputs) are INPUT for decision-making, not the decision itself.

## The rule

After every reviewer call, Claude MUST:

1. **Challenge each recommendation** — ask "do we know this is true, or is the reviewer speculating?"
2. **Check for missing context** — reviewer doesn't see codebase, prior decisions, project constraints, or your stack-specific conventions
3. **Verify numbers** — predictions like "90% speedup" or "20s expected latency" are estimates, not measurements
4. **Look for what reviewer missed** — implementation complexity, side effects, existing code interactions
5. **Present critical assessment to user** — table with "Reviewer said / My evaluation / Reason / Action" for each point

## Workflow

```
Reviewer recommends
  → Claude evaluates critically
  → present BOTH (reviewer output AND Claude's evaluation) to user
  → user decides
```

Skipping the middle step = forwarding reviewer output as-is. This is the most common anti-pattern.

## Anti-patterns (do NOT do these)

### 1. Forwarding reviewer output as-is

Bad:
> "Gemini says we should switch to PostgreSQL. Should I do that?"

Good:
> "Gemini suggested PostgreSQL switch with these reasons (X, Y, Z). I evaluate:
> - X: valid in our case (we have row-level locking needs)
> - Y: doesn't apply (we already use connection pooling)
> - Z: speculation (Gemini doesn't see our actual query patterns)
> My take: defer the switch — Y and Z don't move the needle, X alone isn't worth the migration cost. Your call."

### 2. Accepting all recommendations without questioning

Bad:
> Reviewer returned 8 concerns. Claude implements all 8.

Good:
> Reviewer returned 8 concerns. Claude addresses the 3 with concrete evidence in the codebase, pushes back on 2 that contradict our existing patterns, surfaces 3 as "low-confidence — need user input."

### 3. Using reviewer confidence as proxy for correctness

Bad:
> "Gemini sounded very confident, so this must be right."

Good:
> Confidence ≠ correctness. Gemini Flash is trained to sound confident. Evidence > tone.

### 4. Skipping critical evaluation "because the reviewer is smart"

Bad:
> "Opus is the smartest model, so its critique is authoritative."

Good:
> Smart doesn't mean right when the reviewer lacks context. Opus subagent has no parent conversation context by design — it can miss things Claude knows about.

### 5. Voting between two AIs in Boardroom Debate

Bad:
> "Gemini and Opus both said X, so we do X."

Good:
> Both agreeing is high-signal (worth addressing) but not majority rule. Claude evaluates whether their shared concern actually applies to OUR project's specific constraints. Sometimes both are wrong about the same thing because they share a common blind spot (e.g., both might miss that we have a hard regulatory requirement that overrides their architectural preference).

## Why this rule exists

Reviewers don't see:
- Your codebase and its conventions
- Prior decisions documented in ADRs / CLAUDE.md / memory
- Team-specific constraints (Vadim's review style, BA approval flow)
- Cost/latency reality of your stack
- Customer feedback already received
- What you've already tried and ruled out

A confident-sounding recommendation that ignores any of these factors is wrong-by-default. Critical evaluation is the step that filters reviewer output through what you (and Claude) know that the reviewer doesn't.

## Special case: dual-validation disagreement

When Gemini says X and Opus says NOT-X, this is the highest-value finding in Boardroom Debate. Two model families disagreeing means:

- They surfaced something genuinely contested
- One has context the other doesn't (Gemini has different training data; Opus has different reasoning patterns)
- The "right answer" depends on context only Claude+user know

Don't pick a side mechanically. Investigate WHY they disagree, present both positions with Claude's reasoning about which applies to YOUR situation, let user decide.

## Cost of skipping critical evaluation

Per Session #142 (L4.1 topic clusterer, 2026-05-16): Claude initially proposed "Gemini critique on module design" as FIRST step. Sergey stopped — this turns Gemini into a SEED for the decision, not a validator. Without own thought-through position first, accepting Gemini's recommendation uncritically becomes the path of least resistance. Gemini lacks codebase context — easy to buy a bad idea that "sounds confident."

Codified rule: Own deep thinking FIRST, reviewer SECOND. Then critical evaluation of reviewer's output BEFORE presenting to user.

## How to present a critical evaluation

Standard format — acceptance ledger:

| # | Reviewer concern | Reviewer reasoning | My evaluation | Reason | Action |
|---|---|---|---|---|---|
| 1 | "Switch to PG" | scalability X | Valid for our row-locking case | We have row-locking | Defer to phase 2 |
| 2 | "Use Redis" | speed Y | N/A — we already pool | Existing impl covers | Reject |
| 3 | "Add CDN" | latency Z | Speculation, no measurement | Reviewer guessed | Need data first |

Five columns are non-negotiable. Reviewer output + evaluation + reason + action — without all four, the ledger doesn't filter speculation from signal.

## Related

- `dual-validation.md` — parallel-call protocol that produces the input for critical evaluation
- `decision-framework.md` — when to use which reviewer (the upstream question)
- Skill anti-pattern #5 (in main `SKILL.md`) — accepting output as-is

---
Last verified: 2026-05-27 (consolidated from rnd-hub project `gemini.md` rule + feedback files)
