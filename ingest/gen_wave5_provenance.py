#!/usr/bin/env python3
"""Generate Wave 5 provenance.yaml records + SOURCES.md rows from the authored
occasional-offices files. verify_items are auto-extracted from each file's inline
<!-- VERIFY: '<key>' ... --> comments so the source_reading keys match exactly
(verify_index keys on the FIRST single-quoted reading). Prints the YAML block to
stdout and the SOURCES rows to stderr."""
import sys, glob, re, os

WT = sys.argv[1]
JUS = "http://justus.anglican.org/resources/bcp"
COE = "https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer"

# (service, edition) -> (source_url, status, note)
BAP = f"{JUS}/1549/Baptism_1549.htm"
DATA = {}

def put(svc, ed, url, status, note):
    DATA[(svc, ed)] = (url, status, note)

# ---- Public Baptism ----
put("public-baptism", 1549, f"{JUS}/1549/Baptism_1549.htm", "transcribed",
    "First Edwardian Public Baptism, ministered at the church door. Flagship for the 1552 simplification: it keeps the early signing with the cross (before the second prayer), the exorcism ('I commaunde thee, uncleane spirite'), trine immersion (dipping thrice), the white vesture (Chrisom), and the anointing -- all of which 1552 removes. Church-door/font rubrics kept as printed.")
put("public-baptism", 1552, f"{JUS}/1552/Baptism_1552.htm", "transcribed",
    "Second Edwardian Public Baptism, the famous simplification: the exorcism, the early cross-signing, trine immersion, the chrisom and the anointing are all removed; a single dip and combined vows are used; the Prayer over the Children and the Blessing of the Water are added; the signing with the cross moves to AFTER the baptism; and the Reception and the Thanksgiving after Baptism are added. Ministered at the font (not the church door). git diff v1549 v1552 exposes the reform (README).")
put("public-baptism", 1559, f"{JUS}/1559/Baptism_1559.htm", "transcribed",
    "Elizabethan Public Baptism. Structurally the 1552 rite. Transcribed from the justus 1559 page, which interleaves the 1604 variant readings (footnoted); only the 1559 readings were taken here (the 1604 readings are used in the 1604 files).")
put("public-baptism", 1604, f"{JUS}/1559/Baptism_1559.htm", "reviewed-unchanged",
    "Jacobean Public Baptism. The public-baptism office is unchanged from 1559 (baptism carries no sovereign's name, so the Jacobean monarch change that drove the 1604 Morning/Evening Prayer, Litany and Communion does not touch it); this cell inherits the 1559 office. The only 1604 public-baptism variant the justus 1559 apparatus records is a single spelling nuance in the Flood Prayer ('thy'/'the'), flagged on the 1559 text and not separately applied. (The 1604 changes to private baptism and to the catechism are handled in their own files.)")
put("public-baptism", 1662, f"{COE}/public-baptism-infants", "transcribed",
    "Standard Church of England Public Baptism, from the CoE website (authoritative 1662 publisher; Crown copyright in the UK). Adds the distinct Blessing of the Water ('Almighty everliving God, whose most dearly beloved Son...') as a section in its own right, the Prayer over the Children, and the Reception; the signing with the cross follows the baptism; the closing rubrics carry the confirmation cross-reference and the 30th-Canon (1604) note on the sign of the cross. [square brackets] kept as BCP optional-text typography.")
put("public-baptism", 1637, f"{JUS}/Scotland/Baptism_1637.htm", "transcribed",
    "Scottish 'Laud's Liturgy' Public Baptism. Follows the 1552/1559 shape with 'Presbyter or Minister' throughout; no sovereign's name appears in the office. A bracketed font-hallowing clause is keyed by an asterisk to the font-water rubric (kept as source typography).")
put("public-baptism", 1789, f"{JUS}/1789/Baptism_1789.htm", "transcribed",
    "First American Public Baptism of Infants (the public portion of the 1789 baptism page). The justus e-text renders each rubric's opening pilcrow as a mojibake glyph (dropped as a corrupted marker; mechanical, noted in the file).")
put("public-baptism", 1892, f"{JUS}/1892/Baptism_1892.htm", "transcribed",
    "American 1892 Public Baptism of Infants (public portion). The justus e-text carries a couple of OCR letter-scannos ('graft' for 'grant', 'sternal' for 'eternal'), kept as printed and flagged.")
