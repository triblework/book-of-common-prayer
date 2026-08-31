#!/usr/bin/env python3
"""w10_build_american.py — the 1789/1892/1928 propers (Wave 10, sub-wave 10a).

Authoring-only; NOT published. File -> file; no liturgical text is emitted as
model output.

justus serves ONE synoptic page for the American line ("as found in the 1786
Proposed, 1789, 1892, and 1928 U. S. Books"). Its main text is the 1789 book;
what separates the three in-scope editions lives in the apparatus column. So
1789 is built from the page text and 1892/1928 are DERIVED by applying that
apparatus -- never by inference.

Every entry in DELTAS quotes the note that licenses it. Where a note states a
change but does not locate it precisely enough to apply mechanically (a moved
comma, an unanchored word), the change is recorded as an inline VERIFY rather
than guessed at: a wrong guess would fabricate a reading, which the prime
directive forbids.

The 1786 Proposed Book is out of scope; rows the apparatus marks
"Prop. (1786) Book only" are ignored.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from w10_cite import canonical  # noqa: E402
import w10_slice as W           # noqa: E402

MARKS = [
    ("advent-1", "The First Sunday in Advent"),
    ("advent-2", "The Second Sunday in Advent"),
    ("advent-3", "The Third Sunday in Advent"),
    ("advent-4", "The Fourth Sunday in Advent"),
    ("christmas-day", "The Nativity of our Lord"),
    ("christmas-1", "The Sunday after Christmas-day."),
    ("circumcision", "The Circumcision of Christ."),
    ("christmas-2", "The Second Sunday after Christmas Day."),
    ("epiphany", "The Epiphany, or the Manifestation of"),
    ("epiphany-1", "The First Sunday after the Epiphany."),
    ("epiphany-2", "The Second Sunday after the Epiphany"),
    ("epiphany-3", "The Third Sunday after the Epiphany,"),
    ("epiphany-4", "The Fourth Sunday after the Epiphany."),
    ("epiphany-5", "The Fifth Sunday after the Epiphany."),
    ("epiphany-6", "The Sixth Sunday after the Epiphany."),
    ("septuagesima", "The Sunday called Septuagesima,"),
    ("sexagesima", "The Sunday called Sexagesima,"),
    ("quinquagesima", "The Sunday called Quinquagesima,"),
    ("ash-wednesday", "Ash-Wednesday"),
    ("lent-1", "The First Sunday in Lent."),
    ("lent-2", "The Second Sunday in Lent"),
    ("lent-3", "The Third Sunday in Lent."),
    ("lent-4", "The Fourth Sunday in Lent."),
    ("lent-5", "The Fifth Sunday in Lent."),
]

# Holy Week runs onto the second synoptic page.
MARKS_B = [
    ("palm-sunday", "The Sunday next before Easter."),
    ("monday-before-easter", "Monday before Easter."),
    ("tuesday-before-easter", "Tuesday before Easter."),
    ("wednesday-before-easter", "Wednesday before Easter"),
    ("thursday-before-easter", "Thursday before Easter."),
    ("good-friday", "Good Friday"),
    ("easter-even", "Easter Even."),
    ("easter-day", "Easter-day."),
    ("easter-monday", "Monday in Easter-week."),
    ("easter-tuesday", "Tuesday in Easter-week."),
    ("easter-1", "The First Sunday after Easter."),
    ("easter-2", "The Second Sunday after Easter."),
    ("easter-3", "The Third Sunday after Easter."),
    ("easter-4", "The Fourth Sunday after Easter,"),
    ("easter-5", "The Fifth Sunday after Easter."),
]

# ---- sub-wave 10c: the third American synoptic page ----
MARKS_C = [
    ("ascension-day", "The Ascension-day."),
    ("ascension-1", "Sunday after Ascension-day."),
    ("whitsunday", "Whitsunday."),
    ("whit-monday", "Monday in Whitsun-week."),
    ("whit-tuesday", "Tuesday in Whitsun-week."),
    ("trinity-sunday", "Trinity-Sunday."),
    ("trinity-1", "The First Sunday after Trinity."),
    ("trinity-2", "The Second Sunday after Trinity."),
    ("trinity-3", "The Third Sunday after Trinity."),
    ("trinity-4", "The Fourth Sunday after Trinity."),
    ("trinity-5", "The Fifth Sunday after Trinity."),
    ("trinity-6", "The Sixth Sunday after Trinity."),
    ("trinity-7", "The Seventh Sunday after Trinity."),
    ("trinity-8", "The Eighth Sunday after Trinity."),
    ("trinity-9", "The Ninth Sunday after Trinity"),
    ("trinity-10", "The Tenth Sunday after Trinity."),
    ("trinity-11", "The Eleventh Sunday after Trinity."),
    ("trinity-12", "The Twelfth Sunday after Trinity."),
    ("trinity-13", "The Thirteenth Sunday after Trinity."),
    ("trinity-14", "The Fourteenth Sunday after Trinity."),
    ("trinity-15", "The Fifteenth Sunday after Trinity."),
    ("trinity-16", "The Sixteenth Sunday after Trinity."),
    ("trinity-17", "The Seventeenth Sunday after Trinity."),
    ("trinity-18", "The Eighteenth Sunday after Trinity."),
    ("trinity-19", "The Nineteenth Sunday after Trinity"),
    ("trinity-20", "The Twentieth Sunday after Trinity."),
    ("trinity-21", "The Twenty-first Sunday after Trinity."),
    ("trinity-22", "The Twenty-second Sunday after Trinity."),
    ("trinity-23", "The Twenty-third Sunday after Trinity."),
    ("trinity-24", "The Twenty-fourth Sunday after Trinity."),
    ("trinity-25", "The Twenty-fifth Sunday after Trinity."),
]

SPINES = [("1789_A.md", MARKS), ("1789_B.md", MARKS_B), ("1789_C.md", MARKS_C)]

# "Collect added in 1928." -- 1789 and 1892 print no collect for these days.
COLLECT_FROM_1928 = {"tuesday-before-easter", "wednesday-before-easter"}

SECOND_SERVICE = "twice celebrated on Christmas-day"
COLLECT = re.compile(r"^>\s*The Collects?\.?\s*$", re.I)
READING = re.compile(r"^(?P<label>For the Epistle|The Epistle|The Gospel)[.,]?\s+(?P<cite>\S.*)$", re.I)

# Editorial prose that appears in the flattened text stream.
APPARATUS_PREFIX = (
    "Note that punctuation", "The 1928 Book adds dates", "These two rubrics added",
    "Prop. (1786) Book only", "Heading,", "Heading ", "Rubric added",
    "This rubric", "Collects and readings for", "1786,", "1928:", "1892 only",
    "1928 only", "Readings for the 2nd Sunday", "In the 1928 Book", "The First Sunday"
    " after Christmas Day. in 1928.", "In 1928:", "* ", "† ", "Web author",
)


# An apparatus line that LABELS a per-edition replacement ("1928:",
# "1789, 1892:") is not discarded: parse() consumes it so a delta can take the
# source's own words. Only unlabelled editorial prose is dropped.
VARIANT_LABEL = re.compile(
    r"^(?:1928|1892|1789|1786)(?:,\s*(?:1928|1892|1789|1786))*\s*:", )


def is_apparatus(line):
    bare = re.sub(r"^>\s*", "", line).strip()
    if VARIANT_LABEL.match(bare):
        return False
    return any(bare.startswith(p) for p in APPARATUS_PREFIX)


def parse(block):
    """Split one occasion into its main propers and any second-service block."""
    cell = {"heading": re.sub(r"^>\s*", "", block[0]).strip().rstrip("."),
            "collect": [], "rubrics": [], "epistle": None, "gospel": None,
            "second": None, "variants": []}
    scope, mode = cell, None
    variant_open = False
    for raw in block[1:]:
        line = raw.strip()
        if not line:
            continue
        bare = re.sub(r"^>\s*", "", line).strip()
        # The apparatus prints an edition's replacement text in full, prefixed
        # with the book(s) it belongs to ("1928: The Collect. ..."). Keep those
        # so a delta can take the SOURCE's words.
        m_var = re.match(r"^(?P<eds>(?:1928|1892|1789|1786)(?:,\s*(?:1928|1892|1789|1786))*)\s*:\s*(?P<rest>.*)$", line)
        if m_var:
            # hc_clean can split the prefix ("1928:") from the body it labels,
            # so the body may arrive on the following lines.
            cell["variants"].append([m_var.group("eds"), m_var.group("rest").strip()])
            variant_open = True
            continue
        if variant_open:
            # The label is followed by the variant's own 'The Collect.' heading
            # (or a reading label) and then its text. Consume the heading and
            # take ONE body paragraph, so the variant's words never leak into
            # the base cell's collect.
            if COLLECT.match(line):
                continue
            mr_v = READING.match(bare)
            if mr_v:
                cell["variants"][-1][1] = bare
                variant_open = False
                continue
            if line.startswith(">"):
                continue
            cell["variants"][-1][1] = (cell["variants"][-1][1] + " " + bare).strip()
            variant_open = False
            continue
        if is_apparatus(line):
            continue
        if SECOND_SERVICE in bare:
            cell["second"] = {"collect": [], "rubrics": [bare],
                              "epistle": None, "gospel": None}
            scope, mode = cell["second"], None
            continue
        if COLLECT.match(line):
            mode = "collect"
            continue
        m = READING.match(bare)
        if m:
            slot = "gospel" if m.group("label").lower().startswith("the gospel") else "epistle"
            # The apparatus prints an edition's VARIANT reading after the base
            # one ("1928: The Gospel. St. Mark i. 1."), and flattening can strip
            # the "1928:" prefix onto its own line. The first reading in an
            # occasion is the page's base (1789) text; later ones are variants
            # and are supplied explicitly by DELTAS, so first wins.
            if not scope.get(slot):
                scope[slot] = {"cite": m.group("cite").strip(),
                               "for_the": m.group("label").lower().startswith("for the")}
            mode = slot
            continue
        if line.startswith(">"):
            scope["rubrics"].append(bare)
            continue
        if mode == "collect":
            scope["collect"].append(bare)
    return cell


# ---------------------------------------------------------------------------
# Per-edition deltas, each quoting the apparatus note that licenses it.
# op: title | epistle | gospel | second | verify
# ---------------------------------------------------------------------------
DELTAS = {
    "1892": [
        ("easter-day", "second", True,
         "This rubric, the Collect, and Readings for a second service, were all "
         "added in 1892."),
        ("trinity-25", "title", "The Sunday next before Advent",
         "Title changed to The Sunday next before Advent in 1892."),
        ("christmas-day", "second", True,
         "This rubric, and the Collect, Epistle, and Gospel for a second service, "
         "were all added in the 1892 Book"),
        ("advent-1", "verify", None,
         '* "unto" in 1892 only — the source marks the variant with an asterisk in '
         'the rubric but does not give the surrounding wording, so the 1789 reading '
         "is kept here."),
        ("advent-2", "verify", None,
         "* Comma was before the word 'ever' until 1892."),
        ("christmas-day", "verify", None,
         "* Virgin until 1832 † Holy from 1892"),
    ],
    "1928": [
        ("christmas-day", "second", True,
         "Second service inherited from 1892."),
        ("christmas-1", "title", "The First Sunday after Christmas Day",
         "The First Sunday after Christmas Day. in 1928."),
        ("circumcision", "epistle", "Philippians ii. 9.",
         "1928: The Epistle. Philippians ii. 9."),
        ("circumcision", "verify", None,
         "the apparatus labels the earlier Epistle \"1786, 1786, 1892\" -- 1786 "
         "twice and no 1789 -- evidently a typo for \"1786, 1789, 1892\"; read "
         "as including 1789, whose base text it is."),
        ("epiphany-2", "gospel", "St. Mark i. 1.",
         "1928: The Gospel. St. Mark i. 1."),
        ("epiphany-3", "gospel", "@epiphany-2",
         "In the 1928 Book, the Gospel Readings for the second and third Sundays "
         "after the Epiphany are shifted to the third and fourth Sundays, "
         "respectively."),
        ("epiphany-4", "gospel", "@epiphany-3",
         "In the 1928 Book, the Gospel Readings for the second and third Sundays "
         "after the Epiphany are shifted to the third and fourth Sundays, "
         "respectively."),
        ("epiphany-4", "verify", None,
         "* condemnation in 1928 — and the source does not say what becomes of the "
         "1789 Gospel this shift displaces."),
        ("advent-3", "verify", None, "* against myself in 1928"),
        ("advent-4", "verify", None, "* through Jesus Christ our Lord in 1928"),
        ("epiphany", "verify", None, "This rubric dropped in 1928."),
        # ---- sub-wave 10c ----
        ("ascension-day", "gospel", "St. Luke xxiv. 49.",
         "1928: The Gospel. St. Luke xxiv. 49."),
        ("easter-monday", "collect_variant", "1928",
         "1928: The Collect. <replaced; text taken from the apparatus>"),
        ("easter-tuesday", "collect_variant", "1928",
         "1928: The Collect. <replaced; text taken from the apparatus>"),
        ("whit-monday", "collect_variant", "1928",
         "1928: The Collect. <replaced; text taken from the apparatus>"),
        ("whit-tuesday", "collect_variant", "1928",
         "1928: The Collect. <replaced; text taken from the apparatus>"),
        ("trinity-9", "gospel", "St. Luke xv. 11.",
         "1928: The Gospel. St. Luke xv. 11."),
        ("whitsunday", "verify", None,
         "WHITSUNTIDE. Pentecost, commonly called Whitsunday. in 1928 — and "
         "\"Rubric and Readings for a second service added in 1928\"; the second "
         "service's readings are not separately printed on the page, so they are "
         "not represented here."),
        ("trinity-25", "title", "The Sunday next before Advent",
         "Title changed to The Sunday next before Advent in 1892."),
        ("christmas-2", "verify", None,
         "Readings for the 2nd Sunday after Christmas added in 1928 — the source "
         "prints one set of readings for this day without distinguishing them, so "
         "they are carried at 1928 and omitted at 1789/1892."),
    ],
}


# The apparatus labels the Circumcision Epistle "1786, 1786, 1892" -- 1786 twice
# and no 1789 -- which is evidently a typo for "1786, 1789, 1892": the text it
# labels is the base 1789 reading, and 1928 alone is given a replacement. The
# affected cell carries a VERIFY recording this.
LABEL_TYPOS = {"1786, 1786, 1892": "1786, 1789, 1892"}


def variant_body(variants, edition):
    """The apparatus text belonging to one edition.

    The apparatus labels a replacement with the books it belongs to
    ("1928:", "1789, 1892:") and then quotes the text. Returns the quoted words
    with the leading label stripped, so the SOURCE supplies every word.
    """
    for eds, body in variants:
        eds = LABEL_TYPOS.get(eds.strip(), eds)
        if edition not in [e.strip() for e in eds.split(",")]:
            continue
        body = re.sub(r"^The Collects?\.\s*", "", body).strip()
        if body:
            return body
    return None


def render(cell, verifies):
    parts = [f"# {cell['heading']}", ""]
    for note in verifies:
        parts += [f"<!-- VERIFY: '{cell['heading']}' — {note} -->", ""]

    def section(anchor, slot):
        if not slot or not slot.get("cite"):
            return
        parts.extend([f"## {anchor}", ""])
        if slot.get("for_the"):
            parts.extend(["> For the Epistle.", ""])
        parts.extend([canonical(slot["cite"]), ""])

    if cell["collect"]:
        parts += ["## The Collect", ""]
        for para in cell["collect"]:
            parts += [W.strip_brackets(para, False), ""]
    for rub in cell["rubrics"]:
        parts += ["> " + W.strip_brackets(rub, False), ""]
    section("The Epistle", cell["epistle"])
    section("The Gospel", cell["gospel"])

    sec = cell.get("second")
    if sec:
        if sec["collect"]:
            parts += ["## The Collect (Second Communion)", ""]
            for para in sec["collect"]:
                parts += [W.strip_brackets(para, False), ""]
        for rub in sec["rubrics"]:
            parts += ["> " + W.strip_brackets(rub, False), ""]
        section("The Epistle (Second Communion)", sec["epistle"])
        section("The Gospel (Second Communion)", sec["gospel"])
    return re.sub(r"\n{3,}", "\n\n", "\n".join(parts)).strip() + "\n"


def main():
    base = {}
    for spine, marks in SPINES:
        lines, _ = W.load(spine)
        lines = [ln for ln in lines if not is_apparatus(ln)]
        for slug, block in W.segment(lines, [], marks).items():
            if not slug.startswith("_skip:"):
                base[slug] = parse(block)

    for edition in ("1789", "1892", "1928"):
        applied = []
        for slug, cell in sorted(base.items()):
            cell = {k: (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v)
                    for k, v in cell.items()}
            verifies = []
            keep_second = False
            for ed in ("1892", "1928"):
                if edition == "1789" or (edition == "1892" and ed == "1928"):
                    continue
                for target, op, value, note in DELTAS[ed]:
                    if target != slug:
                        continue
                    if op == "verify":
                        verifies.append(note)
                    elif op == "title":
                        cell["heading"] = value
                        applied.append(f"{slug}:title")
                    elif op in ("epistle", "gospel"):
                        if isinstance(value, str) and value.startswith("@"):
                            # "1928 shifts the Gospel from Sunday X to Sunday Y":
                            # the reading being moved is the PRE-1928 one, which
                            # may live in a labelled variant rather than the base.
                            src = base[value[1:]]
                            moved = src.get(op)
                            if not (moved and moved.get("cite")):
                                prior = variant_body(src["variants"], "1892")
                                mr_p = READING.match(prior) if prior else None
                                moved = ({"cite": mr_p.group("cite").strip(),
                                          "for_the": False} if mr_p else None)
                            cell[op] = dict(moved) if moved else None
                        else:
                            cell[op] = {"cite": value, "for_the": False}
                        applied.append(f"{slug}:{op}")
                    elif op == "second":
                        keep_second = True
                    elif op == "collect_variant":
                        body = variant_body(base[slug]["variants"], value)
                        if not body:
                            raise SystemExit(
                                f"  !! {slug}: no {value!r} variant in the apparatus")
                        cell["collect"] = [body]
                        applied.append(f"{slug}:collect({value})")
            if not keep_second:
                cell["second"] = None
            elif cell["second"]:
                applied.append(f"{slug}:second")
            # Where the page labels the BASE collect with the books it belongs
            # to ("1789, 1892:"), the cell's own collect is empty for those
            # editions -- the words live in the labelled variant. Take them.
            own = variant_body(base[slug]["variants"], edition)
            if own:
                mr_own = READING.match(own)
                if mr_own:
                    # The page labels the base READING with its books too
                    # ("1786, 1789, 1892: The Gospel. St. Luke xvi. 1.").
                    slot = ("gospel" if mr_own.group("label").lower()
                            .startswith("the gospel") else "epistle")
                    if not cell.get(slot) or not cell[slot].get("cite"):
                        cell[slot] = {"cite": mr_own.group("cite").strip(),
                                      "for_the": mr_own.group("label").lower()
                                      .startswith("for the")}
                        applied.append(f"{slug}:{slot}({edition})")
                elif not cell["collect"]:
                    cell["collect"] = [own]
                    applied.append(f"{slug}:collect({edition})")
            # 1789/1892 have no readings for the Second Sunday after Christmas.
            if slug == "christmas-2" and edition in ("1789", "1892"):
                cell["epistle"] = cell["gospel"] = None
            # "Collect added in 1928." -- Tuesday/Wednesday before Easter print
            # no collect in the earlier American books.
            if slug in COLLECT_FROM_1928 and edition in ("1789", "1892"):
                cell["collect"] = []
            W.write_cell(edition, slug, render(cell, verifies))
        print(f"  {edition}: {len(base)} cells, deltas applied: "
              f"{', '.join(sorted(set(applied))) or 'none (base text)'}")


if __name__ == "__main__":
    main()
