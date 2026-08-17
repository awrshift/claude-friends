# Changelog

Notable changes. Breaking changes marked **BREAKING**.

<a id="v400"></a>

## [4.0.0] — 2026-08-17 — Standards pass

No change to how the three review styles behave. This release makes the repository hold itself
to the discipline the skill preaches.

### Added

- **`.claude-plugin/plugin.json`** — the plugin shipped without a manifest, so its name, version
  and description came only from the marketplace entry.
- **`VERSION`** as the single source of the version number; `tools/check-repo.py` fails the build
  if the manifest or the marketplace entry drifts from it.
- **`tools/check-repo.py` + CI** — manifests agree, declared skill directories exist, the CLI
  scripts compile and still expose the commands the docs promise, every link and image resolves,
  no asset is orphaned, and **no document names a model outside the whitelist**.
- **A keyless-path test.** Both CLIs must fail with a clear "set your key" message rather than a
  stack trace — verified in CI with an empty environment, since the scripts also read
  `~/.gemini/api_key` and a bare unset passes on any machine that has the file.
- **`docs/DECISIONS.md`** — the open-decisions board: the marketplace-name mismatch, the stale
  whitelist, whether GPT stays opt-in, and whether reviewers should ever read the repo.
- **`docs/CONTRIBUTING.md`** — how to re-verify a model pin against the live API, and what to run
  before pushing.

### Changed

- **README rebuilt.** Install moved above the fold, one image instead of six, an explicit
  "what it will not do" section, and the trigger catalogue collapsed into a `<details>` block.
  The rename note moved here, where history belongs.
- `metadata.homepage` moved out of the marketplace entry (Claude Code ignores it there and the
  validator warns) into the plugin manifest.

### Verified, not assumed

Both CLIs were run end-to-end against the live APIs on 2026-08-17: Gemini answered on
`gemini-3.5-flash`, OpenAI on `gpt-5.4`. The whitelist's pins are alive — and two generations
behind what the API now serves. That gap is on the board as D4 rather than silently re-pinned,
because moving the default is a measurement, not a version bump.

<a id="v300"></a>

## [3.0.0] — 2026-07-06 — Claude Friends

Renamed from *Don't Ask Me*: it was never about not asking — it is about asking the right
friends. The old repo slug (`awrshift/skill-dont-ask-me`) still redirects. Merged the earlier
`skill-gemini` and `skill-brainstorm` skills, added the optional GPT third family, and moved off
MCP to plain CLI scripts.
