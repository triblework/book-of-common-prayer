#!/usr/bin/env python3
"""w15_witness.py — corrections read from the scan of the original 1928 printing.

Authoring-only; NOT published. See WAVE15_GUIDE.md §3.

The text layers (Wohlers's keyed transcription) are the carrier; the scan
(justus 1928/BCP1929.pdf, "the original 1928 printing") is the witness. Every
row a Wave-15 builder emits was compared by eye with the scan; where the two
disagree, the scan's reading is recorded HERE, with the scan page and the
book page it was read from, and the builders apply it.

Two rules keep this honest:
  * each entry names the TEXT-LAYER reading it replaces, and the builder
    aborts if the text layer no longer reads that way (a stale correction is a
    silent change waiting to happen);
  * nothing here is computed. The Sunday-letter cycle FOUND the calendar
    defects; the scan SUPPLIED every value. Where the scan itself cannot be
    read, the entry carries `verify` and the cell gets an inline VERIFY.

`scan` = page of BCP1929.pdf (1-based); `book` = the printed page number.
"""

CALENDAR = [
    # -- rows the text layer lost outright (gate 1) --
    {"kind": "missing-row", "month": "April", "day": 15, "scan": {"letter": "g"},
     "text_layer": None, "page": 15, "book": "xxix"},
    {"kind": "missing-row", "month": "May", "day": 15, "scan": {"letter": "b"},
     "text_layer": None, "page": 15, "book": "xxix"},
    {"kind": "missing-row", "month": "June", "day": 15, "scan": {"letter": "e"},
     "text_layer": None, "page": 15, "book": "xxix"},
    {"kind": "missing-row", "month": "July", "day": 11, "scan": {"letter": "c"},
     "text_layer": None, "page": 16, "book": "xxx"},
    {"kind": "missing-row", "month": "August", "day": 11, "scan": {"letter": "f"},
     "text_layer": None, "page": 16, "book": "xxx"},
    {"kind": "missing-row", "month": "September", "day": 11,
     "scan": {"letter": "b"}, "text_layer": None, "page": 16, "book": "xxx"},
    # -- Sunday letters keyed wrongly (gate 2) --
    {"kind": "letter", "month": "January", "day": 31, "text_layer": "C",
     "scan": "c", "page": 15, "book": "xxix"},
    {"kind": "letter", "month": "February", "day": 11, "text_layer": "d",
     "scan": "g", "page": 15, "book": "xxix"},
    {"kind": "letter", "month": "March", "day": 11, "text_layer": "d",
     "scan": "g", "page": 15, "book": "xxix"},
    {"kind": "letter", "month": "May", "day": 9, "text_layer": "C",
     "scan": "c", "page": 15, "book": "xxix"},
    {"kind": "letter", "month": "October", "day": 1, "text_layer": "d",
     "scan": "A", "page": 16, "book": "xxx"},
    # -- All Saints: the text layer keys it (with November's letter) against
    #    1 October; the book prints it against 1 November --
    {"kind": "name", "month": "October", "day": 1, "text_layer": "All Saints",
     "scan": "", "page": 16, "book": "xxx"},
    {"kind": "name", "month": "November", "day": 1, "text_layer": "",
     "scan": "All Saints", "page": 16, "book": "xxx"},
]