put("public-baptism", 1928, f"{JUS}/1928/Baptism.htm", "transcribed",
    "American 1928 Holy Baptism (the single office folds infant and adult baptism together via alternate 'When the Office is used for Children/Adults' address blocks, both kept). This edition OMITS the Flood Prayer (only the 'aid of all who need' second prayer survives), prints all three Gospel options (Mark/John/Matthew), the Sursum Corda before the water-blessing, and closes with the apostolic benediction (Ephesians 3) as its Blessing; there is no separate 'Forasmuch' final exhortation.")
put("public-baptism", 1979, f"{JUS}/bcpspecl.txt", "transcribed",
    "Current American Holy Baptism, from the public-domain ASCII e-text (bcpspecl.txt) mechanically reflowed by ingest/transform_1979_baptism.py (source -> script -> file; the modern text is never re-typed, which also avoids an output content-filter false-positive). The 1979 book has a single contemporary-language rite for all ages, so its printed section headings are the anchors and the diff against 1928 reads as the wholesale modern restructure. Mechanically reflowed; verify against a page scan before sign-off.")

# ---- Private Baptism ----
put("private-baptism", 1549, f"{JUS}/1549/Baptism_1549.htm", "transcribed",
    "First Edwardian Private Baptism ('Of them that be baptized in private houses in time of necessity'). Keeps the White Vesture step and a separate Creed step; ends with the conditional 'If thou be not baptized already' form. (The 1549 font-hallowing 'Blessing of the Font' prayers printed after this office are deferred to a later occasional-offices pass.)")
put("private-baptism", 1552, f"{JUS}/1552/Baptism_1552.htm", "transcribed",
    "Second Edwardian Private Baptism. Mirrors the 1552 public simplification: the White Vesture is gone and the Creed is folded into the combined vow.")
put("private-baptism", 1559, f"{JUS}/1559/Baptism_1559.htm", "transcribed",
    "Elizabethan Private Baptism. Transcribed from the 1559 readings on the justus page (the 1604 expansions interleaved there are used in the 1604 file, not here).")
put("private-baptism", 1604, f"{JUS}/1559/Baptism_1559.htm", "transcribed",
    "Jacobean Private Baptism -- the Hampton Court reform. Derived from the 1604 readings interleaved on the justus 1559 page (no separate 1604 book survives there). 1604 restricts the office to a lawful Minister (the added subtitle '[By the lawful Minister...]' and 'the said lawfull Minister' in the form); expands the doubt-rubric to the parish-minister certification; adds a fuller examination ('And because some things essentiall... I demand further of you'); reads 'finde'/'bring'/'all is well done' in the certificate; and reads 'such uncertaine answers' in the conditional rubric. Sections not flagged as changed are the shared 1559/1604 text.")
put("private-baptism", 1662, f"{COE}/private-baptism-infants", "transcribed",
    "Standard Church of England Private Baptism of Children in Houses, from the CoE website. Carries the minister's certification and the receiving-into-the-church / examination / certificate sequence; [square brackets] kept as BCP typography.")
put("private-baptism", 1637, f"{JUS}/Scotland/Baptism_1637.htm", "transcribed",
    "Scottish 'Laud's Liturgy' Private Baptism, with 'Presbyter or Minister' wording throughout.")
put("private-baptism", 1789, f"{JUS}/1789/Baptism_1789.htm", "transcribed",
    "First American Private Baptism of Children (the private-houses portion of the 1789 baptism page). The 1789 source encloses a 'Wilt thou be baptized in this Faith?' exchange in brackets with a footnote calling it an error later omitted in 1832; kept as the 1789 printed text (editorial brackets/asterisk/footnote dropped) and flagged.")
put("private-baptism", 1892, f"{JUS}/1892/Baptism_1892.htm", "transcribed",
    "American 1892 Private Baptism of Children (private portion); the erroneous 'Wilt thou be baptized' exchange is already absent here.")
put("private-baptism", 1928, f"{JUS}/1928/Baptism.htm", "transcribed",
    "American 1928 private-baptism material: the short Private Baptism emergency form, The Receiving of One Privately Baptized, and Conditional Baptism (each printed sub-title given its own heading).")
