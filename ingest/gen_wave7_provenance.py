#!/usr/bin/env python3
"""Generate Wave-7 provenance.yaml records + SOURCES.md 'Uncertain passages' rows
for the Catechism (occasional-offices/catechism).

Scans the authored Wave-7 files for inline `<!-- VERIFY -->` comments and emits, from
the SAME scan, both the machine-readable provenance verify_items and the human SOURCES
rows — so verify_index.py reconciles in both the authoring and published contexts.

Prints/writes two blocks:
  ingest/wave7_provenance_block.yaml   YAML to append under provenance.yaml `records:`
  ingest/wave7_sources_rows.md         Markdown rows for the SOURCES 'Uncertain passages' table
Usage: gen_wave7_provenance.py <authoring-root>

NOTE on justus access: justus.anglican.org's HTTPS vhost 404s every path (an
expired/misconfigured cert setup on a 2010-era Apache/OpenSSL); the content is
served fine over plain HTTP. All justus source_urls here therefore use http://.
"""
import sys, re, os
import yaml


def yd(x):
    return yaml.safe_dump(x, default_flow_style=True, width=10**9,
                          allow_unicode=True).split("\n")[0]

WT = sys.argv[1]
J = "http://justus.anglican.org/resources/bcp/"
COE = "https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer/"
PRAYR = J + "bcpprayr.txt"

# (edition) -> source_url for the catechism. The Catechism is bundled on the
# Confirmation page for 1549/1552/1559/1637; standalone (CoE) for 1662; recast on
# the 1928 Confirmation page (Offices of Instruction); PD e-text for 1979.
URL = {
 "1549": J+"1549/Confirmation_1549.htm",
 "1552": J+"1552/Confirmation_1552.htm",
 "1559": J+"1559/Confirmation_1559.htm",
 "1604": J+"1559/Confirmation_1559.htm",   # derived from the justus 1559 page
 "1662": COE+"catechism",
 "1637": J+"Scotland/Confirmation_1637.htm",
 "1789": J+"1789/Catechism.htm",
 "1928": J+"1928/Confirnation.htm",
 "1979": PRAYR,
}
STATUS = {ed: "transcribed" for ed in URL}
# 1892 Catechism is identical to 1789 (justus states so; confirmed vs the 1892 PDF)
# -> reviewed-unchanged, inherits 1789 (no file). Handled after the main loop.
PDF_1892 = J + "1892/Catechism&Confirm_1892.pdf"


def note_for(ed):
    if ed in ("1549", "1552", "1559"):
        return ("The Catechism is bundled on the Confirmation page "
                f"({ed}/Confirmation_{ed}.htm); only the Catechism Q&A body is transcribed here "
                "(the Confirmation office + its framing rubrics live in confirmation.md). "
                "Pre-1604 form: ends at the Lord's-Prayer exposition, no Sacraments section.")
    if ed == "1604":
        return ("Derived from the justus 1559 Confirmation page, which appends the 1604 additions "
                "under the caption 'Page from the 1604 Book of Common Prayer ... additional questions' "
                "and the note 'The following questions & answers were added in 1604'. The 1604 changes: "
                "(1) the whole Sacraments section is ADDED ('How many Sacraments hath Christ ordained' "
                "-> the Lord's Supper) — the famous flagship diff v1559->v1604; (2) the baptismal-promise "
                "phrase 'all his workes and pompes, the vanities' -> 'all his workes, the pompes and vanities' "
                "(per the page's footnote). No other catechism-body change is apparatused.")
    if ed == "1662":
        return ("1662 Church of England, from the CoE website (PD outside the UK; Crown copyright within "
                "the UK). Site chrome stripped; the heading split ('A Catechism' / 'That is to say' / 'An "
                "Instruction...') recombined into one title line. `BCP 1662`. Catechism-only page (ends at "
                "the Lord's-Supper answer '...be in charity with all men').")
    if ed == "1789":
        return ("American 1789; standalone Catechism page (1789/Catechism.htm), NOT bundled with "
                "Confirmation. Post-1604 form (with Sacraments). American changes vs 1662: 'My "
                "Sponsors in Baptism' (for 'Godfathers and Godmothers'), 'To honour and obey the "
                "civil authority' (for 'the King, and all that are put in authority under him'), and "
                "'from our spiritual enemy' (for 'ghostly enemy'). Unlike the English editions, the "
                "1789 catechism page prints its own concluding catechizing rubrics ('The Minister of "
                "every Parish shall diligently…') — kept here under ## The Rubrics, as they are not in "
                "the separate 1789 confirmation.md. A justus editorial note ('The Catechism text in the "
                "1892 Book is identical…') is dropped as non-liturgical.")
    if ed == "1637":
        return ("Scottish 1637; the Catechism is bundled on the Confirmation page "
                "(Scotland/Confirmation_1637.htm). Post-1604 form (has the Sacraments section). The title "
                "carries the Scottish clause 'and to be used throughout the whole Church of Scotland'.")
    if ed == "1928":
        return ("American 1928; the Catechism was recast as the 'Offices of Instruction' (two Offices with "
                "prayers, hymnody rubrics, and Minister/People responses interwoven with the Q&A), bundled "
                "on the Confirmation page (Confirnation.htm — source filename typo). Represented here under "
                "catechism.md as the 1928 lineal form (the recasting is the meaningful v1892->v1928 diff); "
                "its own headings (First/Second Office, The Creed, The Ten Commandments, The Church, The "
                "Sacraments, The Ministry, ...) are the anchors. The Offices' concluding confirmation-"
                "transition rubric ('So soon as Children...') stays in confirmation.md.")
    if ed == "1979":
        return ("American 1979; 'An Outline of the Faith, commonly called the Catechism' — the "
                "contemporary-language recasting (a commentary on the creeds in Q&A form), from the "
                "public-domain ASCII e-text bcpprayr.txt via ingest/transform_1979_catechism.py "
                "(source -> script -> file; text never re-typed). Its own section headings (Human Nature, "
                "God the Father, ... The Christian Hope) are the anchors; opens with its 'Concerning the "
                "Catechism' preface. Mechanically reflowed — the e-text carries scattered typos (e.g. "
                "'knows' for 'known', 'give' for 'given', 'principle' for 'principal', 'response of God' "
                "for 'response to God'); verify against a page scan before sign-off.")
    return None

