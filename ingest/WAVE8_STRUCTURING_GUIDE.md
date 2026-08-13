# Wave 8 — Ordinal structuring guide (for edition authors / subagents)

You are structuring ONE edition of ONE ordination service (Deacons, Priests, or
Bishops) into the repo format. The words are already transcribed in a byte-faithful
*spine* file. Your job is to add MARKDOWN STRUCTURE (`##` anchors, `> ` rubrics,
`**Label.**` speaker labels) around those words — **never change, add, paraphrase,
modernize, reorder, or invent words.** Exact-source diffs are the whole point;
fabrication is the cardinal sin. When the spine is unclear, keep it as printed and
flag inline `<!-- VERIFY: 'reading' … -->` (doubtful reading FIRST, single-quoted).

## Format (match the exemplars under editions/1549/ordinal/)
- `# ` one title line (title-case the source title, keep the edition's own spelling).
- `## ` anchors from that order's menu below, in the order the SOURCE presents them;
  include only anchors the edition actually has; a section's presence/absence or a
  rename is itself a meaningful diff.
- `> ` for every rubric (italic instruction in the source: "Then the Bishop shall…").
- `**Label.**` bold speaker labels AS PRINTED (`**Answer.**`, `**The Bishop.**`,
  `**The Archbishop.**`). A spoken response keeps its own line.
- One unit per line; blank line between blocks. Keep `[optional]` / bracketed
  rubric options exactly as printed. Keep the ` : ` mediant in Litany invocations.
- DROP page furniture only: site chrome, "Copy to clipboard", app/nav blurbs,
  the Crown-copyright/CUP acknowledgement footer, image captions, printer colophons.

## Per-order anchor menus (fixed by the 1549 flagships — REUSE the names)
Reuse these anchor NAMES so shared sections diff as body changes across editions.
The three orders differ in internal order; follow each order's own sequence.

**Deacons** (`ordinal/ordering-deacons.md`):
`## The Presentation` / `## The Litany` / `## The Epistle` /
`## The Oath of the King's Supremacy` (1662 has no oath here — the Oath of the
Queen's/King's Supremacy was dropped; 1662 instead has the Collect/Epistle/Gospel of
the Communion — use `## The Collect` / `## The Epistle` / `## The Gospel` as printed)
/ `## The Examination` / `## The Ordering` / `## The Communion`.

**Priests** (`ordinal/ordering-priests.md`):
`## The Epistle` / `## The Gospel` / `## Veni, Creator Spiritus` /
`## The Presentation` / `## The Litany` / `## The Oath of the King's Supremacy` /
`## The Exhortation` / `## The Examination` / `## The Prayer` / `## The Ordering` /
`## The Communion`.

**Bishops** (`ordinal/consecration-bishops.md`):
`## The Epistle` / `## The Gospel` / `## The Presentation` /
`## The Oath of Due Obedience` / `## The Litany` / `## The Examination` /
`## Veni, Creator Spiritus` / `## The Consecration` / `## The Delivery of the Bible` /
`## The Communion`.

For 1662/American editions the exact section set differs (e.g. 1662 prints the
Collect/Epistle/Gospel of the Communion, the Nicene Creed, the Veni Creator in two
metrical forms, and the post-Communion collects). Use the menu names where a section
corresponds; add a clearly-named `## ` anchor for anything the source has that the
menu lacks (e.g. `## The Collect`, `## The Nicene Creed`). Note every added anchor in
your report.

## The 1662 flagship (do NOT smooth it away)
- The forms of ordination gain the explicit order-naming:
  Priests: "Receive the Holy Ghost **for the office and work of a Priest** in the
  Church of God, now committed unto thee by the imposition of our hands…"
  Bishops: "Receive the Holy Ghost **for the office and work of a Bishop**…"
  (Deacons keep "Take thou Authority to execute the Office of a Deacon…".)
- The Litany gains "and rebellion" / "and schism" (as in the 1662 Great Litany).
- Keep these exactly; they are the point of the v1604→v1662 diff.

## Royal names in the 1662 Litany (IMPORTANT — keep source + VERIFY)
The CoE source prints the CURRENT Royal Family (e.g. "CHARLES … King", "Queen
Camilla, William Prince of Wales"). Keep the source text verbatim, and add a
`<!-- VERIFY names: … reign-dependent; reconcile against a dated 1662 page scan -->`
on the sovereign line and on the Royal-Family line — matching the existing
editions/1662/the-litany/litany.md treatment. Do NOT substitute period names from
memory.

## Self-check before finishing (REQUIRED)
```
python3 ingest/fidelity_check.py editions/1662/ordinal/<file>.md ingest/spines-w8/<spine>.md
```
Fix any typo you introduced; justify obvious OCR fixes only. Goal: CLEAN or a short
list of justified fixes.

## Report back (do NOT paste the liturgical body)
Return only: (1) file path written; (2) ordered `##` anchors used (flag any added
beyond the menu); (3) line count; (4) fidelity_check result + one-line justification
per flagged word; (5) each `<!-- VERIFY -->` you added, with its reason.
