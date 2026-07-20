# 中华典籍 (Chinese Classics Reader)

A Flask web app for browsing and searching Chinese classical texts: five Traditional Chinese Medicine classics, 《黄帝内经》(Huangdi Neijing — 素问 and 灵枢经, all 81+81 chapters, both fully bilingual Chinese/English), 《神农本草经》(Shennong Bencao Jing, all 364 entries with bilingual Chinese/English text), 《难经》(Nan Jing, the Classic of Difficult Issues — all 81 难 across 13 chapters, Chinese-only for now), 《辅行诀脏腑用药法要》(Tao Hongjing's formulary, Chinese-only for now), and 《伤寒论》(Zhang Zhongjing's Treatise on Cold Damage — 727 entries across 22 chapters, Chinese-only for now); 《周易》(Zhouyi / I Ching), all 64 hexagrams with bilingual Chinese/English text and line diagrams; 《心经》(the Heart Sutra) with bilingual text; and 随笔, a personal journal section. More classics are added over time.

## How it works

The TCM source texts started as raw plain-text scrapes (`sources/`), each bundling extra, unrelated classical texts appended after the wanted content with no clean separator. A one-time parser (`scripts/build_data.py`) extracts just the wanted portions into structured JSON (`data/`):

- **黄帝内经**: split into 素问 (81 chapters) and 灵枢经 (81 chapters), each `{number, title, paragraphs}`. Chapter boundaries are detected by column-0 `N. 标题` headers, filtered to exclude indented table-of-contents lines and stray footnote annotations. The source is missing the "10. 经脉" header in 灵枢经 (a transcription gap); the parser splices it back in at its known content anchor before parsing.
- **神农本草经**: split into 上卷/中卷/下卷, each an ordered list of `{number, text, is_header}` entries. Category dividers like `玉石部上品` are detected by an exact `<category>部<上/中/下>品` pattern and flagged `is_header`; everything else is a herb entry, with wrapped continuation lines reattached.

`scripts/build_data.py` asserts expected chapter/entry counts (81+81 neijing chapters, 10/273/99 bencao entries per juan, 18 category headers) before writing the JSON, so a parsing regression fails loudly instead of silently corrupting the data. It's run manually, not at request time — the app just loads the pre-built JSON.

**难经** is a second text bundled in `sources/shennubencao.txt`, right after 神农本草经 ends. `scripts/build_nanjing.py` handles it separately from `build_data.py` because its numbering scheme is genuinely tricky: the leading arabic number on each entry line is a *local* per-chapter counter that resets at every chapter boundary, not the entry's real number — the authoritative global 1–81 numbering is the Chinese numeral embedded in the entry's own text ("七十八难曰" = the 78th difficulty), which the parser converts to int. Chapter-title markers don't reliably fall between entries (at least one lands mid-entry), so they're treated as pure boundary updates rather than entry delimiters. Inline footnote-reference digits mid-sentence ("菽1之重") are stripped on the same logic as `build_data.py`'s other footnote filtering — this classical text only ever uses Chinese numerals, so a bare arabic digit touching Hanzi is always digitization noise. One genuine source gap (a dropped character in 难34's question) is left as-is rather than silently emended, same policy as 灵枢经's missing header. No English translation yet.

**辅行诀脏腑用药法要** is a third text in the same file, right after 神农本草经 ends and right *before* 难经's position further down — Tao Hongjing's formulary (five-organ tonify/drain decoctions, the 二旦六神 formulas Zhang Zhongjing later renamed when writing 《伤寒论》, five emergency resuscitation techniques, and closing manuscript-comparison footnotes). `scripts/build_fuxingjue.py` parses it. Unlike 难经, there's no uniform "entry" unit here — organ disease-pattern discussion, formula names, indications, ingredient lists, prep instructions, and editorial commentary are all mixed together — so it's modeled as a single flowing document (`{title, paragraphs}`, same shape as `xinjing.json`) rather than a numbered structure. Its digitization convention also differs from 难经: *every* physical line carries its own running number (not just entry-starts), so a new paragraph begins at each numbered line, with rare unnumbered indented lines treated as wrapped continuations. No English translation for 辅行诀 yet.

**伤寒论** is a fourth text, sitting immediately after 辅行诀 — missed on the original bundled-text survey because its title marker is indented (`    《伤寒论》`) while every other marker in this file starts at column 0, so a naive `grep -n "^《"` misses it. `scripts/build_shanghanlun.py` parses its 22-chapter table of contents and 727 entries. Like 难经, chapter numbering resets per-chapter, but unlike 难经 there's no embedded Chinese-numeral global count to recover a true cross-chapter number from — so the parser assigns its own sequential `number` (1..727, reading order) for routing, keeping `chapter_number`/`local_number` for citation display, same overall shape as `nanjing.json`. Real quirks found and handled: chapter 20's title marker is OCR-corrupted (`20 <<辨不可下病脉证并治》`, using `<<` instead of `《`) so chapters are matched against the verified 22-title list rather than by bracket character; a mid-entry quote citing a different classic (`1《阴阳大论》云：...`) isn't mistaken for a chapter marker since real markers have no trailing content after the closing bracket; two instances of scraped website UI text (`打开字典显示相似段落`, a button label from wherever this was scraped, not classical content) are stripped; entry 1 of 伤寒例 has its number directly adjacent to a bracket with no separating whitespace, which required loosening the entry-line regex; and 伤寒例 itself has a genuine gap in the source numbering (entry 4 is followed directly by entry 6, no "5" anywhere), left as-is per the same policy as 难经's and 灵枢经's known gaps. No English translation yet. 《金匮要略》相关讨论 and 《奇经八脉考》 remain unparsed further down in the same source file.

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
- `scripts/build_nanjing.py` — one-time parser, the bundled 难经 text in `sources/shennubencao.txt` → `data/nanjing.json`.
- `scripts/build_fuxingjue.py` — one-time parser, the bundled 辅行诀 text in `sources/shennubencao.txt` → `data/fuxingjue.json`.
- `scripts/build_shanghanlun.py` — one-time parser, the bundled 伤寒论 text in `sources/shennubencao.txt` → `data/shanghanlun.json`.
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
python scripts/build_nanjing.py   # from sources/shennubencao.txt
python scripts/build_fuxingjue.py # from sources/shennubencao.txt
python scripts/build_shanghanlun.py # from sources/shennubencao.txt
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