VERIFY_RE = re.compile(r"<!--\s*VERIFY\b(.*?)-->", re.DOTALL | re.I)
QUOTED_RE = re.compile(r"'([^']+)'")


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

prov_lines = ["", "  # ---- Wave 7: the Catechism ----"]
src_rows = []
for ed in sorted(URL):
    path = f"{WT}/editions/{ed}/occasional-offices/catechism.md"
    vitems = scan_verifies(path)
    rec = [f"  - edition: {ed}",
           "    service: occasional-offices/catechism",
           f"    source_url: {URL[ed]}",
           "    retrieved: 2026-08-13",
           "    cross_check: []",
           f"    status: {STATUS[ed]}",
           "    depth: tier-1",
           "    verifier: bcp-authoring"]
    nt = note_for(ed)
    if nt:
        rec.append(f'    note: "{nt}"')
    if vitems:
        rec.append("    verify_items:")
        for anchor, reading, body in vitems:
            rec.append(f"      - anchor: {yd(anchor)}")
            rec.append(f"        source_reading: {yd(reading)}")
            rec.append(f"        note: {yd(body)}")
            src_rows.append(f"| {ed} Catechism | `{reading}` | {body} |")
    else:
        rec.append("    verify_items: []")
    prov_lines += rec + [""]

# 1892: reviewed-unchanged, inherits 1789 (identical catechism, no file).
prov_lines += [
  "  - edition: 1892",
  "    service: occasional-offices/catechism",
  f"    source_url: {URL['1789']}",
  "    retrieved: 2026-08-13",
  f"    cross_check: [{PDF_1892}]",
  "    status: reviewed-unchanged",
  "    depth: tier-1",
  "    verifier: bcp-authoring",
  '    note: "American 1892; the Catechism is identical to 1789 — justus states \'The Catechism '
  "text in the 1892 Book is identical and so is not given separately', and this was confirmed against "
  "the 1892 Catechism&Confirm PDF (a WordPerfect scan with minor OCR noise but no substantive "
  'change). Inherited from 1789 (no separate file)."',
  "    verify_items: []", ""]

open(f"{WT}/ingest/wave7_provenance_block.yaml", "w").write("\n".join(prov_lines))
open(f"{WT}/ingest/wave7_sources_rows.md", "w").write("\n".join(src_rows) + "\n")
print("PROVENANCE records + SOURCES rows written.")
print("editions:", ", ".join(sorted(URL)))
print("verify_items (SOURCES rows):", len(src_rows))
for r in src_rows:
    print("  ", r)
