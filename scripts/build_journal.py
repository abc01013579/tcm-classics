"""One-time parser: journal/*.md -> data/journal.json.

Run manually, not imported by app.py. Each entry is a Markdown file
named YYYY-MM-DD-slug.md with a small frontmatter block:

---
title: 标题
date: 2026-07-16
---

正文，支持 **Markdown** 格式。

The filename (minus .md) becomes the entry's URL slug.
"""
import json
import re
import sys
from pathlib import Path

import markdown

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
JOURNAL_DIR = ROOT / "journal"
DATA = ROOT / "data"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_entry(path):
    raw = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(raw)
    if not m:
        raise ValueError(f"{path.name}: missing '---' frontmatter block")
    front, body = m.groups()

    meta = {}
    for line in front.splitlines():
        line = line.strip()
        if not line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()

    if "title" not in meta or "date" not in meta:
        raise ValueError(f"{path.name}: frontmatter needs both 'title' and 'date'")

    body = body.strip()
    return {
        "slug": path.stem,
        "date": meta["date"],
        "title": meta["title"],
        "body_text": body,
        "html": markdown.markdown(body),
    }


def build():
    entries = [parse_entry(path) for path in sorted(JOURNAL_DIR.glob("*.md"))]
    entries.sort(key=lambda e: e["date"], reverse=True)

    (DATA / "journal.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(entries)} journal entries to {DATA / 'journal.json'}")


if __name__ == "__main__":
    build()
