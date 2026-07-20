from flask import Flask, render_template, request, abort

import tcm_core as core

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", zhouyi_icon=core.ZHOUYI[0])


@app.route("/neijing")
def neijing_index():
    return render_template("neijing_index.html", books=core.NEIJING_BOOKS)


@app.route("/neijing/<book_slug>/<int:number>")
def neijing_chapter(book_slug, number):
    chapter = core.get_neijing_chapter(book_slug, number)
    if chapter is None:
        abort(404)
    book_name = core.NEIJING_SLUG_TO_NAME[book_slug]
    total = len(core.NEIJING[book_name])
    return render_template(
        "neijing_chapter.html",
        book_slug=book_slug,
        book_name=book_name,
        chapter=chapter,
        total=total,
    )


@app.route("/bencao")
def bencao_index():
    return render_template("bencao_index.html", juan_list=core.BENCAO_JUAN)


@app.route("/bencao/<juan_slug>")
def bencao_juan(juan_slug):
    entries = core.get_bencao_juan(juan_slug)
    if entries is None:
        abort(404)
    return render_template(
        "bencao_juan.html",
        juan_slug=juan_slug,
        juan_name=core.BENCAO_SLUG_TO_NAME[juan_slug],
        entries=entries,
    )


@app.route("/zhouyi")
def zhouyi_index():
    return render_template("zhouyi_index.html", hexagrams=core.ZHOUYI)


@app.route("/zhouyi/<int:number>")
def zhouyi_chapter(number):
    hexagram = core.get_zhouyi_hexagram(number)
    if hexagram is None:
        abort(404)
    return render_template("zhouyi_chapter.html", hexagram=hexagram, total=len(core.ZHOUYI))


@app.route("/xinjing")
def xinjing():
    return render_template("xinjing.html", sutra=core.XINJING)


@app.route("/nanjing")
def nanjing_index():
    return render_template("nanjing_index.html", chapters=core.NANJING_CHAPTERS)


@app.route("/nanjing/<int:number>")
def nanjing_entry(number):
    entry = core.get_nanjing_entry(number)
    if entry is None:
        abort(404)
    return render_template("nanjing_entry.html", entry=entry, total=len(core.NANJING))


@app.route("/journal")
def journal_index():
    return render_template("journal_index.html", entries=core.JOURNAL)


@app.route("/journal/<slug>")
def journal_entry(slug):
    entry = core.get_journal_entry(slug)
    if entry is None:
        abort(404)
    idx = core.JOURNAL.index(entry)
    older_entry = core.JOURNAL[idx + 1] if idx + 1 < len(core.JOURNAL) else None
    newer_entry = core.JOURNAL[idx - 1] if idx > 0 else None
    return render_template(
        "journal_entry.html", entry=entry, older_entry=older_entry, newer_entry=newer_entry
    )


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = core.search(query) if query else []
    return render_template("search.html", query=query, results=results)


if __name__ == "__main__":
    app.run(debug=True)
