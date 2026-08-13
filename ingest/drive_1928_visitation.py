#!/usr/bin/env python3
"""Structure the 1928 American Visitation of the Sick from its justus spine (the
sickness/dying text trips an output content-filter false-positive for a model, so
this flows spine -> code -> file). Words are the spine's; only structure is added.
Usage: drive_1928_visitation.py <spine> <out>"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import spine_struct

spine = open(sys.argv[1], encoding="utf-8").read()
# Drop the running page-header + the two-line source title block; we set our own title.
lines = [l for l in spine.split("\n") if l.strip() != "The Book of Common Prayer (1928)"]
# remove the "The Order for" / "the Visitation of the Sick" heading lines (first occurrence)
cleaned, dropped = [], 0
for l in lines:
    if dropped < 2 and l.strip() in ("The Order for", "the Visitation of the Sick"):
        dropped += 1
        continue
    cleaned.append(l)
spine = "\n".join(cleaned)

cfg = {
  "title": "# The Order for the Visitation of the Sick.",
  "is_pdf": False,
  "mediant": True,
  "fixes": {"ap-pointed": "appointed", "¶ ": "", "¶": ""},
  "anchors": [
    ("The following Service, or any part", "The Introduction", "before"),
    ("Antiphon. Remember not, Lord", "The Antiphon", "before"),
    ("Let us pray.", "The Lord's Prayer", "before"),
    ("Minister. O Lord, save thy servant", "The Suffrages", "before"),
    ("Here may be said any one or more of the Psalms", "The Psalms", "before"),
    ("As occasion demands, the Minister shall address", "The Exhortation", "before"),
    ("Here may the Minister inquire of the sick person", "The Examination", "before"),
    ("Then shall the sick person be moved to make a special confession", "The Absolution", "before"),
    ("THE Almighty Lord, who is a most strong tower", "The Blessing", "before"),
    ("PRAYERS.", "Prayers", "replace"),
    ("LITANY FOR THE DYING.", "The Litany for the Dying", "replace"),
    ("A Commendation", "The Commendation", "before"),
    ("UNCTION OF THE SICK.", "The Unction", "replace"),
    ("The Communion of the Sick", "The Communion of the Sick", "replace"),
  ],
}
out, unplaced = spine_struct.build(spine, cfg)
open(sys.argv[2], "w", encoding="utf-8").write(out)
import re
print("wrote", sys.argv[2], "|", out.count("\n"), "lines |",
      len(re.findall(r"(?m)^## ", out)), "anchors")
if unplaced:
    print("UNPLACED anchors:", [a[1] for a in unplaced])
