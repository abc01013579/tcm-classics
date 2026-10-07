import hashlib
import os
import re
import subprocess
import sys
from datetime import date
from functools import wraps
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

import tcm_core as core

ROOT = Path(__file__).parent
JOURNAL_DIR = ROOT / "journal"
PHOTO_DIR = ROOT / "static" / "journal"
ALLOWED_PHOTO_EXTS = {"jpg", "jpeg", "png", "gif", "webp"}

sys.path.insert(0, str(ROOT / "scripts"))
import build_journal

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-secret-key")

# Short hash of style.css, appended as ?v=... to its URL in base.html, so a
# changed stylesheet gets a new URL and browsers/Cloudflare can't keep serving
# the old one from cache (it's sent with max-age=14400).
CSS_VERSION = hashlib.md5((ROOT / "static" / "style.css").read_bytes()).hexdigest()[:8]


@app.context_processor
def inject_css_version():
    return {"css_version": CSS_VERSION}


CN_DIGITS = "零一二三四五六七八九"


@app.template_filter("cn_num")
def cn_num(n):
    """1..99 as Chinese numerals: 1 -> 一, 10 -> 十, 24 -> 二十四."""
    tens, ones = divmod(n, 10)
    head = "" if tens == 0 else ("十" if tens == 1 else CN_DIGITS[tens] + "十")
    return head + (CN_DIGITS[ones] if ones else "")


@app.template_filter("utf8bits")
def utf8bits(ch):
    """One character's UTF-8 bytes as 8-bit groups: 元 -> 11100101 10000101 10000011."""
    return " ".join(f"{b:08b}" for b in ch.encode("utf-8"))

JOURNAL_PASSWORD = os.environ.get("JOURNAL_PASSWORD")
# .strip(): a token pasted into Render's dashboard can carry a trailing newline,
# which git rejects inside the push URL ("url contains a newline").
GITHUB_PUSH_TOKEN = (os.environ.get("GITHUB_PUSH_TOKEN") or "").strip() or None
GITHUB_REPO = "abc01013579/tcm-classics"

SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authed"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def _slugify(title):
    ascii_title = title.encode("ascii", "ignore").decode("ascii").lower()
    return SLUG_STRIP_RE.sub("-", ascii_title).strip("-")


def _commit_and_push(entry_path, title, extra_paths=()):
    if not GITHUB_PUSH_TOKEN:
        raise RuntimeError("GITHUB_PUSH_TOKEN 未配置，无法推送")

    rel_entry = str(entry_path.relative_to(ROOT))
    rel_extra = [str(p.relative_to(ROOT)) for p in extra_paths]
    run = lambda *cmd: subprocess.run(
        cmd, cwd=ROOT, check=True, capture_output=True, text=True
    )
    committed = False
    try:
        run("git", "add", rel_entry, "data/journal.json", *rel_extra)
        run(
            "git", "-c", "user.name=abc01013579", "-c", "user.email=zhongyuan1358@gmail.com",
            "commit", "-m", f"Add journal entry: {title}",
        )
        committed = True
        push_url = f"https://x-access-token:{GITHUB_PUSH_TOKEN}@github.com/{GITHUB_REPO}.git"
        run("git", "push", push_url, "HEAD:main")
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").replace(GITHUB_PUSH_TOKEN, "***")
        app.logger.error("git %s failed: %s", exc.cmd[1], stderr)
        if committed:
            # push failed after a local commit landed -- unwind it so the working
            # tree/index end up exactly as they were before this attempt, since the
            # caller will delete the new .md file and rebuild journal.json to match.
            subprocess.run(["git", "reset", "HEAD~1"], cwd=ROOT)
        raise RuntimeError("git 提交或推送失败，请稍后重试") from None


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


ZHOUYI_VERSION_MENU = [
    ("", "对照"),
    ("simp", "简体"),
    ("trad", "繁體"),
    ("en", "English"),
    ("seal", "小篆"),
    ("bin", "二进制"),
]


