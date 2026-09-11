#!/usr/bin/env python3
"""w13_fidelity.py — gate 1 for the Psalter: nothing the source does not attest.

For HTML and e-text sources every token must occur in the source's own token
set, built three ways (tags stripped, tags removed, line-break hyphens undone)
because markup splits words. For 1892 the LETTERS come from the PDF and only
the spacing was repaired, so every token must occur in the PDF's whitespace-free
letter stream -- the exact claim the repair makes.
"""
import html as H
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "tools"))
import scrape

FILES = ["psalms-1-50", "psalms-51-100", "psalms-101-150"]
TOK = re.compile(r"[A-Za-z]+")
SUPPLIED = {"psalm", "psalter", "the", "part", "ii", "i"}   # anchors / labels we write


def tokens_of(text):
    out = set()
    for line in text.split("\n"):
        if line.startswith("#") or line.startswith("<!--"):
            continue
        out.update(w.lower() for w in TOK.findall(line))
    return out


def html_tokens(urls):
    toks = set()
    for u in urls:
        raw = H.unescape(scrape.fetch(u))
        for t in (re.sub(r"<[^>]+>", " ", raw), re.sub(r"<[^>]+>", "", raw),
                  re.sub(r"<[^>]+>", "", re.sub(r"-\s*<[^>]+>\s*", "", raw))):
            toks.update(w.lower() for w in TOK.findall(t))
    return toks


def coe_urls():
    import w13_1662
    return w13_1662.pages()


def main():
    import w13_1892_repair as R
    import pypdf
    sources = {
        "1662": html_tokens(coe_urls()),
        "1928": html_tokens(["http://justus.anglican.org/resources/bcp/1928/Psalms%d.htm" % n
                             for n in (1, 2, 3)]),
        "1979": {w.lower() for f in ("bcpsalt1.txt", "bcpsalt2.txt")
                 for w in TOK.findall(scrape.fetch("http://justus.anglican.org/resources/bcp/" + f))},
    }
    # Line-break hyphens are removed by the repair (typography, like the
    # terminal-period rule), so the attested stream drops hyphens too. What it
    # can never do is add, change or reorder a letter -- and that is the test.
    stream = "".join(re.sub(r"[\s-]+", "", p.extract_text() or "").lower()
                     for p in pypdf.PdfReader(R.PDF).pages)
    bad = 0
    for ed in ("1662", "1892", "1928", "1979"):
        for f in FILES:
            txt = open(os.path.join(WT, "editions", ed, "psalter", f + ".md"),
                       encoding="utf-8").read()
            toks = tokens_of(txt) - SUPPLIED
            if ed == "1892":
                missing = sorted(w for w in toks if w not in stream)
            else:
                missing = sorted(toks - sources[ed])
            bad += len(missing)
            print("%s %-16s tokens=%4d %s" % (ed, f, len(toks),
                  "OK" if not missing else "UNATTESTED %s" % missing[:10]))
    print("\nfidelity: %d unattested tokens" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
