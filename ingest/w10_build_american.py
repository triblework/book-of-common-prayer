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
    ("_skip:septuagesima", "The Sunday called Septuagesima,"),
]

SECOND_SERVICE = "twice celebrated on Christmas-day"
COLLECT = re.compile(r"^>\s*The Collect\.?\s*$", re.I)
READING = re.compile(r"^(?P<label>For the Epistle|The Epistle|The Gospel)[.,]?\s+(?P<cite>\S.*)$", re.I)

# Editorial prose that appears in the flattened text stream.
APPARATUS_PREFIX = (
    "Note that punctuation", "The 1928 Book adds dates", "These two rubrics added",
    "Prop. (1786) Book only", "Heading,", "Heading ", "Rubric added",
    "This rubric", "Collects and readings for", "1786,", "1928:", "1892 only",
    "1928 only", "Readings for the 2nd Sunday", "In the 1928 Book", "The First Sunday"
    " after Christmas Day. in 1928.", "In 1928:", "* ", "† ", "Web author",
)


def is_apparatus(line):
    bare = re.sub(r"^>\s*", "", line).strip()
    return any(bare.startswith(p) for p in APPARATUS_PREFIX)


def parse(block):
    """Split one occasion into its main propers and any second-service block."""
    cell = {"heading": re.sub(r"^>\s*", "", block[0]).strip().rstrip("."),
            "collect": [], "rubrics": [], "epistle": None, "gospel": None,
            "second": None}
    scope, mode = cell, None
    for raw in block[1:]:
        line = raw.strip()
        if not line or is_apparatus(line):
            continue
        bare = re.sub(r"^>\s*", "", line).strip()
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
        ("christmas-2", "verify", None,
         "Readings for the 2nd Sunday after Christmas added in 1928 — the source "
         "prints one set of readings for this day without distinguishing them, so "
         "they are carried at 1928 and omitted at 1789/1892."),
    ],
}


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
    lines, _ = W.load("1789_A.md")
    lines = [ln for ln in lines if not is_apparatus(ln)]
    segs = W.segment(lines, [], MARKS)
    base = {}
    for slug, block in segs.items():
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
                            src = base[value[1:]]
                            cell[op] = dict(src[op]) if src.get(op) else None
                        else:
                            cell[op] = {"cite": value, "for_the": False}
                        applied.append(f"{slug}:{op}")
                    elif op == "second":
                        keep_second = True
            if not keep_second:
                cell["second"] = None
            elif cell["second"]:
                applied.append(f"{slug}:second")
            # 1789/1892 have no readings for the Second Sunday after Christmas.
            if slug == "christmas-2" and edition in ("1789", "1892"):
                cell["epistle"] = cell["gospel"] = None
            W.write_cell(edition, slug, render(cell, verifies))
        print(f"  {edition}: {len(base)} cells, deltas applied: "
              f"{', '.join(sorted(set(applied))) or 'none (base text)'}")


if __name__ == "__main__":
    main()
