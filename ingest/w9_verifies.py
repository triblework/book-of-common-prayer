#!/usr/bin/env python3
"""w9_verifies.py — insert Wave-9 <!-- VERIFY --> flags (file -> file).

Each flag goes on its own line immediately AFTER the paragraph line that
contains its anchor substring. The doubtful reading is the FIRST single-quoted
string in the comment (verify_index keys on that). Idempotent: skips a file that
already carries the flag.
"""
import os

HERE = os.path.dirname(__file__)
WT = os.path.abspath(os.path.join(HERE, ".."))

FLAGS = [
    # (edition-relative path, anchor substring, verify comment)
    ("1979/front-matter/concerning-the-service.md",
     "fulfull the functions",
     "<!-- VERIFY: 'fulfull' — the justus 1979 public-domain e-text reads "
     "\"fulfull\"; the printed 1979 Book reads \"fulfil\"; treated as an e-text "
     "typo and left as-sourced pending a page-scan check -->"),

    ("1789/front-matter/preface.md",
     "every true member of our Church",
     "<!-- VERIFY: 'member of our Church. and every sincere Christian' — the "
     "justus 1789 text prints a full stop before a lower-case \"and\"; likely a "
     "comma in the original; left as-sourced pending a 1789 scan -->"),

    ("1637/front-matter/concerning-the-service.md",
     "to fall to thin ground",
     "<!-- VERIFY: 'to fall to thin ground' — probably an OCR rendering of "
     "\"to fall to the ground\"; left as-sourced from justus pending a 1637 scan "
     "-->"),

    ("1549/occasional-offices/private-baptism.md",
     "all those that shall he baptized",
     "<!-- VERIFY: 'all those that shall he baptized' — the justus 1549 text "
     "reads \"shall he baptized\"; an OCR/print slip for \"shall be baptized\"; "
     "left as-sourced pending a 1549 scan -->"),

    ("1637/front-matter/of-ceremonies.md",
     "OF such Ceremonies as be used in the Church, and have had their Beginning",
     "<!-- VERIFY: 'OF such Ceremonies as be used in the Church, and have had "
     "their Beginning by the Institution of Man' — justus notes two leaves are "
     "missing from its 1637 original around this section, so the Of Ceremonies "
     "text may be supplied from a parallel copy; confirm against a 1637 scan -->"),
]


def main():
    for rel, anchor, comment in FLAGS:
        path = os.path.join(WT, "editions", rel)
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
        if any(comment.split("'")[1] in ln and ln.strip().startswith("<!--")
               for ln in lines):
            print(f"  (skip, already flagged) {rel}")
            continue
        out, hit = [], False
        for ln in lines:
            out.append(ln)
            if not hit and anchor in ln:
                out.append(comment)
                hit = True
        if not hit:
            raise SystemExit(f"  !! anchor not found in {rel}: {anchor!r}")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(out))
        print(f"  flagged {rel}")


if __name__ == "__main__":
    main()
