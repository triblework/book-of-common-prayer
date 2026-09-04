#!/usr/bin/env python3
"""w14_build_feasts.py — tables/feasts-and-fasts.md per edition (Wave 14).

Authoring-only; NOT published. source -> script -> file (HANDOFF §6).

"Tables and Rules for the Movable and Immovable Feasts, together with the Days
of Fasting and Abstinence through the whole Year" -- the rules that say which
days the church observes, which take precedence, and which are fasts. This is
LITURGICAL content, unlike the golden-number and Sunday-letter grids that
accompany it, which are computational apparatus excluded by GUIDE ruling B; the
slices below stop before them.

1979 belongs here. "The Calendar of the Church Year" (bcpoffce.txt) prints the
same material rebuilt around a precedence scheme -- Principal Feasts, Sundays,
Holy Days, Days of Special Devotion, Days of Optional Observance -- and is the
lineal successor of the historic Tables and Rules.

1662 is sourced from the Church of England's own PDFs, which for THESE two
tables (unlike the Kalendar and Proper Lessons) print the 1662 text rather than
the post-1922 recension.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "tools"))

import scrape

J = "http://justus.anglican.org/resources/bcp/"
COE = "https://www.churchofengland.org/sites/default/files/2017-10/"

TITLE = ("Tables and Rules for the Feasts and Fasts")

# Markdown-line slices: (url, start-regex, stop-regex)
HTML_SOURCES = {
    # NOTE: these lines carry the "> " rubric marker in the rendered markdown,
    # so the patterns must not be anchored to the start of the line. The stop
    # patterns cut before the golden-number / Sunday-letter / Easter grids,
    # which are computational apparatus (GUIDE ruling B). 1892's own heading
    # carries an OCR slip ("for tbe Movable"), so the match is loose.
    "1789": (J + "1789/Tables&Rules_1789.htm",
             r"RULES, to know when the Moveable Feasts",
             r"TABLES FOR FINDING THE HOLY-DAYS"),
    "1892": (J + "1892/Lectionary_1892.htm",
             r"Tables and Rules for t.e Movable",
             r"THE Numbers prefixed to the several Days|TO FIND THE DOMINICAL"),
}

DROP = re.compile(r"^(The Book of Common Prayer|United States England|"
                  r"Web author|Return to|Skip to|Some functionality|"
                  r"To experience|Menu$|## Social)", re.I)


def md_slice(url, start, stop):
    md = scrape.html_to_markdown(scrape.fetch(url))
    lines = [re.sub(r"\s+", " ", l).strip() for l in md.split("\n")]
    lines = [l for l in lines if l and not DROP.match(l)]
    a = next((i for i, l in enumerate(lines) if re.search(start, l)), None)
    if a is None:
        raise SystemExit("start not found: %s" % url)
    b = next((i for i, l in enumerate(lines[a + 1:], a + 1)
              if re.search(stop, l)), len(lines))
    return lines[a:b]


def build_1979():
    t = scrape.fetch(J + "bcpoffce.txt")
    i = t.find("<The Calendar\nof the Church Year>")
    j = t.find("*January*", i)
    out, buf = [], []
    for l in t[i:j].split("\n"):
        s = l.strip()
        if s.startswith("<page"):
            continue
        # "The Calendar of the Church Year" is the section's own title, which
        # the e-text wraps across two lines; the cell already carries it as its
        # "# " title, so it is not repeated as a heading.
        if s in ("<The Calendar", "of the Church Year>"):
            continue
        if s.startswith("<") and s.endswith(">"):
            if buf:
                out.append(" ".join(buf)); buf = []
            out.append("## " + s.strip("<>").replace("\n", " ").strip())
            continue
        if not s:
            if buf:
                out.append(" ".join(buf)); buf = []
            continue
        buf.append(s.replace("=", "").replace("*", ""))
    if buf:
        out.append(" ".join(buf))
    return [re.sub(r"\s+", " ", x).strip() for x in out if x.strip()]


def build_1662():
    import io
    import urllib.request
    import pypdf
    out = []
    for name, head in (("4-tables-and-rules.pdf", None),
                       ("5-table-vigils-fasts.pdf", None)):
        req = urllib.request.Request(COE + name,
                                     headers={"User-Agent": scrape.USER_AGENT})
        data = urllib.request.urlopen(req, timeout=60).read()
        r = pypdf.PdfReader(io.BytesIO(data))
        for pg in r.pages:
            for l in (pg.extract_text() or "").split("\n"):
                l = re.sub(r"\s+", " ", l).strip()
                if l:
                    out.append(l)
    return out


def write(ed, lines):
    p = os.path.join(WT, "editions", ed, "tables", "feasts-and-fasts.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    body = ["# " + TITLE, ""]
    for l in lines:
        body.append(l if l.startswith("#") else l)
        body.append("")
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(body).rstrip("\n")) + "\n"
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    n = len([l for l in text.split("\n") if l.strip()])
    print("%-5s lines=%3d words=%4d" % (ed, n, len(text.split())))


def main():
    for ed, (url, a, b) in sorted(HTML_SOURCES.items()):
        write(ed, md_slice(url, a, b))
    write("1979", build_1979())
    try:
        write("1662", build_1662())
    except Exception as exc:
        print("1662 SKIPPED -- %s" % exc)


if __name__ == "__main__":
    main()
