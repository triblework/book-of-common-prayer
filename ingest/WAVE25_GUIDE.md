# Wave 25 — the apostrophe (R24) and the possessive of small-capital LORD (R25): guide

Wave 24 left three things in its queue: the twelfth 1892 *LORD'S* (the Churching
office's psalm, never read against the scan); the mix of `'` and `’` in the
cells; and 1928's and 1979's possessives, never read for case. This wave did all
three, with two maintainer rulings (2026-11-06, in the Wave 25 session):

- **R24** — "Curly, all cells": every apostrophe in every cell is `’` (U+2019).
  My recommendation was the straight `'` (the majority form, and what the
  tooling and docs use); the maintainer chose the typographic mark.
- **R25** — the possessive outside the 1892 Psalter: 1892 Churching and 1928
  apply R23 as it stands; for 1979, "Reopen for the possessive (Recommended)":
  R11 is reopened for the possessive only, its s taking its case from the font
  run where the eye agrees.

## What changed

| | cells | what |
|---|---|---|
| R24 | 265 files, all 12 editions | 1,250 apostrophes `'` → `’` (1,118 inside a word, 129 plural possessives, 3 after a digit: *1500’s*) |
| R25, 1892 | `occasional-offices/churching.md` | 1 possessive S → s (scan p. 331, book p. 303) |
| R25, 1928 | the three Psalter files | none: both printings set the S as a small capital |
| R25, 1979 | three Psalter files, `burial.md` | 9 S → s, 1 s → S (Burial); 3 checked and unchanged (115:16, 116:17, Churching) |
| tools | `tools/normalize.py` | the word pattern takes `’` as it took `'` (published: every tag carries it) |

Nothing else in any cell moved (w25_gates, character for character). The
counts before the change (`w25_apostrophes.py` at the base): 1,247 straight and
202 curly apostrophes; curly ones in 35 cells of 1637 (9), 1789 (30), 1892 (89)
and 1928 (74); 22 cells mixed both; about 177 false word pairs between
same-path cells of the American line (1662|1789 25, 1789|1892 43, 1892|1928 74,
1928|1979 35).

## The apostrophe rule (R24 (a))

A straight mark directly after a letter is an apostrophe, whatever follows
(*don't*, *Apostles' Creed*); after a digit, it is one when a letter follows
(*1500's*); a mark NOT after a letter or digit is a quotation mark and is left
alone. Checked before applying: 1979's 10 opening single quotation marks each
pair with a closing one after punctuation (*praise.'*, *more,'*), so no closing
quotation mark follows a letter. The rule is `w25_witness.curl`; comments are
skipped (VERIFY keys are delimited by straight quotes and match provenance and
SOURCES).

Three strays, left for a reading against a page (HANDOFF queue): a mark before
*deliver* in the Fourth Sunday in Advent collect, 1789/1892/1928 (a quotation
mark by the rule, no partner: untouched); a mark after *may* in 1892's For Rain
(an apostrophe by the rule: set `’`); `‘` (U+2018) before *who seek* in 1928's
Public Baptism (untouched). `w25_gates` declares each.

## The possessives

```
w25_crop.py          size-checked sips crop + a Vision line-box OCR made on the spot
                     (WHERE only), the row/zoom crop pair
w25_possessive.py    locate and crop: 1892 Churching (scan p. 331, found by OCR of scan
                     pp. 328-351), 1928's eleven in BOTH printings (w21_*_ocr.json; the
                     psalm's pages from the running heads -- the Psalter-day number in a
                     head is not a psalm), the word at 3x; 1979's thirteen from rendered
                     PDF pages (Quick Look, 4400px). Labels name the place only.
w25_fontruns.py      pypdf visitor_text: the face of every glyph of "Lord's" whose o-r-d is
                     Sabon-RomanSC; the whole file has exactly 13, one per cell place:
                     9 with the s in Sabon-Roman, 4 in Sabon-RomanSC (EVIDENCE only)
w25_eye.txt          the eye reads: 1892 1, 1928 11 (x2 printings), 1979 13
w25_witness.py       curl(); POSSESSIVES (every possessive in 1892/1928/1979 with its
                     book's case and evidence; located by the words before it, exactly
                     once per cell); apply() = keys then curl. `python3 ingest/w25_witness.py`
                     applies it (idempotent), `--check` dry-runs.
w25_apostrophes.py   the survey (per edition and cell; the false word pairs)
w25_gates.py         the gates, --selftest
gen_wave25_provenance.py   one sentence on each of the 265 records (counts from the
                     cells vs the base); re-runnable; proves only `note` changed
```

What the eye saw: 1892 — a lower-case s, the same as the s's of *courts* and
*house* on the row. 1928 — in both printings the S stands level with the small
capitals O R D and above the lower-case s's of the row (*is*, *seat*, *song*), in
the capital's form; plain in the 1929 printing, slighter in the 1952 facsimile's
face, the same reading. 1979 — the rendered glyph is what the font run names in
all 13 (Sabon's small-capital S is visibly taller and wider than its s).

## Gates

`w25_gates` 0 (R24 over 1,277 cells, 1,452 apostrophes all `’`; quotation
marks paired, 3 declared strays; containment: base `4bdec46e` + Wave 25 ==
every cell, and only apostrophes and the 11 s's differ; possessives 1892 ×12,
1928 ×11, 1979 ×13 by font run and eye; normalization unchanged apart from the
character; `--selftest` sensitive). All earlier gates 0, `w13_changelog` 55/55,
`verify_index --check` OK (350 inline / 438 provenance). `w20_gates`' "nothing
else moved" compares with HEAD and reads 1 until the commit, as always.

**Amended, as R18 allows (chains, no live tag):** `w17_gates`, `w18_gates`,
`w21_gates`, `w22_gates`, `w23_gates` apply `w25_witness.apply` (or `curl`) on
the expected side of their containment, so each still proves its own step and
still reads the work tree. `w18_gates`' Navy check and `w23_gates`'
composite-table check compare in R24's encoding. `w14_fidelity` folds `’` to `'`
on both sides before attesting a word (an encoding, not a reading).
`w13_render` applies `w25_witness.apply` as its last step, so `w13_build.py`,
`w13_build_1892.py` and `w13_build_1979.py` still reproduce their cells byte for
byte. `gen_wave24_provenance.py` keeps a later wave's sentence when re-run.

## Lessons

1. **A ruling's answer can differ from the recommendation; the rule that
   carries it out is still yours to state.** "Curly, all cells" needed a rule
   telling apostrophes from quotation marks; it was checked against the whole
   corpus (every quotation mark pairs) before it was applied, and its edge
   cases are declared in the gate rather than guessed.
2. **Two books, two encodings of one word.** The 1892 Standard Book sets the
   possessive's s lower-case; the 1928 book sets it as a small capital. A rule
   about "the possessive" would have been wrong for one of them; reading each
   book was the only way to know.
3. **A born-digital file can say what its letters cannot.** The 1979 text layer
   reads small capitals as lower case, but each glyph's font is recorded; the
   rendered page confirmed the runs at every place. The file itself is
   inconsistent (4 of 13 small-capital S's), and that is carried as printed.
4. **A low-resolution scan defeats pixel measurement.** The 1929 scan's native
   spread is 1,491 px wide; connected components on its grey image fragmented
   the glyphs. The check was discarded rather than tuned until it agreed.
5. **A corpus-wide character change touches every gate that compares text.**
   Run the full set before and after; each failure was either a containment to
   chain or a token pattern that did not know the new character.
