#!/usr/bin/env python3
"""w15_show.py — print emitted lesson rows compactly for the witness pass
(authoring-only helper): w15_show.py SEC START END"""
import re, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
import w15_lessons as L
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    recs, notes = L.main(write_file=False,
                         witness=__import__("os").environ.get("W15_RAW") != "1")
sec, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rows = [r for r in recs if r["sec"] == sec and "label" in r]
for i, r in enumerate(rows[a:b], a):
    print("%3d %-28s | %s" % (i, r["label"][:28], " | ".join(v for _k, v in r["fields"])))
