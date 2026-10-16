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

## R11 — A publisher's own file outranks a volunteer keying of the same book
*Wave 19, 2026-09-18.*

Church Publishing's PDF of the 1979 book and justus's 1993 ASCII e-text are
witnesses of different CLASSES, so R6 is satisfied and the publisher's file
settles a disagreement. Two limits came with it and generalize to any
born-digital witness: its text layer renders the book's small-capital LORD as
"Lord", and it drops the pointing asterisk in about ten verses. **Neither
letter-case nor pointing may be taken from such a file** -- exactly as page
OCR cannot settle `:` against `;` (R7's habit of asking what a witness cannot
say).

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

## R12 — Where a witness is the ONLY source, transcribe it in its own spelling
*(maintainer), Wave 20, 2026-09-25. Refines R7.*

R7 forbids using a witness that disclaims its orthography to OVERRULE another
text's spelling. It does not forbid transcribing that witness where it is the
only source there is. The 1662 Kalendar, Proper Lessons, Proper Psalms and
the two reading rubrics exist on no allow-listed host except the Annexed Book,
so they are transcribed **as the manuscript prints them** — `Epiphanie of our
Ld`, `Hilarie B. &, Conf.`, `Matth.`, `onely`, `vpon` — and the provenance
and `SOURCES.md` say these are the MS's spellings, not the printed Sealed
Books'. Regularizing would mean inventing forms, or borrowing them from
another edition (R1, R2). `texts/normalized` smooths spelling as usual (R9).

Consequence, accepted: those files are in MS orthography while the rest of the
1662 node is the Church of England's modernized text, so a 1559 -> 1662 diff
on them shows two printings' spelling as well as real change.

*Reopened by:* a scan of a printed 1662 book (as for R8). *Not decided by
this:* the communion admission rubric (open question below), where a
modernized carrier cell exists and the question is substitution.

## R13 — Lectionary tables: chapter numerals in arabic; the calendrical apparatus is out
*(maintainer), Wave 20, 2026-09-25, confirming Wave 14's Ruling B and its
citation rule, which until now lived only in `ingest/WAVE14_GUIDE.md` (R10).*

- **Numerals.** Roman chapter numerals are converted to arabic, and the
  printed extent is kept verbatim (`ix to vr. xx` -> `9 to vr. 20`, never
  `9:1-20`). Every Kalendar and Proper Lessons file in the corpus is arabic,
  so a converted cell diffs on its reading, not its notation. Printed marks
  inside a cell (`vi *`) are kept.
- **Apparatus.** The Golden Number, the Roman date (Kalends/Nones/Ides), the
  lunar line (`The Moon hath xxx.`) and the Easter/moveable-feast grids are
  EXCLUDED as computational apparatus — excluded at 1549–1559 from books
  that also print them, so adding them at one edition alone would show them
  falsely "appearing" there. Each exclusion is stated in that file's
  provenance record.
- **Columns the book lacks are omitted, not blanked.** 1662 prints no
  Psalter-day column, so its rows carry no `Psalter Day:` field (as 1789's
  rows do not). A lesson cell the book leaves blank (a holy day, whose lessons
  are in the proper table) is `—`.
- The occasion column's ordinals in the Proper Lessons (`ii`, `xiv`) are
  LABELS, not chapter numbers, and stay roman as printed; so do the Kalendar
  notes. The month heading (`January hath xxxj. dayes`) is carried by the
  `## January` anchor, as in every other Kalendar here.
- What the note column prints goes in `Kalendar Note:`, including `Fast`; a
  month's footnote is a row of its own at the foot of that month,
  `Footnote | <the note as printed>`, so that R17 keeps it whole (as prose the
  splitter would break it at `Exodus 6. is`).

*Reopened by:* a decision to carry the apparatus corpus-wide, which would need
1549–1559 sources that print it (justus's `bcp/` tree is 403 as of
2026-09-25).

## R14 — A second rendering of one file is not a second witness
*Wave 20, 2026-09-25.*

