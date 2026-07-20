"""One-time parser: sources/shennubencao.txt -> data/fuxingjue.json.

Run manually, not imported by app.py. 《辅行诀脏腑用药法要》(Tao Hongjing's
formulary) is bundled in the same raw scrape as 神农本草经 and 难经, right
after 神农本草经 ends -- same "extra text appended with no clean
separator" pattern as everything else in this file. A 《伤寒论》 marker
sits immediately after it (missed on first survey because it's indented,
unlike every other marker in this file, which starts at column 0) --
that boundary is what determines where this text actually ends.

Unlike 难经, this text has no single uniform "entry" unit -- it mixes
organ disease-pattern discussion, formula names, indications,
ingredient lists, preparation instructions, and editorial commentary
("陶云"/"陶隐居曰"/"弘景曰"), plus a closing block of numbered
textual-critical footnotes ("甲本"/"乙本" manuscript-variant notes).
So it's modeled as a single flowing document (same shape as
data/xinjing.json: {title, paragraphs}), not a numbered/chaptered
structure.

Numbering convention here is also different from 难经: EVERY physical
line gets its own running number (not just entry-starts), so a new
paragraph starts at each numbered line; the rare unnumbered,
indented lines are wrapped continuations of the previous line.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
SOURCES = ROOT / "sources"
DATA = ROOT / "data"

TITLE = "輔行訣髒腑用藥法要"
SECTION_START = f"《{TITLE}》"
SECTION_END = "《伤寒论》"

NUMBERED_LINE_RE = re.compile(r"^(\d+)\s+(.*)$")


def parse_fuxingjue(text):
    lines = text.splitlines()
    start = lines.index(SECTION_START)
    # SECTION_END is indented, so match by stripped content, not exact line.
    end = next(i for i in range(start, len(lines)) if lines[i].strip() == SECTION_END)
    lines = lines[start + 1:end]

    paragraphs = []
    buf = []
    last_number = 0

    def flush():
        if buf:
            paragraphs.append("".join(buf))
            buf.clear()

    for raw in lines:
        if raw.strip() == "":
            continue
        m = NUMBERED_LINE_RE.match(raw)
        if m:
            flush()
            last_number = int(m.group(1))
            buf.append(m.group(2))
        elif buf:
            buf.append(raw.strip())
    flush()

    return paragraphs, last_number


def verify_fuxingjue(paragraphs, last_number):
    assert len(paragraphs) > 0, "no paragraphs parsed"
    assert paragraphs[0].startswith("梁"), f"unexpected first paragraph: {paragraphs[0][:20]}"
    assert "小瀉肝湯" in paragraphs, "missing 小泻肝汤 formula name"
    assert "小補腎湯" in paragraphs, "missing 小补肾汤 formula name"
    assert "小玄武湯" in paragraphs, "missing 小玄武汤 formula name (二旦六神 section)"
    assert any(p.startswith("5、") for p in paragraphs), "missing closing 校注 footnote 5"
    print(f"fuxingjue OK: {len(paragraphs)} paragraphs, source numbering ran up to {last_number}")


def main():
    DATA.mkdir(exist_ok=True)
    text = (SOURCES / "shennubencao.txt").read_text(encoding="utf-8")
    paragraphs, last_number = parse_fuxingjue(text)
    verify_fuxingjue(paragraphs, last_number)
    (DATA / "fuxingjue.json").write_text(
        json.dumps({"title": TITLE, "paragraphs": paragraphs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {len(paragraphs)} paragraphs to {DATA / 'fuxingjue.json'}")


if __name__ == "__main__":
    main()
