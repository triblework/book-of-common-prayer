#!/usr/bin/env python3
"""Generate Wave-8 provenance.yaml records + SOURCES.md 'Uncertain passages' rows
for the Ordinal (ordinal/preface, ordinal/ordering-deacons, ordinal/ordering-priests,
ordinal/consecration-bishops), across the nine editions that carry it (English
1549/1552/1559/1604/1662, American 1789/1892/1928/1979). One record per
<service,edition> present cell (authored or inherited); verify_items + SOURCES rows
are scanned from the SAME inline `<!-- VERIFY -->` comments so verify_index.py
reconciles in both the authoring and published contexts.

Writes:  ingest/wave8_provenance_block.yaml   (append under provenance.yaml `records:`)
         ingest/wave8_sources_rows.md          (append to SOURCES 'Uncertain passages')
Usage:   gen_wave8_provenance.py <authoring-root>

justus HTTPS 404s every path (2010-era cert setup); content is served over plain
HTTP, so all justus source_urls use http://.
"""
import sys, re, os
import yaml

WT = sys.argv[1]
J = "http://justus.anglican.org/resources/bcp/"
COE = "https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer/"

SERVICES = ["preface", "ordering-deacons", "ordering-priests", "consecration-bishops"]
EDITIONS = ["1549", "1552", "1559", "1604", "1662", "1789", "1892", "1928", "1979"]
PARENT = {"1552": "1549", "1559": "1552", "1604": "1559", "1662": "1604",
          "1789": "1662", "1892": "1789", "1928": "1892", "1979": "1928"}

# justus per-service filename by era
ENG_COMBINED = {"preface": "1549/Deacons_1549.htm", "ordering-deacons": "1549/Deacons_1549.htm",
                "ordering-priests": "1549/Priests_1549.htm", "consecration-bishops": "1549/Bishops_1549.htm"}
COE_SLUG = {"preface": "form-and-manner-making-ordaining",
            "ordering-deacons": "ordaining-and-consecrating-bishops-priests-and-deacons/ordering-deacons",
            "ordering-priests": "ordaining-and-consecrating-0",
            "consecration-bishops": "ordaining-and-consecrating-1"}
US1789 = {"preface": "1789/Deacon_1789.htm", "ordering-deacons": "1789/Deacon_1789.htm",
          "ordering-priests": "1789/Priests_1789.htm", "consecration-bishops": "1789/Bishops_1789.htm"}


def source_url(ed, svc):
    if ed in ("1549", "1552", "1559"):
        return J + ENG_COMBINED[svc]
    if ed == "1604":
        return J + ENG_COMBINED[svc].replace("1549/", "1549/")  # derived from the 1559 apparatus on the combined page
    if ed == "1662":
        return COE + COE_SLUG[svc]
    if ed == "1789":
        return J + US1789[svc]
    if ed == "1892":
        return J + US1789[svc]  # derived from 1789; 1892 PDF as cross_check
    if ed == "1928":
        return J + "1928/Ordinal.htm"
    if ed == "1979":
        return J + "bcpepscl.txt"


def has_file(ed, svc):
    return os.path.exists(f"{WT}/editions/{ed}/ordinal/{svc}.md")


def nearest_ancestor(ed, svc):
    p = PARENT.get(ed)
    while p:
        if has_file(p, svc):
            return p
        p = PARENT.get(p)
    return None


