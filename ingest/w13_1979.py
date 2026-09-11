#!/usr/bin/env python3
"""w13_1979.py — parse the 1979 Psalter e-text (Wave 13).

Authoring-only; NOT published. PARSES ONLY; w13_render.py writes the cells.

Source: bcpsalt1.txt (Psalms 1-75) + bcpsalt2.txt (76-150), the public-domain
1979 e-text. Layout, verified rather than assumed:

  <Psalm N>  =Latin incipit=        a psalm (the incipit may be absent when
                                    the psalm is divided into Parts)
  <Part I>  =incipit=               1979 divides seven long psalms into Parts
  <Psalm N: Part II>  =incipit=     -- NOT a new psalm
  <Aleph>  =incipit=                Psalm 119's twenty-two portions
  1  first half of verse, *         a verse starts: number + TWO spaces
  /wrapped first half               '/' marks a wrapped line
   second half                      continuation lines, any indentation
  <page N>, <Book One>, *First Day: Morning Prayer*   furniture, skipped

1979 prints verse 1's number, unlike the Coverdale books.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))

J = "http://justus.anglican.org/resources/bcp/"
# The closing '=' is OPTIONAL: nine headings have a TRUNCATED incipit whose
# closing mark was lost in keying ("=Benedicam Domi", "=Deus ultio",
# "=Laudate Domi"). Requiring it made those nine psalms invisible, and their
# verses piled onto the psalm before (Ps 93's run restarted at 1). A truncated
# incipit is carried AS PRINTED and flagged, never completed from memory.
PSALM = re.compile(r"^<Psalm (\d+)>\s*(?:=([^=]*)(=?))?\s*$")
TRUNCATED = []
SUBHEAD = re.compile(r"^<(Part I|Psalm \d+: Part II|[A-Z][a-z]+)>\s*(?:=(.*)=)?\s*$")
VERSE = re.compile(r"^(\d{1,3})\s{2,}(.*)$")
FURNITURE = re.compile(r"^(<page \d+>|<Book [A-Za-z]+>|<The Psalter>|\*[^*]+\*)\s*$")


HEADER_END = "(end of header)"


def load():
    """Concatenate the two parts, each with ITS OWN FTP header stripped.

    Stripping only the first file's header (by starting at "<The Psalter>")
    glued the second file's header -- "FILE 9 of 11 (BCPSALT2.TXT) ..." --
    onto the last verse of the first file, producing a 2,566-character
    "verse". The mediant gate caught it as a verse with five mediants.
    """
    import scrape
    parts = []
    for name in ("bcpsalt1.txt", "bcpsalt2.txt"):
        t = scrape.fetch(J + name)
        i = t.find(HEADER_END)
        if i < 0:
            raise SystemExit("%s: header end marker not found" % name)
        parts.append(t[t.find("\n", i) + 1:])
    return "\n".join(parts)


def parse():
    text = load()
    lines = text.split("\n")
    psalms = {}
    cur = None
    verse = None
    pending = []
    for raw in lines:
        line = raw.rstrip()
        s = line.strip()
        if not s or FURNITURE.match(s):
            continue
        m = PSALM.match(s)
        if m:
            n = int(m.group(1))
            inc = (m.group(2) or "").strip() or None
            if inc and not m.group(3):
                TRUNCATED.append((n, inc))
            cur = psalms[n] = {"incipit": inc, "verses": [],
                               "incipit_truncated": bool(inc and not m.group(3))}
            verse, pending = None, []
            continue
        m = SUBHEAD.match(s)
        if m and cur is not None:
            label = m.group(1)
            if label.startswith("Psalm "):
                label = "Part II"
            pending = [label] + ([m.group(2).strip()] if m.group(2) else [])
            verse = None
            continue
        m = VERSE.match(line)
        if m and cur is not None:
            verse = [int(m.group(1)), m.group(2).strip(), pending or None]
            cur["verses"].append(verse)
            pending = []
            continue
        if verse is not None:
            verse[1] = verse[1] + " " + s.lstrip("/").strip()
    for p in psalms.values():
        p["verses"] = [(v[0], re.sub(r"\s+", " ", v[1]).strip(), v[2])
                       for v in p["verses"]]
    return psalms


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    import w13_1662
    ps = parse()
    bad = w13_1662.gate(ps, "1979")
    print("1979: %d psalms, %d verses, %d with incipit, %d sub-headings"
          % (len(ps), sum(len(p["verses"]) for p in ps.values()),
             sum(1 for p in ps.values() if p["incipit"]),
             sum(1 for p in ps.values() for v in p["verses"] if v[2])))
    print("truncated incipits:", TRUNCATED)
    print("GATE:", "clean" if not bad else "%d problems" % len(bad))
    for b in bad[:12]:
        print("  -", b)