The Annexed Book PDF's June Kalendar page (PDF p. 49) stores its text in a
JBIG2 mask that macOS cannot decode ("Too many symbols in JBIG2 symbol
dictionary"), so every local render of it is blank. Wikimedia's own
server-side rendering of the SAME file
(`…/thumb/4/49/The_Book_of_Common_Prayer.pdf/page49-1920px-…jpg`, fetched
with the scraper's guardrails by `ingest/w20_fetch.py`) decodes it legibly,
and June is read from that. It is the same witness through a different
decoder — usable where the local decoder fails, but never counted as
corroboration (R6), and its use is stated in provenance.

## R15 — 1662's Proper Lessons fit the row model; Proper Psalms come with them
*(maintainer), Wave 20, 2026-09-25.*

`SOURCES.md` recorded "1549–1662 Proper Lessons" as some thirty
per-occasion tables no row model fits. Checked against the scan (PDF pp.
36–38), that is **not true of 1662**: it prints ONE table in two sections
(Sundays; Holy-days), each row an occasion with Mattens and Evensong
readings and, for some occasions, `1. Lesson` / `2. Lesson` sub-rows — the
1789 model exactly. So 1662 gets `tables/proper-lessons.md` in that shape
(Sunday rows carry only the lessons the book prints), and the gap row
narrows to 1549–1604. That narrowed claim rests on those books' own sources
and was **not** re-checked in Wave 20.

The same page prints *Proper Psalms on certein Daies* (six occasions), which
`v1662` lacked with no gap recorded anywhere — a silent absence. It is
transcribed at 1662 as `tables/proper-psalms.md`.

*Reopened by:* a 1549–1604 scan showing whether those books' tables fit the
model too.

## R16 — Setting the Annexed Book's type: typeface, superscripts, signs, letters, spacing
*Wave 20, 2026-09-25 (my call, following corpus practice; the maintainer may
overturn it).*

The Annexed Book's Kalendar sets the greater holy days in bold black-letter
and the lesser commemorations in italic. No table in the corpus encodes
typeface (1559's `§` is a glyph from its justus source, not a convention of
this repo), and the distinction is recoverable from what the tables do say:
a greater holy day has a blank lesson cell and an entry in the Proper Lessons
table. So typeface is not marked. Superscript letters (`Ld` with raised d,
`ye` with raised e) are set inline on the line (`Ld`, `ye`), not expanded
(`Lord`, `the`), since expansion is an editorial reading the book does not
print. A scribal abbreviation sign is set as its Unicode character, not
expanded: `Gregoriꝰ` (U+A770, the -us sign), not `Gregorius`.
The line is drawn by what the sign DOES: a sign that stands in place of
letters the word otherwise lacks is set (`Gregoriꝰ`; the tilde of
`Añunciation`, which stands for the second n); a mark that only FLAGS an
abbreviation over letters that are all printed is not carried, as typeface is
not — so `Ecclus`, which the type marks with a stroke through the l in the
Kalendar and a tilde or cross above it in the Proper Lessons, is set plain.
Letters are set by the glyph the type shows: where the witness's italic or
black-letter capital is the J-form it is set `J` even where it stands for I
(`Jnnocents day.`, `Jsai. 2`), and the I-form is set `I` (`Iudeth`, `Iohn`);
nothing is regularized to either. Readings that look like slips but are
plainly what the type prints (`S Thomos Apost.`) are kept and marked *sic*
in the provenance record, so a later pass does not "correct" them.

In the prose rubrics a line-end hyphen is rejoined (`ap-|pointed`), and the
1892 compositor's space before `;` and `:` is closed up — except the
pointing colon of the Gloria, which stays ` : ` as the corpus prints the
Psalter's. Prose is split by the build as usual, so a numeral's stop makes a
false line break (`in the time of K.` / `H.` / `viii.`) exactly as it already
does in the published 1549 rubric (`And where the cxix.` / `Psalme is…`);
allow-listing `vi`/`viii` would change other editions' published lines, so
it was not done.
A mark that is neither a letter nor an abbreviation sign (the accent over
the n of `Lessońs` in the Scripture rubric) is not carried.

The pilcrow the Proper Psalms table sets before each occasion, and its
`Psalm.` column head, are not carried (the rows use 1789's `Morning:` /
`Evening:` fields); stacked psalm numbers are joined with `, ` as 1789's are.

*Reopened by:* a decision to mark the red-letter/black-letter distinction
corpus-wide.

## R17 — A table row is one unit; the sentence splitter leaves it whole
*Wave 20, 2026-09-25 (my call; a tooling decision the maintainer may revisit).*

`tools/sentence_split.py` breaks a line at `. ` unless the word before is an
allow-listed abbreviation or the next character is a digit. The 1662
Kalendar's cells print their own stops — `Hilarie B. &, Conf.`,
`Luke 1. to 39`, `1. Sam. 2`, `Bl. V. M.` — and splitting there would cut a
row in two. Two remedies were weighed: grow the abbreviation list (which can
silently change how OTHER editions' prose splits, since the build splits
authored text in place), or treat a row as the unit, as the Psalter treats the
verse. The second was taken: a line containing ` | ` is never split.

Measured before the change: across every `tables/` and `psalter/selections`
file in the corpus exactly ONE row depended on the build splitting it —
1789's Proper Psalms, authored with the title fused onto the Christmas row.
That source line was pre-split, so its published text is unchanged; the
full-build diff is the proof that nothing else moved (confirmed in Wave 20:
`texts/` identical to the live tags in every tag but `v1662`). Prose lines (no ` | `)
split exactly as before.

A consequence for the lesson cells: the Wave-14 "trailing-period trap" no
longer bites, but the cell-final stop is still dropped (R13) so that cells
diff against the other editions' on their readings.

*Reopened by:* any table format whose row legitimately spans sentences.

## R18 — A containment gate pins the `authoring` commit its wave started from, never a live tag
*2026-10-16 (my call, at the start of the Wave 21 session; a tooling decision
the maintainer may revisit).*

Waves 17–19 wrote their containment gates ("the published cells plus exactly
this wave's corrections equal the new cells") against the live tag the wave
started from (`v1892`, `v1662^{commit}`, `v1979^{commit}`). Publishing
rewrites every tag (R4), so once a wave's own corrections were published the
gate began re-applying them to cells that already carried them:
`w17_gates` had failed since the Wave 17 publish of 2026-09-18, and the
Wave 18 and 20 guides list it as not run. A gate that cannot be run after its
wave ships enforces nothing (R10).

Ruled: the base of such a gate is the **`authoring` commit the wave started
from**, by full SHA, with the cells read from `editions/<year>/` there.
Authoring history is never rewritten; and an authoring cell equals its
published `texts/original` file apart from the inline flags and the build's
sentence split, which the gates already strip or compare on words. The three
gates were re-pinned (`c8fc6e2`, `6d290b4`, `7e4f14b`) and all pass again.
Every later wave's gate does the same from the start.

*Reopened by:* a change to the build that makes `texts/original` differ from
the authored cell in more than flags and line breaks.

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
