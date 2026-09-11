#!/usr/bin/env python3
"""w13_audit.py — gate 2 for the Psalter: did anything quietly fail to arrive?

Reads the RENDERED cells (not the parsers), so it tests what will be published.

  1. 150 psalms per edition, each a consecutive verse run.
  2. CROSS-EDITION VERSE COUNTS. 1662, 1892 and 1928 number Coverdale alike, so
     a psalm's count must agree across them except where a genuine revision is
     documented below. This is the check that caught this wave's worst bugs --
     2,032 of 2,508 verses in the first 1928 parse -- while the per-psalm run
     check stayed green.
  3. Every 1892 psalm matches 1662 or 1928 (1892 sits between them).
  4. The extras' row counts.

Each exemption names a psalm and carries its evidence (AUDIT_METHOD KNOWN_GOOD).
"""
import os
import re
import sys

WT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["psalms-1-50", "psalms-51-100", "psalms-101-150"]

# 1928 differs from 1662 in these psalms' verse counts -- each a GENUINE
# revision, with the evidence that establishes it.
KNOWN_1928 = {
    14: "1928 removes the Romans-3 interpolation (verses 5-7); the 1928 page's "
        "apparatus: 'additional verses were present prior to 1928'",
    19: "1928 merges the last two verses; apparatus: 'Last verse was two until 1928'",
    45: "1928 re-translates the opening ('overfloweth' for 'is inditing'); the "
        "apparatus quotes the old text in full",
    58: "1928 splits a long Coverdale verse in two at 'let them fall away like water'",
    71: "1928 splits verse 9 at 'God hath forsaken him'; the apparatus quotes the old single verse",
    73: "1928 splits verse 12 at 'and I said, Then have I cleansed my heart in vain'",
    89: "the CoE prints the Book III doxology inside verse 50 (VERIFY); 1928 prints it as verse 51",
    104: "1928 splits verse 35 at 'Praise thou the LORD, O my soul'",
}
EXTRAS = {("1789", "psalter/selections.md"): 10,
          ("1789", "tables/proper-psalms.md"): 6,
          ("1892", "tables/proper-psalms.md"): 16}


def counts(ed):
    out = {}
    for f in FILES:
        cur = None
        for line in open(os.path.join(WT, "editions", ed, "psalter", f + ".md"),
                         encoding="utf-8"):
            m = re.match(r"^## Psalm (\d+)\s*$", line)
            if m:
                cur = int(m.group(1)); out[cur] = []
                continue
            if cur is None or not line.strip() or line[0] in "#>" or line.startswith("<!--"):
                continue
            mv = re.match(r"^(\d{1,3}) ", line)
            out[cur].append(int(mv.group(1)) if mv else 1)
    return out


def main():
    findings = []
    C = {ed: counts(ed) for ed in ("1662", "1892", "1928", "1979")}
    for ed, c in C.items():
        if sorted(c) != list(range(1, 151)):
            findings.append("%s: %d psalms" % (ed, len(c)))
        for n, vs in c.items():
            if vs != list(range(1, len(vs) + 1)):
                findings.append("%s Psalm %d: verse run broken %s" % (ed, n, vs[:8]))
        print("%s: %d psalms, %d verses" % (ed, len(c), sum(len(v) for v in c.values())))
    for n in range(1, 151):
        a, b, c = len(C["1662"][n]), len(C["1892"][n]), len(C["1928"][n])
        if a != c and n not in KNOWN_1928:
            findings.append("Psalm %d: 1662 has %d verses, 1928 %d -- undocumented" % (n, a, c))
        if a == c and n in KNOWN_1928:
            findings.append("Psalm %d: exempted as a 1928 revision but counts agree" % n)
        if b not in (a, c):
            findings.append("Psalm %d: 1892 has %d verses, matching neither 1662 (%d) nor 1928 (%d)" % (n, b, a, c))
    for (ed, rel), want in EXTRAS.items():
        got = sum(1 for l in open(os.path.join(WT, "editions", ed, rel), encoding="utf-8") if " | " in l)
        if got != want:
            findings.append("%s %s: %d rows, want %d" % (ed, rel, got, want))
    print("\naudit: %d anomalies (%d documented 1928 revisions exempted)"
          % (len(findings), len(KNOWN_1928)))
    for f in findings:
        print("  -", f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
