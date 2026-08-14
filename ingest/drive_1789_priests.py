#!/usr/bin/env python3
"""Structure the 1789 U.S. Priests ordinal (justus spine) -> repo file, file->file."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ordinal_struct
WT = os.path.dirname(HERE)

cfg = {
    "title": "# The Form and Manner of Ordering Priests.",
    "drop_hashes": True,
    "footer": "XXXNOFOOTERXXX",
    "labels": ["Answer", "The Bishop"],
    "drop_blocks": [
        "This text in the 1892 Book is essentially identical",
        '"Amen" in italics',
        "* added in the 1892 BCP",
    ],
    "anchors": [
        ("The Presentation", "When the day appointed by the Bishop is come"),
        ("The Litany", "Then the Bishop (commending"),
        ("The Collect", "Then shall be said the Service for the Communion"),
        ("The Epistle", "The Epistle. Eph"),
        ("The Gospel", "After this shall be read for the Gospel"),
        ("The Exhortation", "Then the Bishop shall say unto them as followeth"),
        ("The Examination", "DO you think in your heart"),
        ("The Prayer", "Then shall the Bishop, standing up, say"),
        ("Veni, Creator Spiritus", "After which, shall be sung or said by the Bishop"),
        ("The Ordering", "That done, the Bishop shall pray in this wise"),
        ("The Communion", "When this is done,"),
    ],
    "rubrics": [
        "When the day appointed by the Bishop is come",
        "A Priest shall present unto the Bishop",
        "The Priest shall answer",
        "Then the Bishop shall say unto the People",
        "And if any great Crime",
        "Then the Bishop (commending",
        "Then shall be said the Service for the Communion",
        "The Collect.",
        "The Epistle. Eph",
        "After this shall be read for the Gospel",
        "St. Matt", "St. John",
        "Or else this that followeth",
        "Then the Bishop shall say unto them as followeth",
        "Then shall the Bishop, standing up, say",
        "After this, the Congregation shall be desired",
        "After which, shall be sung or said by the Bishop",
        "Or this.", "Or this",
        "That done, the Bishop shall pray",
        "Let us pray",
        "When this Prayer is done, the Bishop with the Priests present",
        "Then the Bishop shall deliver to every one of them kneeling",
        "When this is done,",
        "The Communion being done",
        "And if, on the same day",
    ],
    "fixes": {
        "examined them, I and think": "examined them, and think",
        "as this Church bath received": "as this Church hath received",
        "weighed these things With yourselves": "weighed these things with yourselves",
        "reading and Weighing the Scriptures": "reading and weighing the Scriptures",
        "When this is done, [the Nicene Creed shall be said, and]* the Bishop": "When this is done, the Bishop",
    },
}

n, unplaced = ordinal_struct.build(
    os.path.join(WT, "ingest/spines-w8/priests_1789.md"),
    os.path.join(WT, "editions/1789/ordinal/ordering-priests.md"),
    cfg)
print("wrote 1789 priests: %d lines; unplaced=%s" % (n, unplaced))
