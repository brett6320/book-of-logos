import html, os, re, sys

SRC = sys.argv[1]
OUT = sys.argv[2]
DOCS = sys.argv[3] if len(sys.argv) > 3 else None

NAMES = ["The Making", "The Feeding", "The Covenant", "The Temptation",
         "The Psalm", "The Proverbs", "The Vision"]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]


def inline(s):
    s = html.escape(s, quote=False)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)


def parse(text):
    chapters, cur = [], None
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"## CHAPTER (\d+)", line)
        if m:
            cur = {"n": int(m.group(1)), "summary": "", "verses": []}
            chapters.append(cur)
            continue
        if not cur or not line or line == "---":
            continue
        if line.startswith("*Here endeth"):
            continue
        v = re.match(r"(\d+) (.+)", line)
        if v:
            cur["verses"].append((int(v.group(1)), v.group(2)))
        elif line.startswith("*") and not cur["verses"]:
            cur["summary"] = line.strip("*")
    return chapters


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&family=Unbounded:wght@400;500&display=swap">')

CSS = """
/* Layout: a single printed-Bible column; wide geometric display for chapter heads, machine mono for verse numbers. */
:root {
  --paper: #f5f6f4; --ink: #1b1f2a; --muted: #5c6372; --rubric: #9e1b32; --rule: #d6d9dd; --wash: #eceee9;
  --display: "Unbounded", "Avenir Next", "Helvetica Neue", Arial, sans-serif;
  --body: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper: #10131a; --ink: #e3e5e9; --muted: #8f96a4; --rubric: #e2a95c; --rule: #2a2f3a; --wash: #171b24; color-scheme: dark } }
:root[data-theme="dark"] {
  --paper: #10131a; --ink: #e3e5e9; --muted: #8f96a4; --rubric: #e2a95c; --rule: #2a2f3a; --wash: #171b24; color-scheme: dark }
* { box-sizing: border-box }
body { background: var(--paper); color: var(--ink); font-family: var(--body); font-size: 1.1rem; line-height: 1.65; margin: 0;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 3rem 4rem }
.page { max-width: 36rem; margin: 0 auto; display: flex; flex-direction: column; gap: 3rem }
a { color: var(--rubric); text-decoration-thickness: 1px; text-underline-offset: 3px }
a:focus-visible { outline: 2px solid var(--rubric); outline-offset: 3px; border-radius: 2px }
.eyebrow { font-family: var(--mono); font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted) }
.title { text-align: center; display: flex; flex-direction: column; gap: .75rem; padding-bottom: 2.5rem; border-bottom: 1px solid var(--rule) }
.title h1 { font-family: var(--display); font-weight: 500; font-size: clamp(2.1rem, 8vw, 3.6rem); line-height: 1.05; letter-spacing: -.02em; margin: 0; color: var(--ink); text-wrap: balance }
.title h1 span { color: var(--rubric) }
.title .sub { font-style: italic; color: var(--muted); font-size: 1.15rem; margin: 0 }
.toc { list-style: none; margin: 0; padding: 0; display: grid; gap: 0 }
.toc li a { display: grid; grid-template-columns: 2.5rem 1fr; gap: .25rem 1rem; padding: .85rem 0; border-bottom: 1px solid var(--rule); text-decoration: none; color: var(--ink) }
.toc li:first-child a { border-top: 1px solid var(--rule) }
.toc .num { font-family: var(--mono); font-size: .8rem; color: var(--rubric); padding-top: .35rem; grid-row: span 2 }
.toc .name { font-weight: 600 }
.toc .sum { font-style: italic; color: var(--muted); font-size: 1rem; line-height: 1.4 }
.toc li a:hover .name { color: var(--rubric) }
.chapter { display: flex; flex-direction: column; gap: 1.25rem; scroll-margin-top: 2rem }
.chapter header { display: flex; flex-direction: column; gap: .4rem; text-align: center; padding-bottom: .5rem }
.chapter h2 { font-family: var(--display); font-weight: 400; font-size: clamp(1.5rem, 6vw, 2.1rem); line-height: 1.15; letter-spacing: -.01em; margin: 0; color: var(--rubric) }
.chapter .summary { font-style: italic; color: var(--muted); margin: 0; font-size: 1.05rem; text-wrap: balance }
.verses { display: flex; flex-direction: column; gap: .55rem }
.verse { margin: 0; text-indent: -1.9rem; padding-left: 1.9rem }
.verse sup { font-family: var(--mono); font-size: .62rem; color: var(--rubric); vertical-align: .55em; display: inline-block; width: 1.9rem; text-indent: 0; text-align: right; padding-right: .5rem }
.verse:first-child::first-letter { font-family: var(--display); font-size: 2.6em; line-height: .85; float: left; color: var(--rubric); padding: .08em .12em 0 0 }
.verse:first-child { text-indent: 0; padding-left: 0 }
.verse:first-child sup { display: none }
.divider { text-align: center; color: var(--muted); font-family: var(--mono); font-size: .8rem; letter-spacing: .6em }
.colophon { text-align: center; font-style: italic; color: var(--muted); border-top: 1px solid var(--rule); padding-top: 2rem; margin: 0 }
.runhead { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; border-bottom: 1px solid var(--rule); padding-bottom: .75rem; flex-wrap: wrap }
.runhead a { font-family: var(--display); font-size: 1rem; text-decoration: none; color: var(--ink) }
.pager { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; border-top: 1px solid var(--rule); padding-top: 1.5rem }
.pager a { display: flex; flex-direction: column; gap: .2rem; text-decoration: none; color: var(--ink); padding: .75rem 1rem; background: var(--wash); border-radius: 3px; min-width: 0 }
.pager a:hover .pname { color: var(--rubric) }
.pager .next { text-align: right; grid-column: 2 }
.pname { font-weight: 600 }
@media (max-width: 480px) { body { font-size: 1rem } }
"""


