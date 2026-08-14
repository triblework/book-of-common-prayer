#!/usr/bin/env python3
"""Split the 1928 U.S. Ordinal (one justus page, all three orders + preface +
the Litany for Ordinations) into the four repo files, file->file. Uses
ingest/ordinal_struct via per-section temp spines."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ordinal_struct
WT = os.path.dirname(HERE)
SPINE = os.path.join(WT, "ingest/spines-w8/ordinal_1928.md")
TMP = os.path.join(HERE, "spines-w8", "_tmp_1928")
os.makedirs(TMP, exist_ok=True)

# OCR line-break hyphens to close up (keep real hyphens: never-fading, self-same,
# well-governing, well-learned).
HYPH = ["breth-ren", "com-mitted", "conform-ity", "conver-sation", "conversa-tion",
        "deter-mined", "inno-cency", "know-ledge", "per-fect", "remem-ber",
        "sal-vation", "them-selves", "Impedi-ment", "impedi-ment"]
FIXES = {h: h.replace("-", "") for h in HYPH}

LABELS = ["Answer", "The Presiding Bishop", "The Bishop", "Bishop", "Minister"]
FOOTER = "Web author"

# section slicing markers, in order
MARKERS = ["THE PREFACE.", "Making Deacons", "Ordering Priests",
           "Consecrating a Bishop", "The Litany and Suffrages"]

DROP_TITLES = ["THE PREFACE.", "The Form and Manner of", "Making Deacons",
               "Ordering Priests", "The Form of Ordaining or", "Consecrating a Bishop",
               "Order of the Protestant Episcopal Church",
               "Making, Ordaining, and Consecrating", "Form of Making, Ordaining"]

RUBRIC_COMMON = [
    "When the day appointed by the Bishop is come", "When all things are duly prepared",
    "The Sermon being ended", "A Priest shall present", "The Priest shall answer",
    "Then", "And Note", "And NOTE", "And another", "Then another",
    "After this", "After which", "He shall then require", "That done", "That ended",
    "Let us pray", "Let us pray.", "Or else", "Or this", "Here, at the", "¶ Here",
    "Veni, Creator Spiritus.", "The Collect.", "The Epistle.", "The Gospel.",
    "For the Epistle.", "And here it must be declared", "And if, on the same day",
    "When this is done", "When this Prayer is done",
]


def blocks_of(text):
    out, cur = [], []
    for ln in text.split("\n"):
        if ln.strip() == "":
            if cur:
                out.append(cur); cur = []
        else:
            cur.append(ln.rstrip())
    if cur:
        out.append(cur)
    return out


def main():
    raw = open(SPINE).read()
    # cut footer
    for foot in (FOOTER,):
        idx = raw.find("\n" + foot)
        if idx > 0:
            raw = raw[:idx]
    blks = blocks_of(raw)

    # locate marker block indices
    idx = {}
    for m in MARKERS:
        for i, b in enumerate(blks):
            if re.sub(r"^>\s*", "", b[0].strip()).startswith(m):
                idx[m] = i
                break
    order = sorted(idx.items(), key=lambda kv: kv[1])
    bounds = {}
    for j, (m, i) in enumerate(order):
        end = order[j + 1][1] if j + 1 < len(order) else len(blks)
        bounds[m] = (i, end)

    def slice_text(m, extra=None):
        i, e = bounds[m]
        chunk = blks[i:e]
        if extra:
            ei, ee = bounds[extra]
            chunk = chunk + blks[ei:ee]
        return "\n\n".join("\n".join(b) for b in chunk)

    def write_tmp(name, text):
        p = os.path.join(TMP, name + ".md")
        open(p, "w").write(text + "\n")
        return p

    jobs = []

    # ---- Preface ----
    jobs.append((write_tmp("preface", slice_text("THE PREFACE.")),
                 "editions/1928/ordinal/preface.md",
                 {"title": "# The Preface.", "drop_blocks": DROP_TITLES,
                  "labels": [], "rubrics": [], "anchors": [], "fixes": FIXES,
                  "footer": FOOTER}))

    # ---- Deacons (+ Litany for Ordinations appended) ----
    jobs.append((write_tmp("deacons", slice_text("Making Deacons", extra="The Litany and Suffrages")),
                 "editions/1928/ordinal/ordering-deacons.md",
                 {"title": "# The Form and Manner of Making Deacons.",
                  "drop_blocks": DROP_TITLES, "labels": LABELS, "fixes": FIXES,
                  "footer": FOOTER, "rubrics": RUBRIC_COMMON,
                  "anchors": [
                      ("The Presentation", "When the day appointed by the Bishop is come"),
                      ("The Litany", "Then the Bishop (commending"),
                      ("The Collect", "Then shall be said the Service for the Communion"),
                      ("The Epistle", "The Epistle. 1 Timothy"),
                      ("The Examination", "Then, the People being seated, the Bishop shall examine"),
                      ("The Ordering", "Then, the People standing, the Bishop shall lay his Hands"),
                      ("The Gospel", "Then one of them, appointed by the Bishop, shall read the Gospel"),
                      ("The Communion", "Then shall the Bishop proceed in the Communion"),
                      ("The Litany for Ordinations", "The Litany and Suffrages"),
                  ]}))

    # ---- Priests ----
    jobs.append((write_tmp("priests", slice_text("Ordering Priests")),
                 "editions/1928/ordinal/ordering-priests.md",
                 {"title": "# The Form and Manner of Ordering Priests.",
                  "drop_blocks": DROP_TITLES, "labels": LABELS, "fixes": FIXES,
                  "footer": FOOTER, "rubrics": RUBRIC_COMMON,
                  "anchors": [
                      ("The Presentation", "When the day appointed by the Bishop is come"),
                      ("The Litany", "Then the Bishop (commending"),
                      ("The Collect", "Then shall be said the Service for the Communion"),
                      ("The Epistle", "The Epistle. Ephesians"),
                      ("The Gospel", "The Gospel. St. Matthew"),
                      ("The Exhortation", "Then, the People being seated, the Bishop shall say unto those"),
                      ("The Examination", "DO you think in your heart"),
                      ("The Prayer", "Then, all standing, shall the Bishop say"),
                      ("Veni, Creator Spiritus", "Veni, Creator Spiritus."),
                      ("The Ordering", "That done, the Bishop shall pray in this wise"),
                      ("The Communion", "When this is done"),
                  ]}))

    # ---- Bishops ----
    jobs.append((write_tmp("bishops", slice_text("Consecrating a Bishop")),
                 "editions/1928/ordinal/consecration-bishops.md",
                 {"title": "# The Form of Ordaining or Consecrating a Bishop.",
                  "drop_blocks": DROP_TITLES, "labels": LABELS, "fixes": FIXES,
                  "footer": FOOTER, "rubrics": RUBRIC_COMMON,
                  "anchors": [
                      ("The Collect", "When all things are duly prepared in the Church"),
                      ("The Epistle", "And another Bishop shall read the Epistle"),
                      ("The Gospel", "Then another Bishop shall read the Gospel"),
                      ("The Presentation", "Then shall follow the Nicene Creed, and after that the Sermon"),
                      ("The Promise of Conformity", "Then shall the Presiding Bishop demand Testimonials"),
                      ("The Litany", "Then the Presiding Bishop shall move the Congregation present to pray"),
                      ("The Examination", "Then, the People being seated, the Presiding Bishop, sitting in his chair shall say to him"),
                      ("Veni, Creator Spiritus", "Then shall the Bishop elect put on the rest"),
                      ("The Consecration", "That ended, the Presiding Bishop shall say"),
                      ("The Delivery of the Bible", "Then the Presiding Bishop shall deliver him the Bible"),
                      ("The Communion", "Then the Presiding Bishop shall proceed in the Communion Service"),
                  ]}))

    for tmp, out, cfg in jobs:
        n, unplaced = ordinal_struct.build(tmp, os.path.join(WT, out), cfg)
        print("%-45s %4d lines  unplaced=%s" % (out, n, unplaced))


if __name__ == "__main__":
    main()
