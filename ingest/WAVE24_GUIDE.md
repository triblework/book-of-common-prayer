# Wave 24 — letter case in the 1892 Psalter (R23): guide

Wave 22 read the 1892 Psalter against the Standard Book scan and keyed, by
eye, 94 places where the cells' letter case differs from the book — then left
them off, because no ruling said whether case follows a page scan. This wave
carries the ruling (**R23**, maintainer, 2026-11-06: "#1 accepted" — correct
all 94 to the book) and the one class those words did not reach, the
possessive, ruled the same day ("Yes, LORD's").

## What changed

`ingest/w22_witness.GROUPS`: **CASE_LORD, CASE_OPENING, CASE_CAPS → ON**.
`w13_build_1892.py` rebuilt the three Psalter cells: 94 corrections in 86 verse
lines (23 of the small-capital divine name — 16 of them the run of "Lord" in
Psalms 139–143 —, 22 verse-1 openings, 49 other capitals: *Most High*,
*anointed*, *Red Sea* …). Checked line by line against the pre-wave cells:
**only letter case moved** (203 letters). Per file: 28 / 29 / 37.

## The possessive (keyed as its own group; ON)

The book sets the possessive of small-capital LORD as capital L, small
capitals ORD, apostrophe and a **lower-case s**; the cells printed *LORD'S*
(eleven Psalter verses; 147:11 with a curly apostrophe, kept). "Correct all
94" covered case, not this encoding question, so it was keyed as its own
group, **CASE_POSSESSIVE**, first OFF so either answer would be a switch; the
maintainer ruled it the same day ("Yes, LORD's") and it is ON: 11
corrections, each one letter S → s. The encoding rule (R23): small capitals
are set as capitals; a lower-case letter the book prints after them stays
lower-case.

```
w24_possessive.py   locate each possessive's printed row (the committed OCR line
                    record says WHERE, restricted to the verse's page from
                    w22_eye.txt; 24:1, a drop-capital row, located by hand) and
                    crop it from the 4400px render: the row with its neighbours,
                    and the row alone at 2x; crops labelled with the verse only
w24_eye.txt         the eleven eye reads (all: lower-case s), with notes
w24_measure.py      a pixel check (sips -> BMP, connected components): this
                    face's small capitals stand AT the x-height, so height
                    cannot tell S from s; the possessive's s measures 35-38 x
                    27-30 px, the same-row s of "is" 35-36 x 28-29, and 56:10's
                    "God's" and "LORD's" both 38 x 30. Finds 8 of the 11 rows.
                    Corroboration only (R14); the reading is the eye's.
w22_eye_2.py        the eleven reads appended to CASE, kind 'possessive'
w22_case_keys.py    now reads its cells at Wave 22's BASE by SHA (see Lessons);
                    -> w22_case_keys.json, 105 keys (the 94 byte-identical)
w24_evidence.py     the ':case:' records of w22_evidence.json, file -> file
                    (94 re-noted, 11 new; nothing else touched)
gen_wave24_provenance.py   one sentence on each 1892 psalter record, counts
                    read from w22_witness; re-runnable (replaces its sentence)
```

Switching a group: `w22_witness.GROUPS`; `python3 ingest/w13_build_1892.py`;
the gates below; `python3 ingest/gen_wave24_provenance.py` (it reads the
switches).

## Gates

`w22_gates` 0 (485 keys dry-run exactly once; 483 enabled applied once;
containment vs `710f635b` holds — the case keys are Wave 22's own, so the gate
needed no change; `--selftest` sensitive). `w17_gates` 0 (it chains whatever
`w22_witness` enables). `w13_fidelity` 0 (case changes add no lower-case word),
`w13_audit` 0, `w13_changelog` 55/55. `w14`–`w23` 0 (`w20_gates`' "nothing
else moved" compares with HEAD and reads 1 until the commit). `verify_index
--check` OK. No flag opened or closed.

## Lessons

1. **A key generator must read the cells its keys will be applied to.**
   `w22_case_keys.py` read the work tree, which equalled Wave 22's base only
   until Wave 22 shipped; re-run now it would have re-keyed against cells
   carrying Wave 22's stops. It reads the base by SHA now (R18's habit).
2. **Know what a measurement can discriminate before trusting it.** The
   height test that would separate small capitals from lower case elsewhere
   fails in this face (small capitals at the x-height); the check is recorded
   with that limit, and the eye read stands.
3. **A ruling's words bound it.** "Correct all 94" covered the keyed case
   differences; the possessive was never among them, so it was keyed OFF as
   its own group and put separately — and the answer was then one switch.
