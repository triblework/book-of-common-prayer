#!/usr/bin/env python3
"""fidelity_check.py — anti-fabrication gate for Wave 4 Holy Communion.

Given an authored edition file and the byte-faithful source spine it was
structured from, confirm that (almost) every WORD of spoken/rubric text in the
authored file also occurs in the spine. Any word present in the authored file
but absent from the spine is a candidate fabrication or a spelling change and is
printed for human review. Markdown structure the author is allowed to ADD
(anchor headings `##`, bold speaker labels, blockquote markers) is stripped
before comparison, and a small stoplist of anchor-menu vocabulary is ignored.

This does not prove correctness (word order/assignment can still be wrong) but it
mechanically rules out invented text — the prime-directive risk.

Usage:
    python3 ingest/fidelity_check.py <authored.md> <spine.md>
Exit 0 = clean (no unexplained words); exit 1 = review needed.
"""
import sys, re
from collections import Counter

# Anchor-menu / structural vocabulary the author may introduce in `##` headings
# even if the word is not in the body. Lower-cased.
ANCHOR_STOP = set("""
the lord lords lord's prayer collect for purity introit summary of law kyrie
eleison gloria in excelsis collects king epistle gospel nicene creed sermon
offertory whole state christs christ church exhortation exhortations invitation
general confession absolution comfortable words sursum corda preface proper
prefaces sanctus humble access consecration communion post oblation thanksgiving
blessing rubrics declaration kneeling summary apostles decalogue commandments
ten prayer of a and administration order holy supper morning matins mass masse
""".split())


def tokens(text: str) -> Counter:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return Counter(w for w in text.split() if w)


def strip_structure(md: str) -> str:
    out = []
    for line in md.splitlines():
        if line.startswith("#"):        # anchor / title — structural, skip
            continue
        line = re.sub(r"^>\s*", "", line)          # rubric marker
        line = re.sub(r"\*\*([^*]*)\*\*", "", line)  # bold speaker label
        line = re.sub(r"<!--.*?-->", "", line)       # VERIFY comments
        out.append(line)
    return "\n".join(out)


def main(authored_path: str, spine_path: str) -> int:
    authored = open(authored_path, encoding="utf-8").read()
    spine = open(spine_path, encoding="utf-8").read()
    a = tokens(strip_structure(authored))
    s = tokens(spine)
    missing = {}
    for w, n in a.items():
        if w in ANCHOR_STOP:
            continue
        if s[w] == 0:
            missing[w] = n
    if missing:
        print(f"REVIEW: {len(missing)} word(s) in authored not found in spine "
              f"({authored_path}):")
        for w in sorted(missing):
            print(f"   {w!r} x{missing[w]}")
        return 1
    print(f"CLEAN: every authored word is attested in the spine ({authored_path})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
