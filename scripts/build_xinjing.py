"""One-time parser: sources/huangdinijing.txt (leading bundled text) -> data/xinjing.json.

Run manually, not imported by app.py. The raw 黄帝内经 scrape bundles an
unrelated short text before the real content starts at "《黄帝内经》":
般若波罗蜜多心经 (the Heart Sutra). build_data.py already skips over it
when parsing 黄帝内经; this script extracts just that leading block instead.

English translations are an original rendering (not parsed from any
source file), paired paragraph-by-paragraph with the classical Chinese.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
SOURCES = ROOT / "sources"
DATA = ROOT / "data"

TITLE_ZH = "般若波羅蜜多心經"
TITLE_EN = "The Heart Sutra"
END_MARKER = "《黄帝内经》"

TRANSLATIONS_EN = [
    "Avalokiteshvara Bodhisattva, while practicing the profound Prajna-paramita "
    "(Perfection of Wisdom), clearly saw that all five skandhas are empty, and "
    "was thereby freed from all suffering and distress.",

    "Shariputra, form is not different from emptiness, emptiness is not different "
    "from form; form itself is emptiness, emptiness itself is form. The same is "
    "true of feeling, perception, mental formations, and consciousness.",

    "Shariputra, all dharmas are marked by emptiness: they neither arise nor "
    "cease, are neither defiled nor pure, neither increase nor decrease.",

    "Therefore, in emptiness there is no form, no feeling, perception, mental "
    "formation, or consciousness; no eye, ear, nose, tongue, body, or mind; no "
    "form, sound, smell, taste, touch, or object of mind; no realm of sight, up "
    "to and including no realm of mind-consciousness.",

    "There is no ignorance, and no ending of ignorance, up to and including no "
    "old age and death, and no ending of old age and death. There is no "
    "suffering, no cause of suffering, no cessation of suffering, and no path.",

    "There is no wisdom and no attainment, because there is nothing to attain. "
    "The Bodhisattva, relying on Prajna-paramita, has a mind free of obstacles. "
    "Because there are no obstacles, there is no fear, and one is far removed "
    "from all distorted dream-thinking, reaching ultimate Nirvana.",

    "All Buddhas of the past, present, and future rely on Prajna-paramita to "
    "attain Anuttara-samyak-sambodhi, supreme perfect enlightenment.",

    "Therefore know that Prajna-paramita is the great mantra, the mantra of "
    "great clarity, the supreme mantra, the unequaled mantra, able to remove "
    "all suffering — this is true, not false.",

    "Therefore proclaim the Prajna-paramita mantra, the mantra that says: "
    "Gate gate paragate parasamgate bodhi svaha! (Gone, gone, gone beyond, "
    "gone completely beyond, awakening, so be it!)",
]


def build():
    text = (SOURCES / "huangdinijing.txt").read_text(encoding="utf-8")
    start = text.index(TITLE_ZH) + len(TITLE_ZH)
    end = text.index(END_MARKER)
    block = text[start:end]

    paragraphs_zh = [
        p.strip() for p in block.split("\n\n")
        if p.strip() and p.strip() not in ("。", "'''")
    ]

    if len(paragraphs_zh) != len(TRANSLATIONS_EN):
        raise ValueError(
            f"expected {len(TRANSLATIONS_EN)} paragraphs, extracted "
            f"{len(paragraphs_zh)}: {paragraphs_zh}"
        )

    data = {
        "title_zh": TITLE_ZH,
        "title_en": TITLE_EN,
        "paragraphs": [
            {"zh": zh, "en": en} for zh, en in zip(paragraphs_zh, TRANSLATIONS_EN)
        ],
    }

    (DATA / "xinjing.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(paragraphs_zh)} paragraphs to {DATA / 'xinjing.json'}")


if __name__ == "__main__":
    build()
