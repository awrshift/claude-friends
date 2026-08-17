# Contributing

Issues and PRs welcome. Two things this repo is strict about, because they are what the product
sells:

## 1. A model id is a dated claim

`skills/claude-friends/references/models.md` is the whitelist, and it carries the date it was
last checked against the live API. Anything that names a model — a script default, a doc, a
table — must use an id that appears there; `tools/check-repo.py` fails the build otherwise.

Re-verify by asking the API, never the release notes you remember:

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY&pageSize=200" \
  | python3 -c "import sys,json;[print(m['name']) for m in json.load(sys.stdin)['models']]"
curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY" \
  | python3 -c "import sys,json;[print(m['id']) for m in sorted(json.load(sys.stdin)['data'], key=lambda x: x['id'])]"
```

A newer model existing is not a reason to re-pin on its own. State what you measured, then move
the default — the whitelist is a claim about what is *best for these three styles*, not about
what is newest.

## 2. Everything that ships must run

Before pushing:

```bash
python3 tools/check-repo.py            # manifests, links, assets, model ids
claude plugin validate .               # the marketplace and the plugin manifest
python3 skills/claude-friends/scripts/gemini.py ask "reply OK"
env -i HOME=/tmp/nokeys PATH="$PATH" python3 skills/claude-friends/scripts/gemini.py ask "hi"   # must fail clearly
```

The last one matters more than it looks: a missing key is the first thing a new user hits, and a
stack trace there costs more users than any feature gains.

## Style

- Docs in English, plain, no filler. If a sentence does not change what the reader does, cut it.
- One home per fact. A number restated in three files is two stale copies waiting to happen.
- A decision that needs the maintainer goes on the board (`docs/DECISIONS.md`), not into prose.
