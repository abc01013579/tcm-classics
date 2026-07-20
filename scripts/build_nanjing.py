"""One-time parser: sources/shennubencao.txt -> data/nanjing.json.

Run manually, not imported by app.py. 《难经》(the Classic of Difficult
Issues) is bundled in the same raw scrape as 神农本草经, right after it
ends (same "extra text appended with no clean separator" quirk that
build_xinjing.py already deals with for the Heart Sutra).

Source quirks handled here:
- The leading arabic number on each entry line (e.g. "10 七十八难曰...")
  is a LOCAL per-chapter counter that resets to 1 at every chapter
  boundary -- it is NOT the entry's real number. The authoritative
  global 1-81 numbering is the Chinese numeral embedded in the entry's
  own text ("七十八难曰" = the 78th difficulty), which runs in
  unbroken sequence across the whole text. That's what gets parsed
  into `number` below.
- The 13 chapter-title marker lines (e.g. "2 《经络大数》") don't
  reliably fall between entries -- at least one lands mid-entry, after
  an entry's question but before its answer finishes. They're treated
  as pure boundary markers (update "current chapter", emit nothing)
  rather than as entry delimiters.
- Footnote lines ("1. 菽 : 原作"叔"。据...本改。", textual-critical
  annotations about restored/emended characters) are filtered out --
  distinguishable from entry-start lines because they have a period
  right after the number ("1.") where entry-starts have whitespace
  ("1  一难曰").
- Inline footnote-reference digits mid-sentence ("菽1之重", pointing to a
  "1. 菽 : 原作..." note elsewhere) are stripped -- the classical text
  only ever uses Chinese numerals, so a bare arabic digit sandwiched
  between Hanzi is always digitization noise, never content.
- 难 34's question has a pre-existing gap in the source itself
  ("声、色、臭、味、，可晓知以不" -- almost certainly missing "液"
  before the comma, since the answer covers all five of 声色臭味液).
  Left as-is rather than silently emended, same policy as the
  documented missing "10. 经脉" header gap in 灵枢经's source.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
SOURCES = ROOT / "sources"
DATA = ROOT / "data"

SECTION_START = "《难经》"
SECTION_END = "《奇经八脉考》"
FIRST_CHAPTER_MARKER = "1《经脉诊候》"

CHAPTER_TITLES = [
    "经脉诊候", "经络大数", "奇经八脉", "荣卫三焦", "藏府配像", "藏府度数",
    "虚实邪正", "藏府传病", "藏府积聚", "泄伤寒", "神圣工巧", "藏府井俞", "用针补泻",
]
CHAPTER_MARKER_RE = re.compile(r"^\d+\s*《([^》]+)》$")
ENTRY_START_RE = re.compile(r"^\d+\s+([一二三四五六七八九十百]+)难曰(.*)$")
FOOTNOTE_RE = re.compile(r"^\d+\.\s")
# A bare number + whitespace that ISN'T a "N难曰" entry start: this is the
# source's running local line-counter landing on a follow-up sub-question
# within the current 难's answer (nested dialogue, not a new difficulty).
# The leading number is transcription noise and gets stripped.
NUMBERED_CONTINUATION_RE = re.compile(r"^\d+\s+(.*)$")

DIGIT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
# Inline footnote-reference digits (e.g. "菽1之重" pointing to a "1. 菽:
# 原作..." textual-critical note elsewhere) -- the classical text itself only
# ever uses Chinese numerals, so any arabic digit sandwiched directly between
# Hanzi is digitization noise, not content.
INLINE_FOOTNOTE_REF_RE = re.compile(r"(?<=[一-鿿])\d+(?=[一-鿿，。；？！、])")


def chinese_to_int(s):
    """Converts a bounded Chinese numeral (1-99) to int, e.g. 八十一 -> 81."""
    if s == "十":
        return 10
    if "十" in s:
        tens_part, _, ones_part = s.partition("十")
        tens = DIGIT[tens_part] if tens_part else 1
        ones = DIGIT[ones_part] if ones_part else 0
        return tens * 10 + ones
    return DIGIT[s]


def parse_nanjing(text):
    lines = text.splitlines()
    start = lines.index(SECTION_START)
    end = lines.index(SECTION_END, start)
    # Skip the table-of-contents preamble between 《难经》 and the real start.
    body_start = lines.index(FIRST_CHAPTER_MARKER, start)
    lines = lines[body_start:end]

    entries = []
    current = None  # {"number", "chapter_number", "chapter_title", "lines": [...]}
    chapter_number = 0
    chapter_title = None

    def flush():
        nonlocal current
        if current is None:
            return
        paragraphs = []
        buf = []
        for line in current["lines"]:
            if line.strip() == "":
                if buf:
                    paragraphs.append("".join(buf))
                    buf = []
            else:
                buf.append(line.strip())
        if buf:
            paragraphs.append("".join(buf))
        paragraphs = [INLINE_FOOTNOTE_REF_RE.sub("", p) for p in paragraphs]
        entries.append({
            "number": current["number"],
            "chapter_number": current["chapter_number"],
            "chapter_title": current["chapter_title"],
            "paragraphs": paragraphs,
        })
        current = None

    for raw in lines:
        cm = CHAPTER_MARKER_RE.match(raw.strip())
        if cm and cm.group(1) in CHAPTER_TITLES:
            chapter_number += 1
            chapter_title = cm.group(1)
            continue

        if FOOTNOTE_RE.match(raw):
            continue

        em = ENTRY_START_RE.match(raw)
        if em:
            flush()
            number = chinese_to_int(em.group(1))
            current = {
                "number": number,
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "lines": [f"{em.group(1)}难曰{em.group(2)}"],
            }
            continue

        if current is not None:
            nc = NUMBERED_CONTINUATION_RE.match(raw)
            current["lines"].append(nc.group(1) if nc else raw)

    flush()
    return entries


def verify_nanjing(entries):
    assert len(entries) == 81, f"expected 81 难 entries, got {len(entries)}"
    numbers = [e["number"] for e in entries]
    assert numbers == list(range(1, 82)), f"entry numbers not contiguous 1..81: {numbers}"
    chapter_numbers = sorted(set(e["chapter_number"] for e in entries))
    assert chapter_numbers == list(range(1, 14)), f"expected chapters 1..13: {chapter_numbers}"
    assert all(e["paragraphs"] for e in entries), "some entry has empty paragraphs"
    assert entries[0]["chapter_title"] == "经脉诊候", entries[0]["chapter_title"]
    assert entries[-1]["chapter_title"] == "用针补泻", entries[-1]["chapter_title"]
    assert entries[0]["paragraphs"][0].startswith("一难曰"), entries[0]["paragraphs"][0]
    assert entries[-1]["paragraphs"][0].startswith("八十一难曰"), entries[-1]["paragraphs"][0]
    print(f"nanjing OK: {len(entries)} 难 across {len(chapter_numbers)} chapters")


def main():
    DATA.mkdir(exist_ok=True)
    text = (SOURCES / "shennubencao.txt").read_text(encoding="utf-8")
    entries = parse_nanjing(text)
    verify_nanjing(entries)
    (DATA / "nanjing.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(entries)} entries to {DATA / 'nanjing.json'}")


if __name__ == "__main__":
    main()
