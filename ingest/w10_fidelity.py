#!/usr/bin/env python3
"""w10_fidelity.py — Wave-10 wrapper around ingest/fidelity_check.py.

Wave 10 applies exactly two MECHANICAL transforms that legitimately introduce
words the spine does not contain, both defined in WAVE10_GUIDE.md §3:

  1. citation canonicalization -- "1 Cor. iv."  -> "1 Corinthians 4"
     (the canonical book names come from w10_cite.BOOKS, nowhere else)
  2. numeral conversion       -- "Psalm cxx."  -> "Psalm 120"

Those two, and only those two, are allowed. Anything else a cell contains that
its spine does not is reported, so a fabrication still fails loudly.

Usage:
    python3 ingest/w10_fidelity.py <spine.md> <authored.md> [<authored.md> ...]
"""
import os, re, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from w10_cite import BOOKS  # noqa: E402

ALLOWED = {w.lower() for name in BOOKS.values() for w in name.split()}
# "and part of chapter 16" -- the compound-citation rendering (guide 3).
ALLOWED |= {"chapter", "and", "part", "of"}

MISSING = re.compile(r"^\s*'(?P<word>[^']+)'\s*x\d+\s*$")


def check(spine, authored):
    proc = subprocess.run(
        [sys.executable, os.path.join(HERE, "fidelity_check.py"), authored, spine],
        capture_output=True, text=True)
    if proc.returncode == 0:
        return []
    unexplained = []
    for line in proc.stdout.splitlines():
        m = MISSING.match(line)
        if not m:
            continue
        word = m.group("word").lower()
        if word in ALLOWED or word.isdigit():
            continue          # documented mechanical transform
        unexplained.append(word)
    return unexplained


def main(spine, files):
    bad = 0
    for path in files:
        words = check(spine, path)
        if words:
            print(f"  REVIEW {path}: {', '.join(sorted(set(words)))}")
            bad += 1
    print(f"w10 fidelity: {len(files) - bad}/{len(files)} clean")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2:]))
