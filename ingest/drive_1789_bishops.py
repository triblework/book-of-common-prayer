#!/usr/bin/env python3
"""Structure the 1789 U.S. Bishops ordinal (justus spine) -> repo file, file->file.
Keeps the 1789 readings; drops the interleaved 1892-difference apparatus (the 1892
presentation rubric, the 1892 hymn-replacement note, etc.) — 1892 is derived
separately from those notes."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ordinal_struct
WT = os.path.dirname(HERE)

cfg = {
    "title": "# The Form of Ordaining or Consecrating a Bishop.",
    "drop_hashes": True,
    "footer": "XXXNOFOOTERXXX",
    "labels": ["Answer", "The Presiding Bishop"],
    "drop_blocks": [
        "This text in the 1892 Book is essentially identical",
        "1789 BCP:",
        "1892 BCP:",
        "Then shall follow the Nicene Creed, and after that the Sermon",  # 1892 presentation rubric
        '* "etc." in 1892',
        "This hymn appears in the 1789 BCP only.",
        "In the 1892 Book, the hymn is replaced by:",
        "Or else the longer paraphrase of the same Hymn",  # 1892 hymn cross-ref
    ],
    "anchors": [
        ("The Collect", "When all things are duly prepared in the Church"),
        ("The Epistle", "And another Bishop shall read the Epistle"),
        ("The Gospel", "Then another Bishop shall read the Gospel"),
        ("The Presentation", "After the Gospel and the Sermon are ended"),
        ("The Promise of Conformity", "Then shall the Presiding Bishop demand Testimonials"),
        ("The Litany", "Then the Presiding Bishop shall move the Congregation present to pray"),
        ("The Examination", "Then the Presiding Bishop, sitting in his chair, shall say to him"),
        ("Veni, Creator Spiritus", "Then shall the Bishop elect put on the rest"),
        ("The Consecration", "That ended, the Presiding Bishop shall say"),
        ("The Delivery of the Bible", "Then the Presiding Bishop shall deliver him the Bible"),
        ("The Communion", "Then the Presiding Bishop shall proceed in the Communion Service"),
    ],
    "rubrics": [
        "When all things are duly prepared in the Church",
        "The Collect.",
        "And another Bishop shall read the Epistle",
        "l Tim. iii.", "1 Tim. iii.",
        "For the Epistle. Acts",
        "Or this.",
        "Then another Bishop shall read the Gospel",
        "St. John", "St. Matt",
        "After the Gospel and the Sermon are ended",
        "Then shall the Presiding Bishop demand Testimonials",
        "He shall then require of him the following Promise",
        "Then the Presiding Bishop shall move the Congregation",
        "And then shall be said the Litany",
        "Then shall be said this Prayer following",
        "Then the Presiding Bishop, sitting in his chair, shall say",
        "Then the Presiding Bishop, standing up, shall say",
        "Then shall the Bishop elect put on",
        "That ended, the Presiding Bishop shall say",
        "Let us pray",
        "Then the Presiding Bishop and Bishops present shall lay",
        "Then the Presiding Bishop shall deliver him the Bible",
        "Then the Presiding Bishop shall proceed in the Communion Service",
        "And for the last Collect",
    ],
    "fixes": {
        "l Tim. iii. 1.": "1 Tim. iii. 1.",
        "called the Elders the Church": "called the Elders of the Church",
        "purchased with his Own blood": "purchased with his own blood",
        "which he bath purchased": "which he hath purchased",
        "according the will of our Lord": "according to the will of our Lord",
        "strange doctrine Contrary to God's Word": "strange doctrine contrary to God's Word",
    },
}

n, unplaced = ordinal_struct.build(
    os.path.join(WT, "ingest/spines-w8/bishops_1789.md"),
    os.path.join(WT, "editions/1789/ordinal/consecration-bishops.md"),
    cfg)
print("wrote 1789 bishops: %d lines; unplaced=%s" % (n, unplaced))
