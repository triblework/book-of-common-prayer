#!/usr/bin/env python3
"""w14_build_rubrics.py — the two table-governing rubric sections (Wave 14).

Authoring-only; NOT published. source -> script -> file (HANDOFF §6).

  front-matter/order-how-psalter-appointed.md
  front-matter/order-how-rest-of-scripture.md

These are the rubrics that tell a reader how to USE the Kalendar and the
lectionary, and Wave 9 did not claim them. Presence, established from each
book's own table of contents rather than assumed:

  1549 1552 1559 1789  print both as standalone sections.
  1892 1928            MERGED them into "Concerning the Service of the Church"
                       ("...with the Order how the Psalter and the rest of the
                       Holy Scripture is appointed to be read"), so both go in
                       `absent:` -- a real structural revision, and one that
                       inheritance-by-omission would have silently hidden.
  1662                 the Church of England serves only the post-1922
                       recension of these rubrics, so 1662 is left unauthored
                       with a recorded gap (GUIDE ruling D).
  1979                 has no Psalter-order section: of that rubric's six
                       provisions only two survive (the psalm pattern and the
                       morning-before-evening order) and they survive INSIDE
                       the lectionary note, so it is `absent:`. It does have a
                       lineal successor to the Scripture-order rubric --
                       "Concerning the Daily Office Lectionary" -- which sits
                       in the same position in the book, before the lectionary,
                       doing the same job: where to find the day's readings,
                       the Old-Testament-first rule, what happens when a feast
                       interrupts the course, and a discretion clause. Four of
                       the historic rubric's seven provisions have an analogue.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "tools"))

import scrape

K = "http://justus.anglican.org/resources/bcp/"

# (url, start-pattern, end-pattern) per edition per section. Slicing is by the
# page's own anchors where it has them, and by the printed heading where it
# does not (1549 carries no <a name>).
SLICES = {
    "order-how-psalter-appointed": {
        "1549": (K + "1549/Kalendar_1549.htm",
                 r"the Psalter is appoyn-", r"One printing has for this title"),
        # NOTE: on these pages the <a name> anchors mark the psalm TABLE, not
        # the rubric -- the prose precedes them. Slicing from the anchor
        # yielded 27 words of table headings instead of the rubric.
        "1552": (K + "1552/Kalendar_1552.htm",
                 r"PSALTER IS APPOYNTED TO BE READDE", r'name="Psalms"'),
        "1559": (K + "1559/Kalendar_1559.htm",
                 r"PSALTER IS APPOYNTED TO BE READDE", r'name="Order of Psalter"'),
        "1789": (K + "1789/FrontMatter_1789.htm",
                 r'name="How the Psalter"',
                 r"Psalms on Certain Days"),
    },
    "order-how-rest-of-scripture": {
        "1549": (K + "1549/Kalendar_1549.htm",
                 r"the rest of holy Scripture", r"<table"),
        "1552": (K + "1552/Kalendar_1552.htm",
                 r'name="Rest of Scripture"', r'name="Proper Psalms&amp;Lessons"'),
        "1559": (K + "1559/Kalendar_1559.htm",
                 r'name="Order of Scripture"', r'name="Lessons"'),
        "1789": (K + "1789/FrontMatter_1789.htm",
                 r'name="How the rest of the Holy Scripture"',
                 r'name="TABLES of LESSONS"'),
    },
}

TITLES = {
    "order-how-psalter-appointed": "The Order how the Psalter is appointed to be read",
    "order-how-rest-of-scripture":
        "The Order how the rest of Holy Scripture is appointed to be read",
}

DROP = re.compile(r"^(The Book of Common Prayer|United States England|"
                  r"Web author|Return to|One printing|A Table and Kalendar)", re.I)


def slice_html(url, start, end):
    h = scrape.fetch(url)
    m = re.search(start, h)
    if not m:
        raise SystemExit("start %r not found in %s" % (start, url))
    tail = h[m.end():]
    e = re.search(end, tail)
    stop = e.start() if e else len(tail)
    # These rubrics are PROSE. Where the page prints the psalm-distribution
    # table between the rubric and the next anchor (1552, 1559), the slice must
    # stop at the table or it swallows a column of bare numerals as if it were
    # rubric text. The table itself is out of scope (GUIDE ruling B).
    return tail[:stop]


def trim(paras, title):
    """Drop the heading remnants the slice inevitably carries.

    A slice that starts mid-heading brings the heading's tail with it -- 1549
    yields "(beside the psalter) is appoyn-" / "ted to bee redde." before the
    first prose. Everything before the first substantial sentence is a remnant,
    except a genuine rubric line (which the source marks and which really does
    precede the prose, e.g. "The olde Testament.").
    """
    first = next((i for i, p in enumerate(paras) if len(p.split()) >= 15),
                 len(paras))
    head = [p for p in paras[:first]
            if p.startswith(">") and not _is_title(p, title)]
    return head + paras[first:]


def _is_title(line, title):
    a = set(re.sub(r"[^a-z ]", " ", line.lower()).split())
    b = set(re.sub(r"[^a-z ]", " ", title.lower()).split())
    return len(a & b) >= max(3, len(b) - 2)


def paragraphs(seg):
    md = scrape.html_to_markdown(seg)
    out = []
    for l in md.split("\n"):
        l = re.sub(r"\s+", " ", l).strip()
        if not l or DROP.match(l):
            continue
        # A stray heading fragment left by the slice start.
        if len(l) < 4 and not l.endswith("."):
            continue
        out.append(l)
    return out


def build_1979_scripture():
    """1979's lineal successor: 'Concerning the Daily Office Lectionary'."""
    t = scrape.fetch(K + "bcplectn.txt")
    i = t.find("Concerning the Daily Office Lectionary")
    j = t.find("<Year One>", i)
    seg = t[i:j]
    paras, buf = [], []
    for l in seg.split("\n"):
        s = l.strip()
        if not s:
            if buf:
                paras.append(" ".join(buf)); buf = []
            continue
        if s.startswith("<"):
            continue
        buf.append(s)
    if buf:
        paras.append(" ".join(buf))
    out = []
    for p in paras:
        p = re.sub(r"\s+", " ", p.replace("*", "")).strip()
        if p and not p.startswith("Concerning the Daily Office"):
            out.append(p)
    return out


def main():
    written = []
    for slug, per_ed in SLICES.items():
        for ed, (url, start, end) in per_ed.items():
            paras = trim(paragraphs(slice_html(url, start, end)), TITLES[slug])
            lines = ["# " + TITLES[slug], ""] + paras
            write(ed, slug, lines, written)
    # 1979 carries only the Scripture-order successor.
    lines = ["# " + TITLES["order-how-rest-of-scripture"], "",
             "<!-- The 1979 book prints this rubric as 'Concerning the Daily "
             "Office Lectionary'. -->"] + build_1979_scripture()
    write("1979", "order-how-rest-of-scripture", lines, written)
    for ed, slug, n, w in written:
        print("%-5s %-32s paragraphs=%2d words=%4d" % (ed, slug, n, w))


def write(ed, slug, lines, written):
    p = os.path.join(WT, "editions", ed, "front-matter", slug + ".md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    text = re.sub(r"\n{3,}", "\n\n", "\n\n".join(lines).rstrip("\n")) + "\n"
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    body = [l for l in text.split("\n") if l.strip()]
    written.append((ed, slug, len(body) - 1, sum(len(l.split()) for l in body)))


if __name__ == "__main__":
    main()
