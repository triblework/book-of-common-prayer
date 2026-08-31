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
    ("st-stephen", "Saint Stevens day."),
    ("st-john-evangelist", "S. John Evangelists day."),
    ("holy-innocents", "Innocents day."),
    ("christmas-1", "The Sund. after Christm. day."),
    ("circumcision", "The Circumcision of Christ"),
    ("epiphany", "The Epiphany."),
    ("epiphany-1", "The first Sunday after the Epiphany."),
    ("epiphany-2", "The second Sunday after the Epiphany."),
    ("epiphany-3", "The third Sunday after the Epiphany."),
    ("epiphany-4", "The iiij. Sunday after the Epiphany."),
    ("epiphany-5", "The fifth Sunday after the Epiphany."),
    ("septuagesima", "The Sunday called Septuagesima."),
    ("sexagesima", "The Sund. called Sexagesima."),
    ("quinquagesima", "The Sunday called Quinquagesima."),
    ("ash-wednesday", "called Ashwednesday."),
    ("lent-1", "The first Sunday in Lent."),
    ("lent-2", "The second Sunday in Lent."),
    ("lent-3", "The third Sunday in Lent"),
    ("lent-4", "The fourth Sunday in Lent"),
    ("lent-5", "The fifth Sunday in Lent"),
    ("palm-sunday", "Sunday next before Easter"),
    # "Munday" -- the page's own spelling.
    ("monday-before-easter", "Munday before Easter."),
    ("tuesday-before-easter", "Tuesday before Easter."),
    ("wednesday-before-easter", "Wednesday before Easter."),
    ("thursday-before-easter", "Thursday before Easter."),
    ("good-friday", "On good Friday."),
    ("easter-even", "Easter Even."),
]

# ---- sub-wave 10c: the second Scottish collects page ----
MARKS_B = [
    ("easter-day", "EASTER DAY."),
    ("easter-monday", "Munday in Easter week."),
    ("easter-tuesday", "Tuesday in Easter week."),
    ("easter-1", "The first Sunday after Easter."),
    ("easter-2", "The ii. Sunday after Easter."),
    ("easter-3", "The iij. Sunday after Easter."),
    ("easter-4", "The fourth Sunday after Easter."),
    ("easter-5", "The fifth Sunday after Easter."),
    ("ascension-day", "The Ascension day."),
    ("ascension-1", "Sunday after Ascension day."),
    ("whitsunday", "Whitsunday."),
    ("whit-monday", "Munday in Whitsun week."),
    ("whit-tuesday", "Tuesday in Whitsun week."),
    ("trinity-sunday", "Trinity Sunday."),
    ("trinity-1", "The first Sunday after Trinity."),
    ("trinity-2", "The second Sunday after Trinity."),
    ("trinity-3", "The iij. Sunday after Trinity."),
    ("trinity-4", "The iiij. Sunday after Trinity."),
    ("trinity-5", "The fifth Sunday after Trinity."),
    ("trinity-6", "The vj. Sunday after Trinity."),
    ("trinity-7", "The vij. Sunday after Trinity."),
    ("trinity-8", "The viij. Sunday after Trinity."),
    ("trinity-9", "The ix. Sunday after Trinity."),
    ("trinity-10", "The x. Sunday after Trinity."),
    ("trinity-11", "The xj. Sunday after Trinity."),
    ("trinity-12", "The xij. Sunday after Trinity."),
    ("trinity-13", "The xiij. Sunday after Trinity."),
    ("trinity-14", "The xiiij. Sunday after Trinity."),
    ("trinity-15", "The xv. Sunday after Trinity."),
    ("trinity-16", "The xvj. Sunday after Trinity."),
    ("trinity-17", "The xvij. Sunday after Trinity."),
    ("trinity-18", "The xviij. Sunday after Trinity."),
    ("trinity-19", "The xix. Sunday after Trinity."),
    ("trinity-20", "The xx. Sunday after Trinity."),
    ("trinity-21", "The xxj. Sunday after Trinity."),
    ("trinity-22", "The xxij. Sunday after Trinity."),
    ("trinity-23", "The xxiij. Sunday after Trinity."),
    ("trinity-24", "The xxiiij. Sunday after Trinity."),
    ("trinity-25", "The xxv. Sunday after Trinity."),
]