def zhouyi_version():
    v = request.args.get("v", "")
    return v if v in dict(ZHOUYI_VERSION_MENU) else ""


@app.route("/zhouyi")
def zhouyi_index():
    return render_template(
        "zhouyi_index.html",
        hexagrams=core.ZHOUYI,
        versions=core.ZHOUYI_VERSIONS,
        v=zhouyi_version(),
        version_menu=ZHOUYI_VERSION_MENU,
    )


@app.route("/zhouyi/<int:number>")
def zhouyi_chapter(number):
    hexagram = core.get_zhouyi_hexagram(number)
    if hexagram is None:
        abort(404)
    return render_template(
        "zhouyi_chapter.html",
        hexagram=hexagram,
        total=len(core.ZHOUYI),
        text=core.ZHOUYI_VERSIONS[str(number)],
        v=zhouyi_version(),
        version_menu=ZHOUYI_VERSION_MENU,
    )


@app.route("/xinjing")
def xinjing():
    return render_template("xinjing.html", sutra=core.XINJING)


@app.route("/fuxingjue")
def fuxingjue():
    return render_template("fuxingjue.html", doc=core.FUXINGJUE)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    next_url = request.values.get("next") or url_for("journal_new")
    if request.method == "POST":
        next_url = request.form.get("next") or next_url
        if JOURNAL_PASSWORD and request.form.get("password") == JOURNAL_PASSWORD:
            session["authed"] = True
            return redirect(next_url)
        error = "密码错误"
    return render_template("login.html", error=error, next=next_url)


@app.route("/logout")
def logout():
    session.pop("authed", None)
    return redirect(url_for("journal_index"))


@app.route("/journal")
def journal_index():
    return render_template("journal_index.html", entries=core.JOURNAL)


@app.route("/journal/new", methods=["GET", "POST"])
@login_required
def journal_new():
    error = None
    form = {"title": "", "date": date.today().isoformat(), "body": "", "body_en": ""}

    if request.method == "POST":
        form["title"] = request.form.get("title", "").strip()
        form["date"] = request.form.get("date", "").strip()
        form["body"] = request.form.get("body", "").strip()
        form["body_en"] = request.form.get("body_en", "").strip()
        photo = request.files.get("photo")
        photo_ext = ""
        if photo and photo.filename:
            photo_ext = secure_filename(photo.filename).rsplit(".", 1)[-1].lower()

        if not form["title"] or not form["date"] or not form["body"]:
            error = "标题、日期、正文都不能为空。"
        elif photo and photo.filename and photo_ext not in ALLOWED_PHOTO_EXTS:
            error = "照片格式需为 jpg/jpeg/png/gif/webp。"
        else:
            slug = f"{form['date']}-{_slugify(form['title']) or 'entry'}"
            path = JOURNAL_DIR / f"{slug}.md"
            if path.exists():
                error = "这个日期和标题已经有一篇随笔了，换个标题试试。"
            else:
                photo_path = None
                if photo and photo.filename:
                    photo_path = PHOTO_DIR / f"{slug}.{photo_ext}"
                    photo.save(photo_path)
                    media_md = f"\n\n![{form['title']}](/static/journal/{photo_path.name})"
                    form["body"] += media_md
                    if form["body_en"]:
                        form["body_en"] += media_md

                content = f"---\ntitle: {form['title']}\ndate: {form['date']}\n---\n\n{form['body']}\n"
                if form["body_en"]:
                    content += f"\n<!--en-->\n\n{form['body_en']}\n"
                path.write_text(content, encoding="utf-8")
                extra_paths = tuple(p for p in (photo_path,) if p)

                try:
                    build_journal.build()
                    _commit_and_push(path, form["title"], extra_paths=extra_paths)
                except Exception as exc:
                    path.unlink(missing_ok=True)
                    for p in extra_paths:
                        p.unlink(missing_ok=True)
                    build_journal.build()
                    error = str(exc)
                else:
                    return redirect(url_for("journal_entry", slug=slug))
                finally:
                    core.reload_journal()

    return render_template("journal_new.html", error=error, form=form)


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
