# 中医典籍 (TCM Classics Reader)

A Flask web app for browsing and searching two Traditional Chinese Medicine classics: 《黄帝内经》(Huangdi Neijing, both 素问 and 灵枢经) and 《神农本草经》(Shennong Bencao Jing).

## How it works

The two source texts started as raw plain-text scrapes (`sources/`), each bundling extra, unrelated classical texts appended after the wanted content with no clean separator. A one-time parser (`scripts/build_data.py`) extracts just the wanted portions into structured JSON (`data/`):

- **黄帝内经**: split into 素问 (81 chapters) and 灵枢经 (81 chapters), each `{number, title, paragraphs}`. Chapter boundaries are detected by column-0 `N. 标题` headers, filtered to exclude indented table-of-contents lines and stray footnote annotations. The source is missing the "10. 经脉" header in 灵枢经 (a transcription gap); the parser splices it back in at its known content anchor before parsing.
- **神农本草经**: split into 上卷/中卷/下卷, each an ordered list of `{number, text, is_header}` entries. Category dividers like `玉石部上品` are detected by an exact `<category>部<上/中/下>品` pattern and flagged `is_header`; everything else is a herb entry, with wrapped continuation lines reattached.

`scripts/build_data.py` asserts expected chapter/entry counts (81+81 neijing chapters, 10/273/99 bencao entries per juan, 18 category headers) before writing the JSON, so a parsing regression fails loudly instead of silently corrupting the data. It's run manually, not at request time — the app just loads the pre-built JSON.

`app.py` serves the parsed data through six read-only routes: a landing page, per-book chapter/juan indexes, a chapter/juan reading view with print support, and a substring search across both texts.

## Project structure

- `app.py` — Flask routes.
- `tcm_core.py` — loads `data/*.json` at import time; chapter/juan lookup and search helpers.
- `scripts/build_data.py` — one-time parser, `sources/*.txt` → `data/*.json`.
- `sources/` — verbatim copies of the original text dumps, kept for reproducibility.
- `data/` — parsed JSON consumed by the app.
- `templates/` — Jinja2 templates (`base.html` layout + one per page).
- `static/style.css` — styling, shared visual language with the sibling `zhouyi-divination` app (warm beige/ink palette, light/dark support, print stylesheet).
- `render.yaml` — Render.com blueprint for one-click deployment.

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`. To regenerate `data/*.json` from the source texts:

```bash
python scripts/build_data.py
```

## Deployment

Deployed on [Render](https://render.com) (free tier) via the included `render.yaml` blueprint, same pattern as `zhouyi-divination`.
