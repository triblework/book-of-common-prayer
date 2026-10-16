# Wave 22 — the 1892 Psalter: every mediant read by eye: guide

The pass Wave 17 said it could not make. Wave 17 read the 1892 Psalter against
the Standard Book scan for words and spelling and checked the pointing only
where a gate flagged it, because page OCR cannot tell `:` from `;`. This wave
read **every mediant in all 2,508 verses by eye**, and the ordinary
punctuation and the unmatched words with it. Rulings **R20** and **R21**.

## The scan (Wave 17's)

`1892Standard/1892standard.pdf`: 596 bitonal JBIG2 pages, no text layer; the
Psalter is scan pp. 357–536, one book page per scan page, one column about
1,620px wide at 4400px, row pitch about 73px. The mediant is an ordinary roman
colon set with a thin space (the compositor also sets a thin space before
`;`); verse 1 opens with a two-line drop capital and only the rest of the
first word in capitals. Scan p. 584 (outside the Psalter) is a true blank (an
80-byte JBIG2 stream), the one 0-line page, checked.

## The method: the machine finds WHERE, the eye says WHAT

```
w22_render.py      pypdf -> Quick Look (out dir a parameter)
w22_ocr.swift      Vision with LINE and WORD boxes (W22_CPU=1 keeps it off the shared
                   Neural Engine queue; same output)
w22_scan.py        a fresh 4400px Psalter record with word boxes -> w22_scan_ocr.json
                   (180 pages, 6,744 lines + 83 from re-reading gap bands)
w22_align.py       Wave 18's skeleton / 4-gram anchors / LIS, taken down to the word:
                   98.4% of words matched, 2,506 of 2,508 verses placed
w22_classify.py    the first pass: for each verse, the OCR mark at the cell's pivot word
                   (':' 2,475 / ';' 6 / ',' 1 / none 12 / unaligned 14) and any colon-class
                   mark elsewhere (175) -> three eye queues: clean 2,311 / flagged 164 / other 33
w22_crops.py       crops of the pivot word with context; bin/w22_strip stacks 40 of them,
                   two columns, labelled ONLY with the verse (never with what to expect)
w22_eye_*.py       the eye reads -> w22_eye.txt (3,386 lines)
w22_control.py     150 clean verses at random, seed 20261016
w22_punct.py       the 440 places where page OCR and cell disagree on a stop -> w22_punct.tsv
w22_unmatched.py   the 725 words the alignment left unmatched, as 585 runs in 26 strips
w22_words.py       word-form candidates -> w22_words.tsv
w22_case.py        letter-case candidates -> w22_case.tsv (groups OFF, see below)
w22_*_keys.py      keys built file -> file; w22_witness.py the groups and switches
w22_evidence.py    -> w22_evidence.json (477 records, every one an eye read + scan page)
w22_gates.py       applied-once, containment vs 710f635b by SHA, one mediant per verse,
                   attestation, flags; --selftest proves each gate fails on a built case
```

Strips read by eye: about 150 (mediant 52 + 22 + 14 + 7; punctuation 11;
words 3 + 26; case 8; re-crops and 3x zooms about 13).

## What it found

- **Pointing: 4 verses.** 39:14 and 100:2, the colon on another word
  (*sojourner*, *ourselves*): moved. 107:1 and 139:7, a `;` at the mediant and
  no colon in the verse: ` : ` kept, flagged (R21: the repo's mediant is a
  structural mark). The control sample disagreed with the machine in **0 of
  150**; the full pass over the 2,051 clean verses found **no further
  difference**.
- **Punctuation: 328 real differences in 440 flagged places** — the carrier
  was keyed over 1662 and carried its stops. 114 commas the book adds, 64 it
  lacks, 80 verse-final `:`/`;` for `.`, 52 `;` for `,`, 14 other, 3 word
  division, 1 uncertain (139:11, damaged type, flagged). Non-mediant stops
  closed up (the carrier's six spaced ` ;` with them).
- **Words: 32 forms Wave 17 missed**, from the eye pass over the unmatched
  words: carrier slips (*thou I walk*, *more then*, *our*/*out* ×2,
  *thy*/*they* ×2, an extra *had*, *good will*) and 1662 spellings where the
  book is modern (*rasor*, *musick*, *havock*, *cloke*, *intreated*,
  *unperfect*, *unpatient*, *slipt*, *stablished*, *strong hold* ×3). 17
  spacing slips. "THE END OF THE PSALTER" deleted from 150:6 (R20).
- **378 edits in 315 verses**: PUNCT 325, WORDS 32, SPACING 17,
  POINTING_MOVE 3 (2 verses), FURNITURE 1. Flags: 3 opened, none closed; the
  water-side note corrected (same key).
- **Letter case: 94 differences, eye-read, keyed, switched OFF** pending a
  ruling: CASE_LORD 23 (small-capital LORD printed "Lord" 16× in Psalms
  139–143; GOD ×3; JEHOVAH 83:18; the reverse at 2:4), CASE_OPENING 22 (the
  book capitalizes only the first word of a verse 1), CASE_CAPS 49 (*Most
  High* ×18, *anointed* ×9, *Red Sea* ×5 …). Also unkeyed: the book sets the
  possessive *LORD's* with a lower-case s where the cells print *LORD'S* (11).

## What the eye and the OCR could and could not tell

- The eye: `:` `;` `,` `.` certain at strip scale (about 0.8); small capitals
  against capitals certain; uncertain only on damaged type (one place). It
  cannot settle a hyphen at a line break (1:3).
- The OCR: reads line-end full stops as colons (42 of 76); never read a
  printed `;` as `:` (0 of 79); reads small-capital LORD as LoRD/Lorn/Lorp.
  Good at finding places, useless as a reading.

## Gates and build

`w22_gates` 0 (474 keys dry-run exactly once with no overlap; 378 enabled keys
applied exactly once; 2,508 verses with exactly one ` : `; 27 introduced
forms in the scan OCR; containment vs `710f635b` in all three files; exactly
the four flags; `--selftest` sensitive). `w13_changelog` 55/55. `w13_audit`
0. `w13_fidelity` 0 after subtracting `w22_witness.introduced()` (as Wave
17's). `w17_gates` now chains Wave 22's corrections in its containment
(published + Wave 17 + Wave 22 == the cell), per R18.

## Lessons

1. **A carrier keyed over another edition carries that edition's
   accidentals.** Stops, case and old spellings all came from 1662; Wave 17
   caught only the classes it listed.
2. **An eye pass over what the machine could NOT align finds what the aligned
   pass cannot.** The carrier's *had*, *our* for *out*, *thy* for *they* were
   all there.
3. **Label a crop with what to look at, never with what to expect.** No cell
   mark and no OCR mark on the strips.
4. **A sweep finds a class, then the class gets its own sweep.** Two "Lord"
   reads led to the 16-place run in Psalms 139–143.
5. **Prove the machine's miss rate before trusting its "clean" class** — and
   then read the clean class anyway when it is cheap: 52 strips bought the
   claim "every mediant read".
