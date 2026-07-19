# 中华典籍 (Chinese Classics Reader)

A Flask web app for browsing and searching Chinese classical texts: two Traditional Chinese Medicine classics, 《黄帝内经》(Huangdi Neijing — 素问 and 灵枢经, all 81+81 chapters, both fully bilingual Chinese/English) and 《神农本草经》(Shennong Bencao Jing, all 364 entries with bilingual Chinese/English text); 《周易》(Zhouyi / I Ching), all 64 hexagrams with bilingual Chinese/English text and line diagrams; 《心经》(the Heart Sutra) with bilingual text; and 随笔, a personal journal section. More classics are added over time.

## How it works

The TCM source texts started as raw plain-text scrapes (`sources/`), each bundling extra, unrelated classical texts appended after the wanted content with no clean separator. A one-time parser (`scripts/build_data.py`) extracts just the wanted portions into structured JSON (`data/`):

- **黄帝内经**: split into 素问 (81 chapters) and 灵枢经 (81 chapters), each `{number, title, paragraphs}`. Chapter boundaries are detected by column-0 `N. 标题` headers, filtered to exclude indented table-of-contents lines and stray footnote annotations. The source is missing the "10. 经脉" header in 灵枢经 (a transcription gap); the parser splices it back in at its known content anchor before parsing.
- **神农本草经**: split into 上卷/中卷/下卷, each an ordered list of `{number, text, is_header}` entries. Category dividers like `玉石部上品` are detected by an exact `<category>部<上/中/下>品` pattern and flagged `is_header`; everything else is a herb entry, with wrapped continuation lines reattached.

`scripts/build_data.py` asserts expected chapter/entry counts (81+81 neijing chapters, 10/273/99 bencao entries per juan, 18 category headers) before writing the JSON, so a parsing regression fails loudly instead of silently corrupting the data. It's run manually, not at request time — the app just loads the pre-built JSON.

**神农本草经's English translation** was produced by 14 parallel translation agents (~26 entries each, checked into `scripts/bencao_en_batches/` for reproducibility) plus 18 hand-translated section headers, assembled by `scripts/build_bencao_en.py` into `data/bencao_en.json` — same shape as `bencao.json` so `tcm_core.py` can zip the two lists by index and pair Chinese with English per entry.

**素问's and 灵枢经's English translations** were each produced by parallel translation agents working from chapter batches (bin-packed by character count so no chapter was ever split across a batch — 21 batches for 素问 in `scripts/suwen_en_batches/`, 18 for 灵枢经 in `scripts/lingshu_en_batches/`, both checked into the repo for reproducibility), assembled by `scripts/build_neijing_en.py` into `data/neijing_en.json` — `tcm_core.get_neijing_chapter()` zips each chapter's Chinese and English paragraphs by index. All 81+81 chapters of both books are translated; the lookup's Chinese-only fallback path remains in place for any future untranslated classic.

**周易** is generated from the sibling `zhouyi-divination` app's hexagram data (`scripts/build_zhouyi.py` imports `cs001.py`/`cs001_en.py`/`yijing_core.py` from `../yijing_app`) into a self-contained `data/zhouyi.json`, including each hexagram's six-line bit pattern for rendering the yang/yin diagram.

**心经** (the Heart Sutra) is extracted from the same bundled-text quirk in `sources/huangdinijing.txt` that `build_data.py` already skips over — the raw scrape has the sutra's Chinese text sitting before the real 《黄帝内经》 content starts. `scripts/build_xinjing.py` pulls that block out and pairs it paragraph-by-paragraph with an original English translation (not parsed from any source) into `data/xinjing.json`.

**随笔** entries are hand-written Markdown files under `journal/` (see "Adding a journal entry" below), parsed by `scripts/build_journal.py` into `data/journal.json`.

`app.py` serves the parsed data through read-only routes: a landing page, per-book chapter/juan/hexagram/entry indexes, reading views with print support, and a substring search across all texts (Chinese and English).

## Project structure

- `app.py` — Flask routes.
- `tcm_core.py` — loads `data/*.json` at import time; chapter/juan/hexagram/entry lookup and search helpers.
- `scripts/build_data.py` — one-time parser, `sources/*.txt` → `data/{neijing,bencao}.json`.
- `scripts/build_bencao_en.py` — assembles `scripts/bencao_en_batches/*.json` + hand-translated headers → `data/bencao_en.json`.
- `scripts/build_neijing_en.py` — assembles `scripts/{suwen,lingshu}_en_batches/*.json` → `data/neijing_en.json`.
- `scripts/build_zhouyi.py` — one-time parser, sibling `yijing_app`'s hexagram data → `data/zhouyi.json`.
- `scripts/build_xinjing.py` — one-time parser, the bundled Heart Sutra text in `sources/huangdinijing.txt` → `data/xinjing.json`.
- `scripts/build_journal.py` — one-time parser, `journal/*.md` → `data/journal.json`.
- `sources/` — verbatim copies of the original TCM text dumps, kept for reproducibility.
- `journal/` — hand-written Markdown journal entries (source of truth for 随笔).
- `data/` — parsed JSON consumed by the app.
- `templates/` — Jinja2 templates (`base.html` layout + one per page).
- `static/style.css` — styling, shared visual language with the sibling `zhouyi-divination` app (warm beige/ink palette, light/dark support, print stylesheet).
- `render.yaml` — Render.com blueprint for one-click deployment.

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`. To regenerate `data/*.json`:

```bash
python scripts/build_data.py      # from sources/*.txt
python scripts/build_bencao_en.py # from scripts/bencao_en_batches/*.json
python scripts/build_neijing_en.py # from scripts/{suwen,lingshu}_en_batches/*.json
python scripts/build_zhouyi.py    # from the sibling yijing_app (must be checked out alongside this repo)
python scripts/build_xinjing.py   # from sources/huangdinijing.txt
python scripts/build_journal.py   # from journal/*.md
```

## Adding a journal entry

Create a Markdown file in `journal/` named `YYYY-MM-DD-slug.md` (the filename becomes the URL slug) with a small frontmatter block:

```
---
title: 标题
date: 2026-07-16
---

正文，支持 **Markdown** 格式。
```

Then run `python scripts/build_journal.py` to regenerate `data/journal.json`, and commit + push both the new Markdown file and the regenerated JSON.

To include a photo, drop the image file into `static/journal/` and reference it with a site-absolute path: `![描述](/static/journal/photo.jpg)`. Standard Markdown image syntax renders through as-is (no special handling needed beyond `.journal-body img` styling in `static/style.css`).

To include a video, drop the file into `static/journal/` and embed it with raw HTML (Markdown has no native video syntax, but `python-markdown` passes untouched HTML blocks straight through):

```html
<video controls width="100%">
  <source src="/static/journal/clip.mp4" type="video/mp4">
</video>
```

Keep clips small (well under ~20MB). Video files are committed straight into the git repo like everything else here, and git doesn't compress video well — large files bloat the repo permanently, and Render's free-tier instance has to serve them without a CDN. For anything longer than a short clip, upload it to YouTube/Bilibili (unlisted is fine) and embed with an `<iframe>` instead.

## Deployment

Deployed on [Render](https://render.com) (free tier) via the included `render.yaml` blueprint, same pattern as `zhouyi-divination`.