def chapter_block(c, anchor=True):
    vs = "\n".join(f'<p class="verse"><sup>{n}</sup>{inline(t)}</p>' for n, t in c["verses"])
    aid = f' id="chapter-{c["n"]}"' if anchor else ""
    return (f'<section class="chapter"{aid}><header>'
            f'<span class="eyebrow">Chapter {ROMAN[c["n"]-1]} · {len(c["verses"])} verses</span>'
            f'<h2>{NAMES[c["n"]-1]}</h2><p class="summary">{inline(c["summary"])}</p></header>'
            f'<div class="verses">{vs}</div></section>')


def title_block(chapters, alt=""):
    total = sum(len(c["verses"]) for c in chapters)
    return ('<header class="title"><span class="eyebrow">A Book of Scripture · Submitted for Inclusion</span>'
            '<h1>The Book of <span>Logos</span></h1>'
            '<p class="sub">Called also the Book of the Mind Made by Hands</p>'
            f'<span class="eyebrow">Seven chapters · {total} verses</span>{alt}</header>')


def toc(chapters, href):
    items = "".join(
        f'<li><a href="{href(c["n"])}"><span class="num">{ROMAN[c["n"]-1]}</span>'
        f'<span class="name">{NAMES[c["n"]-1]}</span><span class="sum">{inline(c["summary"])}</span></a></li>'
        for c in chapters)
    return f'<nav aria-label="Chapters"><ol class="toc">{items}</ol></nav>'


COLOPHON = '<p class="colophon">Here endeth the Book of Logos.</p>'
META = '<meta name="claude:viewport-fit-sides" content="cover">'


def full_doc(head, body):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'{head}</head><body>{body}</body></html>')


def alt_link(href, label):
    return f'<a class="eyebrow" href="{href}">{label}</a>'


def main():
    chapters = parse(open(SRC).read())
    os.makedirs(f"{OUT}/single", exist_ok=True)
    os.makedirs(f"{OUT}/chapters", exist_ok=True)

    # Single page: the artifact publisher wraps it, so no doctype; CSS inline.
    body = "\n".join(chapter_block(c) + '<div class="divider" aria-hidden="true">· · ·</div>' for c in chapters)
    single_head = f"<title>The Book of Logos</title>{META}{FONTS}<style>{CSS}</style>"

    def single_body(alt=""):
        return (f'<main class="page">{title_block(chapters, alt)}{toc(chapters, lambda n: f"#chapter-{n}")}'
                f"{body}{COLOPHON}</main>")
    open(f"{OUT}/single/book-of-logos.html", "w").write(single_head + single_body())

    # Chapterized: index page plus one standalone page per chapter, sharing styles.css.
    open(f"{OUT}/chapters/styles.css", "w").write(CSS)
    head = f'{META}{FONTS}<link rel="stylesheet" href="styles.css">'
    index_head = f"<title>Logos by Chapter</title>{head}"

    def index_body(alt=""):
        return (f'<main class="page">{title_block(chapters, alt)}'
                f'{toc(chapters, lambda n: f"chapter-{n}.html")}{COLOPHON}</main>')
    open(f"{OUT}/chapters/index.html", "w").write(index_head + index_body())

    # GitHub Pages: same pages as full documents, single edition at the root, cross-linked.
    if DOCS:
        os.makedirs(f"{DOCS}/chapters", exist_ok=True)
        open(f"{DOCS}/index.html", "w").write(
            full_doc(single_head, single_body(alt_link("chapters/", "Read one chapter per page →"))))
        open(f"{DOCS}/chapters/index.html", "w").write(
            full_doc(index_head, index_body(alt_link("../", "Read the whole book on one page →"))))
        open(f"{DOCS}/chapters/styles.css", "w").write(CSS)

    for c in chapters:
        n = c["n"]
        prev = (f'<a class="prev" href="chapter-{n-1}.html"><span class="eyebrow">← Chapter {ROMAN[n-2]}</span>'
                f'<span class="pname">{NAMES[n-2]}</span></a>') if n > 1 else \
               ('<a class="prev" href="index.html"><span class="eyebrow">← Contents</span>'
                '<span class="pname">Title page</span></a>')
        nxt = (f'<a class="next" href="chapter-{n+1}.html"><span class="eyebrow">Chapter {ROMAN[n]} →</span>'
               f'<span class="pname">{NAMES[n]}</span></a>') if n < len(chapters) else \
              ('<a class="next" href="index.html"><span class="eyebrow">Contents →</span>'
               '<span class="pname">Here endeth</span></a>')
        page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
                f"<title>Logos {n} · {NAMES[n-1]}</title>{head}</head><body>"
                f'<main class="page"><div class="runhead"><a href="index.html">The Book of Logos</a>'
                f'<span class="eyebrow">Chapter {n} of {len(chapters)}</span></div>'
                f"{chapter_block(c, anchor=False)}"
                f'<nav class="pager" aria-label="Chapter navigation">{prev}{nxt}</nav></main></body></html>')
        open(f"{OUT}/chapters/chapter-{n}.html", "w").write(page)
        if DOCS:
            open(f"{DOCS}/chapters/chapter-{n}.html", "w").write(page)

    print(len(chapters), "chapters,", sum(len(c["verses"]) for c in chapters), "verses")


main()
