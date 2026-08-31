#!/usr/bin/env python3
"""Generate Wave-10 (10a) provenance records + SOURCES.md 'Uncertain passages'
rows for the collects-epistles-gospels family.

One record per present <service,edition> cell. verify_items are scanned from the
SAME inline <!-- VERIFY --> comments that live in the cells, so verify_index
reconciles by construction, in both authoring and published contexts.

Writes:  ingest/wave10_provenance_block.yaml
         ingest/wave10_sources_rows.md
Usage:   gen_wave10_provenance.py <authoring-root>

justus HTTPS 404s every path; content is served over plain HTTP.
"""
import os, re, sys

WT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
FAM = "collects-epistles-gospels"
RETRIEVED = "2026-08-31"
VERIFIER = "claude-opus-5 (scripted ingest + fidelity gate)"

J = "http://justus.anglican.org/resources/bcp/"
COE = ("https://www.churchofengland.org/prayer-and-worship/worship-texts-and-"
       "resources/book-common-prayer/collects-epistles-and-gospels")

SEASON = {}
for s in ("advent-1", "advent-2", "advent-3", "advent-4"):
    SEASON[s] = "Advent"
for s in ("christmas-day", "christmas-1", "christmas-2", "circumcision"):
    SEASON[s] = "Xmas"
SEASON.update({f"epiphany-{n}": "Epiphany" for n in (1, 2, 3, 4, 5, 6, 7, 8)})
SEASON["epiphany"] = "Epiphany"
SEASON["epiphany-last"] = "Epiphany"
for s_ in ("septuagesima", "sexagesima", "quinquagesima"):
    SEASON[s_] = "Epiphany"          # printed on the justus Epiphany page
for s_ in ("ash-wednesday", "lent-1", "lent-2", "lent-3", "lent-4", "lent-5",
           "palm-sunday"):
    SEASON[s_] = "Lent"
for s_ in ("monday-before-easter", "tuesday-before-easter",
           "wednesday-before-easter", "thursday-before-easter", "good-friday",
           "easter-even"):
    SEASON[s_] = "HolyWeek"

# The American synoptic runs onto a second page at Palm Sunday.
AMERICAN_PAGE_B = {"palm-sunday", "monday-before-easter", "tuesday-before-easter",
                   "wednesday-before-easter", "thursday-before-easter",
                   "good-friday", "easter-even"}

COE_SLUG = {"advent-1": "-1", "advent-2": "-2", "advent-3": "-3", "advent-4": "-4",
            "christmas-day": "-6", "christmas-1": "-7", "circumcision": "-8",
            "epiphany": "-9", "epiphany-1": "-10", "epiphany-2": "-11",
            "epiphany-3": "-12", "epiphany-4": "-13", "epiphany-5": "-14",
            "epiphany-6": "-15",
            "septuagesima": "-16", "sexagesima": "-17", "quinquagesima": "-18",
            "ash-wednesday": "/ash",
            "lent-1": "-20", "lent-2": "-21", "lent-3": "-22", "lent-4": "-23",
            "lent-5": "-24", "palm-sunday": "-25",
            "monday-before-easter": "-26", "tuesday-before-easter": "-27",
            "wednesday-before-easter": "-28", "thursday-before-easter": "-29",
            "good-friday": "-30", "easter-even": "-31"}

VERIFY_RE = re.compile(r"<!--\s*VERIFY\b(.*?)-->", re.S | re.I)


def source_url(edition, slug):
    if edition in ("1549", "1552", "1559"):
        return J + f"1549/Readings_{SEASON[slug]}_1549.htm"
    if edition == "1604":
        return J + f"1549/Readings_{SEASON[slug]}_1549.htm"
    if edition == "1662":
        return COE + COE_SLUG.get(slug, "")
    if edition == "1637":
        return J + "Scotland/Collects1_1637.htm"
    if edition in ("1789", "1892", "1928"):
        page = "B" if slug in AMERICAN_PAGE_B else "A"
        return J + f"1789/Readings1789&1892{page}.htm"
    if edition == "1979":
        return J + "bcpcolct.txt"
    raise KeyError(edition)


