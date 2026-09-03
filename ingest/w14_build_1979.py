#!/usr/bin/env python3
"""w14_build_1979.py — write the two 1979 lectionary cells (Wave 14).

Authoring-only; NOT published. source -> script -> file: no liturgical body is
ever emitted as model tokens (HANDOFF §6). Pays the Wave-10 Decision-C(4) debt:
1979's reading sets had no representation in the repo because three reading sets
per day cannot fit the single-citation slot the historic propers use.

Both files are `tables/` cells present ONLY at 1979 (GUIDE ruling C): they are
keyed by liturgical week, not by civil calendar date, so they are structurally
incommensurable with the historic Kalendar and must not share its path.

Emits a verify manifest to ingest/wave14_1979_verifies.json for
gen_wave14_provenance.py, so every inline <!-- VERIFY --> gets its provenance
row and SOURCES.md row without hand-transcription.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "tools"))

import w14_1979

OUT = os.path.join(WT, "editions", "1979", "tables")
VERIFY_JSON = os.path.join(HERE, "wave14_1979_verifies.json")

# A first field that begins with a digit or "Canticle" is the appointed Psalm;
# anything else ("Liturgy of the Palms:", "The Great Vigil:") is a service label
# the book prints, and must NOT be relabelled as a psalm.
PSALM_HEAD = re.compile(r"^(?:[0-9]|Canticle\b)")

# "Various Occasions" are printed as a numbered list ("2. Of the Holy Spirit").
# A bare digit + period is a sentence boundary to sentence_split.py, which would
# break the row in half (GUIDE §3.1), so the printed ordinal becomes its own
# leading field. The ordinal is preserved exactly; only its list period moves.
ORDINAL = re.compile(r"^(\d+)\.\s+(.*)$")

# Entries whose field count differs from the norm for a defensible reason. Two
# tiers per AUDIT_METHOD §"the pattern": a categorical rule, and named cases.
EUCH_NORM = 4          # psalm + three readings
DO_NORM = 3            # three readings

# Categorical: Easter Week weekdays print psalm + Acts + Gospel (no OT lesson);
# vigil ("Eve of ...") offices and Christmas Eve print two readings.
def euch_expected(entry):
    if "Easter Week" in entry["occasion"]:
        return {3, 4}
    if entry["section"] in ("The Common of Saints", "Various Occasions",
                            "Holy Days"):
        return {3, 4, 5, 6, 7}
    return {EUCH_NORM}


def do_expected(entry):
    d = entry["day"]
    if d.startswith("Eve of") or d.startswith("Christmas Eve"):
        return {2}
    if "Easter Week" in (entry["week"] or "") and d == "Easter Day":
        return {2, 3}
    return {DO_NORM}


def _row(fields):
    return " | ".join(fields)


def _verify(key, note):
    return "<!-- VERIFY: '%s'; %s -->" % (key, note)


def build_eucharistic(entries, verifies):
    lines = ["# The Lectionary", ""]
    section = None
    for e in entries:
        if e["section"] != section:
            section = e["section"]
            lines += ["## " + section, ""]
            if section == "Year A":
                key = "Year A: First and Second Sundays of Advent"
                note = ("the public-domain e-text loses page 889 entirely, taking "
                        "the '<Year A>' heading, the close of 'Concerning the "
                        "Lectionary', and Year A's First and Second Sundays of "
                        "Advent; the rows are absent rather than reconstructed")
                lines += [_verify(key, note), ""]
                verifies.append({"service": "tables/eucharistic-lectionary",
                                 "anchor": section, "source_reading": key,
                                 "note": note})
        occ = e["occasion"]
        lead = []
        mo = ORDINAL.match(occ)
        if mo:
            lead, occ = [mo.group(1)], mo.group(2)
        if e["subtitle"]:
            occ = "%s (%s)" % (occ, e["subtitle"])
        cits = list(e["citations"])
        if cits and PSALM_HEAD.match(cits[0]):
            cits[0] = "Psalm: " + cits[0]
        lines.append(_row(lead + [occ] + cits))
        if len(e["citations"]) not in euch_expected(e):
            key = cits[-1] if cits else occ
            note = ("the e-text yields %d citation fields where this occasion "
                    "takes %s; carried exactly as the e-text prints it, not "
                    "repaired (page %s)"
                    % (len(e["citations"]),
                       "/".join(str(x) for x in sorted(euch_expected(e))),
                       e["page"]))
            lines.append(_verify(key, note))
            verifies.append({"service": "tables/eucharistic-lectionary",
                             "anchor": e["section"], "source_reading": key,
                             "note": note})
        lines.append("")
    return lines


def build_daily_office(entries, verifies):
    lines = ["# The Daily Office Lectionary", ""]
    year = week = None
    for e in entries:
        if e["year"] != year:
            year = e["year"]
            lines += ["## " + (year or "Year One"), ""]
        if e["week"] != week:
            week = e["week"]
            lines += ["### " + (week or "(unnamed week)"), ""]
            if week and ";" in week:
                key = week
                note = ("the e-text merges a reading line into this week "
                        "heading; the heading is carried as printed and the "
                        "displaced readings are not reconstructed")
                lines += [_verify(key, note), ""]
                verifies.append({"service": "tables/daily-office-lectionary",
                                 "anchor": year, "source_reading": key,
                                 "note": note})
        ps = e["psalms"]
        # The book's own note licenses the split: "those for the morning are
        # given first, and then those for the evening". Only split when the
        # printed line has exactly one ';' -- otherwise carry it whole.
        if ps.count(";") == 1:
            m, ev = [x.strip() for x in ps.split(";")]
            psf = ["Morning Psalms: " + m, "Evening Psalms: " + ev]
        else:
            psf = ["Psalms: " + ps]
        lines.append(_row([e["day"]] + psf + e["readings"]))
        if len(e["readings"]) not in do_expected(e):
            key = (e["readings"][-1] if e["readings"]
                   else "%s / %s / %s" % (year, week, e["day"]))
            note = ("the e-text yields %d readings where this office takes %s; "
                    "carried exactly as the e-text prints it, not repaired"
                    % (len(e["readings"]),
                       "/".join(str(x) for x in sorted(do_expected(e)))))
            lines.append(_verify(key, note))
            verifies.append({"service": "tables/daily-office-lectionary",
                             "anchor": year, "source_reading": key,
                             "note": note})
        lines.append("")
    return lines


def main():
    lines = w14_1979.load_lines()
    eu, do = w14_1979.split_books(lines)
    E = w14_1979.parse_eucharistic(eu)
    D = w14_1979.parse_daily_office(do)

    # GATE: nothing may silently vanish between parse and write.
    assert len(E) == 280, "eucharistic entry count changed: %d" % len(E)
    assert len(D) == 784, "daily office entry count changed: %d" % len(D)

    verifies = []
    eu_lines = build_eucharistic(E, verifies)
    do_lines = build_daily_office(D, verifies)

    os.makedirs(OUT, exist_ok=True)
    for name, body in (("eucharistic-lectionary.md", eu_lines),
                       ("daily-office-lectionary.md", do_lines)):
        text = "\n".join(body).rstrip("\n") + "\n"
        text = re.sub(r"\n{3,}", "\n\n", text)
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    with open(VERIFY_JSON, "w", encoding="utf-8") as fh:
        json.dump(verifies, fh, indent=1)

    # Report STRUCTURE only, never bodies.
    for name in ("eucharistic-lectionary.md", "daily-office-lectionary.md"):
        p = os.path.join(OUT, name)
        body = open(p, encoding="utf-8").read().split("\n")
        rows = [l for l in body if " | " in l]
        print("%-32s lines=%4d rows=%4d h2=%d h3=%d verify=%d"
              % (name, len(body), len(rows),
                 sum(1 for l in body if l.startswith("## ")),
                 sum(1 for l in body if l.startswith("### ")),
                 sum(1 for l in body if l.startswith("<!-- VERIFY"))))
    print("verify manifest: %d items -> %s" % (len(verifies), VERIFY_JSON))


if __name__ == "__main__":
    main()
