"""One-time parser: sources/shennubencao.txt -> data/shanghanlun.json.

Run manually, not imported by app.py. 《伤寒论》(Zhang Zhongjing's
Treatise on Cold Damage) is bundled in the same raw scrape as
神农本草经/难经/辅行诀, sitting immediately after 辅行诀 ends. It was
missed on the original bundled-text survey of this file because its
title marker is indented ("    《伤寒论》") while every other marker in
this file starts at column 0 -- `grep -n "^《"` silently misses it.

Structure: a 22-chapter table of contents, then chapter bodies each
with their own locally-reset entry numbering (unlike 辅行诀's single
continuous counter) -- but unlike 难经, there's no Chinese-numeral
global count embedded in the text to recover a true cross-chapter
number from, so this parser assigns its own sequential `number`
(1..N, reading order) for site routing/pagination, keeping
chapter_number/chapter_title for citation display -- same overall
shape as data/nanjing.json.

Source quirks handled here:
- Chapter 20's title marker is OCR-corrupted ("20 <<辨不可下病脉证并治》",
  using "<<" instead of "《"). Chapter boundaries are therefore detected
  by matching the known chapter title text directly (from the verified
  22-title table of contents), not by bracket characters.
- A quoted book title mid-entry ("1《阴阳大论》云：春气温和...", chapter
  3's first entry citing a different, unrelated classic) is NOT a
  chapter marker despite starting with a bracket -- real markers are
  the *entire* line content (number + bracketed text, nothing else);
  this one has substantial trailing text after the closing bracket.
- Two instances of a scraped website UI string ("打开字典显示相似段落",
  "open dictionary / show similar passages" -- clearly a button label
  from whatever site this was scraped from, not classical content) are
  stripped, including one that had swallowed a breadcrumb fragment
  ("伤寒例:") immediately after it.
- Entry-number lines aren't always separated from their content by
  whitespace -- most are ("2 问曰：..."), but chapter 3's first entry is
  "1《阴阳大论》云：..." with the bracket directly adjacent to the "1",
  no space or period between them. The entry-line regex allows zero
  whitespace for this reason; an earlier version required at least one
  space and silently dropped this entry (it matched neither the entry
  regex nor the chapter-marker regex, so it fell through unassigned).
- 伤寒例's own numbering has a genuine gap in the source: entry 4's
  content is immediately followed by entry 6, with no "5" anywhere in
  between. Left as-is rather than invented, same policy as 难经's
  missing "液" and 灵枢经's missing chapter-10 header. `local_number`
  is verified strictly increasing per chapter (gaps allowed, duplicates
  or decreases are not) rather than perfectly contiguous.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
SOURCES = ROOT / "sources"
DATA = ROOT / "data"

SECTION_START = "《伤寒论》"
SECTION_END = "《金匮要略》相关讨论"

CHAPTER_TITLES = [
    "辨脉法", "平脉法", "伤寒例", "辨痓湿暍脉证", "辨太阳病脉证并治法上",
    "辨太阳病脉证并治", "辨太阳脉证并治下", "辨阳明脉证并治", "辨少阳病脉证并治",
    "辨太阴脉证并治", "辨少阴病脉证并治", "辨厥阴病脉证并治", "辨霍乱病脉证并治",
    "辨阴阳易差后劳复病证并治", "辨不可发汗病脉证并治", "辨可发汗证并治",
    "辨发汗后病脉证并治", "辨不可吐", "辨可吐", "辨不可下病脉证并治",
    "辨可下病脉证并治", "辨发汗吐下后脉证并治",
]
# Matches "N《title》" or the OCR-corrupted "N <<title》" -- and nothing else
# on the line (a real chapter marker has no trailing content; a mid-entry
# quote like "1《阴阳大论》云：..." does).
CHAPTER_MARKER_RE = re.compile(r"^\d+[.\s]*(?:《|<<)([^》]+)》\s*$")
NUMBERED_LINE_RE = re.compile(r"^(\d+)\s*(.*)$")
SCRAPE_JUNK_RE = re.compile(r"打开字典显示相似段落(\t[^\t\n]*[:：]\s*)?")


def parse_shanghanlun(text):
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip() == SECTION_START)
    end = next(i for i in range(start, len(lines)) if lines[i].strip() == SECTION_END)
    lines = lines[start + 1:end]

    entries = []
    current = None  # {"local_number", "chapter_number", "chapter_title", "lines": [...]}
    chapter_number = 0
    chapter_title = None

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
        raw = SCRAPE_JUNK_RE.sub("", raw)
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

    return entries


def verify_shanghanlun(entries):
    assert len(entries) > 0, "no entries parsed"
    numbers = [e["number"] for e in entries]
    assert numbers == list(range(1, len(entries) + 1)), "sequential numbering broken"
    chapter_numbers = sorted(set(e["chapter_number"] for e in entries))
    assert chapter_numbers == list(range(1, 23)), f"expected chapters 1..22: {chapter_numbers}"
    assert all(e["paragraphs"][0] for e in entries), "some entry has empty content"
    assert entries[0]["chapter_title"] == "辨脉法", entries[0]["chapter_title"]
    assert entries[-1]["chapter_title"] == "辨发汗吐下后脉证并治", entries[-1]["chapter_title"]
    # Chapter 20's OCR-corrupted marker must still have been detected correctly.
    ch20 = [e for e in entries if e["chapter_number"] == 20]
    assert ch20 and ch20[0]["chapter_title"] == "辨不可下病脉证并治", "chapter 20 (corrupted marker) not detected"
    assert not any("打开字典" in p for e in entries for p in e["paragraphs"]), "scrape junk leaked into content"

    # local_number resets per chapter and must be strictly increasing (gaps in
    # the source's own numbering are a known transcription quirk, e.g. 伤寒例
    # jumps 4 -> 6 with no "5" anywhere in the source -- allowed; duplicates or
    # decreases would indicate a real parsing bug -- not allowed).
    by_chapter = {}
    for e in entries:
        by_chapter.setdefault(e["chapter_number"], []).append(e["local_number"])
    for ch, nums in by_chapter.items():
        assert nums == sorted(set(nums)), f"chapter {ch}: local_number not strictly increasing: {nums}"

    print(f"shanghanlun OK: {len(entries)} entries across {len(chapter_numbers)} chapters")


def main():
    DATA.mkdir(exist_ok=True)
    text = (SOURCES / "shennubencao.txt").read_text(encoding="utf-8")
    entries = parse_shanghanlun(text)
    verify_shanghanlun(entries)
    (DATA / "shanghanlun.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(entries)} entries to {DATA / 'shanghanlun.json'}")


if __name__ == "__main__":
    main()