# Tables and Rules (feasts-and-fasts). Substring replacements, each of which
# must occur exactly once in the built text. Scan page 17 = book pp. xxxi-xxxii.
FEASTS = [
    # book p. xxxi (scan 16, right-hand page)
    {"text_layer": "whether be fore or after", "scan": "whether before or after",
     "why": "kerning space (both halves are words, so de-kerning cannot join them)",
     "page": 16, "book": "xxxi"},
    {"text_layer": "The Circumcision of our Lord Jesus CHRIST",
     "scan": "The Circumcision of our Lord JESUS CHRIST",
     "why": "the text layer keys this one entry in mixed case; the scan prints "
            "the same small capitals as the other three JESUS CHRIST entries",
     "page": 16, "book": "xxxi"},
    {"text_layer": "St. Philip and St. James. Apostles",
     "scan": "St. Philip and St. James, Apostles", "why": "keyed period for comma",
     "page": 16, "book": "xxxi"},
    {"text_layer": "St. John. Apostle and Evangelist",
     "scan": "St. John, Apostle and Evangelist", "why": "keyed period for comma",
     "page": 16, "book": "xxxi"},
    # book p. xxxii (scan 17, left-hand page)
    {"text_layer": "II The Ember Days", "scan": "II. The Ember Days",
     "why": "the ordinal's period is not keyed", "page": 17, "book": "xxxii"},
    {"text_layer": "Wednesday, Friday. and Saturday",
     "scan": "Wednesday, Friday, and Saturday", "why": "keyed period for comma",
     "page": 17, "book": "xxxii"},
    {"text_layer": "II All the Fridays", "scan": "III. All the Fridays",
     "why": "the third ordinal is keyed as II, without its period",
     "page": 17, "book": "xxxii"},
    {"text_layer": "the Monday. Tuesday,", "scan": "the Monday, Tuesday,",
     "why": "keyed period for comma", "page": 17, "book": "xxxii"},
    {"text_layer": "COLLECT, EPISTLE, AND GOSPEL ARE",
     "scan": "COLLECT, EPISTLE, GOSPEL ARE",
     "why": "the original printing has no AND. The transcription was keyed "
            "from a later printing (its page numbers are not the original's), "
            "so this may be a later reading rather than a keying slip; v1928 "
            "carries the original", "page": 17, "book": "xxxii"},
    {"text_layer": "Thanks giving Day", "scan": "Thanksgiving Day",
     "why": "kerning space", "page": 17, "book": "xxxii"},
]

# The psalm tables and the Selections (book pp. vii-ix; scan pages 4-5).
# `table` names the builder's row list the substring must occur in exactly once.
PSALMS = [
    # Proper Psalms for Seasons and Days (book pp. vii-viii)
    {"table": "proper", "text_layer": "Psalms: 40:1–16. 90; 65, 103",
     "scan": "Morning: 40:1-16, 90 | Evening: 65, 103",
     "why": "keyed period for comma; with the comma restored the row has the "
            "table's Morning;Evening shape", "page": 4, "book": "vii"},
    {"table": "proper", "text_layer": "Psalms: 97, 110; 22. 23",
     "scan": "Morning: 97, 110 | Evening: 22, 23",
     "why": "keyed period for comma (as above)", "page": 4, "book": "vii"},
    # WITHDRAWN in Wave 16. Wave 15 read Palm Sunday's damaged last figure as
    # "132" (VERIFY) and overrode the text layer's "131". Re-examined at pixel
    # level, the figure has a serifed top with its stem centred beneath it --
    # this face's old-style 1; the old-style 2 of "24" on the same line hooks
    # to the right. The 1936 printing (1928/BCP1936.pdf scan p. 6, book p. x;
    # a new setting in lining figures) prints "Also 24, 130, 131" cleanly. So
    # the text layer's 131 stands and no correction is recorded here.
    {"table": "proper", "text_layer": "Morning: 22:1-19,", "scan": "Morning: 22:1-9,",
     "why": "the original printing reads 22: 1-9. The transcription was keyed "
            "from a later printing, so 1-19 may be a later reading rather than "
            "a keying slip; v1928 carries the original", "page": 5, "book": "viii"},
    {"table": "proper", "text_layer": "Psalms: 65. 67, 104, 144",
     "scan": "Psalms: 65, 67, 104, 144", "why": "keyed period for comma",
     "page": 5, "book": "viii"},
    {"table": "notes", "text_layer": "NOTE. That Proper Psalms",
     "scan": "NOTE, That Proper Psalms", "why": "keyed period for comma",
     "page": 5, "book": "viii"},
    # Selections of Psalms (book p. viii)
    {"table": "selections", "text_layer": "4, 31:1-6, 91. 134",
     "scan": "4, 31:1-6, 91, 134", "why": "keyed period for comma",
     "page": 5, "book": "viii"},
    {"table": "selections", "text_layer": "19, 24, 103, 148. 149. 150",
     "scan": "19, 24, 103, 148, 149, 150", "why": "keyed periods for commas",
     "page": 5, "book": "viii"},
    # A Table of Psalms for the Sundays of the Church Year (pp. viii-ix)
    {"table": "sunday", "text_layer": "Morning: 96., 97", "scan": "Morning: 96, 97",
     "why": "stray keyed period", "page": 5, "book": "viii"},
    {"table": "sunday", "text_layer": "Morning: 75. 76", "scan": "Morning: 75, 76",
     "why": "keyed period for comma", "page": 5, "book": "viii"},
    {"table": "sunday", "text_layer": "Morning: 63. 65", "scan": "Morning: 63, 65",
     "why": "keyed period for comma", "page": 5, "book": "viii"},
    {"table": "sunday", "text_layer": "Easter Day | Morning: 2, 57, 111 | Evening: 113, 116, 117",
     "scan": "Easter Day | Morning: 2, 57, 111 | Evening: 113, 114, 118",
     "why": "the text layer keys 116, 117 (the Second Sunday after Easter's "
            "evening psalms, two rows below); the scan reads 114, 118",
     "page": 5, "book": "ix"},
    {"table": "sunday", "text_layer": "Evening: 148.149, 150",
     "scan": "Evening: 148, 149, 150", "why": "keyed period for comma",
     "page": 5, "book": "ix"},
    # Psalms for Special Occasions (p. ix)
    {"table": "special", "text_layer": "117, 126. 132, 138",
     "scan": "117, 126, 132, 138", "why": "keyed period for comma",
     "page": 5, "book": "ix"},
]

