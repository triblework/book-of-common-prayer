#!/usr/bin/env python3
"""w16_gates.py — the Wave-16 gates: fabrication, loss, structure.

Authoring-only. Run after w16_build.py and w13_build_extras.py.

  1. FABRICATION. Every word of every new cell occurs in its carrier, once the
     recorded witness corrections are reversed; every witness reading occurs
     in its witness.
  2. LOSS. Every word the carrier prints in the slice occurs in the cell.
  3. STRUCTURE. Paragraph and row counts, the Selections and the corrected
     Proper Psalms agreeing value for value with the 1892 Standard Book, and
     the 1892 Tables and Rules keeping every word of its Wave-14 cell.
  4. SENSITIVITY. Readings the witnesses reject must not appear.
"""
from __future__ import annotations
import collections
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "tools"))

import scrape
import w15_src as S
import w16_build as B
import w16_witness as W
import w13_build_extras as X

WORD = re.compile(r"[A-Za-z][A-Za-z’']*")
findings = []


def ed(rel):
    return open(os.path.join(WT, "editions", rel), encoding="utf-8").read()


def body(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return "\n".join(l for l in text.split("\n") if not l.startswith("# "))


def words(s):
    return [w.lower().replace("’", "'") for w in WORD.findall(s)]


def check(label, ok, detail=""):
    print("%-7s %s %s" % ("OK" if ok else "ANOMALY", label, detail))
    if not ok:
        findings.append(label)


def unapply(text, corrections):
    for c in corrections:
        text = text.replace(c["witness"], c["carrier"])
    return text


def html_words(url):
    raw = scrape.fetch(url)
    return set(words(B.txt(raw))) | set(words(re.sub(r"<[^>]+>", " ", raw)))


# ------------------------------------------------------------ 1. fabrication
def fabrication():
    fm = html_words(B.FM1892)
    std = set(words(B.std1892_page(8) + B.std1892_page(9)))
    lec = set(words(" ".join(t for _y, _x, t, _s in S.runs("LEC", 1))))
    lec |= set(words(S.layout("LEC", 1)))
    c92 = unapply(body(ed("1892/front-matter/concerning-the-service.md")),
                  W.CONCERNING_1892)
    miss = sorted(set(words(c92)) - fm)
    check("1892 Concerning: every word in Front_Matter_1892.htm", not miss, miss[:6])
    wit = sorted(set(words(" ".join(c["witness"] for c in W.CONCERNING_1892))) - std)
    check("1892 Concerning: every witness reading in the Standard Book", not wit, wit)
    c28 = body(ed("1928/front-matter/concerning-the-service.md"))
    miss = sorted(set(words(c28)) - lec - {"ecclesiastical"})
    check("1928 Concerning: every word in the text layer", not miss, miss[:6])
    # "Eccle-" + "siastical" is a rejoined line-break hyphen: attest the pieces
    check("1928 Concerning: 'Ecclesiastical' rejoined from 'Eccle-'/'siastical'",
          "eccle" in lec and "siastical" in lec)
    lec92 = html_words(B.LEC1892)
    f92 = body(ed("1892/tables/feasts-and-fasts.md"))
    miss = sorted(set(words(f92)) - lec92)
    check("1892 Tables and Rules: every word in Lectionary_1892.htm", not miss, miss[:6])


# ------------------------------------------------------------ 2. loss
def loss():
    import html as H
    h = scrape.fetch(B.FM1892)
    a = re.search(r"CONCERNING(?:\s|<[^>]+>)+THE(?:\s|<[^>]+>)+SERVICE", h).end()
    b = re.search(r"ORDER(?:\s|<[^>]+>)+HOW(?:\s|<[^>]+>)+THE(?:\s|<[^>]+>)+PSALTER",
                  h[a:]).start() + a
    # the slice runs from inside the heading to the next heading's first
    # word, so its tail ("OF THE CHURCH.") and "THE" before ORDER are allowed
    src = collections.Counter(words(B.txt(h[a:b])))
    cell = collections.Counter(words(unapply(
        body(ed("1892/front-matter/concerning-the-service.md")), W.CONCERNING_1892)))
    lost = src - cell - collections.Counter({"of": 1, "the": 2, "church": 1})
    check("1892 Concerning: no word of the source lost", not lost, dict(lost))
    L = S.layout("LEC", 1).split("\n")
    i = next(k for k, l in enumerate(L) if l.strip() == "Service of the Church")
    j = next(k for k, l in enumerate(L) if "THE USE OF THE PSALTER" in l)
    src = collections.Counter(words(re.sub(r"-\n\s*", "", "\n".join(L[i + 1:j]))))
    src["tfor"] -= 1; src["for"] += 1; src["he"] -= 1; src["the"] += 1  # drop cap
    cell = collections.Counter(words(body(ed("1928/front-matter/concerning-the-service.md"))))
    lost = +(src - cell)
    check("1928 Concerning: no word of the text layer lost", not lost, dict(lost))


# ------------------------------------------------------------ 3. structure
def paras(rel):
    return [l for l in body(ed(rel)).split("\n") if l.strip()]


def structure():
    check("1892 Concerning: 4 paragraphs",
          len(paras("1892/front-matter/concerning-the-service.md")) == 4)
    check("1928 Concerning: 3 paragraphs",
          len(paras("1928/front-matter/concerning-the-service.md")) == 3)
    sel = paras("1892/psalter/selections.md")
    check("1892 Selections: 20 rows, First..Twentieth",
          [r.split(" | ")[0].upper() for r in sel] == B.ORD)
    t = B.std1892_page(9)
    std = B.selections_from(re.sub(r"\s+", " ", t[:t.index("THE ORDER HOW")])
                            .replace("NINETWWNTH", "NINETEENTH"))
    diff = [o for o, r in zip(B.ORD, sel) if B.psalm_list(re.sub(
        r"(?<=\d)\.(?=\s*\d)", ",", std[o])) != r.split("Psalms: ")[1]]
    check("1892 Selections: every row equals the Standard Book's", not diff, diff)

    # Proper Psalms 1892: corrected rows == Standard Book, value for value
    rows = [r for r in paras("1892/tables/proper-psalms.md")]
    t = B.std1892_page(8)
    t = re.sub(r"\b(?:Morning|Evening)[.,]?", " ", t[t.index("PROPER PSALMS ON"):])
    t = re.sub(r"\s+", " ", t.replace("PROPER PSALMS ON CERTAIN DAYS.", ""))
    G = r"(\d+(?:\s*[,.]\s*\d+)*)"
    stdrows = {re.sub(r"[^A-Z]", "", m.group(1)): (m.group(2), m.group(3))
               for m in re.finditer(r"([A-Z][A-Z’'. \-]+?)\.?\s+" + G + r"\s+" + G, t)}
    norm = lambda s: ", ".join(re.findall(r"\d+", s))
    alias = {"CHRITMASDAY": "CHRISTMASDAY", "FIRSTSUNDAYINADVENT": "FIRSTSUNDAYINADVENT"}
    std = {alias.get(k, k): (norm(a), norm(b)) for k, (a, b) in stdrows.items()}
    bad = []
    for r in rows:
        d, m, e = [re.sub(r"^\w+: ", "", f) for f in r.split(" | ")]
        k = re.sub(r"[^A-Z]", "", d.upper())
        if std.get(k) != (m, e):
            bad.append((d, std.get(k)))
    check("1892 Proper Psalms: 16 rows, each = the Standard Book (labels, values)",
          len(rows) == 16 and not bad, bad[:3])
    fm = {re.sub(r"[^a-z]", "", d.lower()): (m, e) for d, m, e in
          X.proper_table(B.FM1892, "TABLE OF PROPER PSALMS ON CERTAIN DAYS")}
    for c in W.PROPER_1892:
        f = c["witness"].rstrip(" |").split(" | ")
        k = re.sub(r"[^a-z]", "", f[0].lower())
        vals = tuple(re.sub(r"^\w+: ", "", x) for x in f[1:])
        ok = k in fm and (not vals or fm[k] == vals)
        check("1892 Proper Psalms: FM1892 agrees with the correction to %r" % f[0], ok)

    # Tables and Rules 1892: every word of the Wave-14 cell kept
    old = subprocess.run(["git", "show", "e50503f4:editions/1892/tables/feasts-and-fasts.md"],
                         cwd=WT, capture_output=True, text=True).stdout
    new = ed("1892/tables/feasts-and-fasts.md")
    tok = lambda s: collections.Counter(re.findall(r"[^\s>]+", s.replace("above,the", "above, the")))
    lost, added = tok(old) - tok(new), tok(new) - tok(old)
    brace = collections.Counter({"is": 6, "Sunday": 3, "after": 3, "before": 3,
                                 "Weeks": 3, "Easter.": 6})
    check("1892 Tables and Rules: no word of the Wave-14 cell lost", not lost, dict(lost))
    check("1892 Tables and Rules: only the brace table's shared words added",
          added == brace, dict(added - brace))
    L = paras("1892/tables/feasts-and-fasts.md")
    # the Table of Feasts prints 14 entries in its left column and 15 in its
    # right (All Sundays ... St. James; the Transfiguration ... Whitsun week)
    f0 = L.index("TO BE OBSERVED IN THIS CHURCH THROUGHOUT THE YEAR.")
    f1 = L.index("A TABLE OF FASTS.")
    check("1892 Tables and Rules: 8 rule rows, 29 feasts, 2 fasts, 4 numbered days",
          sum(bool(re.search(r" (before|after) Easter\.$", l)) for l in L) == 8
          and f1 - f0 - 1 == 29
          and L[f1 + 1:f1 + 3] == ["Ash-Wednesday.", "Good Friday."]
          and sum(bool(re.match(r"^[IVX]+\. ", l)) for l in L) == 4)


# ------------------------------------------------------------ 4. sensitivity
MUST_NOT = [
    ("1892/front-matter/concerning-the-service.md", "think lit"),
    ("1928/front-matter/concerning-the-service.md", "Church. and"),
    ("1928/front-matter/concerning-the-service.md", "Ordinary. may"),
    ("1928/front-matter/concerning-the-service.md", "Book. it"),
    ("1928/front-matter/concerning-the-service.md", "Eccle-"),
    ("1892/tables/proper-psalms.md", "180"),
    ("1892/tables/proper-psalms.md", "190"),
    ("1892/tables/proper-psalms.md", "84, 99, 132"),
    ("1892/tables/proper-psalms.md", "Mas-day"),
    ("1928/tables/proper-psalms.md", "24, 130, 132"),
    ("1892/tables/feasts-and-fasts.md", "\n\nJESUS CHRIST."),
]


def sensitivity():
    hits = [(f, s) for f, s in MUST_NOT if s in ed(f)]
    check("sensitivity: %d rejected readings absent" % len(MUST_NOT), not hits, hits)


if __name__ == "__main__":
    fabrication()
    loss()
    structure()
    sensitivity()
    print("\nw16 gates: %d anomalies" % len(findings))
    sys.exit(1 if findings else 0)
