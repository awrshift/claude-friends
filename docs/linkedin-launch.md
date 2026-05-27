# LinkedIn Launch Post

Draft for the public announcement of `/dont-ask-me` on LinkedIn.
6-slide carousel + post body. English version below; Russian is a TODO.

---

## Post body

```
Caught yourself doing this lately?

The AI generates a wall of code. Then asks:
"Want me to use approach A, B, or C? I'd recommend B."

You stare at the options. You have no real way to verify
which one is right. You shrug. "Yeah, go with B." Ship.

That's the silent failure mode of every AI-assisted
developer in 2026. Including me — until I stopped doing it.

6 months of writing production code with Claude, 24/7,
and I realized: I was making 50 "informed" decisions a
day that weren't informed at all. The model wasn't
deceiving me. The structure was. One model presents
options + its own recommendation = a choice with no
choice. You don't have the expertise to push back on
every claim. You shouldn't have to.

So I built a cheat code.

/dont-ask-me — open-source plugin for Claude Code.

Next time the AI asks you to validate its recommendation,
you don't fake expertise. You just say:

  "ask Gemini about this"
  "sanity check that"
  "what would another model say?"

Claude takes its own answer to a different model family
(Gemini, or an isolated second Claude with no memory of
your conversation). The second model reviews in isolated
context, via a structured prompt — not "what's the truth",
but "what did the first model miss". That's the fact-check
you weren't doing because you couldn't.

Then Claude doesn't blindly accept the critique either.
It weighs the second opinion against your code, your docs,
your repo — and shows you both sides as a small ledger.
You make the call from a real position.

Two model families. Different blind spots. Critical
synthesis. Not consensus, not voting — your decision,
informed.

Two holes of vibe-coding closed in one move:
1. Blind agreement with one model's confidence.
2. The fact-check step you keep skipping.

Works with Claude + Gemini. Works with any two models
from different labs — the strength isn't the models,
it's the structure.

Open-source. MIT. Plugin for Claude Code.

→ github.com/awrshift/skill-dont-ask-me

#ClaudeCode #AI #VibeCoding #DevTools #Anthropic
```

---

## Carousel — 6 slides, in this exact order

| # | Slide | File |
|---|---|---|
| 1 | CHOICE WITH NO CHOICE — hook | `assets/carousel/01-choice.png` |
| 2 | × 50 TIMES A DAY — repetition pain | `assets/carousel/02-repeat.png` |
| 3 | THE CHEAT CODE — solution in one phrase | `assets/carousel/03-cheat-code.png` |
| 4 | DIFFERENT FAMILY. DIFFERENT BLIND SPOTS — how it works | `assets/carousel/04-isolated.png` |
| 5 | NOT CONSENSUS. NOT VOTING — critical synthesis | `assets/carousel/05-synthesis.png` |
| 6 | SHIP WITH CONVICTION — CTA with URL | `assets/carousel/06-ship.png` |

---

## Publication checklist

- [ ] Upload 6 carousel images in order (LinkedIn carousel post type, NOT single image)
- [ ] Paste post body above
- [ ] Verify hashtags rendered as links (LinkedIn may need a refresh)
- [ ] Post timing: Tue/Wed/Thu, 8-10am PST or 12-2pm NYC for US tech audience
- [ ] Within 30 minutes of publishing: drop one comment of your own continuing the thread (extends reach via algorithm)
- [ ] Pin the post to your profile for the first 48 hours

---

## TODO

- [ ] Russian translation (if dual-language feed)
- [ ] Short-form variant for X/Twitter (single image + 280 chars)
- [ ] Dev.to / Hashnode mirror (Markdown port — README already covers most of it)
