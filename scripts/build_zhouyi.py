"""One-time parser: sibling yijing_app's cs001.py / cs001_en.py -> data/zhouyi.json.

Run manually, not imported by app.py. Pulls the 64-hexagram Chinese and
English text that already exists in the Zhouyi divination app (same
project family, c:/webdev-projects/python projects/yijing_app) and
reshapes it into a self-contained JSON so this repo doesn't depend on
that one at runtime.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
YIJING_APP = ROOT.parent / "yijing_app"

sys.path.insert(0, str(YIJING_APP))
import cs001
import cs001_en
import yijing_core

NAME_EN_RE = re.compile(r"^(.+?) \((.+?)\): (.*)$")

# yijing_core.HEXAGRAM_KEYS maps (bottom-to-top 0/1 tuple) -> "dataNN"; invert it.
BITS_BY_INDEX = {name: key for key, name in yijing_core.HEXAGRAM_KEYS}


def build():
    hexagrams = []
    for n in range(1, 65):
        idx = f"data{n:02d}"
        zh = getattr(cs001, idx)
        en = getattr(cs001_en, idx)

        chinese, _, judgment_zh = zh["name"].partition(": ")
        m = NAME_EN_RE.match(en["name"])
        if not m:
            raise ValueError(f"Unexpected en name format for {idx}: {en['name']!r}")
        chinese_en, title_en, judgment_en = m.groups()

        # bottom-to-top (初爻 first), 1 = yang (solid), 0 = yin (broken)
        bits_bottom_up = list(BITS_BY_INDEX[idx])

        hexagrams.append({
            "number": n,
            "chinese": chinese,
            "title_en": title_en,
            "judgment_zh": judgment_zh,
            "judgment_en": judgment_en,
            "lines_zh": [zh[f"y{i:02d}"] for i in range(1, 7)],
            "lines_en": [en[f"y{i:02d}"] for i in range(1, 7)],
            "bits_bottom_up": bits_bottom_up,
        })

    assert len(hexagrams) == 64
    (DATA / "zhouyi.json").write_text(
        json.dumps(hexagrams, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(hexagrams)} hexagrams to {DATA / 'zhouyi.json'}")


if __name__ == "__main__":
    build()
