"""One-time parser: sources/shennubencao.txt -> data/qijingbamai.json.

Run manually, not imported by app.py. 《奇经八脉考》(Li Shizhen's Ming-era
study of the Eight Extraordinary Meridians) is the last text bundled in
this raw scrape, sitting immediately after 难经 ends (build_nanjing.py's
own SECTION_END is this text's opening marker) and running to EOF -- no
further 《...》 section follows it in the file.

Structure: like 伤寒论, named heading markers ("chapters") each contain
their own locally-reset entry numbering, with no cross-chapter Chinese-
numeral count to recover a true global number from -- so this parser
assigns its own sequential `number` (1..N, reading order) for site
routing, same shape as data/shanghanlun.json (number/local_number/
chapter_number/chapter_title/paragraphs).

Source quirks handled here:
- The very first entry (a Siku-Quanshu-style bibliographic abstract
  starting "《奇经八脉考》一卷，明李时珍撰...") sits before ANY heading
  marker -- there's no 《提要》 marker in the source. It's given the
  editorial chapter_title "提要" (chapter 1) purely for site navigation;
  every other chapter_title is the source's own heading text verbatim.
- The 《八脉》 heading has scraped UI text trailing it on the same line
  ("《八脉》[查看正文] [修改] [查看历史]") -- same website-scrape-junk
  pattern as 伤寒论's "打开字典显示相似段落". Stripped by allowing
  trailing "[...]" groups in the chapter-marker regex.
- 冲脉为病 has a genuine gap in the source's own local numbering: entry
  7's content runs directly into entry 9 with no "8" anywhere in the
  source -- left as-is, same policy as 伤寒论's 伤寒例 4->6 gap and
  难经's missing 液.
- 释音 (the closing glossary) is numbered 1-81, but 81 is not a glossary
  term -- it's the book's own closing colophon line ("奇经八脉考卷终")
  that the source's running numbering swept up as if it were the next
  entry. Dropped rather than kept as a fake glossary term, verified by
  assertion so a source change would fail loudly instead of silently
  keeping garbage.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
SOURCES = ROOT / "sources"
DATA = ROOT / "data"

SECTION_START = "《奇经八脉考》"

CHAPTER_TITLES = [
    "奇经八脉总说", "八脉", "阴维脉", "阳维脉", "二维为病", "阴蹻脉", "阳蹻脉",
    "二蹻为病", "冲脉", "冲脉为病", "任脉", "任脉为病", "督脉", "督脉为病",
    "带脉", "带脉为病", "气口九道脉", "释音",
]
CHAPTER_MARKER_RE = re.compile(r"^《([^》]+)》\s*(?:\[[^\]]*\]\s*)*$")
NUMBERED_LINE_RE = re.compile(r"^(\d+)\s+(.*)$")
COLOPHON = "奇经八脉考卷终"


def parse_qijingbamai(text):
    lines = text.splitlines()
    start = lines.index(SECTION_START)
    lines = lines[start + 1:]

    entries = []
    current = None  # {"local_number", "chapter_number", "chapter_title", "lines": [...]}
    chapter_number = 1
    chapter_title = "提要"

    def flush():
        nonlocal current
        if current is None:
            return
        text_joined = "".join(current["lines"]).strip()
        if text_joined:
            entries.append({
                "number": len(entries) + 1,
                "local_number": current["local_number"],
                "chapter_number": current["chapter_number"],
                "chapter_title": current["chapter_title"],
                "paragraphs": [text_joined],
            })
        current = None

    for raw in lines:
        if raw.strip() == "":
            continue

        cm = CHAPTER_MARKER_RE.match(raw.strip())
        if cm and cm.group(1) in CHAPTER_TITLES:
            flush()
            chapter_number += 1
            chapter_title = cm.group(1)
            continue

        m = NUMBERED_LINE_RE.match(raw)
        if m:
            flush()
            current = {
                "local_number": int(m.group(1)),
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "lines": [m.group(2)],
            }
            continue

        if current is not None:
            current["lines"].append(raw.strip())
    flush()

    assert entries[-1]["chapter_title"] == "释音" and entries[-1]["paragraphs"] == [COLOPHON], \
        f"expected trailing colophon entry, got: {entries[-1]}"
    entries.pop()  # not a real glossary term -- see module docstring

    return entries


def _chapter_number_of(entries, title):
    for e in entries:
        if e["chapter_title"] == title:
            return e["chapter_number"]
    raise AssertionError(f"chapter {title!r} not found")


def verify_qijingbamai(entries):
    assert len(entries) > 0, "no entries parsed"
    numbers = [e["number"] for e in entries]
    assert numbers == list(range(1, len(entries) + 1)), "sequential numbering broken"
    chapter_numbers = sorted(set(e["chapter_number"] for e in entries))
    assert chapter_numbers == list(range(1, 20)), f"expected chapters 1..19 (incl. 提要): {chapter_numbers}"
    assert all(e["paragraphs"][0] for e in entries), "some entry has empty content"
    assert entries[0]["chapter_title"] == "提要", entries[0]["chapter_title"]
    assert entries[0]["paragraphs"][0].startswith("《奇经八脉考》一卷，明李时珍撰"), entries[0]["paragraphs"][0][:20]
    assert entries[-1]["chapter_title"] == "释音", entries[-1]["chapter_title"]
    assert entries[-1]["paragraphs"][0].startswith("洒洒"), entries[-1]["paragraphs"][0]
    assert not any(COLOPHON in p for e in entries for p in e["paragraphs"]), "colophon leaked into an entry"
    assert any(e["chapter_title"] == "八脉" for e in entries), "《八脉》chapter (scrape-junk heading) not detected"

    by_chapter = {}
    for e in entries:
        by_chapter.setdefault(e["chapter_number"], []).append(e["local_number"])
    for ch, nums in by_chapter.items():
        assert nums == sorted(set(nums)), f"chapter {ch}: local_number not strictly increasing: {nums}"

    chongmai_weibing = by_chapter[_chapter_number_of(entries, "冲脉为病")]
    assert 7 in chongmai_weibing and 8 not in chongmai_weibing and 9 in chongmai_weibing, \
        "expected 冲脉为病's known 7->9 numbering gap (no 8 in the source)"

    print(f"qijingbamai OK: {len(entries)} entries across {len(chapter_numbers)} chapters")


def main():
    DATA.mkdir(exist_ok=True)
    text = (SOURCES / "shennubencao.txt").read_text(encoding="utf-8")
    entries = parse_qijingbamai(text)
    verify_qijingbamai(entries)
    (DATA / "qijingbamai.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(entries)} entries to {DATA / 'qijingbamai.json'}")


if __name__ == "__main__":
    main()
