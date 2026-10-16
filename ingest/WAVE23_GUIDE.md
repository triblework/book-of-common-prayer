# Wave 23 — the rest of the 1979 text against the publisher's file: guide

Wave 19 collated the 1979 Psalter against Church Publishing's own PDF and
repaired seven named dropouts; it measured the rest and left it as "~110
paragraphs to look at next". This wave looked at all of it: every paragraph
of every 1979 cell outside the Psalter, the Daily Office Lectionary row by
row, and the 1993 keying's own markup and hard wrap. Rulings **R22** and the
**R11 addendum**; rulings A0–A16 of the batch of 2026-10-16.

## The witness is a composite — read it first (R7)

Church Publishing's PDF prints book pages (PDF page = book page), but two runs
were replaced after 1979 and each carries the producer's slug on every page:
**pp. 19–30 are a 2008 Calendar** (`cpg-bcp-calendar.indd … 06/12/08`, with
commemorations added since 1979) and **pp. 889–932 are the 2007 Revised
Common Lectionary** (`RCL pages for BCP 4/13/07`). So `tables/calendar.md`
and `tables/eucharistic-lectionary.md` have no witness in this file; gate 4
keeps both at their base text, and 100 of the 1979 flags (84 three-year
readings, 16 eucharistic-table) cannot close from it. The text layer also
confuses 1/I and ]/1 (never taken), and in the Daily Office Lectionary prints
citations no printing could have (`Mark. 23:1-12`, `10:2S-37`), so a citation
disagreement there is settled by the file only when a second check agrees.

The file names each run's font — Sabon-Roman, -Italic (rubrics, speaker
names), -Bold (titles), -RomanSC (small capitals). That structured the
restored passages (a rubric is italic; a speaker's line opens with an italic
name) and found where collects end. It also means the small-capital LORD is
recoverable from this file after all; **no case was taken this wave** (A16),
and that pass is queued.

## The pipeline (`ingest/w23_*`)

```
w19_witness_text.py   the page text (pypdf; gitignored cache)
w23_book.py           the book's structure: fonts per run, page furniture
w23_survey.py         every cell paragraph located in the book word for word (the standing 1979
                      survey, R22): 2,849 / 3,184 prose paragraphs verbatim before the wave,
                      rubrics 94.2%; sensitivity 300/300 on four injected defect kinds
w23_classify.py       the misses classed: keying defect / re-wrap / spelling / leaked markup
w23_flags.py          each of the 127 open flags looked up in the book
w23_tables.py         the Daily Office Lectionary, occasion-keyed, five fold levels, with a
                      second check for disputes; sensitivity 200/200 both ways
w23_items.py          -> w23_witness_items.py (every keyed item), w23_evidence.json, w23_dropped.json
w23_hand.py           hand-keyed restorations by anchor (text cut from the page by the script)
w23_dol_extra.py      the Holy Days / Special Occasions tables from the carrier, field-checked
w23_witness.py        the groups and the STAGE switch; w23_apply.py applies file -> file
w23_reflow.py         the prayers' hard wrap joined to the book's paragraphs (runs last)
w23_gates.py          evidence, Wave-19 residue, the two untouchable cells, containment vs
                      710f635b by SHA, no markup survives, run-on guard, flag count
w23_report.py         the report's tables
```

## What it found and changed (four commits, in this order)

1. **Corrections, restorations, the lectionary** — 865 keyed items: WORDS 297,
   SPELLING 12, PASSAGES 104 (51 hand-keyed), HEADINGS 2 (text only; slugs
   kept, R22), MEDIANT_STOPS 193, RUBRIC_STOPS 28, PUNCT 90, DOL_ROWS 33,
   DOL_FIX 58, DOL_MARKS 13, DOL_XMAS 11, DOL_DISPUTED 3, FLAGS 21; plus the
   new cell `tables/daily-office-lectionary-holy-days.md` (45 rows, 8 from the
   witness). 19 flags closed (the 8 absent collects, 11 lectionary rows), 23
   opened (15 numeral disputes carrying both readings, 3 regenerated rows, 2
   Holy Days disputes, 3 Burial psalm verses whose repair would take a
   mediant). 1979 flags 127 → 131.
2. **Markup** — 479 normalizations in 93 cells: `=x=` 208, broken speaker
   labels 85, `&V.`/`&R.` 80, `&mdash.` → the book's blank 32, `[[ ]]` 26,
   `&N.` 23, the rest 13.
3. **Re-flow** — 81 prayers cells, 572 breaks joined, 665 fragments → 93
   paragraphs, 92 of them word for word in the book.
4. The report generator.

After all three, 11 of 2,176 prose paragraphs still differ from the book, all
accounted for: 3 editorial notes, 5 refused glyph readings, 2 flagged Burial
verses, 1 running head.

## What the review caught (and the gates now refuse)

The first build passed every gate; checks the gates lacked found real
defects, the builder was fixed and the commits rebuilt: a word item at a
wrapped fragment's edge took in the next fragment (gate 8, run-on); Evening
Prayer Rite Two's invitation and four collects are Morning Prayer's text in
the e-text (a size guard; the five paragraphs hand-keyed); paragraphs cut
short at an edge (an edge guard; 11 passages hand-keyed); a running head read
as text (a furniture guard); and 14 case errors from a keep-case rule applied
too broadly (now same word, same place only).

## Counts worth keeping

- 335 word items found, 330 verified in page context, 11 dropped (5 glyph
  cases, 3 look-alike matches, 1 unverified, 2 mended by the re-flow).
- 29 restorations refused by the mechanical keying: 25 hand-keyed, 2 were
  catechism page markers, 2 flagged.
- Lectionary: 95.8% of 3,951 citations match at some fold; 820 rows against
  the e-text's 784 (8 lost rows, 28 swallowed by 19 merged rows); 26
  disputes through the second check (15 flagged, 8 cell kept, 3 book taken).

## Lessons

1. **Read the slugs.** A publisher's file can be a later state of the book on
   some pages and not others; the production slug on each page says which.
2. **A survey is part of the wave, and a probe is a tool to be measured**: the
   word-for-word probe found 11% of paragraphs differing where the nine-word
   probe had found 6%.
3. **Gates test what you thought of; write the check you did not.** The
   run-on, the MP-in-EP collects and the edge-cut passages passed every gate
   and failed a re-survey of the output.
4. **Restored text flows page → script → file**, anchored on both sides, with
   the font runs telling rubric from text.
5. **Pin a wave's gate to its own end commit when a later wave edits the same
   cells** (w19_gates, R18).
