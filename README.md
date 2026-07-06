<div align="center">

![Claude Code](https://img.shields.io/badge/Claude%20Code-D97757?style=for-the-badge&logo=claude&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

# Don't Ask Me

**Stop nodding when AI hands you "options". Built-in second opinion from a model that doesn't share Claude's blind spots.**

</div>

---

<table>
<tr>
<td width="50%"><img src="assets/carousel/01-choice.png" alt="Choice with no choice"></td>
<td width="50%"><img src="assets/carousel/02-repeat.png" alt="x50 times a day"></td>
</tr>
<tr>
<td width="50%"><img src="assets/carousel/03-cheat-code.png" alt="The cheat code: ask Gemini"></td>
<td width="50%"><img src="assets/carousel/04-isolated.png" alt="Different family, different blind spots"></td>
</tr>
<tr>
<td width="50%"><img src="assets/carousel/05-synthesis.png" alt="Not consensus, not voting"></td>
<td width="50%"><img src="assets/carousel/06-ship.png" alt="Ship with conviction"></td>
</tr>
</table>

---

## Install

```
/plugin marketplace add awrshift/skill-dont-ask-me
```

Then set your Gemini key (free tier at [aistudio.google.com](https://aistudio.google.com)):

```bash
pip install google-genai

# Store the key once — read automatically by every shell, no `export` needed:
mkdir -p ~/.gemini && printf '%s' 'your_key_here' > ~/.gemini/api_key && chmod 600 ~/.gemini/api_key
```

> Prefer an env var? `export GOOGLE_API_KEY=your_key_here` works too and overrides the file.
> A bare `GOOGLE_API_KEY=...` line in `~/.env` will **not** work — nothing sources it in a fresh shell.

## Three modes — Claude picks one based on what you type

| Mode | Trigger phrase | What happens |
|---|---|---|
| **Second opinion** | *"sanity check"*, *"am I missing something"* | One reviewer (Gemini or isolated Claude). ~3¢ |
| **Full review** | *"this is important"*, *"run a full review"* | Both reviewers in parallel. ~7¢ |
| **Group discussion** | *"help me choose"*, *"brainstorm options"* | 3-round debate. ~25¢ |

## Just say what you need — no exact phrases required

Claude reads your intent and picks the right mode. Some natural ways to trigger each:

**Want a quick sanity check?**
> *"sanity check this"* · *"am I missing something"* · *"stress-test this"* · *"critique this"* · *"give me a second opinion"* · *"cross-check this"* · *"review this"* · *"thoughts?"* · *"is this right?"* · *"devil's advocate"* · *"poke holes in this"* · *"what could go wrong"*

**High-stakes, want both reviewers?**
> *"this is important"* · *"run a full review"* · *"check before I send"* · *"before publishing"* · *"big decision"* · *"high-stakes review"* · *"boardroom debate"* · *"dual validation"* · *"two independent opinions"* · *"don't let me ship something dumb"* · *"this can't be wrong"*

**Choosing between options?**
> *"help me choose between"* · *"brainstorm options"* · *"I have several paths"* · *"I have 3 angles on this"* · *"multiple options to weigh"* · *"diverge and converge"* · *"multi-round brainstorm"* · *"round-table discussion"* · *"compare these approaches"* · *"what's the best direction"*

**Calling a model directly?**
> *"ask Gemini"* · *"ask Opus"* · *"what would Gemini say"* · *"let's get a second model on this"* · *"another perspective please"*

If none of these fit, just describe what you're stuck on. Claude figures out which mode helps.

## Full docs

[**SKILL.md**](skills/dont-ask-me/SKILL.md) — how it works, when to invoke, anti-patterns, CLI reference.

## License

MIT. PRs welcome.
