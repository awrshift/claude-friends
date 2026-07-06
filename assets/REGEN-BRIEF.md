# Graphics regeneration brief — Claude Friends

The carousel + banner still carry the old "Don't Ask Me / ask Gemini" narrative. This brief re-scripts
them for **Claude Friends** ("ask your friends"). Keep the existing look so the set stays coherent.

## Style lock (all slides)
- Hand-drawn black-ink **stick-figure comic** (xkcd / whiteboard doodle), white background, thin black border box.
- **Exactly one accent color** — the Claude terracotta `#D97757` — used sparingly (a shirt letter, a highlight, a heart). Everything else is black on white.
- Hand-drawn **CAPS title** across the top; hand-drawn **lowercase caption** (1–2 lines) across the bottom.
- Square **1024×1024** (carousel). Banner (`og-banner.png`) is wide — same style, single strong line.
- Loose, slightly-wonky lettering is on-brand; don't chase perfect type.

## The narrative arc (what changes)
Slides 1–2 (the problem) stay. Slide 3 is the pivot — the solution is no longer "a cheat code: ask Gemini"
but "**ask your friends**". Slides 4–6 keep their idea, reskinned to the friends motif.

| # | file | TITLE (top) | Scene | CAPTION (bottom) |
|---|---|---|---|---|
| 1 | `01-choice.png` | CHOICE WITH NO CHOICE | *(unchanged)* confused figure; a smug figure holds an A/B/C list, shirt reads **C** (accent) | AI gives you 3 options. And tells you which is best. |
| 2 | `02-repeat.png` | ...50 TIMES A DAY | *(unchanged)* the same figure nodding along, small clock/repeat marks | You just nod. Every single time. |
| 3 | `03-friends.png` **(rename)** | ASK YOUR FRIENDS | The worried figure turns to **three friends** side by side — one with a 🔷 (Google), one a plain twin labelled "fresh eyes", one with a ⚫ (accent heart on the middle one). Old "cheat code / Gemini" gag GONE. | Claude has friends. When it matters, it asks them. |
| 4 | `04-isolated.png` | DIFFERENT MINDS, DIFFERENT BLIND SPOTS | Two friends look at the same drawing on an easel; each circles a *different* flaw (one accent circle) | Where one is blind, another sees. |
| 5 | `05-synthesis.png` | NOT A VOTE | The main figure at a table with the friends' notes, drawing its OWN conclusion (accent check on the chosen one) | You still decide. Friends are input, not a vote. |
| 6 | `06-ship.png` | SHIP WITH FRIENDS | The figure confidently shipping a box/rocket, the three friends giving a thumbs-up (one accent) | Decide with conviction. Not alone. |

## Banner (`og-banner.png`)
One figure in the center, three smaller friend-figures around it, a single accent line/heart connecting them.
Wordmark: **Claude Friends**. Sub: *ask your friends.* Terracotta accent only.

## How to regenerate
The originals look image-model-generated. Reproduce with an image model (e.g. Gemini Nano Banana Pro)
using the style-lock above as the system framing and one slide's TITLE + scene + CAPTION per prompt.
Generate 3–4 variants per slide, pick the one whose text is cleanest, iterate on the pivot slide (#3) first.
Rename `03-cheat-code.png` → `03-friends.png` and update the `<img>` in `README.md`.
