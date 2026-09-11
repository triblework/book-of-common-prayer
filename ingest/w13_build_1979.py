#!/usr/bin/env python3
"""w13_build_1979.py — write the 1979 psalter cells (Wave 13)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w13_1979
import w13_1662
import w13_render


def main():
    ps = w13_1979.parse()
    bad = w13_1662.gate(ps, "1979")
    if bad:
        raise SystemExit("1979 gate failed: %s" % bad[:5])
    for n, p in ps.items():
        if p.get("incipit_truncated"):
            p.setdefault("verifies", []).append((
                "incipit", p["incipit"],
                "the 1979 e-text truncates this Latin incipit and loses its "
                "closing mark; all nine such headings have lost the same "
                "syllable (the incipits break off at 'Domi' or 'ultio', as if "
                "'num' was dropped in keying). Carried exactly as printed and "
                "not completed"))
    an, man = w13_render.render("1979", ps, "*", number_first=True)
    json.dump(man, open(os.path.join(HERE, "wave13_1979_verifies.json"), "w"),
              indent=1)
    print("1979 written: %d psalms, %d verses; mediant anomalies %d; VERIFY %d"
          % (len(ps), sum(len(p["verses"]) for p in ps.values()), len(an),
             len(man)))
    for a in an[:12]:
        print("   Psalm %d verse %s: %d mediants" % a)


if __name__ == "__main__":
    main()
