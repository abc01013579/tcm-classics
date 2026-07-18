"""Assembles the English translation of 素问 into data/neijing_en.json.

Run manually, not imported by app.py. Combines:
- data/neijing.json (the existing parsed Chinese structure, authoritative for
  chapter ordering)
- scripts/suwen_en_batches/batch_NN_en.json (21 files) — per-chapter English
  translations of all 81 素问 chapters, originally produced by parallel
  translation agents (bin-packed into 21 roughly-balanced batches by
  character count, never splitting a chapter) and checked into the repo
  here for reproducibility, rather than left in ephemeral scratch space.

灵枢经 has no English translation yet (a future phase); it is omitted from
the output entirely, and tcm_core.py falls back to Chinese-only rendering
for it.

Output shape: {"素问": [{"number", "title_en", "paragraphs_en"}, ...]} — the
same per-chapter ordering as neijing.json's 素问 list, so tcm_core.py can
zip the two lists by index to pair Chinese and English per chapter.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
BATCH_DIR = Path(__file__).parent / "suwen_en_batches"


def load_translations():
    by_number = {}
    for i in range(1, 22):
        path = BATCH_DIR / f"batch_{i:02d}_en.json"
        for chapter in json.loads(path.read_text(encoding="utf-8")):
            by_number[chapter["number"]] = chapter
    return by_number


def build():
    neijing = json.loads((DATA / "neijing.json").read_text(encoding="utf-8"))
    translations = load_translations()

    suwen_en = []
    missing = []
    for chapter in neijing["素问"]:
        t = translations.get(chapter["number"])
        if t is None:
            missing.append(chapter["number"])
            continue
        if len(t["paragraphs_en"]) != len(chapter["paragraphs"]):
            raise ValueError(
                f"chapter {chapter['number']}: paragraph count mismatch "
                f"zh={len(chapter['paragraphs'])} en={len(t['paragraphs_en'])}"
            )
        suwen_en.append(
            {
                "number": chapter["number"],
                "title_en": t["title_en"],
                "paragraphs_en": t["paragraphs_en"],
            }
        )

    if missing:
        print(f"note: {len(missing)} chapters untranslated, will fall back to Chinese-only: {missing}")

    (DATA / "neijing_en.json").write_text(
        json.dumps({"素问": suwen_en}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(suwen_en)}/81 素问 chapters to {DATA / 'neijing_en.json'}")


if __name__ == "__main__":
    build()
