# RULINGS — the standing editorial decisions, and what would reopen them

Authoring-only (not stamped into published commits). **This is the register a
future session reads before deciding anything.** Each entry says what was
ruled, when, why, what it governs, and what evidence would reopen it. Waves
record their own detail in `ingest/WAVE*_GUIDE.md` and in `HANDOFF.md`; this
file exists so a decision is never re-litigated from memory, and so a decision
made for one passage is applied to the next one that looks like it.

Rulings marked **(maintainer)** were made by the repository's owner. The rest
are standing policies of the project, adopted in a wave and never since
contradicted; a maintainer can overturn any of them.

---

## R1 — Source every word; never invent, never transcribe from memory
*Standing, from the brief. Governs everything.*

Every published word comes from an allow-listed public-domain source, is
verified, and anything doubtful is flagged inline with `<!-- VERIFY: ... -->`
and indexed in `provenance.yaml` (authoring) and `SOURCES.md` (published).
Where a source is defective or missing, **record the gap**; do not reconstruct.

## R2 — No backward derivation
*(maintainer), Wave 13, 2026-09-11.*

Never reconstruct an older edition's text from a newer edition's text or from
its editorial apparatus. The first Wave-13 proposal derived the 1892 and 1789
psalters from the 1928 page's sidebar notes; it was withdrawn, because an
apparatus is only as complete as its editor — the absence of a note is not
evidence that nothing changed — and a derived text would pass the fidelity gate
while being wrong. Every edition comes from its own source; where there is
none, the edition is a **recorded gap** (1789's Psalter still is).

*Reopened by:* nothing short of a source for that edition itself.

## R3 — `absent:` is a positive historical claim
*Standing; learned in Wave 12, enforced after Waves 14 and 15.*

`absent:` in `editions.yaml` asserts that **the book does not contain the
section**. If a book has a section but no allow-listed source gives us its
text, the service is present-but-unauthored: it inherits, with
`status: inherited-unreviewed`, and the gap is stated in `NOTICE.md` and
`SOURCES.md`. Wave 14 had to correct two of its own locked rulings that would
otherwise have published false claims about the 1979 and 1637 books; Wave 15
added the corollary that **a table of contents is not evidence of absence** —
check the pages.

## R4 — Publishing is force-push, and needs an explicit go-ahead
*Standing, absolute.*

`build_history.py --publish` rewrites `main`, `scottish`, `american` and all
twelve `vYYYY` tags. Never run the pushes without the maintainer saying so in
that session. Afterwards record the published tips in `NOTICE.md`,
`HANDOFF.md` and the project memory, and verify local == remote for every ref.

## R5 — A file holds what its book prints under that title
*Wave 9 precedent (`of-ceremonies`), reused in Waves 11 and 16.*

Section identity is by **title and slug**, not by where the book physically
prints it. A prayer printed inline after the Litany in 1552 and as its own
section in 1662 keeps one path, so the diff shows the words changing rather
than a file moving; the change of placement is recorded as a book-order note in
`NOTICE.md` and the provenance record. The builder aligns by PATH — moving a
file manufactures a false deletion-plus-addition in the very diff the repo
exists to show.

## R6 — Two keyings are not two witnesses
*Waves 16–17.*

Two transcriptions that share freak errors (`Eqypt`, `stretch our her hands`)
are one witness, however independent they look. Corroboration requires a source
of a different KIND — a page image, an independently compiled change log. This
is why the 1892 Standard Book's keyed PDF was withdrawn as a witness in Wave 16
and only the page scan settled anything in Wave 17.

## R7 — Read a witness's own preface before collating against it
*Wave 18, 2026-09-18.*

A source can be authoritative about words and worthless about accidentals. The
**Annexed Book** — the manuscript annexed to the Act of Uniformity 1662, the
legal standard of that text — states in its 1892 printers' preface that the
printed Sealed Books "differ considerably from that original standard in
various details of orthography and punctuation" and that the MS was "not to be
a standard of orthography". So it settles **words and structure** and may never
be used to settle a spelling. Corollary: know which text you are collating.
For 1662 there are three — the Church of England's current authorized text
(our carrier), the Annexed Book (this witness), and the printed 1662 books (no
scan of one has been found on an allow-listed host).

## R8 — Print what the original copies print; where the original leaves a space, SHOW the space
*(maintainer), Wave 18, 2026-09-18. The governing rule for reign-dependent and
person-dependent readings.*

Where the carrier supplies a name that the original book does not have, prefer
the original. Where the original leaves a **blank** for a name to be supplied,
print the blank visibly — as a modern book does when it prints
`N. ________` — rather than carrying a living person's name or reconstructing
a historical one.

Applied in Wave 18 to the 1662 Prayer for the Royal Family (Morning Prayer,
Evening Prayer, the Litany, the Ordinal's litany): "Queen Camilla, William
Prince of Wales, the Princess of Wales, and all the Royal Family" is removed
and `________` is set in its place, because the Annexed Book leaves that
passage blank on the page. Three limits came with it:

- **An attested name is not blanked.** The book prays for "King Charles", so
  the monarch stands as the source prints him.
- **Nothing is reconstructed into the blank.** What the printed Sealed Books
  named there is unknown; that stays flagged, and a scan of a Sealed Book
  would resolve it.
- **A heading is not changed to match a witness.** The Annexed Book's title
  breaks off at "A Prayer for"; the cell keeps `## A Prayer for the Royal
  Family`, because headings are the anchors this service diffs on across nine
  editions (see R5). The unfinished title is recorded in the flag.

Also applied: the 1662 Sea rubric now reads "his Majesty's Navy" (the book:
"also vsed in his Majesties Navy every day"), which is a word and so within
what the witness can settle (R7).

*Reopened by:* a scan of a printed 1662 book, which would supply the names
that belong in the blank.

## R9 — Normalization is spelling only
*Standing (`tools/normalization_rules.yaml`).*

`texts/normalized` may change spelling and nothing else — never vocabulary,
word order or punctuation — and the rules are ordered, transparent and
deterministic.

## R10 — A rule that lives only in a guide is not enforced
*Wave 18.*

Two lines of Church of England website chrome sat inside a published 1662 file
from Wave 6 to Wave 18, although the Wave-8 structuring guide said to drop site
furniture. It took a gate (`ingest/w18_gates.py`, corpus-wide) to catch it.
**When a wave states a rule, ask what would fail if it were broken**, and write
that check.

---

The work queue that these rulings govern is kept in `HANDOFF.md` §8, under
"THE QUEUE, in priority order", with the reachability of each source as it was
last checked.

## Open questions awaiting a ruling

- **The 1662 communion admission rubric.** What the carrier prints (an account
  to the Ordinary, seven days, an opportunity for interview) is no part of the
  1662 text: the Annexed Book prints the "open and notorious evil liver" rubric
  of 1549–1604 (scan page 246). Substituting it would mean setting a paragraph
  of the manuscript's own orthography inside an otherwise modernized cell —
  which R8 does not settle, because this is a whole paragraph of different
  text, not a blank. Options: leave it flagged as now; set the Annexed Book's
  rubric in the MS's spelling, marked; or wait for a printed-1662 scan.
  Flagged inline and in `SOURCES.md`.
- **The 1945 lectionary revision** (Wave 14, maintainer-ruled to omit). justus
  publishes the 1928 lectionary twice; `v1928` carries the original (in use
  1928–1944). If the 1945 revision is ever wanted it needs its own
  representation — a second node or a sibling file — never a silent overwrite.
- **The 1789 Psalter** remains a recorded gap under R2; justus's dated change
  table could inform a future attempt, but the maintainer ruled it out as a
  source to derive from.
