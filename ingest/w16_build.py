#!/usr/bin/env python3
"""w16_build.py — the Wave-16 cells (the backlog pass). Authoring-only.

source -> script -> file (HANDOFF §6). Writes:

  1892 front-matter/concerning-the-service.md   Front_Matter_1892.htm
                                                (witness: 1892 Standard Book)
  1928 front-matter/concerning-the-service.md   Lectionary_1928.pdf sheet 1
                                                (witness: the BCP1929.pdf scan)
  1892 psalter/selections.md                    Front_Matter_1892.htm
                                                (witness: 1892 Standard Book)
  1892 tables/feasts-and-fasts.md               Lectionary_1892.htm, rebuilt
                                                in the 1928 cell's line shape

SLOT IDENTITY (the backlog question). `front-matter/concerning-the-service`
holds whatever each book prints under the title "Concerning the Service of the
Church": the 1549 Preface renamed in 1662 on the English line, and on the
American line the rules text that 1892 introduced, 1928 rewrote and 1979
replaced. 1979's text was put in this slot in Wave 9 on exactly that basis, so
1892 and 1928 follow the same precedent. 1789 prints nothing under the title
and stays `absent:`, so v1789 deletes the file and v1892 re-creates it.

In both books the rules text is followed, under separate headings, by the two
"Order how..." rubrics, which are their own cells (Wave 15). This cell stops
before them.
"""
from __future__ import annotations
import glob
import html as H
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "tools"))

import scrape
import w15_src as S
import w16_witness as W

J = "http://justus.anglican.org/resources/bcp/"
FM1892 = J + "1892/Front_Matter_1892.htm"
LEC1892 = J + "1892/Lectionary_1892.htm"
STD1892 = J + "1892Standard/front_matter.pdf"
CONCERNING = "Concerning the Service of the Church"


def std1892_path():
    """The raw Standard Book PDF in scrape-cache (fetched like the Wave-15
    PDFs: bytes cached beside the text cache with a .pdf suffix)."""
    p = scrape._cache_path(STD1892).with_suffix(".pdf")
    if not p.exists():
        raise SystemExit("fetch %s raw into scrape-cache first" % STD1892)
    return str(p)


def std1892_page(n):
    import pypdf
    return pypdf.PdfReader(std1892_path()).pages[n - 1].extract_text() or ""