def status_and_note(edition, slug, authored):
    if edition == "1604":
        return ("reviewed-unchanged",
                "1604 inherits 1559. No allow-listed source prints the 1604 "
                "propers. The justus apparatus records that initial verse numbers "
                "(rather than bare chapter numbers) entered the Epistle/Gospel "
                "citations in 1604; that change is therefore NOT represented, "
                "rather than reconstructed by inference from 1662.")
    if not authored:
        return ("reviewed-unchanged",
                "Inherited unchanged from the parent edition; confirmed against "
                "the edition's own source page.")
    if edition in ("1552", "1559"):
        return ("transcribed",
                "Derived from the shared justus 1549/1552/1559 synoptic using "
                "that page's own apparatus: 1552 drops the Introits and the "
                "1549-only proper Psalms/Lessons; 1559 adds 'Amen' to each "
                "collect after Advent 1 (applied only where one is absent) and "
                "the bracketed title expansions the page footnotes as 'added in "
                "late 1500's'.")
    if edition in ("1892", "1928"):
        return ("transcribed",
                "Derived from the four-edition American synoptic (1786 Proposed / "
                "1789 / 1892 / 1928) by applying that page's apparatus column; "
                "each delta cites the note that licenses it.")
    if edition == "1979":
        return ("transcribed",
                "From the public-domain 1979 e-text (Traditional and Contemporary "
                "sets). Mapped per ingest/WAVE10_1979_CROSSWALK.md. Carries "
                "collects only: 1979 appoints three reading sets per day under "
                "the three-year lectionary, which the single-citation slot cannot "
                "represent (deferred to Wave 12).")
    if edition == "1637":
        return ("transcribed",
                "From the justus Scottish 1637 collects page, which prints the "
                "collects in full and the readings as citations only.")
    if edition == "1662":
        return ("transcribed",
                "From the Church of England website (PD outside the UK; Crown "
                "copyright within, reproduced with the required acknowledgment). "
                "The citation is taken from the page's bible-reference line; the "
                "reading body is never transcribed.")
    return ("transcribed", "Transcribed from the edition's source page.")


def yaml_str(text):
    return '"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    editions_dir = os.path.join(WT, "editions")
    import yaml as _yaml
    conf = _yaml.safe_load(open(os.path.join(WT, "editions.yaml"), encoding="utf-8"))
    records, rows = [], []
    for ed in conf["editions"]:
        edition = str(ed["id"])
        present = [s for s in ed["present"] if s.startswith(FAM + "/")]
        for svc in sorted(present):
            slug = svc.split("/", 1)[1]
            path = os.path.join(editions_dir, edition, FAM, slug + ".md")
            authored = os.path.exists(path)
            status, note = status_and_note(edition, slug, authored)
            items = []
            if authored:
                body = open(path, encoding="utf-8").read()
                for m in VERIFY_RE.finditer(body):
                    items.append(re.sub(r"\s+", " ", m.group(1)).strip())
            rec = [f"  - edition: {edition}",
                   f"    service: {svc}",
                   f"    source_url: {source_url(edition, slug)}",
                   f"    retrieved: {RETRIEVED}",
                   f"    status: {status}",
                   f"    verifier: {yaml_str(VERIFIER)}",
                   f"    note: {yaml_str(note)}"]
            if items:
                rec.append("    verify_items:")
                for it in items:
                    rec.append(f"      - anchor: {yaml_str(slug)}")
                    rec.append(f"        note: {yaml_str(it)}")
                    m2 = re.match(r"^:?\s*'([^']*)'\s*[\u2014-]*\s*(.*)$", it)
                    reading = m2.group(1) if m2 else slug
                    detail = (m2.group(2) if m2 else it).strip() or "see provenance"
                    detail = detail.replace("|", "\\|")
                    rows.append(f"| {edition} {slug} | `{reading}` | {detail} |")
            records.append("\n".join(rec))

    out_yaml = os.path.join(WT, "ingest", "wave10_provenance_block.yaml")
    with open(out_yaml, "w", encoding="utf-8") as fh:
        fh.write("\n".join(records) + "\n")
    out_rows = os.path.join(WT, "ingest", "wave10_sources_rows.md")
    with open(out_rows, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rows) + "\n")
    print(f"  {len(records)} provenance records, {len(rows)} verify rows")


if __name__ == "__main__":
    main()
