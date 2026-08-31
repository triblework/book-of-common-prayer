#!/usr/bin/env python3
"""w10_audit.py — cross-edition anchor audit for the propers (Wave 10).

Authoring-only. The fidelity gate proves nothing was INVENTED; this proves
nothing was silently LOST. For each occasion it compares the anchor set across
every edition that carries it and reports an edition missing an anchor that a
majority of its siblings have.

That is the failure mode the gate cannot see: a parser bug once dropped the
Passion Gospels from Palm Sunday and Good Friday, and every remaining word was
still perfectly attested, so fidelity stayed green.

Legitimate absences are expected (1549-only Introits; the Holy Week days that
carry no proper Collect; 1979's collect-only cells), so this REPORTS rather
than fails.

Usage: python3 ingest/w10_audit.py [editions-root]
"""
import os, re, sys
from collections import defaultdict

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else
                       os.path.join(os.path.dirname(__file__), "..", "editions"))
FAM = "collects-epistles-gospels"
ANCHOR = re.compile(r"^## (.+)$", re.M)

# Anchors whose absence is a known feature, not a loss.
EXPECTED_ABSENT = {
    "The Introit": lambda ed: ed != "1549",
    "The Introit (Second Communion)": lambda ed: ed != "1549",
    "The Collect (Contemporary)": lambda ed: ed != "1979",
    "The Proper Lessons": lambda ed: ed != "1549",
    "The Epistle": lambda ed: ed == "1979",
    "The Gospel": lambda ed: ed == "1979",
    "The Collect (Second Communion)": lambda ed: True,
    "The Epistle (Second Communion)": lambda ed: True,
    "The Gospel (Second Communion)": lambda ed: True,
}

# Confirmed against the sources: an absence that IS the book, keyed by
# (slug, edition, anchor) with the reason.
KNOWN_GOOD = {
    ("easter-even", ed, "The Collect"): "1549-1559 print no proper Collect for "
    "Easter Even -- only the Epistle and Gospel. 1662 adds one."
    for ed in ("1549", "1552", "1559")
}
KNOWN_GOOD[("advent-4", "1979", "The Collect")] = (
    "The traditional-language collect is lost from the public-domain 1979 "
    "e-text (a 1993 keying dropout); flagged inline, not reconstructed.")


def main():
    cells = defaultdict(dict)          # slug -> edition -> set(anchors)
    for edition in sorted(os.listdir(ROOT)):
        d = os.path.join(ROOT, edition, FAM)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            body = open(os.path.join(d, fn), encoding="utf-8").read()
            cells[fn[:-3]][edition] = set(ANCHOR.findall(body))

    findings = 0
    for slug in sorted(cells):
        per_ed = cells[slug]
        counts = defaultdict(int)
        for anchors in per_ed.values():
            for a in anchors:
                counts[a] += 1
        for anchor, n in sorted(counts.items()):
            if n <= len(per_ed) / 2:
                continue                       # not a majority anchor
            for edition, anchors in sorted(per_ed.items()):
                if anchor in anchors:
                    continue
                exempt = EXPECTED_ABSENT.get(anchor)
                if exempt and exempt(edition):
                    continue
                if (slug, edition, anchor) in KNOWN_GOOD:
                    continue
                print(f"  MISSING  {slug:<24} {edition}  '{anchor}' "
                      f"(present in {n}/{len(per_ed)} editions)")
                findings += 1
    print(f"w10 audit: {len(cells)} occasions, {findings} anomal"
          f"{'y' if findings == 1 else 'ies'} to review")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
