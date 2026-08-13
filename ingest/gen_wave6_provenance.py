#!/usr/bin/env python3
"""Generate Wave-6 provenance.yaml records + SOURCES.md 'Uncertain passages' rows.

Scans the authored Wave-6 files for inline `<!-- VERIFY -->` comments and emits, from
the SAME scan, both the machine-readable provenance verify_items and the human SOURCES
rows — so verify_index.py reconciles in both the authoring and published contexts.

Prints two blocks to stdout:
  ===PROVENANCE===   YAML to append under provenance.yaml `records:`
  ===SOURCES===      Markdown rows to append to the SOURCES 'Uncertain passages' table
Usage: gen_wave6_provenance.py <authoring-root>
"""
import sys, re, os
import yaml


def yd(x):
    """YAML-dump a scalar as its single value line (safe_dump appends a '...' end
    marker and a trailing newline; width=10**9 keeps the value un-wrapped)."""
    return yaml.safe_dump(x, default_flow_style=True, width=10**9,
                          allow_unicode=True).split("\n")[0]

WT = sys.argv[1]
J = "http://justus.anglican.org/resources/bcp/"
COE = "https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer/"
ETX = J + "bcpastrl.txt"

SVCS = ["matrimony", "visitation-sick", "burial", "churching", "commination"]

# (service, edition) -> source_url. 1604 rows that INHERIT 1559 are omitted here and
# handled as reviewed-unchanged with no file.
URL = {
 "matrimony": {"1549": J+"1549/Marriage_1549.htm", "1552": J+"1552/Marriage_1552.htm",
   "1559": J+"1559/Marriage_1559.htm", "1662": COE+"form-solemnization-matrimony",
   "1637": J+"Scotland/Marriage_1637.htm", "1789": J+"1789/Marriage_1789.htm",
   "1892": J+"1892/Marriage_1892.pdf", "1928": J+"1928/Marriage.htm", "1979": ETX},
 "visitation-sick": {"1549": J+"1549/Visitation_Sick_1549.htm", "1552": J+"1552/Visitation_Sick_1552.htm",
   "1559": J+"1559/Visitation_Sick_1559.htm", "1662": COE+"visitation-sick",
   "1637": J+"Scotland/Visitation_Sick_1637.htm", "1789": J+"1789/Visitation_Sick_1789.htm",
   "1892": J+"1892/Visitation_Sick_1892.pdf", "1928": J+"1928/Visitation_Sick.htm", "1979": ETX},
 "burial": {"1549": J+"1549/Burial_1549.htm", "1552": J+"1552/Burial_1552.htm",
   "1559": J+"1559/Burial_1559.htm", "1662": COE+"burial-dead",
   "1637": J+"Scotland/Burial_1637.htm", "1789": J+"1789/Burial_1789.htm",
   "1892": J+"1892/Burial_1892.pdf", "1928": J+"1928/Burial.htm", "1979": ETX},
 "churching": {"1549": J+"1549/Purification_Women_1549.htm", "1552": J+"1552/Churching_Women_1552.htm",
   "1559": J+"1559/Churching_of_Women_1559.htm", "1662": COE+"churching-women",
   "1637": J+"Scotland/Churching_of_Women_1637.htm", "1789": J+"1789/Churching_of_Women_1789.htm",
   "1892": J+"1892/Churching_of_Women_1892.pdf", "1928": J+"1928/Marriage.htm", "1979": ETX},
 "commination": {"1549": J+"1549/Ashwednesday_1549.htm", "1552": J+"1552/Commination_1552.htm",
   "1559": J+"1559/Churching_of_Women_1559.htm", "1662": COE+"commination",
   "1637": J+"Scotland/Commination_1637.htm"},
}
# 1604 inheritance: services whose 1604 is reviewed-unchanged from 1559 (no file)
INHERIT_1604 = {"matrimony", "visitation-sick", "commination"}
# 1604 derived (file authored) + the delta note
DERIVED_1604 = {
 "burial": ("Derived from the 1559 justus page, which footnotes the single 1604 change: "
            "the procession rubric 'go eyther unto the churche' -> 'into the churche'."),
 "churching": ("Derived from the 1559 justus page, which footnotes the 1604 change: the four "
               "suffrage speaker labels 'Priest' -> 'Minister' (Hampton Court)."),
}
# per-cell notes for special sourcing
def note_for(svc, ed):
    if ed == "1979":
        n = {"matrimony": "The Celebration and Blessing of a Marriage (+ An Order for Marriage, Additional Directions)",
             "visitation-sick": "Ministration to the Sick (Parts I-III + Prayers for the Sick)",
             "burial": "The Burial of the Dead, Rite One (office body) + Rite Two (separate section)",
             "churching": "A Thanksgiving for the Birth or Adoption of a Child"}[svc]
        return (f"1979: {n}, from the public-domain ASCII e-text bcpastrl.txt via "
                f"ingest/transform_1979_{svc.replace('-sick','').replace('-','_')}.py "
                "(source -> script -> file). Mechanically reflowed; verify against a page scan.")
    if ed == "1892":
        return ("American 1892; justus serves this office only as a text-layer PDF (its HTML index "
                "links back to the 1789 page). Extracted with pypdf layout mode via "
                "ingest/pdf_spine.py; obvious PDF-layout artifacts (drop-caps, split/joined words, "
                "line-break hyphenation) fixed. Verify against the 1892 Standard scan.")
    if ed == "1662":
        extra = " (+ the Communion of the Sick page)" if svc == "visitation-sick" else ""
        return (f"1662 Church of England{extra}, from the CoE website (PD outside the UK; Crown "
                "copyright within the UK). Site chrome stripped. `BCP 1662`.")
    if ed == "1928" and svc == "churching":
        return ("American 1928; the Churching is bundled on the Marriage page after the marriage "
                "service (Marriage.htm#Churching_Women) — only the Churching is transcribed here.")
    if ed == "1559" and svc == "commination":
        return ("1559; the Commination is bundled after the Churching on Churching_of_Women_1559.htm "
                "(#Commination) — only the Commination is transcribed here.")
    if ed == "1549" and svc == "commination":
        return ("1549; the Commination is printed as 'The First Day of Lent, commonly called "
                "Ash-Wednesday' (Ashwednesday_1549.htm); subsequent books title it 'A Commination'.")
    if ed == "1549" and svc == "churching":
        return "1549; titled 'The Order of the Purification of Women' (the older name for the Churching)."
    return None