def txt(s):
    """HTML fragment -> text: tags out, entities decoded, whitespace folded."""
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def write(ed, rel, title, lines, sep="\n\n"):
    p = os.path.join(WT, "editions", ed, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    text = sep.join(["# " + title] + lines) + "\n"
    if sep == "\n":
        text = text.replace("# " + title + "\n", "# " + title + "\n\n", 1)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("%s %-38s lines=%d words=%d"
          % (ed, rel, len(lines), sum(len(l.split()) for l in lines)))


# ------------------------------------------------------- Concerning, 1892
def concerning_1892():
    h = scrape.fetch(FM1892)
    T = r"(?:\s|<[^>]+>)+"                          # words split by markup
    a = re.search(T.join(["CONCERNING", "THE", "SERVICE", "OF", "THE",
                          r"CHURCH\."]), h)
    if not a:
        raise SystemExit("1892 Concerning: heading not found")
    b = re.search(T.join(["ORDER", "HOW", "THE", "PSALTER"]), h[a.end():])
    seg = h[a.end():a.end() + b.start()]
    seg = seg[seg.index("</p>") + 4:]              # past the heading's close
    seg = seg[:seg.rindex("<p")]                   # before the next heading
    paras = [txt(x) for x in re.split(r"<br\s*/?>", seg, flags=re.I)]
    paras = [p for p in paras if p]
    if len(paras) != 4:
        raise SystemExit("1892 Concerning: %d paragraphs, want 4" % len(paras))
    body = W.apply("\n".join(paras), W.CONCERNING_1892, "1892 concerning")
    lines = body.split("\n")
    for v in W.CONCERNING_1892_VERIFY:
        k = [i for i, l in enumerate(lines) if v["reading"] in l]
        if len(k) != 1:
            raise SystemExit("1892 Concerning VERIFY %r: %d hits" % (v["reading"], len(k)))
        lines[k[0]] += "\n<!-- VERIFY: '%s' %s -->" % (v["reading"], v["verify"])
    write("1892", "front-matter/concerning-the-service.md", CONCERNING, lines)


# ------------------------------------------------------- Concerning, 1928
def concerning_1928():
    lines = S.layout("LEC", 1).split("\n")
    a = next(i for i, l in enumerate(lines) if l.strip() == "Service of the Church")
    b = next(i for i, l in enumerate(lines) if "THE USE OF THE PSALTER" in l)
    body = [l.rstrip() for l in lines[a + 1:b] if l.strip()]
    # The drop capital T is displaced by layout mode to the start of the
    # SECOND line ("Tfor Evening Prayer"); it belongs before "HE Order".
    m = re.match(r"^\s*T(for Evening)", body[1])
    if not m or not body[0].strip().startswith("HE Order"):
        raise SystemExit("1928 Concerning: drop capital not where expected")
    body[0] = "    T" + body[0].strip()
    body[1] = body[1].replace("T" + m.group(1), m.group(1), 1)
    # A paragraph opens on an indented line that follows a finished sentence;
    # the drop capital's two lines are indented without opening one.
    paras = []
    for l in body:
        if not paras or (re.match(r"^\s{2,}", l) and paras[-1].endswith(".")):
            paras.append(l.strip())
        elif paras[-1].endswith("-") and l.strip()[:1].islower():
            paras[-1] = paras[-1][:-1] + l.strip()   # "Eccle-" + "siastical"
        else:
            paras[-1] += " " + l.strip()
    paras = [S.norm_ws(p) for p in paras]
    if len(paras) != 3:
        raise SystemExit("1928 Concerning: %d paragraphs, want 3" % len(paras))
    body = W.apply("\n".join(paras), W.CONCERNING_1928, "1928 concerning")
    write("1928", "front-matter/concerning-the-service.md", CONCERNING,
          body.split("\n"))


# ------------------------------------------------------- Selections, 1892
ORD = ["FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH",
       "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH", "THIRTEENTH",
       "FOURTEENTH", "FIFTEENTH", "SIXTEENTH", "SEVENTEENTH", "EIGHTEENTH",
       "NINETEENTH", "TWENTIETH"]
LIST = r"(\d+(?:\s*[,.]\s*\d+|\s+to\s+v\.\s*\d+)*)"


def selections_from(text):
    """'FIRST. Psalms. 1, 15, 91 ELEVENTH. ...' -> {ordinal: psalm list}. The
    table is printed in two columns, so the keyed text interleaves the rows
    (First, Eleventh, Second, ...); each entry is keyed by its own ordinal."""
    text = re.sub(r"\bPsalms\.\s*", "", text)
    out = {}
    for m in re.finditer(r"\b([A-Z]+)\s*\.\s*" + LIST, text):
        if m.group(1) in ORD:
            out[m.group(1)] = m.group(2)
    return out


def psalm_list(s):
    """Typographic normalization only: one space after each comma, and
    "v.7" -> "v. 7" (the Standard Book's keying spaces it)."""
    s = re.sub(r"\s*,\s*", ", ", s.strip())
    return re.sub(r"\bv\.\s*(\d)", r"v. \1", s)


def selections_1892():
    h = scrape.fetch(FM1892)
    a = h.index("SELECTIONS OF PSALMS.")
    b = h.index("REST OF THE HOLY", a)
    # small capitals are keyed as a capital plus a tag ("F</font>IRST"), so
    # tags are removed without a space before the ordinals are read
    carrier = selections_from(re.sub(r"(?<=\b[A-Z]) (?=[A-Z]+\s*\.)", "",
                                     txt(h[a:b])))
    t = std1892_page(9)
    std = selections_from(re.sub(r"\s+", " ", t[:t.index("THE ORDER HOW")])
                          .replace("NINETWWNTH", "NINETEENTH"))
    if sorted(carrier) != sorted(ORD):
        raise SystemExit("1892 Selections: carrier has %d of 20" % len(carrier))
    rows, disagree = [], []
    for o in ORD:
        c = psalm_list(carrier[o])
        s = psalm_list(re.sub(r"(?<=\d)\.(?=\s*\d)", ",", std.get(o, "")))
        if c != s:
            disagree.append((o, c, s))
        rows.append("%s | Psalms: %s" % (o.title(), c))
    # The Standard Book keys "4. 31 to v. 7" -- a period for the comma, which
    # the comparison above already folds; any OTHER disagreement is a finding.
    if disagree:
        raise SystemExit("1892 Selections: carrier and Standard Book disagree: %r"
                         % disagree)
    write("1892", "psalter/selections.md", "Selections of Psalms", rows, sep="\n")


# ------------------------------------------------------- Feasts, 1892
# Obvious keying noise, cleaned narrowly (HANDOFF §4; never a change of
# reading): a missing space after a comma.
FEASTS_NOISE = [("In addition to the above,the first", "In addition to the above, the first")]


def brs(cell):
    """A table cell's <br>-separated lines, each with a flag: True when the
    line opens with non-breaking spaces (a wrapped continuation)."""
    out = []
    for piece in re.split(r"<br\s*/?>", cell, flags=re.I):
        t = txt(piece)
        if t:
            out.append((t, bool(re.match(r"^\s*(?:<[^>]+>\s*)*(?:&nbsp;\s*){2,}", piece))))
    return out


def tds(table):
    return re.findall(r"<td\b[^>]*>(.*?)</td>", table, re.S | re.I)


def feasts_1892():
    """Tables and Rules, 1892, in the 1928 cell's shape (w15_feasts.py): each
    heading, rule, table entry and numbered day on its own line. The WORDS are
    the page's, unchanged (the printed OCR slips "tbe", "EASTER.DAY" and
    "Authorlty" stay: no 1892 witness prints this section); only the line
    structure is rebuilt. Wave 14 emitted it one HTML fragment per line, so a
    wrapped entry ("The Circumcision of our Lord" / "JESUS CHRIST.") and each
    brace column read as separate lines, and `v1892 -> v1928` was mostly
    re-lining."""
    h = scrape.fetch(LEC1892)
    a = re.search(r"Tables\s+and Rules for t.e Movable", h).start()
    # the page's own anchor for the golden-number apparatus, which is excluded
    b = h.index('name="Tables_HolyDays"', a)
    seg = h[h.rfind("<p", 0, a):h.rfind("<p", 0, b)]
    out = []
    # 1. the head: headings, then the three rules (one <p>, split at <br>)
    head, rest = seg.split("</table>", 1)
    for p in re.findall(r"<p\b[^>]*>(.*?)</p>", head, re.S | re.I):
        out += [t for t, _ in brs(p)]
    # 2. the two brace tables: names } verb { values } tail. A brace prints
    # the shared words once for four rows; each row reads across it --
    # "Septuagesima Sunday is Nine Weeks before Easter." -- as the 1928 book
    # sets these rules. The words are the page's; the shared ones repeat.
    tables = re.findall(r"<table\b.*?</table>", rest, re.S | re.I)
    for tb in tables[:2]:
        c = tds(tb)
        if len(c) != 4:
            raise SystemExit("1892 feasts: brace table has %d cells" % len(c))
        names, vals = [t for t, _ in brs(c[0])], [t for t, _ in brs(c[2])]
        if len(names) != 4 or len(vals) != 4:
            raise SystemExit("1892 feasts: brace rows %d/%d" % (len(names), len(vals)))
        out += ["%s %s %s %s" % (n, txt(c[1]), v, txt(c[3]))
                for n, v in zip(names, vals)]
    # 3. the Table of Feasts: its two headings, then two columns of entries,
    # left column first (the printed reading order); a line opening with
    # non-breaking spaces continues the entry above it
    after = rest.split(tables[1], 1)[1]
    pre, feasts_tb = after.split(tables[2], 1)[0], tables[2]
    heads = [txt(p) for p in re.findall(r"<p\b[^>]*>(.*?)(?=<p\b|</p>|</div>|$)",
                                        pre, re.S | re.I)]
    out += [t for t in heads if t]
    for col in tds(feasts_tb):
        entries = []
        for t, cont in brs(col):
            if cont and entries:
                entries[-1] += " " + t
            else:
                entries.append(t)
        out += entries
    # 4. the Table of Fasts: heading, then two entries set on one line
    after = after.split(feasts_tb, 1)[1]
    pre = after.split(tables[3], 1)[0]
    for p in re.findall(r"<p\b[^>]*>(.*?)</p>", pre, re.S | re.I):
        if not txt(p):
            continue
        parts = re.split(r"(?:&nbsp;){3,}", p)
        out += [txt(x) for x in parts if txt(x)]
    # 5. Other Days of Fasting: the heading's second line, then numbered days
    for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", tables[3], re.S | re.I):
        c = [txt(x) for x in tds(tr)]
        c = [x for x in c if x]
        if len(c) == 1:
            out.append(c[0])
        elif re.match(r"^[IVX]+\.$", c[0]):
            out.append(" ".join(c))
        else:
            raise SystemExit("1892 feasts: unexpected fasting row %r" % c[:1])
    # 6. the Thanksgiving-day paragraph (its table runs on into the excluded
    # apparatus, so the slice ends inside it)
    tail = after.split(tables[3], 1)[1]
    for p in re.findall(r"<p\b[^>]*>(.*?)</p>", tail, re.S | re.I):
        if txt(p):
            out.append(txt(p))
    text = "\n".join(out)
    for bad, good in FEASTS_NOISE:
        if text.count(bad) != 1:
            raise SystemExit("1892 feasts noise %r: %d hits" % (bad, text.count(bad)))
        text = text.replace(bad, good)
    write("1892", "tables/feasts-and-fasts.md",
          "Tables and Rules for the Feasts and Fasts", text.split("\n"))


if __name__ == "__main__":
    concerning_1892()
    concerning_1928()
    selections_1892()
    feasts_1892()
