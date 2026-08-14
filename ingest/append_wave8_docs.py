#!/usr/bin/env python3
"""Append Wave-8 provenance records to provenance.yaml, insert the Uncertain-passages
rows into SOURCES.md, and add the Ordinal source-scope section. Idempotent-ish:
refuses if the Wave-8 marker is already present."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)

# ---- provenance.yaml ----
prov = open(f"{WT}/provenance.yaml").read()
block = open(f"{HERE}/wave8_provenance_block.yaml").read()
if "Wave 8: the Ordinal" not in prov:
    open(f"{WT}/provenance.yaml", "w").write(prov.rstrip("\n") + "\n" + block.rstrip("\n") + "\n")
    print("provenance.yaml: appended Wave-8 records")
else:
    print("provenance.yaml: Wave-8 already present, skipped")

# ---- SOURCES.md ----
src_path = f"{WT}/repo-root/SOURCES.md"
lines = open(src_path).read().split("\n")
rows = open(f"{HERE}/wave8_sources_rows.md").read().rstrip("\n").split("\n")

if "1662 Ordering of Deacons" not in "\n".join(lines):
    # insert rows at the end of the Uncertain-passages table (before the next "## ")
    hdr = next(i for i, l in enumerate(lines) if l.startswith("## Uncertain passages"))
    nxt = next(i for i in range(hdr + 1, len(lines)) if lines[i].startswith("## "))
    # walk back over blank lines to the last table row
    j = nxt - 1
    while j > hdr and lines[j].strip() == "":
        j -= 1
    lines = lines[:j + 1] + rows + lines[j + 1:]
    print("SOURCES.md: inserted %d Uncertain-passages rows" % len(rows))
else:
    print("SOURCES.md: Uncertain rows already present, skipped")

scope = [
 "",
 "## Ordinal (Wave 8)",
 "",
 "The Ordinal — the Preface, the Ordering of Deacons, the Ordering of Priests, and the",
 "Consecration of Bishops — across the nine editions that carry it (English",
 "1549/1552/1559/1604/1662, American 1789/1892/1928/1979). **Absent from the Scottish",
 "line:** the 1637 book contained no Ordinal (Laud's Liturgy omitted it), and 1764/1929",
 "are Communion-only, so all four services are `absent:` at 1637 and inherited-absent",
 "thereafter. The 1549 node carries the separately-published **1550 Ordinal** (bound into",
 "the book only from 1552) — see NOTICE.md for that placement decision.",
 "",
 "| Edition | Source | Notes |",
 "|---------|--------|-------|",
 "| 1549 | justus `1549/{Deacons,Priests,Bishops}_1549.htm` (synoptic) | = the 1550 Ordinal; base readings |",
 "| 1552 | same synoptic page, 1552 apparatus | delivery of instruments (porrection) removed; vesture stripped |",
 "| 1559 | same synoptic page, 1559 apparatus | anti-papal Litany clause removed; King's Oath → Queen's Oath |",
 "| 1604 | derived from 1559 (no justus page) | Deacons/Bishops only: Elizabeth→James, Queen→King in the oaths |",
 "| 1662 | CoE website (`form-and-manner-making-ordaining` + three sub-pages) | forms gain the order-naming; preface gains the episcopal-succession clause |",
 "| 1789 | justus `1789/{Deacon,Priests,Bishops}_1789.htm` | King's-Supremacy oath dropped → Promise of Conformity; dual priest form |",
 "| 1892 | derived from 1789 (`1892/Ordinations_1892.pdf` cross-check) | Nicene-Creed rubric additions; printed hymn → cross-reference |",
 "| 1928 | justus `1928/Ordinal.htm` | adds the Litany for Ordinations + a second metrical Veni Creator |",
 "| 1979 | `bcpepscl.txt` via transform | contemporary-language rites (own section headings) |",
 "",
]
txt = "\n".join(lines)
if "## Ordinal (Wave 8)" not in txt:
    txt = txt.rstrip("\n") + "\n" + "\n".join(scope) + "\n"
    print("SOURCES.md: appended Ordinal source-scope section")
open(src_path, "w").write(txt)
print("done")
