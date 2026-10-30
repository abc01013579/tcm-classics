"""One-time parser: journal/*.md -> data/journal.json.

Run manually, not imported by app.py. Each entry is a Markdown file
named YYYY-MM-DD-slug.md with a small frontmatter block:

---
title: 标题
date: 2026-07-16
---

正文，支持 **Markdown** 格式。

The filename (minus .md) becomes the entry's URL slug.

Optional bilingual entries: put an `<!--en-->` marker on its own line
after the Chinese body, followed by an English translation. Paragraphs
(split on blank lines) are paired 1:1 by position with the Chinese
paragraphs above the marker -- same convention as data/xinjing.json --
so the Chinese and English paragraph counts must match exactly, or
build fails loudly rather than silently misaligning the zip.
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
EN_MARKER = "<!--en-->"

# A YouTube link at the end of a line (alone or after a label like
# "talk: https://...") becomes a clickable link plus an embedded player.
YOUTUBE_RE = re.compile(
    r"^(.*?)(https?://(?:www\.|m\.)?(?:youtube\.com/(?:watch\?v=|shorts/)|youtu\.be/)"
    r"([\w-]{11})\S*)\s*$"
)


def _embed_youtube(text):
    out = []
    in_fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else YOUTUBE_RE.match(line)
        if not m:
            out.append(line)
            continue
        label, url, video_id = m.groups()
        if label.strip():
            out.append(f'{label}<a href="{url}">{url}</a>')
            out.append("")
        out.append(
            f'<div class="video-embed"><iframe src="https://www.youtube.com/embed/{video_id}" '
            'title="YouTube video" allowfullscreen loading="lazy"></iframe></div>'
        )
        out.append("")
    return "\n".join(out)


def _render(text):
    return markdown.markdown(_embed_youtube(text), extensions=["tables", "fenced_code"])


def _strip_p_tag(html):
    if html.startswith("<p>") and html.endswith("</p>"):
        return html[3:-4]
    return html


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

    bilingual = EN_MARKER in body
    pairs = None
    if bilingual:
        zh_part, en_part = body.split(EN_MARKER, 1)
        zh_paragraphs = [p.strip() for p in zh_part.strip().split("\n\n") if p.strip()]
        en_paragraphs = [p.strip() for p in en_part.strip().split("\n\n") if p.strip()]
        if len(zh_paragraphs) != len(en_paragraphs):
            raise ValueError(
                f"{path.name}: {len(zh_paragraphs)} zh paragraphs vs "
                f"{len(en_paragraphs)} en paragraphs -- must match 1:1"
            )
        pairs = [
            (
                _strip_p_tag(_render(zh)),
                _strip_p_tag(_render(en)),
            )
            for zh, en in zip(zh_paragraphs, en_paragraphs)
        ]
        body = zh_part.strip()

    return {
        "slug": path.stem,
        "date": meta["date"],
        "title": meta["title"],
        "body_text": body,
        "html": _render(body),
        "bilingual": bilingual,
        "pairs": pairs,
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
