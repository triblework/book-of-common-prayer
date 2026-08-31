#!/usr/bin/env python3
"""w10_build_english.py — build the 1549/1552/1559 propers (Wave 10, sub-wave 10a).

Authoring-only; NOT published. File -> file: the collect text flows
spine -> script -> editions/<year>/collects-epistles-gospels/<slug>.md and is
never emitted as model output.

The three books share one annotated justus page. Their differences come only
from that page's own apparatus, and are applied here explicitly:

  1552  drops the Introits and the 1549-only proper Psalms/Lessons.
  1559  as 1552, plus: "'Amen' added at the end of this and each subsequent
        collect in the 1559 edition only" (applied CONDITIONALLY -- most
        collects already end in Amen, so appending blindly would fabricate a
        reading), plus the occasion-title expansions the page brackets and
        footnotes as "added in late 1500's".

The "late 1500's" footnote does not name a book, so every title it affects
carries an inline VERIFY.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w10_slice as W

SEASONS = [
    ("1549_advent.md", "notes_Advent.txt", [
        ("advent-1", "> The fyrst Sonday in Advente."),
        ("advent-2", "> The second sunday."),
        ("advent-3", "> The thirde sonday"),
        ("advent-4", "> The fourth sonday"),
    ]),
    ("1549_Xmas.md", "notes_Xmas.txt", [
        ("christmas-day", "> Proper Psalmes and lessons on Christmas day."),
        ("st-stephen", "> St. Stephin's Day."),
        ("st-john-evangelist", "Sayncte John Evangelistes"),
        ("holy-innocents", "The Innocentes"),
        ("christmas-1", "The Sunday after"),
        ("circumcision", "The Circumcision"),
    ]),
    ("1549_Epiphany.md", "notes_Epiphany.txt", [
        ("epiphany", "> The Epiphanie."),
        ("epiphany-1", "> The firste Sonday after the Epiphanye."),
        ("epiphany-2", "> The second Sonday."),
        ("epiphany-3", "> The thirde Soondaye"),
        ("epiphany-4", "> The iiii Sonday"),
        ("epiphany-5", "> The v. Sonday"),
        ("septuagesima", "> The sonday called Septuagesima."),
        ("sexagesima", "> The Sunday called Sexagesima."),
        ("quinquagesima", "> The Sonday called Quinquagesima."),
    ]),
    # ---- sub-wave 10b ----
    ("1549_Lent.md", "notes_Lent.txt", [
        ("ash-wednesday", "> The fyrst day of Lent"),
        ("lent-1", "> The first Sonday in Lent."),
        ("lent-2", "> The seconde Sonday"),
        ("lent-3", "> The iii. Sonday"),
        ("lent-4", "> The iiii Sonday"),
        ("lent-5", "> The v. Sonday"),
        ("palm-sunday", "> The Sonday next before Easter."),
    ]),
    ("1549_HolyWeek.md", "notes_HolyWeek.txt", [
        ("monday-before-easter", "> Monday before Easter."),
        ("tuesday-before-easter", "> Tewesday before Easter."),
        ("wednesday-before-easter", "> Wednesday before Easter."),
        ("thursday-before-easter", "> Thursday before Easter."),
        ("good-friday", "> On good Fryday."),
        ("easter-even", "> Easter Even."),
    ]),
    # ---- sub-wave 10c ----
    ("1549_EasterWeek.md", "notes_EasterWeek.txt", [
        ("easter-day", "> Easter Daye."),
        ("easter-monday", "> Monedaye in Easter weke."),
        ("easter-tuesday", "> Tuisdaye in Easter weke."),
    ]),
    ("1549_EasterSeason.md", "notes_EasterSeason.txt", [
        ("easter-1", "> The first Sondaie after Easter."),
        ("easter-2", "> The second Sondaie after Easter."),
        ("easter-3", "> The iii Sondaye"),
        ("easter-4", "> The iiii Sondaye"),
        ("easter-5", "> The v. Sondaie"),
    ]),
    ("1549_AscensionWhitsuntide.md", "notes_AscensionWhitsuntide.txt", [
        ("ascension-day", "> The Assencion Day."),
        ("ascension-1", "> The Sonday after the Ascencion."),
        ("whitsunday", "> Whit-Sunday."),
        ("whit-monday", "> Monday in whitsonweke."),
        ("whit-tuesday", "> Tuesday."),
    ]),
    ("1549_TrinityA.md", "notes_TrinityA.txt", [
        ("trinity-sunday", "> Trinitie Sonday."),
        ("trinity-1", "> The first Sonday after Trinitie Sonday."),
        ("trinity-2", "> The second Sondaye"),
        ("trinity-3", "> The third sonday"),
        ("trinity-4", "> The fourth Sondaye"),
        ("trinity-5", "> The v Sunday"),
        ("trinity-6", "> The vi Sondaie"),
        ("trinity-7", "> The vii Sonday"),
        ("trinity-8", "> The eight Sonday"),
    ]),
    ("1549_TrinityB.md", "notes_TrinityB.txt", [
        ("trinity-9", "> The ix Sonday."),
        ("trinity-10", "> The x Sonday."),
        ("trinity-11", "> The xi Sonday."),
        ("trinity-12", "> The xii Sunday."),
        ("trinity-13", "> The xiii Sonday."),
        ("trinity-14", "> The xiiii Sonday."),
        ("trinity-15", "> The xv Sonday."),
        ("trinity-16", "> The xvi Sonday."),
    ]),
    ("1549_TrinityC.md", "notes_TrinityC.txt", [
        ("trinity-17", "> The xvii Sondaye."),
        ("trinity-18", "> The xviii Sondaye."),
        ("trinity-19", "> The xix Sundaie."),
        ("trinity-20", "> The xx Sondaie."),
        ("trinity-21", "> The xxi Sondaie."),
        ("trinity-22", "> The xxii Sondaye."),
        ("trinity-23", "> The xxiii Sondaye."),
        ("trinity-24", "> The xxiiii Sondaye."),
        ("trinity-25", "> The xxv Sondaye."),
    ]),
    # ---- sub-wave 10d: the Saints' Days ----
    # Markers omit the "> " prefix: not every heading on these pages carries the
    # pilcrow hc_clean converts (St. Bartholomew's does not).
    ("1549_SaintsA.md", "notes_SaintsA.txt", [
        ("st-andrew", "Sainct Andrewes Daye."),
        ("st-thomas", "Saynct Thomas the Apostle."),
        ("conversion-st-paul", "The conversion of sainct Paule."),
        ("purification", "The Purificacion of Saint Mary the Virgin."),
        ("st-matthias", "Saint Mathies' daie."),
        ("annunciation", "The Annunciacion of the virgin Marie."),
        ("st-mark", "Sainct Markes day."),
        ("st-philip-st-james", "Sainct Philip and James."),
        ("st-barnabas", "Saint Barnabe Apostle."),
        ("st-john-baptist", "Saint John Baptist."),
    ]),
    ("1549_SaintsB.md", "notes_SaintsB.txt", [
        ("st-peter", "Saint Peter's Day."),
        ("st-mary-magdalene", "Sainct Mary Magdalene."),
        ("st-james", "Sainct James the Apostle."),
        ("st-bartholomew", "Sainct Bartholomewe"),
        ("st-matthew", "Sayncte Matthewe"),
        ("st-michael", "Saynte Michaell and all Angels."),
        ("st-luke", "Sainct Luke evangelist."),
        ("st-simon-st-jude", "Symon and Jude Apostles."),
        ("all-saints", "All Saynctes."),
    ]),
]

# The page prints Christmas Day's block under its proper-lessons rubric rather
# than a bare occasion title; the index page and every later book title it
# "Christmas Day".
TITLE_OVERRIDE = {"christmas-day": "Christmas Day"}

# Titles whose expansion the page footnotes only as "added in late 1500's".
LATE_1500S = {"advent-3", "advent-4", "epiphany-3", "epiphany-4", "epiphany-5",
              "ash-wednesday", "lent-2", "lent-3", "lent-4", "lent-5",
              "easter-3", "easter-4", "easter-5", "trinity-2", "trinity-3",
              "trinity-4", "trinity-5", "trinity-6", "trinity-7", "trinity-8",
              "st-matthew", "st-bartholomew"}

VERIFY_LATE = ("<!-- VERIFY: '{title}' — the source brackets this title expansion "
               "and footnotes it only as \"added in late 1500's\", without naming "
               "a book; represented here as entering at 1559. -->")


def build():
    written = {}
    for spine, notes_file, marks in SEASONS:
        # Source the TEXT COLUMN directly. The apparatus quotes the text it
        # discusses -- whole collects, whole readings -- so no content-based
        # filter can tell a genuine line from a quoted one; using the column
        # removes the entire class of silent loss. (w10_textspine.py)
        text_spine = "text_" + spine[len("1549_"):]
        lines, _, _ = W.load(text_spine)
        segs = W.segment(lines, [], marks)
        for slug, block in segs.items():
            if slug.startswith("_skip:"):
                continue
            for edition in ("1549", "1552", "1559"):
                # The justus index marks St. Mary Magdalene "1549 only": the
                # feast is dropped at 1552. Authoring it for the later books
                # would assert a day they do not keep.
                if slug == "st-mary-magdalene" and edition != "1549":
                    continue
                want_introit = edition == "1549"
                keep_bracket = edition == "1559"
                cell = W.parse_cell(block, want_introit=want_introit)
                title = TITLE_OVERRIDE.get(
                    slug, W.strip_brackets(cell["heading"], keep_bracket))
                title = title.strip().rstrip(".")
                if edition == "1559" and slug != "advent-1":
                    cell["collect"] = [W.add_amen(p) for p in cell["collect"]]
                    if cell.get("second", {}).get("collect"):
                        cell["second"]["collect"] = [
                            W.add_amen(p) for p in cell["second"]["collect"]]
                text = W.render(cell, title, edition, want_introit, keep_bracket)
                if slug in LATE_1500S:
                    verify = VERIFY_LATE.format(title=title)
                    text = text.replace(f"# {title}\n",
                                        f"# {title}\n\n{verify}\n", 1)
                path = W.write_cell(edition, slug, text)
                written.setdefault(edition, []).append(os.path.basename(path))
    for edition, files in sorted(written.items()):
        print(f"  {edition}: {len(files)} cells -> {', '.join(sorted(files))}")


if __name__ == "__main__":
    build()
