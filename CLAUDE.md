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

**Bilingual fallback**: `tcm_core.get_neijing_chapter()` and `search()` degrade gracefully per-chapter when no English exists yet for a given book/number — `bilingual: False`, Chinese-only rendering — rather than requiring full-book translation before anything ships. `NEIJING_EN_BY_NUMBER` is keyed by book name (素问/灵枢经) then chapter number, so this fallback and the lookup are book-agnostic; don't hardcode a specific book's slug/name into lookup logic.

**Print stylesheet caveats** (`static/style.css`, `@media print`): the reading container must not have a `border` — a bordered box taller than one printed page gets silently clipped by the browser past the first page. Elements that convey meaning purely through `background` (e.g. the hexagram yin/yang bars in `.hexagram-diagram`) need `print-color-adjust: exact` *and* a non-background fallback (a border), because browsers strip background graphics by default when printing and that setting is outside this app's control.

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
