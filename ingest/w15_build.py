#!/usr/bin/env python3
"""w15_build.py — rebuild every Wave-15 cell, in order (authoring-only).

  1928 tables/calendar.md               w15_calendar.py
  1928 tables/feasts-and-fasts.md       w15_feasts.py
  1928 tables/proper-psalms.md,
       psalter/selections.md            w15_psalms.py
  1928 front-matter/order-how-*.md      w15_rubrics.py
  1928 tables/proper-lessons.md         w15_lessons.py
  1892 front-matter/order-how-*.md      w14_build_rubrics.py (+ 1549-1789,
                                        1979: byte-identical except the two
                                        1789 slice fragments Wave 15 removes)
  1979 tables/calendar.md               w14_build_1979_calendar.py (29 Feb)

Then run the gates: w15_fidelity.py and w15_audit.py (and w14_audit.py,
which carries the cross-edition checks for tables/ and front-matter/).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["w15_calendar.py", "w15_feasts.py", "w15_psalms.py", "w15_rubrics.py",
         "w15_lessons.py", "w14_build_rubrics.py", "w14_build_1979_calendar.py"]

for step in STEPS:
    r = subprocess.run([sys.executable, os.path.join(HERE, step)],
                       capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines()
    print("%-28s %s" % (step, out[-1] if out else ""))
    if r.returncode:
        print("\n".join(out))
        raise SystemExit("%s failed" % step)
