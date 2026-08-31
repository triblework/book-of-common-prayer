#!/usr/bin/env python3
"""w10_build_scottish.py — the 1637 Scottish propers (Wave 10, sub-wave 10a).

Authoring-only; NOT published. File -> file; no liturgical text is emitted as
model output.

The justus Scotland page prints the collects in full and the readings as
CITATIONS ONLY ("Rom. 13.8. [-14]"), which is exactly this wave's reading depth.
The bracketed closing verse is Wohlers' editorial identification, so w10_cite
drops it; the initial verse is what the book prints.

Two features of this source are represented rather than smoothed away:

  * The Sunday after Christmas Day prints NO collect of its own -- it
    cross-references Christmas Day ("...&c. as upon Christmas day."). That
    cross-reference IS the printed text, so it stands as the collect.
  * The Gospel announcement rubrics (the people standing, "Thanks be to thee,
    O Lord") are printed ONCE, as general directions at Advent 1, and belong to
    the Gospel section there.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from w10_cite import canonical  # noqa: E402
import w10_slice as W           # noqa: E402

MARKS = [
    ("advent-1", "The first Sunday in Advent."),
    ("advent-2", "The second Sunday in Advent."),
    ("advent-3", "The third Sunday in Advent."),
    ("advent-4", "The fourth Sunday in Advent."),
    ("christmas-day", "Christmas day."),
    ("_skip:st-stephen", "Saint Stevens day."),
    ("_skip:st-john-evangelist", "S. John Evangelists day."),
    ("_skip:holy-innocents", "Innocents day."),
    ("christmas-1", "The Sund. after Christm. day."),
    ("circumcision", "The Circumcision of Christ"),
    ("epiphany", "The Epiphany."),
    ("epiphany-1", "The first Sunday after the Epiphany."),
    ("epiphany-2", "The second Sunday after the Epiphany."),
    ("epiphany-3", "The third Sunday after the Epiphany."),
    ("epiphany-4", "The iiij. Sunday after the Epiphany."),
    ("epiphany-5", "The fifth Sunday after the Epiphany."),
    ("_skip:septuagesima", "The Sunday called Septuagesima."),
]

CITE_LINE = re.compile(r"^[0-9A-Za-z][A-Za-z. ]*\.? ?[0-9]+\.[0-9]+\.(\s*\[-[0-9]+\])?$")
EPISTLE = re.compile(r"^>?\s*(For the Epistle|The Epistle)\s*\.?\s*$", re.I)
GOSPEL = re.compile(r"^>?\s*The Gospel\s*\.?\s*$", re.I)
COLLECT = re.compile(r"^>?\s*The Collect\s*\.?\s*$", re.I)

# Editorial prose on the Scotland page (not Prayer-Book text).
APPARATUS = ("In the original, the Epistles and Gospels are printed at length",
             "only the citations are given here")


def parse(block):
    cell = {"heading": re.sub(r"^>\s*", "", block[0]).strip().rstrip("."),
            "collect": [], "epistle": None, "gospel": None,
            "epistle_rubrics": [], "gospel_rubrics": []}
    # The page uses two layouts: Advent 1 interleaves label/citation, while every
    # later occasion prints BOTH labels and then both citations (a two-column
    # artefact). Queueing citations in document order and filling Epistle then
    # Gospel reads both layouts correctly.
    cites = []
    mode = "collect"
    for raw in block[1:]:
        line = raw.strip()
        if not line or any(a in line for a in APPARATUS):
            continue
        bare = re.sub(r"^>\s*", "", line).strip()
        if COLLECT.match(line):
            mode = "collect"
            continue
        if EPISTLE.match(line):
            mode = "epistle"
            cell["epistle"] = {"cite": None,
                               "for_the": bare.lower().startswith("for the")}
            continue
        if GOSPEL.match(line):
            mode = "gospel"
            cell["gospel"] = {"cite": None, "for_the": False}
            continue
        if CITE_LINE.match(bare):
            cites.append(bare)
            continue
        if mode == "collect":
            if not line.startswith(">"):
                cell["collect"].append(bare)
            continue
        if line.startswith(">"):
            # The Gospel-announcement directions are printed between the Epistle
            # label and its citation; they govern the Gospel.
            cell["gospel_rubrics"].append(bare)
    for slot in ("epistle", "gospel"):
        if cell[slot] and not cell[slot]["cite"] and cites:
            cell[slot]["cite"] = cites.pop(0)
    if cites:
        raise SystemExit(f"  !! {cell['heading']!r}: unassigned citations {cites}")
    return cell


def render(cell):
    parts = [f"# {cell['heading']}", ""]
    if cell["collect"]:
        parts += ["## The Collect", ""]
        for para in cell["collect"]:
            parts += [W.strip_brackets(para, False), ""]
    for anchor, slot, rubrics in (
            ("The Epistle", cell["epistle"], cell["epistle_rubrics"]),
            ("The Gospel", cell["gospel"], cell["gospel_rubrics"])):
        if not slot or not slot.get("cite"):
            continue
        parts += [f"## {anchor}", ""]
        if slot.get("for_the"):
            parts += ["> For the Epistle.", ""]
        for rub in rubrics:
            parts += ["> " + rub, ""]
        parts += [canonical(slot["cite"]), ""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(parts)).strip() + "\n"


def main():
    lines, _ = W.load("1637_A.md")
    segs = W.segment(lines, [], MARKS)
    n = 0
    for slug, block in segs.items():
        if slug.startswith("_skip:"):
            continue
        cell = parse(block)
        W.write_cell("1637", slug, render(cell))
        ep = cell["epistle"] and cell["epistle"]["cite"]
        go = cell["gospel"] and cell["gospel"]["cite"]
        print(f"  {slug:14s} collect_paras={len(cell['collect'])} "
              f"rubrics={len(cell['gospel_rubrics'])}  {ep} / {go}")
        n += 1
    print(f"1637: {n} cells")


if __name__ == "__main__":
    main()
