#!/usr/bin/env python3
"""Insert `<!-- VERIFY -->` lines after specific lines in Wave-8 American files,
in-place (file->file; keeps large liturgical text out of model output). Each rule
is (file, marker_substring, verify_comment). The verify line is inserted on its own
line immediately after the FIRST line containing the marker (idempotent: skips if
the next line is already that comment)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)

RULES = [
    ("editions/1789/ordinal/ordering-priests.md",
     "for that and ability is given of God alone",
     "<!-- VERIFY: 'for that and ability'; the 1662 reads 'for that will and ability'; the 1789 justus HTML likely dropped 'will' in OCR; kept as printed; confirm against a 1789 page scan -->"),
    ("editions/1789/ordinal/ordering-priests.md",
     "and to make both yourselves and them as much as in lieth",
     "<!-- VERIFY: 'as much as in lieth'; likely 'as much as in you lieth' (word 'you' dropped in OCR); kept as printed; confirm against a 1789 page scan -->"),
    ("editions/1789/ordinal/ordering-priests.md",
     "That neither devil, world, nor",
     "<!-- VERIFY: 'That neither devil, world, nor'; the following metrical line likely began 'flesh,' (dropped in OCR — cf. 1662 'nor flesh, against us'); kept as printed; confirm against a 1789 page scan -->"),
    ("editions/1789/ordinal/consecration-bishops.md",
     "That neither devil, world, nor",
     "<!-- VERIFY: 'That neither devil, world, nor'; the following metrical line likely began 'flesh,' (dropped in OCR — cf. 1662 'nor flesh, against us'); kept as printed; confirm against a 1789 page scan -->"),
]


def main():
    for rel, marker, comment in RULES:
        path = os.path.join(WT, rel)
        lines = open(path).read().split("\n")
        out, done = [], False
        for i, ln in enumerate(lines):
            out.append(ln)
            if not done and marker in ln:
                nxt = lines[i + 1] if i + 1 < len(lines) else ""
                if nxt.strip() != comment:
                    out.append(comment)
                done = True
        if not done:
            print("WARN marker not found in %s: %r" % (rel, marker))
        open(path, "w").write("\n".join(out))
    print("done")


if __name__ == "__main__":
    main()
