# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pip install -r requirements.txt
python app.py                      # runs at http://127.0.0.1:5000, debug=True
```

Regenerating `data/*.json` (each script is one-time/manual, run only when its upstream source changes — `app.py` just loads the pre-built JSON at import time, never runs these itself):

```bash
python scripts/build_data.py       # sources/huangdinijing.txt, sources/shennubencao.txt -> data/neijing.json, data/bencao.json
python scripts/build_nanjing.py    # sources/shennubencao.txt (a second bundled text within it) -> data/nanjing.json
python scripts/build_fuxingjue.py  # sources/shennubencao.txt (a third bundled text within it) -> data/fuxingjue.json
python scripts/build_shanghanlun.py # sources/shennubencao.txt (a fourth bundled text within it) -> data/shanghanlun.json
python scripts/build_qijingbamai.py # sources/shennubencao.txt (a fifth bundled text within it) -> data/qijingbamai.json
python scripts/build_bencao_en.py  # scripts/bencao_en_batches/*.json -> data/bencao_en.json
python scripts/build_neijing_en.py # scripts/{suwen,lingshu}_en_batches/*.json -> data/neijing_en.json
python scripts/build_zhouyi.py     # sibling ../yijing_app's hexagram data -> data/zhouyi.json (yijing_app must be checked out alongside this repo)
python scripts/build_xinjing.py    # sources/huangdinijing.txt -> data/xinjing.json
python scripts/build_journal.py    # journal/*.md -> data/journal.json
```

There is no test suite or linter configured in this repo.

## Architecture

Flask app with no database and no request-time parsing: `tcm_core.py` loads every `data/*.json` file into module-level globals at import time, and `app.py`'s routes just look values up and hand them to Jinja templates. All the real work — turning messy source text into structured, bilingual JSON — happens ahead of time via the `scripts/build_*.py` scripts, whose output is committed to `data/` so the app never re-derives it.

**Two-stage pipeline per classic**: parse Chinese source → translate to English → assemble. Stage 1 (`scripts/build_data.py`, `build_zhouyi.py`, `build_xinjing.py`, `build_journal.py`) turns raw sources into `{number/title, paragraphs}`-shaped Chinese JSON. Stage 2, where it exists, produces English text that a `build_*_en.py` script zips against the Chinese by index into `data/*_en.json`. `tcm_core.py` then zips Chinese and English paragraph lists together at lookup time (see `get_neijing_chapter`) — **this means paragraph counts between a chapter's Chinese and English lists must match exactly, or the zip silently misaligns.**

**How English translations get produced**: not by a single LLM call per book. Chapters/entries are bin-packed into batches by character count (a chapter/entry is never split across a batch boundary), each batch is handed to a separate translation agent running in parallel, and every batch's raw output is checked into `scripts/{suwen,lingshu,bencao}_en_batches/` for reproducibility — the `data/*_en.json` files are a build artifact of these batches, not hand-edited. This is how 素问 (21 batches), 灵枢经 (18 batches), and 神农本草经 (14 batches + 18 hand-translated headers) were done; the same pattern is the template for adding English to any future untranslated classic. When doing this, keep a shared terminology glossary (e.g. 黄帝→Huangdi, 经脉→channels, 阴阳→yin and yang untranslated) across all batches of one book so parallel agents don't diverge on rendering of recurring terms.

**Multiple bundled texts in one source file — verify section boundaries by grep, don't trust a first-pass survey**: `sources/shennubencao.txt` contains 神农本草经, 难经, 辅行诀脏腑用药法要, 伤寒论, and 《奇经八脉考》 (all parsed as of 2026-07-19), plus 《金匮要略》相关讨论 (brief mentions only, not a separate parseable text). 伤寒论 itself was missed on the *first* survey of this file because its title marker `《伤寒论》` is indented while every other marker starts at column 0 — `grep -n "^《"` silently misses it. Before assuming you've found every section boundary in a bundled source file, grep for `《.*》` WITHOUT a column-0 anchor, not just `^《`. 《奇经八脉考》 is the last text in the file, running to EOF with no closing section marker after it.

**Each bundled text has its own numbering quirks — verify empirically, don't extrapolate from the last one**: 难经's leading arabic number is a *local* per-chapter counter (resets at chapter boundaries); the real number is a Chinese numeral embedded in the entry's own text. 辅行诀's leading number is different again — a single continuous counter with no resets, incrementing on *every* physical line (not just entry-starts), which is why it's modeled as a flat `{title, paragraphs}` document (same shape as `xinjing.json`) rather than a numbered/chaptered structure like `nanjing.json`. 伤寒论 resets per-chapter like 难经, but has no embedded Chinese-numeral global count to recover a true number from, so `build_shanghanlun.py` assigns its own sequential number for routing. It also had messier source noise than the other two: an OCR-corrupted chapter marker (`<<` instead of `《`), scraped website UI text (`打开字典显示相似段落`) leaking into the content, an entry whose number had zero separating whitespace before its content (silently dropped until the entry-line regex was loosened), and a genuine gap in the source's own numbering. When investigating a new bundled text, always `grep -n` for the *real* file line number before using it in `sed` — it is very easy to mistake a number printed as part of the source's own content (a local counter, a footnote reference) for an actual file line number, and this happened repeatedly while scoping both 辅行诀 and 伤寒论.

**Bilingual fallback**: `tcm_core.get_neijing_chapter()` and `search()` degrade gracefully per-chapter when no English exists yet for a given book/number — `bilingual: False`, Chinese-only rendering — rather than requiring full-book translation before anything ships. `NEIJING_EN_BY_NUMBER` is keyed by book name (素问/灵枢经) then chapter number, so this fallback and the lookup are book-agnostic; don't hardcode a specific book's slug/name into lookup logic.

**Print stylesheet caveats** (`static/style.css`, `@media print`): the reading container must not have a `border` — a bordered box taller than one printed page gets silently clipped by the browser past the first page. Elements that convey meaning purely through `background` (e.g. the hexagram yin/yang bars in `.hexagram-diagram`) need `print-color-adjust: exact` *and* a non-background fallback (a border), because browsers strip background graphics by default when printing and that setting is outside this app's control.

**随笔 (journal) entry style — two registers, pick per entry**: personal/philosophical essays (e.g. 厥孚复利, 定投的威力, 毒药攻邪五谷为养) read best as flowing prose paragraphs with no headers, building to a closing line that ties back to the entry's theme. Explanatory/informational entries (e.g. 太阳与地球协同孕育地球生命) read best sectioned — `##` headers, bullet/numbered lists, a closing `## 小结` — confirmed 2026-07-20 as the preferred style for this register ("simple and essential, well structured"). Don't force one register onto the other topic type.

## Project structure

- `app.py` — Flask routes only; no business logic.
- `tcm_core.py` — loads `data/*.json` at import time; all chapter/juan/hexagram/entry lookup and cross-text search live here.
- `sources/` — verbatim copies of original text dumps (kept for reproducibility, not regenerated).
- `scripts/` — the build pipeline described above, plus the checked-in translation batches.
- `data/` — parsed/assembled JSON consumed by the app; regenerate via the `build_*.py` scripts, don't hand-edit.
- `journal/` — hand-written Markdown source of truth for 随笔 entries (see README's "Adding a journal entry" for the frontmatter format and the commit step after `build_journal.py`).
- `templates/` — Jinja2, `base.html` layout plus one template per page type.
- `static/style.css` — shared visual language with the sibling `zhouyi-divination` (`yijing_app`) app.

## Deployment

Render.com (free tier) via `render.yaml`, auto-deploys on push to `main`.
