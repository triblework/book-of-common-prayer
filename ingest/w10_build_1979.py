#!/usr/bin/env python3
"""w10_build_1979.py — the 1979 propers (Wave 10, sub-wave 10a).

Authoring-only; NOT published. Text flows e-text -> script -> file.

Driven by ingest/WAVE10_1979_CROSSWALK.md. Per Decision C:
  * Traditional collect  -> '## The Collect'               (carries v1928->v1979)
  * Contemporary collect -> '## The Collect (Contemporary)' (alongside, so its
    larger rewrite does not corrupt the lineage diff)
  * NO Epistle/Gospel anchors: 1979 appoints three reading sets per Sunday
    (the three-year lectionary), structurally incommensurable with the single
    citation the historic books print. Deferred to Wave 12.

E-text dropouts are flagged inline and never reconstructed.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w10_1979                 # noqa: E402
import w10_slice as W           # noqa: E402

# slug -> the 1979 occasion heading in bcpcolct.txt
MAP = [
    ("advent-1", "First Sunday of Advent"),
    ("advent-2", "Second Sunday of Advent"),
    ("advent-3", "Third Sunday of Advent"),
    ("advent-4", "Fourth Sunday of Advent"),
    ("christmas-day", "The Nativity of Our Lord:  Christmas Day"),
    ("christmas-1", "First Sunday after Christmas Day"),
    ("christmas-2", "Second Sunday after Christmas Day"),
    ("circumcision", "The Holy Name"),
    ("epiphany", "The Epiphany"),
    ("epiphany-1", "First Sunday after the Epiphany:  The Baptism of our Lord"),
    ("epiphany-2", "Second Sunday after the Epiphany"),
    ("epiphany-3", "Third Sunday after the Epiphany"),
    ("epiphany-4", "Fourth Sunday after the Epiphany"),
    ("epiphany-5", "Fifth Sunday after the Epiphany"),
    ("epiphany-6", "Sixth Sunday after the Epiphany"),
    ("epiphany-7", "Seventh Sunday after the Epiphany"),
    ("epiphany-8", "Eighth Sunday after the Epiphany"),
    ("epiphany-last", "Last Sunday after the Epiphany"),
    # ---- sub-wave 10b ----
    # 1979 keeps every 10b day but renames several; same day -> same slug, and
    # the rename is a heading diff. It DROPS the pre-Lent "Gesima" Sundays
    # entirely (septuagesima/sexagesima/quinquagesima appear nowhere in the
    # book), so those are `absent:` at 1979 rather than force-mapped.
    ("ash-wednesday", "Ash Wednesday"),
    ("lent-1", "First Sunday in Lent"),
    ("lent-2", "Second Sunday in Lent"),
    ("lent-3", "Third Sunday in Lent"),
    ("lent-4", "Fourth Sunday in Lent"),
    ("lent-5", "Fifth Sunday in Lent"),
    ("palm-sunday", "Sunday of the Passion:  Palm Sunday"),
    ("monday-before-easter", "Monday in Holy Week"),
    ("tuesday-before-easter", "Tuesday in Holy Week"),
    ("wednesday-before-easter", "Wednesday in Holy Week"),
    ("thursday-before-easter", "Maundy Thursday"),
    ("good-friday", "Good Friday"),
    ("easter-even", "Holy Saturday"),
]

# Dropped by 1979 -> `absent:` in editions.yaml, never mapped onto a 1979 collect.
DROPPED_1979 = ["septuagesima", "sexagesima", "quinquagesima"]

DEFECT = ("<!-- VERIFY: '{occ}' — the {which}-language collect for this day is "
          "absent from the public-domain e-text (a dropout in its 1993 keying, "
          "not a feature of the book); not reconstructed. -->")

READINGS_NOTE = (
    "<!-- VERIFY: '{occ}' — 1979 appoints three reading sets for this day under "
    "the three-year lectionary, which the single Epistle/Gospel slot cannot "
    "represent; deferred to the lectionary-tables wave. -->")


def title_of(name):
    return " ".join(name.replace("  ", " ").split())


def main():
    trad = w10_1979.load("Traditional")
    contemp = w10_1979.load("Contemporary")
    n = 0
    for slug, occ in MAP:
        t = trad.get(occ)
        c = contemp.get(occ)
        if not t and not c:
            print(f"  !! {slug}: {occ!r} in neither set")
            continue
        title = title_of(occ)
        parts = [f"# {title}", ""]
        if not t:
            parts += [DEFECT.format(occ=title, which="traditional"), ""]
        if not c:
            parts += [DEFECT.format(occ=title, which="contemporary"), ""]
        parts += [READINGS_NOTE.format(occ=title), ""]
        for anchor, data in (("The Collect", t),
                             ("The Collect (Contemporary)", c)):
            if not data or not data["collects"]:
                continue
            parts += [f"## {anchor}", ""]
            for i, body in enumerate(data["collects"]):
                if i:
                    parts += ["> Or this.", ""]
                parts += [body, ""]
        text = "\n".join(parts)
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        W.write_cell("1979", slug, text.strip() + "\n")
        flags = []
        if not t:
            flags.append("no-trad")
        if not c:
            flags.append("no-contemp")
        print(f"  {slug:<15} trad={len(t['collects']) if t else 0} "
              f"contemp={len(c['collects']) if c else 0} {' '.join(flags)}")
        n += 1
    print(f"1979: {n} cells")


if __name__ == "__main__":
    main()