# The two rubrics (book p. vii, scan 4; the Scripture rubric, scan 6).
RUBRICS = [
    {"cell": "psalter", "text_layer": "That on other days. instead",
     "scan": "That on other days, instead", "why": "keyed period for comma",
     "page": 4, "book": "vii"},
    # A READING OF THE ORIGINAL PRINTING, not a keying slip. The transcription
    # (keyed from a later printing) has these two sentences rewritten to fit
    # the church-year Table of Lessons ("any day of the week"; "Upon any
    # weekday, other than a Holy Day, the Lessons appointed for any day").
    # The original 1928 printing still prints the older wording, pointing to
    # "that day of the month" and "the Calendar" -- and as two paragraphs.
    {"cell": "scripture",
     "text_layer": "appointed for any day of the week, in place of the Second "
                   "Lesson for the Sunday. Upon any weekday, other than a Holy "
                   "Day, the Lessons appointed for any day",
     "scan": "appointed for that day of the month, in place of the Second "
             "Lesson for the Sunday.\n\nUpon any day for which no Proper Lessons "
             "are provided, the Lessons appointed in the Calendar for any day",
     "why": "the original printing's wording (a later printing revised it)",
     "page": 6, "book": "x"},
]

# The three tables of lessons (book pp. x-xxviii; scan pages 6-15). Keyed by
# section ("cy" Christian Year, "fh" Fixed Holy Days, "so" Special
# Occasions), the Sunday that opens the row's week (cy only), the row label and
# the column; `field: "label"` corrects the row label itself.
# The entries themselves live in w15_lessons_witness.json, written by
# w15_addw.py from the parse (so each text-layer reading is copied, not typed).
import json as _json
import os as _os
_P = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                   "w15_lessons_witness.json")
LESSONS = _json.load(open(_P, encoding="utf-8")) if _os.path.exists(_P) else []

# The footnotes under the Christian-Year table, as the original prints them
# (the text layer keys the Ember note twice, in two forms). Each printed once:
# p. xi (Ember Days; Christmas Eve), p. xv (Ember Days), p. xviii (Ascension).
LESSON_NOTES = [
    "* Optional Lessons for the Ember Days.",
    "† These Lessons may be used on Christmas Eve.",
    "* Optional Lessons for the Eve of Ascension Day.",
]
