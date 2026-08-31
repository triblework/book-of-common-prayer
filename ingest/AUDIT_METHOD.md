# Verification method: two gates, not one

Authoring-only, and deliberately **wave-agnostic**. Wave 10 is where the second
gate was first written, but nothing here is specific to the propers. Read this
before designing verification for any future wave or audit initiative.

## Why one gate is not enough

The prime directive has two distinct failure modes, and they need different
instruments:

| failure | question | instrument |
|---|---|---|
| **fabrication** | did text appear that the source does not attest? | `ingest/fidelity_check.py` (+ a wave wrapper) |
| **silent loss** | did text the source attests quietly fail to arrive? | `ingest/w10_audit.py` (the pattern below) |

A fidelity gate compares authored words against the source spine, so it catches
invention. **It is structurally blind to omission**: if a parser drops a whole
section, every remaining word is still perfectly attested and the gate stays
green. That is the more dangerous failure, because the output looks clean and the
diff looks intentional — a missing section reads as "this edition didn't have
it", which is a false historical claim rather than an obvious error.

This is not hypothetical. In Wave 10c the audit found:

- **The Passion Gospels had vanished** from Palm Sunday and Good Friday in all
  three English editions. The apparatus column sometimes quotes a reading in
  full, beginning with the very citation line it discusses, and the apparatus
  filter's substring test suppressed the genuine line.
- **Holy Week days had lost their readings.** Skipping the Introit block for
  books that print no Introit also skipped the days that carry readings but no
  collect.

Fidelity was green throughout. Both were caught only by asking a different
question.

## The pattern (reusable)

`ingest/w10_audit.py` implements it for per-occasion files; the shape generalizes
to any family where the same logical unit exists across editions:

1. **Build the anchor set per (unit, edition)** — the `##` headings in each cell.
2. **Take the cross-edition majority** for each anchor. An anchor most editions
   carry is a structural expectation, not an accident.
3. **Report any edition missing a majority anchor.**
4. **Exempt what is genuinely the book, explicitly.** Two tiers, both in the
   script and both auditable:
   - `EXPECTED_ABSENT` — categorical rules ("only 1549 prints Introits";
     "1979 carries no single Epistle/Gospel").
   - `KNOWN_GOOD` — a specific `(unit, edition, anchor)` with a one-line reason
     ("1549–1559 print no proper Collect for Easter Even; 1662 adds one").
5. **Report, do not fail.** Legitimate absence is common in this corpus, so the
   audit is a review instrument. Its target state is zero anomalies with every
   exemption carrying a written reason — which is itself a record of what each
   book does and does not contain.

## Rules of thumb

- **Run it every sub-wave**, alongside fidelity. Cheap, and it front-runs the
  build.
- **An exemption must state a source-checked reason.** An exemption without one
  is a silenced bug. When adding one, confirm the absence against the source
  first — that is how the Easter Even and Holy Week collect-less days were
  established as features rather than faults.
- **A count that comes up short is a finding.** Several Wave-10 bugs surfaced as
  a cell count one or four lower than expected, before the audit even ran. Assert
  expected counts where they are known.
- **Suspect empty diffs.** The 1928 variant-leakage bug showed up as `git diff`
  producing *nothing* between two editions that certainly differ. An empty diff
  where change is expected is evidence, not reassurance.
- **When a parser is fixed, re-run both gates over everything**, not just the
  cell that failed. The fixes in 10c changed output for occasions that had never
  been flagged.


## Corollary: prefer a structural discriminator to a content filter

Wave 10d ended by deleting a filter rather than improving it, and that is the
transferable lesson.

The propers pages are two-column. The apparatus column **quotes the text it
discusses** — often a whole collect or a whole reading. So a filter that decides
"is this line apparatus?" from the line's *content* is attempting something
impossible: the genuine line and the quoted line are the same words. Every
version of that filter silently deleted real text, and each fix only moved the
failure somewhere new.

The fix was to stop filtering and read the **left column** instead
(`ingest/w10_textspine.py`). Where the text came from is structural, knowable,
and not a judgement call.

When ingesting a new source, ask early: *what structural fact distinguishes the
content I want from the content I don't?* Markup position, cell width, element
class. If the answer is "I'll recognize it when I see it", expect silent loss.

Three traps met while doing this, worth checking for in any table-based source:

- **A column can be split.** These pages divide the 450-wide text column into two
  225-wide halves for some occasions. Keying on the *text* width missed those;
  keying on the *apparatus* width (consistently 150) and treating everything else
  as text is the robust polarity — enumerate the narrow, well-defined thing, not
  the open-ended one.
- **Don't classify a cell by sniffing its contents.** Looking for an Arial font
  inside a cell misread a text cell that happened to contain one, and dropped a
  whole occasion. Use the cell's own attributes.
- **Markup fragments words.** Drop-capitals and headings broken after their first
  word arrive as separate pieces, so heading markers stop matching. Rejoin short
  leading fragments before matching anything.

And a pattern-matching caution learned twice in one wave: **a matcher widened to
catch a rare case will catch common ones too.** Broadening the citation matcher to
see single-chapter books ("Jude 1.") made ordinary prose match; widening the
cross-reference matcher made a general rubric ("The sixth Sunday, if there be so
many...") look like a shared reading, which stole a section and orphaned a real
citation. Both were caught only because the builder **aborts on an unassigned
citation** rather than dropping it. Build such assertions in deliberately: they
turn a silent loss into a loud stop.