NOTE_FAMILY = {
 "1549": ("English 1549 node = the separately-published 1550 Ordinal (bound into the book "
          "from 1552; the 1549 book proper had no Ordinal — see NOTICE). From the justus synoptic "
          "page 'The Ordinal from the 1549, 1552 and 1559 Books of Common Prayer' (1549/*_1549.htm), "
          "title-page 1550; the 1550 readings are taken as the base."),
 "1552": ("English 1552, from the same justus synoptic page's 1552 apparatus (roman base + "
          "'[…] added 1552' inserts + '1552, 59:' branches). Flagship v1549->v1552: the delivery of "
          "instruments (porrection) removed — priests lose 'the Chalice or cuppe with the breade', "
          "bishops lose the pastoral staff and the Bible-on-neck; the plain-Albe / surplice-cope "
          "vesture is 1550-only."),
 "1559": ("English 1559 (Elizabethan), from the same synoptic page's '1559:' branches. Flagship "
          "v1552->v1559: the anti-papal Litany clause ('tyrannye of the Bysshop of Rome') removed; the "
          "Oath of the King's Supremacy replaced by the Oath of the Queen's Sovereignty; the sovereign "
          "petition recast for Elizabeth."),
 "1604": ("English 1604 (Jacobean); no separate justus Ordinal page — DERIVED from 1559 per the "
          "synoptic page's own 1604 apparatus ('Kings supremacie in 1604' + bracketed [Kings]/[his] "
          "readings). Only the Deacons (Litany sovereign petition Elizabeth->James; Queen's oath->King's) "
          "and Bishops (Queen's Mandate/Sovereignty->King's; 'at the last daye' loses 'daye') differ; "
          "Priests and Preface inherit 1559 unchanged."),
 "1662": ("1662 Church of England, from the CoE website (PD outside the UK; Crown copyright within). "
          "Site chrome / Crown-CUP acknowledgement stripped. Flagship v1604->v1662: the ordination forms "
          "gain the explicit order-naming ('Receive the Holy Ghost FOR THE OFFICE AND WORK OF A "
          "Priest/Bishop…'); the Preface gains the anti-Puritan episcopal-succession clause ('…or hath "
          "had formerly Episcopal Consecration or Ordination'). The embedded Litany prints the reigning "
          "Royal Family (reign-dependent — flagged)."),
 "1789": ("American 1789, from the justus per-order pages (Deacon/Priests/Bishops_1789.htm; the "
          "Ordinal Preface heads the Deacon page). Flagship v1662->v1789: the Oath of the King's "
          "Supremacy is DROPPED and (bishops) replaced by the Promise of Conformity to the Doctrine, "
          "Discipline, and Worship of the Protestant Episcopal Church; the priest rite offers BOTH the "
          "1662 form and the older 'Take thou Authority to execute the Office of a Priest' form. The "
          "justus HTML carries scattered OCR noise (flagged inline); dropped justus editorial "
          "'…identical in the 1892 Book…' apparatus notes."),
 "1892": ("American 1892; justus states the Ordinal text 'is essentially identical' to 1789, 'any "
          "differences … indicated' (1892 PDF Ordinations_1892.pdf as cross-check). Only Priests (the "
          "Communion rubric adds 'the Nicene Creed shall be said, and') and Bishops (the presentation "
          "rubric adds the Nicene Creed; '&c.'->'etc.'; the printed metrical hymn replaced by a "
          "cross-reference to the longer paraphrase in the Ordering of Priests) differ; Deacons and "
          "Preface inherit 1789."),
 "1928": ("American 1928, from the justus one-page Ordinal (1928/Ordinal.htm; all three orders + "
          "preface + the Litany for Ordinations, appended to the Deacons file). Its own printed headings "
          "are the anchors; OCR line-break hyphens closed up. Adds the option of the Litany for "
          "Ordinations and a second metrical Veni Creator ('True Promise of the Father thou')."),
 "1979": ("American 1979 (current); the contemporary-language Ordination rites, from the public-domain "
          "ASCII e-text bcpepscl.txt (Episcopal Services) via ingest/transform_1979_ordinal.py "
          "(source -> script -> file; text never re-typed). The rite's own headings (The Presentation, "
          "The Examination, The Consecration of the Bishop/Priest/Deacon, …) are the anchors; the Litany "
          "for Ordinations is appended to the Deacons file. Mechanically reflowed — the e-text carries "
          "some OCR artifacts; verify against a page scan before sign-off."),
}

VERIFY_RE = re.compile(r"<!--\s*VERIFY\b(.*?)-->", re.DOTALL | re.I)
QUOTED_RE = re.compile(r"'([^']+)'")


def yd(x):
    return yaml.safe_dump(x, default_flow_style=True, width=10**9, allow_unicode=True).split("\n")[0]


def scan_verifies(path):
    out = []
    if not os.path.exists(path):
        return out
    text = open(path, encoding="utf-8").read()
    for m in VERIFY_RE.finditer(text):
        body = " ".join(m.group(1).split())
        body = re.sub(r"^:\s*", "", body)
        q = QUOTED_RE.search(body)
        reading = q.group(1) if q else body
        anchor = "?"
        for hm in re.finditer(r"(?m)^##+\s+(.+)$", text[:m.start()]):
            anchor = hm.group(1).strip()
        out.append((anchor, reading, body))
    return out


prov_lines = ["", "  # ---- Wave 8: the Ordinal ----"]
src_rows = []
SVC_LABEL = {"preface": "Preface", "ordering-deacons": "Ordering of Deacons",
             "ordering-priests": "Ordering of Priests", "consecration-bishops": "Consecration of Bishops"}

for svc in SERVICES:
    for ed in EDITIONS:
        sid = f"ordinal/{svc}"
        path = f"{WT}/editions/{ed}/ordinal/{svc}.md"
        authored = has_file(ed, svc)
        rec = [f"  - edition: {ed}", f"    service: {sid}",
               f"    source_url: {source_url(ed, svc)}",
               "    retrieved: 2026-08-13"]
        if ed == "1892":
            rec.append(f"    cross_check: [{J}1892/Ordinations_1892.pdf]")
        else:
            rec.append("    cross_check: []")
        if authored:
            status = "transcribed"
        else:
            anc = nearest_ancestor(ed, svc)
            status = "reviewed-unchanged"
        rec.append(f"    status: {status}")
        rec.append("    depth: tier-1")
        rec.append("    verifier: bcp-authoring")
        note = NOTE_FAMILY[ed]
        if not authored:
            anc = nearest_ancestor(ed, svc)
            note = (f"{SVC_LABEL[svc]}: unchanged from {anc} in this edition — inherited from {anc} "
                    f"(no separate file). {note}")
        rec.append(f"    note: {yd(note)}")
        vitems = scan_verifies(path)
        if vitems:
            rec.append("    verify_items:")
            for anchor, reading, body in vitems:
                rec.append(f"      - anchor: {yd(anchor)}")
                rec.append(f"        source_reading: {yd(reading)}")
                rec.append(f"        note: {yd(body)}")
                src_rows.append(f"| {ed} {SVC_LABEL[svc]} | `{reading}` | {body} |")
        else:
            rec.append("    verify_items: []")
        prov_lines += rec + [""]

open(f"{WT}/ingest/wave8_provenance_block.yaml", "w").write("\n".join(prov_lines))
open(f"{WT}/ingest/wave8_sources_rows.md", "w").write("\n".join(src_rows) + "\n")
print("records:", len(SERVICES) * len(EDITIONS), "| verify_items (SOURCES rows):", len(src_rows))
for r in src_rows:
    print("  ", r[:140])
