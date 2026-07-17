"""Assembles the English translation of 神农本草经 into data/bencao_en.json.

Run manually, not imported by app.py. Combines:
- data/bencao.json (the existing parsed Chinese structure, authoritative for
  ordering and is_header flags)
- scripts/bencao_en_batches/batch_NN_en.json (14 files) — per-entry English
  translations of the 364 herb/mineral/animal entries, originally produced
  by 14 parallel translation agents (~26 entries each) and checked into the
  repo here for reproducibility, rather than left in ephemeral scratch space
- hand-translated section headers (short, formulaic category names)

Output has the exact same shape as bencao.json ({juan: [{number, text,
is_header}, ...]}) so tcm_core.py can zip the two lists by index to pair
Chinese and English for each entry.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
BATCH_DIR = Path(__file__).parent / "bencao_en_batches"

HEADER_TRANSLATIONS = {
    "玉石部上品": "Minerals and Stones — Superior Grade",
    "玉石部中品": "Minerals and Stones — Middle Grade",
    "玉石部下品": "Minerals and Stones — Lower Grade",
    "草部上品": "Herbs — Superior Grade",
    "草部中品": "Herbs — Middle Grade",
    "草部下品": "Herbs — Lower Grade",
    "木部上品": "Trees and Wood — Superior Grade",
    "木部中品": "Trees and Wood — Middle Grade",
    "木部下品": "Trees and Wood — Lower Grade",
    "蟲獸部上品": "Insects and Animals — Superior Grade",
    "蟲獸部中品": "Insects and Animals — Middle Grade",
    "蟲獸部下品": "Insects and Animals — Lower Grade",
    "果菜部上品": "Fruits and Vegetables — Superior Grade",
    "果菜部中品": "Fruits and Vegetables — Middle Grade",
    "果菜部下品": "Fruits and Vegetables — Lower Grade",
    "米穀部上品": "Grains — Superior Grade",
    "米穀部中品": "Grains — Middle Grade",
    "米穀部下品": "Grains — Lower Grade",
}


def load_translations():
    by_key = {}
    for i in range(1, 15):
        path = BATCH_DIR / f"batch_{i:02d}_en.json"
        for entry in json.loads(path.read_text(encoding="utf-8")):
            by_key[(entry["juan"], entry["number"])] = entry["en"]
    return by_key


def build():
    bencao = json.loads((DATA / "bencao.json").read_text(encoding="utf-8"))
    translations = load_translations()

    bencao_en = {}
    missing = []
    for juan, entries in bencao.items():
        out = []
        for e in entries:
            if e["is_header"]:
                text_en = HEADER_TRANSLATIONS.get(e["text"])
                if text_en is None:
                    missing.append(("header", juan, e["text"]))
            else:
                text_en = translations.get((juan, e["number"]))
                if text_en is None:
                    missing.append(("entry", juan, e["number"]))
            out.append({"number": e["number"], "text": text_en, "is_header": e["is_header"]})
        bencao_en[juan] = out

    if missing:
        raise ValueError(f"missing {len(missing)} translations: {missing[:10]}")

    (DATA / "bencao_en.json").write_text(
        json.dumps(bencao_en, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total = sum(len(v) for v in bencao_en.values())
    print(f"wrote {total} entries (incl. headers) to {DATA / 'bencao_en.json'}")


if __name__ == "__main__":
    build()
