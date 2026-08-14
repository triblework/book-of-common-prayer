#!/usr/bin/env python3
"""Generate Wave-9 provenance.yaml records + SOURCES.md 'Uncertain passages' rows
for the front-matter family (front-matter/preface, front-matter/concerning-the-service,
front-matter/of-ceremonies, front-matter/ratification). One record per present
<service,edition> cell (authored or inherited); verify_items + SOURCES rows are
scanned from the SAME inline <!-- VERIFY --> comments so verify_index reconciles
in both authoring and published contexts.

Writes:  ingest/wave9_provenance_block.yaml   (append under provenance.yaml records:)
         ingest/wave9_sources_rows.md          (append to SOURCES 'Uncertain passages')
Usage:   gen_wave9_provenance.py <authoring-root>

justus HTTPS 404s every path; content is served over plain HTTP -> http:// urls.
"""
import sys, re, os
import yaml

WT = sys.argv[1]
J = "http://justus.anglican.org/resources/bcp/"
COE = "https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer/"

# present cells per service, in build order
PRESENT = {
    "concerning-the-service": ["1549", "1552", "1559", "1604", "1662", "1637", "1979"],
    "of-ceremonies":          ["1549", "1552", "1559", "1604", "1662", "1637"],
    "preface":                ["1662", "1789", "1892", "1928", "1979"],
    "ratification":           ["1789", "1892", "1928", "1979"],
}
PARENT = {"1552": "1549", "1559": "1552", "1604": "1559", "1662": "1604",
          "1637": "1604", "1764": "1637", "1929": "1764",
          "1789": "1662", "1892": "1789", "1928": "1892", "1979": "1928"}

SVC_LABEL = {"preface": "The Preface",
             "concerning-the-service": "Concerning the Service of the Church",
             "of-ceremonies": "Of Ceremonies",
             "ratification": "The Ratification"}

# authored-cell source URLs
SRC = {
    ("concerning-the-service", "1549"): J + "1549/front_matter_1549.htm",
    ("concerning-the-service", "1552"): J + "1552/Front_matter_1552.htm",
    ("concerning-the-service", "1662"): COE + "concerning-service-church",
    ("concerning-the-service", "1637"): J + "Scotland/front_matter_1637.htm",
    ("concerning-the-service", "1979"): J + "bcpoffce.txt",
    ("of-ceremonies", "1549"): J + "1549/Of_Ceremonies_1549.htm",
    ("of-ceremonies", "1662"): COE + "concerning-ceremonies-why-some-be",
    ("of-ceremonies", "1637"): J + "Scotland/front_matter_1637.htm",
    ("preface", "1662"): COE + "preface",
    ("preface", "1789"): J + "1789/FrontMatter_1789.htm",
    ("ratification", "1789"): J + "1789/FrontMatter_1789.htm",
}