# ---- sub-wave 10d: the Saints' Days page ----
# Two headings wrap across lines, so the marker is the first line only.
MARKS_C = [
    ("st-andrew", "Saint Andrews day."),
    ("st-thomas", "Saint Thomas the Apostle."),
    ("conversion-st-paul", "The Conversion of S. Paul."),
    ("purification", "The Purification of Saint"),
    ("st-matthias", "Saint Matthias day."),
    ("annunciation", "Annunciation of the blessed"),
    ("st-mark", "Saint Markes day."),
    ("st-philip-st-james", "Saint Philip and James day."),
    ("st-barnabas", "Saint Barnabe Apostle."),
    ("st-john-baptist", "Saint John Baptist."),
    ("st-peter", "Saint Peters day."),
    ("st-james", "S. James the Apostle"),
    ("st-bartholomew", "S. Bartholomew the Apostle."),
    ("st-matthew", "Saint Matthew the Apostle."),
    ("st-michael", "Saint Michael and all Angels."),
    ("st-luke", "Saint Luke the Evangelist."),
    ("st-simon-st-jude", "Simon and Jude Apostles."),
    ("all-saints", "All Saints day."),
]

SPINES = [("1637_A.md", MARKS), ("1637_B.md", MARKS_B), ("1637_C.md", MARKS_C)]

# Chapter-and-verse is the normal printed form ("Rom. 13.8."). A SINGLE number
# is valid only for a single-chapter book -- Jude, Philemon, 2 and 3 John --
# which print just a verse ("Jude 1. [-8]"). Allowing a bare number for any book
# made ordinary text match and left real citations unassigned.
ONE_CHAPTER = r"(?:Jude|Philemon|Philem\.|2 ?(?:St\. ?)?John|3 ?(?:St\. ?)?John)"
CITE_LINE = re.compile(
    r"^(?:[0-9A-Za-z][A-Za-z. ]*\.? ?[0-9]+\.[0-9]+\.(?:\s*\[-[0-9:a-z]+\])?"
    r"|" + ONE_CHAPTER + r"\.? ?[0-9]+\.(?:\s*\[-[0-9:a-z]+\])?)$")
EPISTLE = re.compile(r"^>?\s*(For the Epistle|The Epistle)\s*\.?\s*$", re.I)
GOSPEL = re.compile(r"^>?\s*The Gospel\s*\.?\s*$", re.I)
COLLECT = re.compile(r"^>?\s*The Collects?\s*\.?\s*$", re.I)

# Editorial prose on the Scotland page (not Prayer-Book text).
# Only these two phrasings denote a reading shared with another day.
# A looser pattern also matched general directions ("The sixth Sunday,
# if there be so many..."), stealing a section and orphaning a real
# citation.
CROSSREF_RE = re.compile(r"(?:the same (?:that is )?appo[iy]nted|&c\.? as upon)", re.I)

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
            if mode in ("epistle", "gospel") and cell.get(mode) and CROSSREF_RE.search(bare):
                # No citation of its own: the day refers to another's reading.
                cell[mode]["crossref"] = bare
                continue
            # The Gospel-announcement directions are printed between the Epistle
            # label and its citation; they govern the Gospel.
            cell["gospel_rubrics"].append(bare)
    for slot in ("epistle", "gospel"):
        if cell[slot] and not cell[slot]["cite"] and not cell[slot].get("crossref") and cites:
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
        if not slot or not (slot.get("cite") or slot.get("crossref")):
            continue
        parts += [f"## {anchor}", ""]
        if slot.get("for_the"):
            parts += ["> For the Epistle.", ""]
        for rub in rubrics:
            parts += ["> " + rub, ""]
        parts += [canonical(slot["cite"]) if slot.get("cite")
                  else "> " + slot["crossref"], ""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(parts)).strip() + "\n"


def main():
    n = 0
    for spine, marks in SPINES:
        lines, _, _ = W.load(spine)
        for slug, block in W.segment(lines, [], marks).items():
            if slug.startswith("_skip:"):
                continue
            cell = parse(block)
            W.write_cell("1637", slug, render(cell))
            n += 1
    print(f"1637: {n} cells")


if __name__ == "__main__":
    main()
