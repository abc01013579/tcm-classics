"""One-time parser: sources/*.txt -> data/*.json. Run manually, not imported by app.py."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
SOURCES = ROOT / "sources"
DATA = ROOT / "data"

BOOK_NAMES = ("素问", "灵枢经")
JUAN_NAMES = ("上卷", "中卷", "下卷")

SECTION_RE = re.compile(r"^《([^》]+)》$")
CHAPTER_HEADER_RE = re.compile(r"^(\d+)\.\s*(.+?)\s*$")
BENCAO_ENTRY_RE = re.compile(r"^(\d+)\s+(.*)$")
BENCAO_HEADER_RE = re.compile(r"^[^\s，。；、]{1,6}部[上中下]品$")

# The source transcription drops the "10. 经脉" header in 灵枢经 (chapter 9's
# body runs straight into chapter 10's), so its opening line is spliced back
# in as a synthetic header before parsing.
MISSING_NEIJING_HEADER_ANCHOR = (
    "雷公问于黄帝曰：“禁脉”之言，凡刺之理，经脉为始，营其所行，制其度量，内次五藏，外别六府，愿尽闻其道。"
)
MISSING_NEIJING_HEADER = "10. 经脉"


def parse_neijing(text):
    lines = text.splitlines()
    anchor_idx = lines.index(MISSING_NEIJING_HEADER_ANCHOR)
    lines[anchor_idx:anchor_idx] = [MISSING_NEIJING_HEADER, ""]
    books = {}
    current_book = None
    current_chapter = None  # {"number", "title", "lines": [raw lines]}
    chapters = None
    started = False

    def flush_chapter():
        nonlocal current_chapter
        if current_chapter is None:
            return
        paragraphs = []
        buf = []
        for line in current_chapter["lines"]:
            if line.strip() == "":
                if buf:
                    paragraphs.append("".join(buf))
                    buf = []
            else:
                buf.append(line.strip())
        if buf:
            paragraphs.append("".join(buf))
        chapters.append({
            "number": current_chapter["number"],
            "title": current_chapter["title"],
            "paragraphs": paragraphs,
        })
        current_chapter = None

    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        m = SECTION_RE.match(raw.strip())
        if m:
            name = m.group(1)
            if name == "黄帝内经":
                started = True
                i += 1
                continue
            if not started:
                i += 1
                continue
            flush_chapter()
            if name in BOOK_NAMES:
                current_book = name
                chapters = []
                books[current_book] = chapters
                i += 1
                continue
            else:
                break

        if started and current_book is not None:
            is_header = False
            if raw == raw.lstrip():
                hm = CHAPTER_HEADER_RE.match(raw)
                if hm:
                    title = hm.group(2)
                    if ":" not in title and "：" not in title:
                        if i + 1 < n and lines[i + 1].strip() == "":
                            is_header = True

            if is_header:
                flush_chapter()
                current_chapter = {"number": int(hm.group(1)), "title": hm.group(2), "lines": []}
                i += 2  # skip header line + following blank line
                continue

            if current_chapter is not None:
                current_chapter["lines"].append(raw)

        i += 1

    flush_chapter()
    return books


def parse_bencao(text):
    lines = text.splitlines()
    juans = {}
    current_juan = None
    entries = None
    current_entry = None  # {"number", "parts": [str,...]}

    def flush_entry():
        nonlocal current_entry
        if current_entry is None:
            return
        entry_text = "".join(current_entry["parts"]).strip()
        is_header = bool(BENCAO_HEADER_RE.match(entry_text))
        entries.append({
            "number": current_entry["number"],
            "text": entry_text,
            "is_header": is_header,
        })
        current_entry = None

    started = False
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        m = SECTION_RE.match(stripped)
        if m:
            name = m.group(1)
            flush_entry()
            if name in JUAN_NAMES:
                started = True
                current_juan = name
                entries = []
                juans[current_juan] = entries
                continue
            elif started:
                break
            else:
                continue

        if not started or current_juan is None:
            continue

        em = BENCAO_ENTRY_RE.match(raw)
        if em:
            flush_entry()
            current_entry = {"number": int(em.group(1)), "parts": [em.group(2)]}
            continue

        if current_entry is not None and stripped and raw != raw.lstrip():
            current_entry["parts"].append(stripped)

    flush_entry()
    return juans


def verify_neijing(books):
    for name in BOOK_NAMES:
        chapters = books[name]
        assert len(chapters) == 81, f"{name}: expected 81 chapters, got {len(chapters)}"
        numbers = [c["number"] for c in chapters]
        assert numbers == list(range(1, 82)), f"{name}: chapter numbers not contiguous 1..81: {numbers}"
        assert all(c["paragraphs"] for c in chapters), f"{name}: some chapter has empty paragraphs"
    assert books["素问"][0]["title"] == "上古天真论", books["素问"][0]["title"]
    print(f"neijing OK: 素问={len(books['素问'])} chapters, 灵枢经={len(books['灵枢经'])} chapters")


def verify_bencao(juans):
    expected_max = {"上卷": 10, "中卷": 273, "下卷": 99}
    header_total = 0
    for name in JUAN_NAMES:
        entries = juans[name]
        numbers = [e["number"] for e in entries]
        assert numbers == list(range(1, expected_max[name] + 1)), (
            f"{name}: expected 1..{expected_max[name]}, got {numbers[:5]}...{numbers[-5:]}"
        )
        header_total += sum(1 for e in entries if e["is_header"])
    assert header_total == 18, f"expected 18 header entries total, got {header_total}"
    assert juans["中卷"][0] == {"number": 1, "text": "玉石部上品", "is_header": True}, juans["中卷"][0]
    assert juans["中卷"][1]["text"].startswith("玉泉"), juans["中卷"][1]["text"]
    print(f"bencao OK: 上卷={len(juans['上卷'])} 中卷={len(juans['中卷'])} 下卷={len(juans['下卷'])}, headers={header_total}")


def main():
    DATA.mkdir(exist_ok=True)

    neijing_text = (SOURCES / "huangdinijing.txt").read_text(encoding="utf-8")
    books = parse_neijing(neijing_text)
    verify_neijing(books)
    (DATA / "neijing.json").write_text(
        json.dumps(books, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    bencao_text = (SOURCES / "shennubencao.txt").read_text(encoding="utf-8")
    juans = parse_bencao(bencao_text)
    verify_bencao(juans)
    (DATA / "bencao.json").write_text(
        json.dumps(juans, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("Wrote data/neijing.json and data/bencao.json")


if __name__ == "__main__":
    main()