VERIFY_RE = re.compile(r"<!--\s*VERIFY\b(.*?)-->", re.DOTALL | re.I)
QUOTED_RE = re.compile(r"'([^']+)'")

SVC_LABEL = {"matrimony": "Matrimony", "visitation-sick": "Visitation of the Sick",
             "burial": "Burial", "churching": "Churching", "commination": "Commination"}

def scan_verifies(path):
    out = []
    if not os.path.exists(path):
        return out
    text = open(path, encoding="utf-8").read()
    # find the nearest preceding ## anchor for each VERIFY, for the provenance anchor field
    for m in VERIFY_RE.finditer(text):
        body = " ".join(m.group(1).split())
        body = re.sub(r"^:\s*", "", body)   # drop the leading ':' after VERIFY
        q = QUOTED_RE.search(body)
        reading = q.group(1) if q else body
        anchor = "?"
        for hm in re.finditer(r"(?m)^##+\s+(.+)$", text[:m.start()]):
            anchor = hm.group(1).strip()
        # short human note = the comment minus the leading "'reading' " if present
        out.append((anchor, reading, body))
    return out

prov_lines = ["", "  # ---- Wave 6: pastoral occasional offices ----"]
src_rows = []
for svc in SVCS:
    for ed in sorted(URL.get(svc, {})):
        path = f"{WT}/editions/{ed}/occasional-offices/{svc}.md"
        vitems = scan_verifies(path)
        rec = [f"  - edition: {ed}",
               f"    service: occasional-offices/{svc}",
               f"    source_url: {URL[svc][ed]}",
               "    retrieved: 2026-08-13",
               "    cross_check: []",
               "    status: transcribed",
               "    depth: tier-1",
               "    verifier: bcp-authoring"]
        nt = note_for(svc, ed)
        if nt:
            rec.append(f'    note: "{nt}"')
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
    # 1604 handling
    if svc in INHERIT_1604:
        prov_lines += [
          "  - edition: 1604",
          f"    service: occasional-offices/{svc}",
          f"    source_url: {URL[svc]['1559']}",
          "    retrieved: 2026-08-13",
          "    cross_check: []",
          "    status: reviewed-unchanged",
          "    depth: tier-1",
          "    verifier: bcp-authoring",
          f'    note: "1604: unchanged from 1559 (the justus 1559 page shows no 1604 apparatus for this office); inherits the 1559 text."',
          "    verify_items: []", ""]
    elif svc in DERIVED_1604:
        path = f"{WT}/editions/1604/occasional-offices/{svc}.md"
        vitems = scan_verifies(path)
        rec = ["  - edition: 1604",
               f"    service: occasional-offices/{svc}",
               f"    source_url: {URL[svc]['1559']}",
               "    retrieved: 2026-08-13",
               "    cross_check: []",
               "    status: transcribed",
               "    depth: tier-1",
               "    verifier: bcp-authoring",
               f'    note: "{DERIVED_1604[svc][1]}"']
        if vitems:
            rec.append("    verify_items:")
            for anchor, reading, body in vitems:
                rec.append(f"      - anchor: {yd(anchor)}")
                rec.append(f"        source_reading: {yd(reading)}")
                rec.append(f"        note: {yd(body)}")
                src_rows.append(f"| 1604 {SVC_LABEL[svc]} | `{reading}` | {body} |")
        else:
            rec.append("    verify_items: []")
        prov_lines += rec + [""]

open(f"{WT}/ingest/wave6_provenance_block.yaml", "w").write("\n".join(prov_lines))
open(f"{WT}/ingest/wave6_sources_rows.md", "w").write("\n".join(src_rows) + "\n")
print("PROVENANCE records + SOURCES rows written.")
print("verify_items (SOURCES rows):", len(src_rows))
