"""One-time builder: data/zhouyi.json -> data/zhouyi_versions.json.

Run manually, not imported by app.py. Needs OpenCC at build time only
(pip install opencc); the app just loads the JSON this writes.

Produces a simplified (简体) and a traditional (繁體) rendering of every
hexagram's name, judgment, and lines, for the /zhouyi?v=... version switch.

The source text in zhouyi.json is already traditional for hexagrams 2-64,
and keeps the classical forms 无 and 于 (not 無 / 於). Only hexagram 1 (乾)
came through from yijing_app in simplified characters. So:

- 繁體 = the source, with hexagram 1's simplified characters fixed by an
  explicit table (OpenCC's s2t would also rewrite 无->無, 于->於, 凶->兇,
  群->羣, which is wrong for this text).
- 简体 = OpenCC t2s of that traditional text, except for KEEP_TRAD below.
"""
import json
import sys
from pathlib import Path

import opencc

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"

# The only simplified characters in the source (all in hexagram 1).
HEX1_TO_TRAD = str.maketrans("贞终见龙厉跃渊潜飞", "貞終見龍厲躍淵潛飛")

# Characters t2s must leave alone:
#   乾 - qián (the hexagram name, 乾乾) is 乾 in simplified Chinese too;
#        t2s gives 干. (The gān "dried" uses in 噬嗑 are handled in to_simp.)
#   纆 餗 繻 撝 - t2s gives rare forms (𬙊 𫗧 𦈡 㧑) most fonts can't show;
#               printed simplified editions of the Zhouyi keep these.
KEEP_TRAD = set("乾纆餗繻撝")

T2S = opencc.OpenCC("t2s")


def to_trad(text):
    return text.translate(HEX1_TO_TRAD)


def to_simp(trad):
    simp = T2S.convert(trad)
    if len(simp) != len(trad):
        raise ValueError(f"t2s changed length: {trad!r} -> {simp!r}")
    simp = "".join(t if t in KEEP_TRAD else s for t, s in zip(trad, simp))
    # ...but in 噬嗑 (21) 噬乾胏 / 噬乾肉, 乾 is gān "dried", which IS 干.
    return simp.replace("噬乾", "噬干")


def render(hexagram, convert):
    return {
        "chinese": convert(hexagram["chinese"]),
        "judgment": convert(hexagram["judgment_zh"]),
        "lines": [convert(line) for line in hexagram["lines_zh"]],
    }


def main():
    zhouyi = json.loads((DATA / "zhouyi.json").read_text(encoding="utf-8"))
    out = {}
    for h in zhouyi:
        trad = render(h, to_trad)
        simp = {
            "chinese": to_simp(trad["chinese"]),
            "judgment": to_simp(trad["judgment"]),
            "lines": [to_simp(line) for line in trad["lines"]],
        }
        out[str(h["number"])] = {"trad": trad, "simp": simp}
    (DATA / "zhouyi_versions.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(out)} hexagrams to data/zhouyi_versions.json")


if __name__ == "__main__":
    main()
