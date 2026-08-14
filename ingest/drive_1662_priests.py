#!/usr/bin/env python3
"""Structure the 1662 Priests ordinal (CoE spine) -> repo file, file->file."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, HERE)
import ordinal_struct
WT = os.path.dirname(HERE)

cfg = {
    "title": "# The Form and Manner of Ordering of Priests.",
    "drop_hashes": True,
    "footer": "Text from The Book of Common Prayer",
    "labels": ["Answer", "The Bishop"],
    "anchors": [
        ("The Presentation", "When the day appointed by the Bishop is come"),
        ("The Litany", "Then the Bishop (commending such as shall be found meet"),
        ("The Collect", "Then shall be sung or said the Service for the Communion"),
        ("The Epistle", "The Epistle. Ephesians"),
        ("The Gospel", "After this shall be read for the Gospel"),
        ("The Exhortation", "Then the Bishop, sitting in his Chair, shall say unto them"),
        ("The Examination", "Do you think in your heart that you be truly called"),
        ("The Prayer", "Then shall the Bishop, standing up, say"),
        ("Veni, Creator Spiritus", "After which shall be sung or said by the Bishop"),
        ("The Ordering", "That done, the Bishop shall pray in this wise"),
        ("The Communion", "When this is done, the Nicene Creed"),
    ],
    "rubrics": [
        "When the day appointed by the Bishop is come",
        "First, the Archdeacon",
        "The Archdeacon shall answer",
        "Then the Bishop shall say unto the people",
        "And if any great crime",
        "Then the Bishop (commending",
        "Then shall be sung or said the Service for the Communion",
        "The Collect",
        "The Epistle. Ephesians",
        "After this shall be read for the Gospel",
        "St. Matthew", "St. John",
        "Or else this that followeth",
        "Then the Bishop, sitting in his Chair, shall say unto them",
        "Then shall the Bishop, standing up, say",
        "After this, the Congregation shall be desired",
        "After which shall be sung or said by the Bishop",
        "Or this:",
        "That done, the Bishop shall pray",
        "Let us pray",
        "When this prayer is done, the Bishop with the Priests present shall lay",
        "Then the Bishop shall deliver to every one of them kneeling the Bible",
        "When this is done, the Nicene Creed",
        "The Communion being done",
        "And if on the same day the Order of Deacons",
    ],
    "fixes": {"accord- ing": "according"},
}
# NOTE: the standalone "> The Bishop." block (line 11) is a rubric attribution in
# the CoE source; the INLINE "The Bishop.Are you persuaded…" lines are speaker
# labels. The label regex handles the inline ones; "The Bishop." is also listed as
# a rubric trigger so the bare attribution stays a rubric. Because the bare block's
# first line is exactly "The Bishop." it matches the rubric trigger first.

n, unplaced = ordinal_struct.build(
    os.path.join(WT, "ingest/spines-w8/priests_1662.md"),
    os.path.join(WT, "editions/1662/ordinal/ordering-priests.md"),
    cfg)
print("wrote 1662 priests: %d lines; unplaced=%s" % (n, unplaced))