put("private-baptism", 1979, f"{JUS}/bcpspecl.txt", "transcribed",
    "Current American 'Emergency Baptism' -- the modern equivalent of Private Baptism -- plus the Conditional Baptism rule, from the public-domain ASCII e-text (bcpspecl.txt) via ingest/transform_1979_baptism.py (source -> script -> file). Mechanically reflowed; verify against a page scan before sign-off.")

# ---- Baptism of Riper Years ----
put("baptism-riper-years", 1662, f"{COE}/public-baptism-such-are-riper", "transcribed",
    "The Ministration of Baptism to such as are of Riper Years -- a wholly new office ADDED in 1662 (occasioned by the baptism of adults after the Commonwealth and in the growing colonies). Follows the infant office's shape but for adults answering for themselves (Question/Answer labels), with the Nicodemus Gospel (John 3) in place of Mark 10; the closing rubric cross-references the infant offices. From the CoE website.")
put("baptism-riper-years", 1789, f"{JUS}/1789/Baptism_1789.htm", "transcribed",
    "First American Baptism to such as are of Riper Years (the adult-baptism portion of the 1789 baptism page). The justus e-text carries recurring 'he'-for-'be' and 'm'-for-'in' scannos in the trailing directions, kept as printed and flagged.")
put("baptism-riper-years", 1892, f"{JUS}/1892/Baptism_1892.htm", "transcribed",
    "American 1892 Baptism to such as are of Riper Years (adult portion). Same class of e-text 'he'-for-'be' scannos in the closing directions, kept as printed and flagged.")

# ---- Confirmation ----
put("confirmation", 1549, f"{JUS}/1549/Confirmation_1549.htm", "transcribed",
    "First Edwardian Confirmation. The page bundles the Catechism (deferred to the Catechism wave); only the Confirmation office is transcribed. 1549 keeps the signing with the cross ('I sign thee with the sign of the cross') and the 'Sign them, O Lord' versicle, and the sevenfold-gifts prayer prays God to 'send down from heaven... thy holy ghost'.")
put("confirmation", 1552, f"{JUS}/1552/Confirmation_1552.htm", "transcribed",
    "Second Edwardian Confirmation, the flagship 1549->1552 change: the signing with the cross is REMOVED and the imposition of hands takes the enduring form 'Defend, O Lord, this child with thy heavenly grace...'; the versicle pair 'The Lord be with you / And with thy spirit' becomes 'Lord, hear our prayer / And let our cry come to thee'; the sevenfold prayer is reworded ('strengthen them... daily increase in them thy manifold gifts'). git diff v1549 v1552 exposes the change.")
put("confirmation", 1559, f"{JUS}/1559/Confirmation_1559.htm", "transcribed",
    "Elizabethan Confirmation (1552 shape). Transcribed from the 1559 readings on the justus page; the two 1604 word-variants it footnotes ('bothe' removed, 'prayer'->'prayers') are applied in the 1604 file.")
put("confirmation", 1604, f"{JUS}/1559/Confirmation_1559.htm", "transcribed",
    "Jacobean Confirmation, derived from the 1559 office via the justus 1559 apparatus (no separate 1604 page survives there). The two documented office changes are applied: 'bothe' is removed from the versicle response ('Which hath made heaven and earth') and 'prayer' becomes 'prayers' ('Lord hear our prayers'). The famous 1604 addition to the CATECHISM (the sacraments Q&A) belongs to the Catechism service (a later wave), not this office.")
put("confirmation", 1662, f"{COE}/order-confirmation", "transcribed",
    "Standard Church of England Order of Confirmation, from the CoE website. Adds over 1552 the Renewal of Vows ('Do ye here, in the presence of God, and of this Congregation, renew the solemn promise and vow...') after the preface, and a Lord's Prayer after the imposition of hands; no signing with the cross. [square brackets] kept as BCP typography.")
put("confirmation", 1637, f"{JUS}/Scotland/Confirmation_1637.htm", "transcribed",
    "Scottish 'Laud's Liturgy' Confirmation (1552 shape: imposition 'Defend, O Lord', no signing with the cross, no renewal of vows). Bundled catechism Q&A skipped.")
