# Open decisions — the board

Decisions that need the maintainer, not the agent. One row each: the question, the
recommendation, and what it costs to be wrong. Settled ones move to `CHANGELOG.md` and leave
this board.

## Naming and distribution

| # | Question | Recommendation | Cost of being wrong |
|---|---|---|---|
| D1 | The marketplace is registered as `awrshift-claude-friends`, so users install with `@awrshift-claude-friends` while the plugin, repo and skill are all `claude-friends`. Rename the marketplace? | **Not yet.** Each user registers one marketplace per name; renaming silently orphans everyone who already added it, and the gain is cosmetic. Do it only alongside a release note that spells out the re-add step. | Medium — breaks existing installs. |
| D2 | Submit to the community marketplace (`anthropics/claude-plugins-community`)? | **Yes, once the model whitelist has a dated re-verification in place** (see D4). A plugin whose whole value is "the friends are current" cannot ship with a stale pin table. | Medium — a public listing pins a commit and is a public first impression. |
| D3 | Keep GPT as an opt-in third family, or promote it to a default friend? | **Keep it opt-in.** It needs a paid key, and the third leg's marginal value over Gemini + fresh-eyes Claude is modest outside the highest-stakes reviews. | Low. |

## The friends themselves

| # | Question | Recommendation | Cost of being wrong |
|---|---|---|---|
| D4 | The whitelist claims "nothing has displaced 3.5 Flash", but `gemini-3.6-flash` and `gemini-3.7-flash` are live, and the GPT table calls `gpt-5.6` preview-only while three 5.6 variants are serving. Re-pin now, or measure first? | **Measure, then re-pin.** Both current pins still work, so nothing is broken — but a whitelist is a claim about what is best, and it is now two generations behind. Run the same head-to-head this repo used in the 2026-05 audit before moving the default. | Low to fix, high to leave: the product's promise is currency. |
| D5 | Should the skill's `description` keep the full trigger-phrase catalogue? | **Trim it.** Every character of a skill description sits in context for every session of every user, and the catalogue is ~1.4k characters of near-duplicates. Keep the distinct intents; the README's `<details>` block can hold the long list. | Low. |
| D6 | Reviewers see the brief only, never the repo (except the isolated Claude, which reads files). Make repo-reading available to Gemini via a bundled file-passer? | **No.** It multiplies token cost and pastes private code into a second vendor. The current split — external family for concepts and currency, isolated Claude for file-level facts — is the honest one. | Low, but reversing later is awkward once users expect it. |

## Recently settled

- Renamed from *Don't Ask Me* → *Claude Friends* (v3.0.0). The old repo slug still redirects.
- MCP dropped in favour of CLI scripts: one less moving part, and the scripts are inspectable.
