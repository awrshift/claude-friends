#!/usr/bin/env python3
"""Repo integrity checks — the drift this kit keeps finding in other people's repos.

Deterministic, stdlib-only, no auth: runs in CI and on your machine identically.

  1. manifests parse, and VERSION / plugin.json / marketplace.json agree
  2. every marketplace `source` and every declared skill directory exists
  3. every skill has frontmatter with a description; every agent has a name
  4. the CLI scripts compile and expose the commands the docs promise
  5. every relative link and every image embed in the markdown resolves
  6. no asset is orphaned (nothing embeds it)
  7. every model id named in the docs is on the whitelist in references/models.md

usage: python3 tools/check-repo.py     # exit 1 on any failure
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fail: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        fail.append(msg)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — any parse problem is a failure
        fail.append(f"{path}: {exc}")
        return None


# 1 + 2 — manifests -----------------------------------------------------------------
version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
market = load(ROOT / ".claude-plugin" / "marketplace.json") or {}
check(market.get("metadata", {}).get("version") == version,
      f"marketplace metadata.version != VERSION {version}")
for entry in market.get("plugins", []):
    src = (ROOT / entry["source"]).resolve()
    check(src.exists(), f"marketplace entry {entry['name']}: source {entry['source']} does not exist")
    check(entry.get("version") == version,
          f"marketplace entry {entry['name']}: version {entry.get('version')} != VERSION {version}")
    for skill_dir in entry.get("skills", []):
        d = (ROOT / skill_dir).resolve()
        check((d / "SKILL.md").exists(), f"declared skill dir has no SKILL.md: {skill_dir}")
plugin = load(ROOT / ".claude-plugin" / "plugin.json") or {}
check(plugin.get("version") == version, f"plugin.json: version {plugin.get('version')} != VERSION {version}")

# 3 — the CLI scripts the whole product rests on -------------------------------------
import py_compile

for script in ROOT.glob("skills/*/scripts/*.py"):
    try:
        py_compile.compile(str(script), doraise=True)
    except Exception as exc:  # noqa: BLE001
        fail.append(f"{script.relative_to(ROOT)}: does not compile — {exc}")
    body = script.read_text(encoding="utf-8")
    for cmd in ("ask", "second-opinion"):
        check(f'"{cmd}"' in body or f"'{cmd}'" in body,
              f"{script.relative_to(ROOT)}: no '{cmd}' command, but the docs promise it")

# 4 — skills and agents -------------------------------------------------------------
for skill in ROOT.glob("skills/*/SKILL.md"):
    head = skill.read_text(encoding="utf-8")[:1200]
    check(head.startswith("---"), f"{skill}: no frontmatter")
    check("description:" in head, f"{skill}: frontmatter has no description")
for agent in ROOT.glob("agents/*.md"):
    head = agent.read_text(encoding="utf-8")[:400]
    check(head.startswith("---") and "name:" in head, f"{agent}: no name in frontmatter")

# 5 + 6 — links and assets ----------------------------------------------------------
link_re = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
html_img_re = re.compile(r'<img[^>]+src="([^"]+)"')   # the README embeds the carousel as HTML
embedded: set[Path] = set()
for md in ROOT.rglob("*.md"):
    if ".git/" in str(md):
        continue
    body = md.read_text(encoding="utf-8", errors="ignore")
    for target in link_re.findall(body) + html_img_re.findall(body):
        target = target.split("#")[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (md.parent / target).resolve()
        check(resolved.exists(), f"{md.relative_to(ROOT)}: dead link -> {target}")
        if resolved.suffix.lower() in {".png", ".jpg", ".svg", ".gif"}:
            embedded.add(resolved)

for asset in ROOT.rglob("assets/**/*.png"):
    check(asset.resolve() in embedded, f"orphan asset: {asset.relative_to(ROOT)} is embedded nowhere")

# 7 — every model id in the docs must be whitelisted --------------------------------
models_doc = ROOT / "skills" / "claude-friends" / "references" / "models.md"
gpt_doc = ROOT / "skills" / "claude-friends" / "references" / "third-family-gpt.md"
whitelist: set[str] = set()
for doc in (models_doc, gpt_doc):
    if doc.exists():
        whitelist |= set(re.findall(r"`(gemini-[a-z0-9.-]+|gpt-[a-z0-9.-]+)`", doc.read_text(encoding="utf-8")))
# a family name (gemini-3, gpt-5) is prose; a pinned model has a minor version or a suffix
model_re = re.compile(r"\b(gemini-[0-9]+\.[0-9][a-z0-9.-]*|gemini-[0-9]+-[a-z][a-z0-9.-]*|gpt-[0-9]+\.[0-9][a-z0-9.-]*)\b")
for src in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.py")):
    if ".git/" in str(src) or src.name in {"models.md", "third-family-gpt.md", "CHANGELOG.md", "DECISIONS.md"}:
        continue
    for found in set(model_re.findall(src.read_text(encoding="utf-8", errors="ignore"))):
        check(found in whitelist,
              f"{src.relative_to(ROOT)}: model id `{found}` is not in the whitelist (references/models.md)")

# ----------------------------------------------------------------------------------
if fail:
    print(f"✗ {len(fail)} problem(s):")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("✔ repo checks passed")
