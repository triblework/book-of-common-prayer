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
    # ---- sub-wave 10c: days that correspond ----
    # 1979 counts Easter Day itself as the First Sunday of Easter, so its
    # ordinals sit one ahead of the historic "Sundays AFTER Easter" -- the same
    # DAYS under a different reckoning.
    ("easter-day", "Easter Day"),
    ("easter-monday", "Monday in Easter Week"),
    ("easter-tuesday", "Tuesday in Easter Week"),
    ("easter-1", "Second Sunday of Easter"),
    ("easter-2", "Third Sunday of Easter"),
    ("easter-3", "Fourth Sunday of Easter"),
    ("easter-4", "Fifth Sunday of Easter"),
    ("easter-5", "Sixth Sunday of Easter"),
    ("ascension-day", "Ascension Day"),
    ("ascension-1", "Seventh Sunday of Easter:  The Sunday after Ascension Day"),
    ("whitsunday", "The Day of Pentecost:  Whitsunday"),
    ("trinity-sunday", "First Sunday after Pentecost:  Trinity Sunday"),
    # 1979-only days in Easter Week: no historic ancestor -> their own slugs.
    ("easter-wednesday", "Wednesday in Easter Week"),
    ("easter-thursday", "Thursday in Easter Week"),
    ("easter-friday", "Friday in Easter Week"),
    ("easter-saturday", "Saturday in Easter Week"),
    # ---- 10c: collect LINEAGE (maintainer decision (a), 2026-08-31) ----
    # Where a Sunday after Trinity's collect survives in 1979 at a PROPER, the
    # 1979 collect is placed at the historic slug so the modernization diff
    # reads. Only high full-text agreement counts as descent here, since no day
    # corresponds; see WAVE10_1979_CROSSWALK.md.
    # NOTE: this attaches a collect to a day 1979 does not observe. Recorded as
    # requiring revision.
    ("trinity-4", "Proper 12"),
    ("trinity-7", "Proper 17"),
    ("trinity-11", "Proper 21"),
    ("trinity-12", "Proper 22"),
    ("trinity-13", "Proper 26"),
    ("trinity-17", "Proper 23"),
    ("trinity-19", "Proper 19"),
    ("trinity-20", "Proper 2"),
    # ---- sub-wave 10d: the Holy Days ----
    # Same feast on the same date -> same slug; where 1979 renames the day, that
    # is a heading diff on the same file.
    ("st-andrew", "Saint Andrew"),
    ("st-thomas", "Saint Thomas"),
    ("st-stephen", "Saint Stephen"),
    ("st-john-evangelist", "Saint John"),
    ("holy-innocents", "The Holy Innocents"),
    ("conversion-st-paul", "Conversion of Saint Paul"),
    ("purification", "The Presentation"),          # 2 February, renamed
    ("st-matthias", "Saint Matthias"),
    ("annunciation", "The Annunciation"),
    ("st-mark", "Saint Mark"),
    ("st-philip-st-james", "Saint Philip and Saint James"),
    ("st-barnabas", "Saint Barnabas"),
    ("st-john-baptist", "The Nativity of Saint John the Baptist"),
    ("st-peter", "Saint Peter and Saint Paul"),    # 29 June; 1979 adds Paul
    ("st-mary-magdalene", "Saint Mary Magdalene"), # 1549 only, then restored 1979
    ("st-james", "Saint James"),
    ("transfiguration", "The Transfiguration"),
    ("st-bartholomew", "Saint Bartholomew"),
    ("st-matthew", "Saint Matthew"),
    ("st-michael", "Saint Michael and All Angels"),
    ("st-luke", "Saint Luke"),
    ("st-simon-st-jude", "Saint Simon and Saint Jude"),
    ("all-saints", "All Saint's Day"),
    # 1979 Holy Days with no historic counterpart -> their own slugs.
    ("st-joseph", "Saint Joseph"),
    ("the-visitation", "The Visitation"),
    ("st-mary-the-virgin", "Saint Mary the Virgin"),
    ("st-james-of-jerusalem", "Saint James of Jerusalem"),
    ("independence-day", "Independence Day"),
    ("thanksgiving-day", "Thanksgiving Day"),
]

# Absent at 1979: the day is not observed and no confident descendant is placed.
# trinity-1 and trinity-6 DO have confident descendants (1979's Epiphany 6 and
# Easter 6), but those 1979 occasions are already carried at their own day slugs;
# repeating them here would duplicate one text at two slugs.
DROPPED_10C = ["whit-monday", "whit-tuesday",
               "trinity-1", "trinity-2", "trinity-3", "trinity-5", "trinity-6",
               "trinity-8", "trinity-9", "trinity-10", "trinity-14",
               "trinity-15", "trinity-16", "trinity-18", "trinity-21",
               "trinity-22", "trinity-23", "trinity-24", "trinity-25"]

# Dropped by 1979 -> `absent:` in editions.yaml, never mapped onto a 1979 collect.
DROPPED_1979 = ["septuagesima", "sexagesima", "quinquagesima"]

DEFECT = ("<!-- VERIFY: '{occ}' — the {which}-language collect for this day is "
          "absent from the public-domain e-text (a dropout in its 1993 keying, "
          "not a feature of the book); not reconstructed. -->")

LINEAGE_NOTE = (
    "<!-- VERIFY: '{occ}' — placed at `{slug}` by COLLECT LINEAGE, not by day: "
    "1979 replaces the Sundays after Trinity with calendar-dated Propers, so it "
    "does not observe this day. See ingest/WAVE10_1979_CROSSWALK.md; this "
    "representation is flagged for revision. -->")

TRUNCATED_NOTE = (
    "<!-- VERIFY: '{occ}' — the collect under `{which}` breaks off mid-sentence "
    "in the public-domain e-text (a dropout in its 1993 keying, not a feature of "
    "the book); carried as the source has it and NOT reconstructed. -->")

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
        if slug.startswith("trinity-") and occ.startswith("Proper"):
            parts += [LINEAGE_NOTE.format(occ=title, slug=slug), ""]
        for anchor, data in (("The Collect", t),
                             ("The Collect (Contemporary)", c)):
            if not data or not data["collects"]:
                continue
            parts += [f"## {anchor}", ""]
            if any(w10_1979.looks_truncated(b) for b in data["collects"]):
                parts += [TRUNCATED_NOTE.format(occ=title, which=anchor), ""]
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
