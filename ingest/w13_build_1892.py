#!/usr/bin/env python3
"""w13_build_1892.py — write the 1892 psalter cells (Wave 13).

The text is the 1892 PDF's own letters after the whitespace repair; it was
tested against an INDEPENDENT witness (the justus dated change log): 51 of 55
applicable entries agree, including 32 of the 35 changes the log dates to 1892
itself -- which is what establishes that this PDF genuinely is the 1892 text.

WAVE 17 corrects it against a SCAN of the 1892 Standard Book (see
ingest/w17_witness.py). The PDF turns out not to be the 1892 text in its
spelling (it prints shew/judgement where the book prints show/judgment), in
sixteen hyphenated words, in the four readings the change log had flagged, in
three other flagged readings, and in the pointing of seven verses. All
fourteen of Wave 13's VERIFYs are resolved; one new one takes their place.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w13_1892
import w13_1662
import w13_render
import w17_witness

LOG = ("the justus table of pre-1928 U.S. psalter changes (1789/Psalter1789&"
       "1892.htm) says this reading was %s; the 1892 PDF prints the other. One "
       "of the two sources is wrong here and only a page scan can say which. "
       "Carried as the 1892 PDF prints it")
# Wave 17: every entry that stood here is resolved from the scan of the 1892
# Standard Book, and the corrections live in ingest/w17_witness.py. What
# remains is the one reading the scan cannot settle, because the page breaks
# the word across a line.
V1892 = dict(w17_witness.VERIFY)


def main():
    ps = w13_1892.parse()
    bad = w13_1662.gate(ps, "1892")
    if bad or w13_1892.DROPPED:
        raise SystemExit("1892 gate: %s / dropped %s" % (bad, w13_1892.DROPPED))
    log = w17_witness.apply(ps)
    for (n, v), (key, note) in V1892.items():
        ps[n].setdefault("verifies", []).append((v, key, note))
    an, man = w13_render.render("1892", ps, ":")
    json.dump(man, open(os.path.join(HERE, "wave13_1892_verifies.json"), "w"),
              indent=1)
    import collections
    kinds = collections.Counter(k for k, *_ in log)
    print("1892: %d psalms, %d verses; mediant anomalies %d %s; VERIFY %d; "
          "witness corrections %d %s"
          % (len(ps), sum(len(p["verses"]) for p in ps.values()), len(an),
             an[:12], len(man), sum(kinds.values()), dict(kinds)))


if __name__ == "__main__":
    main()