NOTE = {
 ("concerning-the-service", "1549"): (
   "1549 original Preface ('There was never any thing by the wit of man so well "
   "devised...') — titled simply 'The Preface' in 1549; this is the piece later "
   "(1662) renamed 'Concerning the Service of the Church'. From the justus 1549 "
   "front-matter page (modern-spelling transcription); the title page, contents, "
   "and Kalendar on that page are out of Wave-9 scope."),
 ("concerning-the-service", "1552"): (
   "1552, from the justus 1552 front-matter page. Flagship v1549->v1552: the "
   "Preface gains the Archbishop-appeal clause and three closing directives (that "
   "Priests and Deacons say the daily Office; and that the Curate toll a bell)."),
 ("concerning-the-service", "1662"): (
   "1662 Church of England, from the CoE website (PD outside the UK; Crown "
   "copyright within; site chrome / Crown-CUP acknowledgement stripped). Flagship "
   "v1604->v1662: the 1549 'Preface' is RENAMED 'Concerning the Service of the "
   "Church' and modernised; a wholly new Preface ('It hath been the wisdom...') is "
   "added alongside it (front-matter/preface, absent 1549-1604)."),
 ("concerning-the-service", "1637"): (
   "1637 Scottish (Laud's Liturgy) — a DISTINCT preface ('The Church of Christ "
   "hath in all ages had a prescript forme of Common prayer...'), naming King "
   "James and the reigning Charles; from the justus Scotland 1637 front-matter "
   "page. Flagship v1604->v1637 (scottish line): the English 'There was never any "
   "thing' preface is wholly replaced by the Scottish one. The Proclamation and "
   "Kalendar on that page are out of scope."),
 ("concerning-the-service", "1979"): (
   "1979 American — a modern 'Concerning the Service of the Church' (directions on "
   "the regular services, orders of ministry, hymns and anthems), RE-ADDED after "
   "the American line dropped the piece at 1789. From the public-domain ASCII "
   "e-text bcpoffce.txt via ingest/w9_american.py (source -> script -> file). "
   "Mechanically reflowed; carries an e-text typo (flagged)."),
 ("of-ceremonies", "1549"): (
   "1549 'Of Ceremonies, why some be abolished and some retained' — from the "
   "justus 1549 Of Ceremonies page, where it is printed at the END of the book "
   "(with the 'Certain notes' and colophon, both out of scope). Placement moved to "
   "the FRONT in 1552 (a book-order change recorded in NOTICE, not a text diff)."),
 ("of-ceremonies", "1662"): (
   "1662, from the CoE website. Modernised spelling; text otherwise continuous "
   "with the Edwardian/Elizabethan Of Ceremonies."),
 ("of-ceremonies", "1637"): (
   "1637 Scottish, from the justus Scotland 1637 front-matter page. justus notes "
   "two leaves are missing from its original around this section (flagged); the Of "
   "Ceremonies text may be supplied from a parallel copy."),
 ("preface", "1662"): (
   "The 1662 Preface ('It hath been the wisdom of the Church of England, ever "
   "since the first compiling of her Publick Liturgy...') — a 1662 ADDITION "
   "(absent 1549-1604). From the CoE website. Flagship v1604->v1662: a clean "
   "insertion of the whole piece."),
 ("preface", "1789"): (
   "The American Preface ('It is a most invaluable part of that blessed liberty "
   "wherewith Christ hath made us free...', William White, 1789) — a DISTINCT "
   "preface replacing the English 1662 one. From the justus 1789 front-matter "
   "page. Flagship v1662->v1789: the English Preface is wholly replaced by the "
   "American Preface; the Ratification is added; 'Concerning the Service' and 'Of "
   "Ceremonies' are dropped. Carries a source punctuation oddity (flagged)."),
 ("ratification", "1789"): (
   "The Ratification of the Book of Common Prayer (Convention of 16 October 1789) "
   "— AMERICAN ONLY. From the justus 1789 front-matter page. New at v1789 "
   "(v1662->v1789)."),
}

VERIFY_RE = re.compile(r"<!--\s*VERIFY\b(.*?)-->", re.DOTALL | re.I)
QUOTED_RE = re.compile(r"'([^']+)'")


def yd(x):
    return yaml.safe_dump(x, default_flow_style=True, width=10**9,
                          allow_unicode=True).split("\n")[0]


def has_file(ed, svc):
    return os.path.exists(f"{WT}/editions/{ed}/front-matter/{svc}.md")


def nearest_ancestor(ed, svc):
    p = PARENT.get(ed)
    while p:
        if has_file(p, svc):
            return p
        p = PARENT.get(p)
    return None


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
        anchor = "The Preface"
        for hm in re.finditer(r"(?m)^#+\s+(.+)$", text[:m.start()]):
            anchor = hm.group(1).strip()
        out.append((anchor, reading, body))
    return out


prov_lines = ["", "  # ---- Wave 9: the front-matter ----"]
src_rows = []

for svc in ["preface", "concerning-the-service", "of-ceremonies", "ratification"]:
    for ed in PRESENT[svc]:
        sid = f"front-matter/{svc}"
        path = f"{WT}/editions/{ed}/front-matter/{svc}.md"
        authored = has_file(ed, svc)
        anc = None if authored else nearest_ancestor(ed, svc)
        url = SRC.get((svc, ed)) or (SRC.get((svc, anc)) if anc else "")
        rec = [f"  - edition: {ed}", f"    service: {sid}",
               f"    source_url: {url}",
               "    retrieved: 2026-08-14"]
        if ed == "1892" and svc in ("preface", "ratification"):
            rec.append(f"    cross_check: [{J}1892/BCP_1892.htm]")
        elif ed == "1928" and svc in ("preface", "ratification"):
            rec.append(f"    cross_check: [{J}1928/Front_Matter_1928.pdf]")
        else:
            rec.append("    cross_check: []")
        status = "transcribed" if authored else "reviewed-unchanged"
        rec.append(f"    status: {status}")
        rec.append("    depth: tier-1")
        rec.append("    verifier: bcp-authoring")
        if authored:
            note = NOTE[(svc, ed)]
        else:
            note = (f"{SVC_LABEL[svc]}: unchanged from {anc} in this edition — "
                    f"inherited from {anc} (no separate file). "
                    + NOTE[(svc, anc)])
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

open(f"{WT}/ingest/wave9_provenance_block.yaml", "w").write("\n".join(prov_lines))
open(f"{WT}/ingest/wave9_sources_rows.md", "w").write("\n".join(src_rows) + "\n")
ncells = sum(len(v) for v in PRESENT.values())
print("records:", ncells, "| verify_items (SOURCES rows):", len(src_rows))
for r in src_rows:
    print("  ", r[:150])
