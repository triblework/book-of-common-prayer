#!/usr/bin/env python3
"""Append Wave-9 provenance records to provenance.yaml, insert the Uncertain-passages
rows into SOURCES.md, and add the front-matter source-scope section. Idempotent-ish:
refuses if the Wave-9 marker is already present."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)

# ---- provenance.yaml ----
prov = open(f"{WT}/provenance.yaml").read()
block = open(f"{HERE}/wave9_provenance_block.yaml").read()
if "Wave 9: the front-matter" not in prov:
    open(f"{WT}/provenance.yaml", "w").write(
        prov.rstrip("\n") + "\n" + block.rstrip("\n") + "\n")
    print("provenance.yaml: appended Wave-9 records")
else:
    print("provenance.yaml: Wave-9 already present, skipped")

# ---- SOURCES.md ----
src_path = f"{WT}/repo-root/SOURCES.md"
lines = open(src_path).read().split("\n")
rows = open(f"{HERE}/wave9_sources_rows.md").read().rstrip("\n").split("\n")

if "1979 Concerning the Service of the Church | `fulfull`" not in "\n".join(lines):
    hdr = next(i for i, l in enumerate(lines) if l.startswith("## Uncertain passages"))
    nxt = next(i for i in range(hdr + 1, len(lines)) if lines[i].startswith("## "))
    j = nxt - 1
    while j > hdr and lines[j].strip() == "":
        j -= 1
    lines = lines[:j + 1] + rows + lines[j + 1:]
    print("SOURCES.md: inserted %d Uncertain-passages rows" % len(rows))
else:
    print("SOURCES.md: Uncertain rows already present, skipped")

scope = [
 "",
 "## Front-matter (Wave 9)",
 "",
 "The prefatory matter — **The Preface**, **Concerning the Service of the Church**,",
 "**Of Ceremonies (why some be abolished and some retained)**, and the American",
 "**Ratification** — under `front-matter/`. Presence differs sharply by line and is",
 "the point of the wave:",
 "",
 "- **Concerning the Service of the Church** is the 1549 original Preface (\"There was",
 "  never any thing by the wit of man...\"), titled simply *The Preface* through 1604 and",
 "  **renamed** *Concerning the Service of the Church* in 1662. English 1549-1662 and",
 "  Scottish 1637 (a wholly distinct Scottish preface); the American line **drops** it at",
 "  1789 and **re-adds** a new modern one at 1979.",
 "- **The Preface** (\"It hath been the wisdom of the Church of England...\") is a **1662",
 "  addition** (absent 1549-1604); the American line has its **own** Preface (\"It is a",
 "  most invaluable part of that blessed liberty...\", 1789+), inherited 1892/1928/1979.",
 "- **Of Ceremonies** runs from 1549 (printed at the *end* of the 1549 book, moved to the",
 "  *front* in 1552 — a book-order change, see NOTICE) through 1662 and Scottish 1637;",
 "  **absent from the American line**.",
 "- **The Ratification** is **American only** (1789+).",
 "- 1764/1929 (Communion-only Scottish line) carry no front-matter.",
 "",
 "The title pages, Tables of Contents, Kalendars, the 1559 Act of Uniformity, and the",
 "1637 royal Proclamation that share these source pages are book-structure / tables and",
 "are out of Wave-9 scope; the 1979 \"Historical Documents of the Church\" (Articles of",
 "Religion etc.) is back-matter, likewise out of scope.",
 "",
 "| Edition | Source | Notes |",
 "|---------|--------|-------|",
 "| 1549 | justus `1549/front_matter_1549.htm`, `1549/Of_Ceremonies_1549.htm` | original Preface + Of Ceremonies (Of Ceremonies at the book's end) |",
 "| 1552 | justus `1552/Front_matter_1552.htm` | Preface adds the Archbishop clause + three closing directives; Of Ceremonies now at the front (inherits 1549 text) |",
 "| 1559 | justus `1559/front_matter_1559.htm` (reviewed) | Preface/Of Ceremonies unchanged from 1552 → inherited |",
 "| 1604 | derived (reviewed-unchanged) | front-matter unchanged from 1559 → inherited |",
 "| 1662 | CoE website (`preface`, `concerning-service-church`, `concerning-ceremonies-why-some-be`) | new Preface added; 1549 Preface renamed *Concerning the Service of the Church* |",
 "| 1637 | justus `Scotland/front_matter_1637.htm` | distinct Scottish Preface (names James & Charles); Of Ceremonies (two source leaves missing — flagged) |",
 "| 1789 | justus `1789/FrontMatter_1789.htm` | American Preface + Ratification; drops Concerning-the-Service and Of Ceremonies |",
 "| 1892 | inherited from 1789 (`1892/BCP_1892.htm` cross-check) | Preface + Ratification unchanged |",
 "| 1928 | inherited from 1789 (`1928/Front_Matter_1928.pdf` cross-check) | Preface + Ratification unchanged (1928 front-matter PDF has a garbled font layer; relied on cross-source stability) |",
 "| 1979 | `bcpoffce.txt` via transform | re-adds a modern *Concerning the Service of the Church*; Preface + Ratification are the 1789 documents reprinted (inherited) |",
 "",
]
txt = "\n".join(lines)
if "## Front-matter (Wave 9)" not in txt:
    txt = txt.rstrip("\n") + "\n" + "\n".join(scope) + "\n"
    print("SOURCES.md: appended front-matter source-scope section")
open(src_path, "w").write(txt)
print("done")
