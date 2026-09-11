#!/usr/bin/env python3
"""w13_build_1892.py — write the 1892 psalter cells (Wave 13).

The text is the 1892 PDF's own letters after the whitespace repair; it was
tested against an INDEPENDENT witness (the justus dated change log): 51 of 55
applicable entries agree, including 32 of the 35 changes the log dates to 1892
itself -- which is what establishes that this PDF genuinely is the 1892 text.
The disagreements are carried as the PDF prints them, each with a VERIFY.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w13_1892
import w13_1662
import w13_render

LOG = ("the justus table of pre-1928 U.S. psalter changes (1789/Psalter1789&"
       "1892.htm) says this reading was %s; the 1892 PDF prints the other. One "
       "of the two sources is wrong here and only a page scan can say which. "
       "Carried as the 1892 PDF prints it")
V1892 = {
    (18, 10): ("cherubins", LOG % "changed to 'Cherubims' in 1790 and 'Cherubim' in 1793"),
    (42, 9): ("the water-pipes", LOG % "changed to 'thy water-pipes' in 1892"),
    (68, 27): ("Zebulon", LOG % "restored to 'Zabulon' in 1892"),
    (83, 9): ("Midianites", LOG % "restored to 'Madianites' in 1892"),
    (68, 31): ("Eqypt", "the 1892 PDF's text layer reads 'Eqypt' (a q for the g); "
                        "almost certainly a keying slip for 'Egypt', but carried "
                        "exactly as the source prints it. Confirm against a scan"),
    (102, 4): ("liked", "the 1892 PDF's letters spell 'withered liked grass' where "
                        "1662 and 1928 read 'withered like grass'; carried as the "
                        "source prints it, not corrected toward another edition. "
                        "Confirm against a scan"),
    (50, 17): ("has cast", "the 1892 PDF's letters spell 'has cast' where 1662 "
                           "reads 'hast cast'; carried as the source prints it. "
                           "Confirm against a scan"),
}
MISSING = ("the 1892 PDF prints this verse with NO mediant -- no colon anywhere "
           "in its text layer -- where 1662 and 1928 both point it. Carried as "
           "the source prints it; the pointing is not imported from another "
           "edition. Confirm against a scan")
for _k in ((14, 7), (17, 3), (35, 20), (45, 11), (115, 8)):
    V1892[_k] = ("no mediant", MISSING)
V1892[(10, 4)] = ("semicolon at the mediant",
                  "the 1892 PDF prints a semicolon where 1662 and 1928 print the "
                  "mediant, so the verse carries no ' : '. Carried as printed")
V1892[(77, 18)] = ("two colons",
                   "the 1892 PDF prints a colon where 1662 has a semicolon, so "
                   "this verse carries two. Carried as printed")


def main():
    ps = w13_1892.parse()
    bad = w13_1662.gate(ps, "1892")
    if bad or w13_1892.DROPPED:
        raise SystemExit("1892 gate: %s / dropped %s" % (bad, w13_1892.DROPPED))
    for (n, v), (key, note) in V1892.items():
        ps[n].setdefault("verifies", []).append((v, key, note))
    an, man = w13_render.render("1892", ps, ":")
    json.dump(man, open(os.path.join(HERE, "wave13_1892_verifies.json"), "w"),
              indent=1)
    print("1892: %d psalms, %d verses; mediant anomalies %d %s; VERIFY %d"
          % (len(ps), sum(len(p["verses"]) for p in ps.values()), len(an),
             an[:12], len(man)))


if __name__ == "__main__":
    main()
