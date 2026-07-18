"""Assembles the English translation of 素问 and 灵枢经 into data/neijing_en.json.

Run manually, not imported by app.py. For each book, combines:
- data/neijing.json (the existing parsed Chinese structure, authoritative for
  chapter ordering)
- scripts/{suwen,lingshu}_en_batches/batch_NN_en.json — per-chapter English
  translations of all 81 chapters, originally produced by parallel
  translation agents (bin-packed into batches by character count, never
  splitting a chapter) and checked into the repo here for reproducibility,
  rather than left in ephemeral scratch space.

Output shape: {"素问": [...], "灵枢经": [...]}, each a list of
{"number", "title_en", "paragraphs_en"} in the same per-chapter ordering as
neijing.json's lists, so tcm_core.py can zip Chinese and English by index.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
SCRIPTS = Path(__file__).parent

BOOKS = [
    ("素问", SCRIPTS / "suwen_en_batches", 21),
    ("灵枢经", SCRIPTS / "lingshu_en_batches", 18),
]


def load_translations(batch_dir, batch_count):
    by_number = {}
    for i in range(1, batch_count + 1):
        path = batch_dir / f"batch_{i:02d}_en.json"
        for chapter in json.loads(path.read_text(encoding="utf-8")):
            by_number[chapter["number"]] = chapter
    return by_number


def build():
    neijing = json.loads((DATA / "neijing.json").read_text(encoding="utf-8"))

    output = {}
    for book_name, batch_dir, batch_count in BOOKS:
        translations = load_translations(batch_dir, batch_count)

        book_en = []
        missing = []
        for chapter in neijing[book_name]:
            t = translations.get(chapter["number"])
            if t is None:
                missing.append(chapter["number"])
                continue
            if len(t["paragraphs_en"]) != len(chapter["paragraphs"]):
                raise ValueError(
                    f"{book_name} chapter {chapter['number']}: paragraph count mismatch "
                    f"zh={len(chapter['paragraphs'])} en={len(t['paragraphs_en'])}"
                )
            book_en.append(
                {
                    "number": chapter["number"],
                    "title_en": t["title_en"],
                    "paragraphs_en": t["paragraphs_en"],
                }
            )

        if missing:
            print(f"note: {book_name} has {len(missing)} untranslated chapters, will fall back to Chinese-only: {missing}")

        output[book_name] = book_en
        print(f"assembled {len(book_en)}/{len(neijing[book_name])} {book_name} chapters")

    (DATA / "neijing_en.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {DATA / 'neijing_en.json'}")


if __name__ == "__main__":
    build()
