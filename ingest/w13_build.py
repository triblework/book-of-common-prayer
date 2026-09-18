#!/usr/bin/env python3
"""w13_build.py — write the 1662 and 1928 psalter cells (Wave 13).

1979 has its own builder (w13_build_1979.py); 1892 needs the whitespace repair
and is built separately (w13_1892.py).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w13_1662
import w13_1928
import w13_render
import w18_witness

# 1662 readings held for VERIFY. Wave 18 read all three against the Annexed
# Book -- the manuscript annexed to the Act of Uniformity 1662, reproduced in
# type by HMSO in 1892 (ingest/w18_witness.py) -- and all three are settled:
#   2:12, 68:1  the 1662 text prints a mediant the CoE text has lost. Restored
#               by w18_witness.POINTING, which is applied below.
#   89:50       the doxology really does stand inside verse 50, after a single
#               mediant, with no verse 51 following. The carrier was right.
# Nothing here is imported from another edition; the readings come off the
# page (ingest/w18_evidence.json).
V1662 = {}


V1928 = {
    (18, 28): ("no mediant",
               "the justus 1928 text prints this verse without its asterisk; "
               "the 1662 text has a mediant here. Carried as justus prints it. "
               "Confirm against a 1928 scan"),
    (109, 21): ("no mediant",
                "the justus 1928 text prints this verse without its asterisk; "
                "the 1662 text has a mediant here. Carried as printed. Confirm "
                "against a 1928 scan"),
    (119, 1): ("no mediant",
               "the justus 1928 text prints the first verse of Psalm 119 "
               "without its asterisk; the 1662 text has a mediant here. Carried "
               "as printed. Confirm against a 1928 scan"),
}


def main():
    ps = w13_1662.parse()
    bad = w13_1662.gate(ps, "1662")
    if bad:
        raise SystemExit("1662 gate: %s" % bad)
    fixed = w18_witness.apply(ps)          # Wave 18: two mediants off the page
    print("1662: %d mediants restored from the Annexed Book %s"
          % (len(fixed), [(n, v) for _k, n, v, _t in fixed]))
    for (n, v), (key, note) in V1662.items():
        ps[n].setdefault("verifies", []).append((v, key, note))
    an, man = w13_render.render("1662", ps, ":")
    print("1662: %d psalms, %d verses; mediant anomalies %s; VERIFY %d"
          % (len(ps), sum(len(p["verses"]) for p in ps.values()), an, len(man)))
    m1662 = man

    ps = w13_1928.parse()
    bad = w13_1662.gate(ps, "1928")
    if bad:
        raise SystemExit("1928 gate: %s" % bad)
    for (n, v), (key, note) in V1928.items():
        ps[n].setdefault("verifies", []).append((v, key, note))
    an, man = w13_render.render("1928", ps, "*")
    print("1928: %d psalms, %d verses; mediant anomalies %d %s"
          % (len(ps), sum(len(p["verses"]) for p in ps.values()), len(an), an[:10]))
    json.dump(m1662 + man, open(os.path.join(HERE, "wave13_verifies.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
