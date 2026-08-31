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
