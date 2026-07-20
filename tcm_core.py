import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
NEIJING = json.loads((DATA_DIR / "neijing.json").read_text(encoding="utf-8"))
NEIJING_EN = json.loads((DATA_DIR / "neijing_en.json").read_text(encoding="utf-8"))
NEIJING_EN_BY_NUMBER = {
    name: {c["number"]: c for c in chapters} for name, chapters in NEIJING_EN.items()
}
BENCAO = json.loads((DATA_DIR / "bencao.json").read_text(encoding="utf-8"))
BENCAO_EN = json.loads((DATA_DIR / "bencao_en.json").read_text(encoding="utf-8"))
ZHOUYI = json.loads((DATA_DIR / "zhouyi.json").read_text(encoding="utf-8"))
ZHOUYI_BY_NUMBER = {h["number"]: h for h in ZHOUYI}

JOURNAL = json.loads((DATA_DIR / "journal.json").read_text(encoding="utf-8"))
JOURNAL_BY_SLUG = {e["slug"]: e for e in JOURNAL}

XINJING = json.loads((DATA_DIR / "xinjing.json").read_text(encoding="utf-8"))

FUXINGJUE = json.loads((DATA_DIR / "fuxingjue.json").read_text(encoding="utf-8"))

NANJING = json.loads((DATA_DIR / "nanjing.json").read_text(encoding="utf-8"))
NANJING_BY_NUMBER = {e["number"]: e for e in NANJING}

NANJING_CHAPTERS = []
for _entry in NANJING:
    if not NANJING_CHAPTERS or NANJING_CHAPTERS[-1]["number"] != _entry["chapter_number"]:
        NANJING_CHAPTERS.append({
            "number": _entry["chapter_number"],
            "title": _entry["chapter_title"],
            "entries": [],
        })
    NANJING_CHAPTERS[-1]["entries"].append(_entry)

NEIJING_BOOKS = [
    {"slug": "suwen", "name": "素问", "chapters": NEIJING["素问"]},
    {"slug": "lingshu", "name": "灵枢经", "chapters": NEIJING["灵枢经"]},
]
NEIJING_SLUG_TO_NAME = {b["slug"]: b["name"] for b in NEIJING_BOOKS}

def _bilingual_entries(juan_name):
    zh_list = BENCAO[juan_name]
    en_list = BENCAO_EN[juan_name]
    return [
        {
            "number": zh["number"],
            "is_header": zh["is_header"],
            "text": zh["text"],
            "text_en": en["text"],
        }
        for zh, en in zip(zh_list, en_list)
    ]


BENCAO_JUAN = [
    {"slug": "shang", "name": "上卷", "entries": _bilingual_entries("上卷")},
    {"slug": "zhong", "name": "中卷", "entries": _bilingual_entries("中卷")},
    {"slug": "xia", "name": "下卷", "entries": _bilingual_entries("下卷")},
]
BENCAO_SLUG_TO_NAME = {j["slug"]: j["name"] for j in BENCAO_JUAN}
BENCAO_JUAN_BY_SLUG = {j["slug"]: j for j in BENCAO_JUAN}

SNIPPET_RADIUS = 40


def get_neijing_chapter(book_slug, number):
    book_name = NEIJING_SLUG_TO_NAME.get(book_slug)
    if book_name is None:
        return None
    for chapter in NEIJING[book_name]:
        if chapter["number"] != number:
            continue
        en = NEIJING_EN_BY_NUMBER.get(book_name, {}).get(number)
        if en is None:
            return {**chapter, "title_en": None, "bilingual": False}
        return {
            "number": chapter["number"],
            "title": chapter["title"],
            "title_en": en["title_en"],
            "paragraphs": chapter["paragraphs"],
            "pairs": list(zip(chapter["paragraphs"], en["paragraphs_en"])),
            "bilingual": True,
        }
    return None


def get_bencao_juan(juan_slug):
    juan = BENCAO_JUAN_BY_SLUG.get(juan_slug)
    if juan is None:
        return None
    return juan["entries"]


def get_zhouyi_hexagram(number):
    return ZHOUYI_BY_NUMBER.get(number)


def get_nanjing_entry(number):
    return NANJING_BY_NUMBER.get(number)


def get_journal_entry(slug):
    return JOURNAL_BY_SLUG.get(slug)


def _snippet(text, index, match_len):
    start = max(0, index - SNIPPET_RADIUS)
    end = min(len(text), index + match_len + SNIPPET_RADIUS)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    return prefix + text[start:end] + suffix


def search(query):
    results = []
    for book in NEIJING_BOOKS:
        for chapter in book["chapters"]:
            en = NEIJING_EN_BY_NUMBER.get(book["name"], {}).get(chapter["number"])
            paragraphs_en = en["paragraphs_en"] if en else [None] * len(chapter["paragraphs"])
            for zh_para, en_para in zip(chapter["paragraphs"], paragraphs_en):
                haystack = f"{zh_para}\n{en_para}" if en_para else zh_para
                idx = haystack.find(query)
                if idx != -1:
                    results.append({
                        "source": f"《{book['name']}》{chapter['title']}",
                        "url_book_slug": book["slug"],
                        "url_number": chapter["number"],
                        "kind": "neijing",
                        "snippet": _snippet(haystack, idx, len(query)),
                    })

    for juan in BENCAO_JUAN:
        for entry in juan["entries"]:
            haystack = f"{entry['text']}\n{entry['text_en']}"
            idx = haystack.find(query)
            if idx != -1:
                results.append({
                    "source": f"《神农本草经》{juan['name']}",
                    "url_juan_slug": juan["slug"],
                    "kind": "bencao",
                    "snippet": _snippet(haystack, idx, len(query)),
                })

    for hexagram in ZHOUYI:
        texts = [hexagram["judgment_zh"], hexagram["judgment_en"], *hexagram["lines_zh"], *hexagram["lines_en"]]
        for text in texts:
            idx = text.find(query)
            if idx != -1:
                results.append({
                    "source": f"《周易》{hexagram['number']}. {hexagram['chinese']} ({hexagram['title_en']})",
                    "url_number": hexagram["number"],
                    "kind": "zhouyi",
                    "snippet": _snippet(text, idx, len(query)),
                })
                break

    for entry in NANJING:
        haystack = "".join(entry["paragraphs"])
        idx = haystack.find(query)
        if idx != -1:
            results.append({
                "source": f"《难经》{entry['chapter_title']}·{entry['number']}",
                "url_number": entry["number"],
                "kind": "nanjing",
                "snippet": _snippet(haystack, idx, len(query)),
            })

    for i, para in enumerate(XINJING["paragraphs"]):
        haystack = f"{para['zh']}\n{para['en']}"
        idx = haystack.find(query)
        if idx != -1:
            results.append({
                "source": f"《{XINJING['title_zh']}》({XINJING['title_en']})",
                "kind": "xinjing",
                "snippet": _snippet(haystack, idx, len(query)),
            })

    for para in FUXINGJUE["paragraphs"]:
        idx = para.find(query)
        if idx != -1:
            results.append({
                "source": f"《{FUXINGJUE['title']}》",
                "kind": "fuxingjue",
                "snippet": _snippet(para, idx, len(query)),
            })
            break

    for entry in JOURNAL:
        haystack = f"{entry['title']}\n{entry['body_text']}"
        idx = haystack.find(query)
        if idx != -1:
            results.append({
                "source": f"《随笔》{entry['title']} · {entry['date']}",
                "url_slug": entry["slug"],
                "kind": "journal",
                "snippet": _snippet(haystack, idx, len(query)),
            })

    return results
