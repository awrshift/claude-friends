<div align="center">

![Claude Code](https://img.shields.io/badge/Claude%20Code-D97757?style=for-the-badge&logo=claude&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

# Don't Ask Me

Claude checks its own work with a second AI before it bothers you.

</div>

---

## What this is

You ask Claude to write something. Before it gives you the answer, it quietly asks Gemini what's wrong with it. For bigger decisions, it also asks a second Claude (running with no memory of your conversation) to look for blind spots. You see what the two reviewers agreed on, where they disagreed, and the version Claude wants to ship.

That's it. Three review modes. Claude picks which one based on what you typed.

## When you'd use it

You wrote a launch announcement and you're not sure the wording lands. You're picking between three architecture options and going in circles. You shipped a fix three times and it still doesn't work and you're tempted to try a fourth. You're writing pricing copy for a regulated industry and one wrong word costs you.

The skill is for moments where one AI is not enough but you don't want to read three separate AI outputs and reconcile them yourself.

## The three modes

You don't pick the mode. Claude reads what you typed and picks. Here's what they look like.

**Second opinion** is for when you're not sure. You say something like "sanity check this brief" or "am I missing anything in this plan". Claude sends your work to one reviewer (either Gemini or an isolated Claude Opus, depending on what you're checking). The reviewer comes back with top concerns and hidden assumptions. Claude reads the critique, tells you which parts hold up and which don't, and you decide. Costs around 1-5 cents.

**Full review** is the headline. You say "run a full review on this" or "this is important, double-check it before I send". Claude sends your work to both reviewers at the same time. They don't see each other's responses, so they can't agree out of politeness. Claude builds a small table: what each reviewer flagged, where they agreed, where they disagreed, and what to actually change. The disagreements are usually where the real value is. Costs around 5-8 cents. Worth it for anything you can't easily walk back.

**Group discussion** is for when you have two or three viable options and you're stuck choosing. You say "help me pick between these three angles" or "brainstorm options for the homepage". Claude runs a three-round debate with Gemini: round one generates seven or more ideas, round two kills the weak ones down to two or three survivors, you weigh in, round three picks one and writes a concrete plan with a go/no-go signal. Takes 5-10 minutes and costs about 25 cents.

If you're just asking for a fact ("what's the current Next.js version") that's not this skill. Claude Code already has a search tool. Use that.

## Three things that actually happened with this

**The landing page nobody could fix.** We were rebuilding a marketing page against a reference site. First pass looked off but we couldn't articulate why. Two screenshots and one Gemini call later, we had a list of specific CSS fixes per section. Second pass was good enough to ship. Without this loop we'd probably still be there saying "hmm, looks better, maybe?".

**The bug at 2am.** A streaming endpoint was timing out. We tried three fixes and none worked. Sent the bug plus the three failed attempts to Gemini. Thirty seconds later it said the timer logic was wrong: one timer was eating the whole budget, we needed two separate timers with different cutoff behavior. That was the architectural reframe we couldn't see from inside the code.

**The compliance disaster we caught at draft time.** A product feature for financial advisors. Copy looked fine to us. We ran a full review. Gemini caught language that would have triggered a US strict-liability rule. The isolated Claude caught a separate omission that would have failed a FINRA disclosure requirement. Neither reviewer caught the other one's issue. Both were real. We fixed both before shipping. One reviewer would have caught one of them, maybe.

We've run the full review six times in one architecture session, and every single one came back with a load-bearing problem we'd missed. The validation overhead was about 4% of session time. The cost of being wrong was an ADR rewrite or a production incident. Math works.

## What it costs

Single review: 1-5 cents per call. Full review (both reviewers): 5-8 cents. Group discussion (three rounds): about 25 cents. If you accidentally trigger validation on something small, no big deal. Your monthly cost stays in single dollars unless you're running hundreds of validations per day.

The rule of thumb is simple: cost of validating is almost always less than the cost of being wrong times the chance of being wrong. The full review is the same price as a coffee and catches things that would cost you a customer.

## Install

```
/plugin marketplace add awrshift/skill-dont-ask-me
```

That handles everything.

If you'd rather do it by hand:

```bash
mkdir -p ~/.claude/skills/dont-ask-me/{scripts,references,agents}
curl -sL https://raw.githubusercontent.com/awrshift/skill-dont-ask-me/main/SKILL.md \
  -o ~/.claude/skills/dont-ask-me/SKILL.md
curl -sL https://raw.githubusercontent.com/awrshift/skill-dont-ask-me/main/scripts/gemini.py \
  -o ~/.claude/skills/dont-ask-me/scripts/gemini.py
curl -sL https://raw.githubusercontent.com/awrshift/skill-dont-ask-me/main/agents/idea-validator.md \
  -o ~/.claude/agents/idea-validator.md
```

## Setup

Three steps, two minutes, once.

