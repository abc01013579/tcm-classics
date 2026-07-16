import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
NEIJING = json.loads((DATA_DIR / "neijing.json").read_text(encoding="utf-8"))
BENCAO = json.loads((DATA_DIR / "bencao.json").read_text(encoding="utf-8"))
ZHOUYI = json.loads((DATA_DIR / "zhouyi.json").read_text(encoding="utf-8"))
ZHOUYI_BY_NUMBER = {h["number"]: h for h in ZHOUYI}

NEIJING_BOOKS = [
    {"slug": "suwen", "name": "素问", "chapters": NEIJING["素问"]},
    {"slug": "lingshu", "name": "灵枢经", "chapters": NEIJING["灵枢经"]},
]
NEIJING_SLUG_TO_NAME = {b["slug"]: b["name"] for b in NEIJING_BOOKS}

BENCAO_JUAN = [
    {"slug": "shang", "name": "上卷", "entries": BENCAO["上卷"]},
    {"slug": "zhong", "name": "中卷", "entries": BENCAO["中卷"]},
    {"slug": "xia", "name": "下卷", "entries": BENCAO["下卷"]},
]
BENCAO_SLUG_TO_NAME = {j["slug"]: j["name"] for j in BENCAO_JUAN}

SNIPPET_RADIUS = 40


def get_neijing_chapter(book_slug, number):
    book_name = NEIJING_SLUG_TO_NAME.get(book_slug)
    if book_name is None:
        return None
    for chapter in NEIJING[book_name]:
        if chapter["number"] == number:
            return chapter
    return None


def get_bencao_juan(juan_slug):
    juan_name = BENCAO_SLUG_TO_NAME.get(juan_slug)
    if juan_name is None:
        return None
    return BENCAO[juan_name]


def get_zhouyi_hexagram(number):
    return ZHOUYI_BY_NUMBER.get(number)


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
            for paragraph in chapter["paragraphs"]:
                idx = paragraph.find(query)
                if idx != -1:
                    results.append({
                        "source": f"《{book['name']}》{chapter['title']}",
                        "url_book_slug": book["slug"],
                        "url_number": chapter["number"],
                        "kind": "neijing",
                        "snippet": _snippet(paragraph, idx, len(query)),
                    })

    for juan in BENCAO_JUAN:
        for entry in juan["entries"]:
            idx = entry["text"].find(query)
            if idx != -1:
                results.append({
                    "source": f"《神农本草经》{juan['name']}",
                    "url_juan_slug": juan["slug"],
                    "kind": "bencao",
                    "snippet": _snippet(entry["text"], idx, len(query)),
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

    return results