put("confirmation", 1789, f"{JUS}/1789/Confirmation_1789.htm", "transcribed",
    "First American Order of Confirmation. Carries the 1662 additions (Renewal of Vows, Lord's Prayer). A whole-word scanno ('under took' for 'undertook') kept as printed and flagged.")
put("confirmation", 1892, f"{JUS}/1892/Confirmation_1892.htm", "transcribed",
    "American 1892 Order of Confirmation, with a printed Presentation and an Acts 8 Lesson before the renewal. The salutation's speaker label is scrambled in the e-text (reconstructed and flagged); 'under took' scanno kept and flagged.")
put("confirmation", 1928, f"{JUS}/1928/Confirnation.htm", "transcribed",
    "American 1928 Order of Confirmation. The page bundles the Offices of Instruction (a catechism, deferred to the Catechism wave); only 'The Order of Confirmation' is transcribed. Adds a second renewal question ('DO ye promise to follow Jesus Christ...') and the Lord's-Prayer doxology. The salutation's speaker label is scrambled in the e-text (reconstructed and flagged). NOTE the justus filename is 'Confirnation.htm' (a typo in the source URL).")
put("confirmation", 1979, f"{JUS}/bcpastrl.txt", "transcribed",
    "Current American Confirmation (with forms for Reception and the Reaffirmation of Baptismal Vows), the first of the Pastoral Offices, from the public-domain ASCII e-text (bcpastrl.txt) via ingest/transform_1979_confirmation.py (source -> script -> file). NOTE: Confirmation lives in bcpastrl.txt, not bcpepscl.txt (which holds the Ordination rites). Mechanically reflowed; verify against a page scan before sign-off.")

# ---- auto-extract verify_items from the files ----
def verify_items(svc, ed):
    path = f"{WT}/editions/{ed}/occasional-offices/{svc}.md"
    if not os.path.exists(path):
        return []
    items, anchor = [], None
    for ln in open(path, encoding="utf-8"):
        if ln.startswith("## "):
            anchor = ln[3:].strip()
        m = re.search(r"<!--\s*VERIFY:\s*(.*?)-->", ln)
        if m:
            body = m.group(1).strip()
            key = re.search(r"'([^']+)'", body)
            if not key:
                continue
            items.append((anchor or "(preface)", key.group(1), body))
    return items

def yesc(s):  # minimal YAML double-quote escaping
    return s.replace("\\", "\\\\").replace('"', '\\"')

order = ["public-baptism", "private-baptism", "baptism-riper-years", "confirmation"]
eds = [1549, 1552, 1559, 1604, 1662, 1637, 1789, 1892, 1928, 1979]

out = []
out.append("")
out.append("  # ==================== Wave 5: Baptism family + Confirmation ====================")
sources_rows = []
for svc in order:
    out.append(f"  # ---- {svc} ----")
    for ed in eds:
        if (svc, ed) not in DATA:
            continue
        url, status, note = DATA[(svc, ed)]
        out.append(f"  - edition: {ed}")
        out.append(f"    service: occasional-offices/{svc}")
        out.append(f"    source_url: {url}")
        out.append(f"    retrieved: 2026-08-12")
        out.append(f"    cross_check: []")
        out.append(f"    status: {status}")
        out.append(f"    depth: tier-1")
        out.append(f"    verifier: bcp-authoring")
        if url.startswith(COE):
            out.append(f"    acknowledgment: \"BCP 1662\"")
        out.append(f"    note: \"{yesc(note)}\"")
        vis = verify_items(svc, ed)
        if not vis:
            out.append(f"    verify_items: []")
        else:
            out.append(f"    verify_items:")
            for anchor, key, body in vis:
                out.append(f"      - anchor: {anchor}")
                out.append(f"        source_reading: \"{yesc(key)}\"")
                out.append(f"        note: \"{yesc(body)}\"")
                sources_rows.append((f"{ed}", f"occasional-offices/{svc}", anchor, key, body))
        out.append("")

sys.stdout.write("\n".join(out))
# SOURCES rows to stderr
for ed, svc, anchor, key, body in sources_rows:
    sys.stderr.write(f"| {ed} | {svc} | {anchor} | `{key}` | {body} |\n")