1. Get a Gemini API key at [aistudio.google.com](https://aistudio.google.com). Click "Create API Key", copy it.
2. Add `GOOGLE_API_KEY=your_key_here` to your `.env` file.
3. Run `pip install google-genai`.

Gemini has a free tier that's enough for personal use. No credit card needed to start.

To confirm the full review will work, check that the second reviewer file landed where it should: `ls ~/.claude/agents/idea-validator.md`. The plugin install does this for you, but worth verifying once.

## Why two AIs from different labs

If both reviewers come from the same lab, they share training data and they share the same blind spots. Two voices saying the same thing.

Gemini and Claude are trained differently. Where Claude gets confidently wrong, Gemini often gets it right. Where Gemini gets it wrong, Claude does. The disagreements are where the value lives.

The isolated Claude is the same model family as your main Claude, but it has no memory of your conversation. It can't be primed by your framing. It comes in cold and reads only the artifact you sent.

So the full review gives you three independent angles instead of three voices repeating the same answer. In practice, that's the difference between catching a problem at draft time and finding it after a customer complaint.

---

<details>
<summary><strong>For developers: CLI, internals, migration</strong></summary>

### CLI commands

All commands work from any shell once `GOOGLE_API_KEY` is set.

```bash
GEMINI=~/.claude/skills/dont-ask-me/scripts/gemini.py

# Single critique (adversarial system prompt)
python3 $GEMINI second-opinion @prompt.txt --save out.md

# Deep reasoning with high thinking
python3 $GEMINI think "Design a caching strategy for 10M users"

# Visual comparison
python3 $GEMINI second-opinion @prompt.txt --image ours.png --image ref.png --save review.md

# Structured extraction
python3 $GEMINI extract "Parse this invoice..." --json-mode

# Parallel batch
python3 $GEMINI second-opinion @aspect1.txt --save r1.md &
python3 $GEMINI second-opinion @aspect2.txt --save r2.md &
wait
```

### Models

`gemini-3.5-flash` is the primary model for everything (ask, second-opinion, think, extract). Cheap, fast, frontier on agentic and coding benchmarks.

`gemini-3.1-pro-preview` is available via the `-m` flag for pure-math reasoning where Flash falls short (ARC-AGI-style problems). In a controlled A/B on adversarial critique, Flash 3.5 beat Pro by 5 findings, ran 22% faster, cost 33% less, and had zero factual errors. So Pro stays as a fallback, not a default.

### How full review actually runs

Claude writes the artifact, then sends two tool calls in the same response:

```python
# Bash call
python3 ~/.claude/skills/dont-ask-me/scripts/gemini.py second-opinion @prompt.md --save gemini-out.md

# Agent call to the isolated Opus subagent (same message)
Agent(subagent_type="idea-validator", prompt="<artifact pasted inline>")
```

Same message is non-negotiable. If you do them sequentially, the second reviewer sees the first reviewer's output in the tool result and you lose independence. Two echoes instead of two minds.

Then Claude reads both outputs, builds an acceptance ledger (concern, what Gemini said, what Opus said, Claude's take, action), evaluates the critique against your project context, and presents to you. You make the final call. The skill never votes between the two AIs.

### Things to avoid

Don't send `@file:` references in Gemini prompts. Gemini Flash will silently hallucinate content when the file ref fails to load and you'll get a plausible-looking review that cites identifiers from a file that wasn't actually there. Paste content inline. Verify identifiers in the response match your input.

Don't ask Gemini before you've formed your own opinion. The skill is a validator, not a seed. If Claude goes to Gemini without a thought-through position first, it's easy to accept whatever Gemini says, and Gemini doesn't have your codebase context.

Don't use full review for trivial stuff. Save it for genuinely high-stakes work.

Don't forward reviewer output as-is. The reviewer is input for your decision, not the decision itself. Filter through what you know that the reviewer doesn't.

### File layout

```
SKILL.md                       read by Claude when the skill triggers
scripts/gemini.py              CLI wrapper around the Gemini API
agents/idea-validator.md       the isolated Opus subagent (copy to ~/.claude/agents/)
references/
  round-table.md               full three-round group discussion protocol
  dual-validation.md           parallel call protocol and ledger format
  decision-framework.md        which reviewer to pick when
  critical-evaluation.md       why reviewer output is not your decision
  models.md                    Gemini model specs and pricing
  parameters.md                all CLI flags
```

### Migrating from `awrshift/skill-gemini` or `awrshift/skill-brainstorm`

This skill replaces both.

```
/plugin marketplace remove awrshift/skill-gemini
/plugin marketplace remove awrshift/skill-brainstorm
/plugin marketplace add awrshift/skill-dont-ask-me
```

All previous CLI commands work unchanged. The new pieces are the full review (parallel dual validation with the isolated subagent), the group discussion (was the brainstorm skill, now a built-in mode), and the style router that picks based on what you type.

`awrshift/skill-gemini` got renamed to `awrshift/skill-dont-ask-me` so the old URL redirects. `awrshift/skill-brainstorm` is archived with a pointer to this repo.

</details>

---

## License

MIT.

## Contributing

PRs welcome. Useful contributions: edge cases where the full review missed something and why, simpler ways to explain any concept that's still confusing, new chat phrases that should trigger a mode but currently don't.

Open an issue or PR at [github.com/awrshift/skill-dont-ask-me](https://github.com/awrshift/skill-dont-ask-me).
