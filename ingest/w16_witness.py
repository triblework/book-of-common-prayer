#!/usr/bin/env python3
"""w16_witness.py — Wave 16 (the backlog pass): readings a witness supplies.

Authoring-only; NOT published. See WAVE16_GUIDE.md.

Same two rules as w15_witness.py: every entry names the CARRIER reading it
replaces, and the builder aborts if the carrier no longer reads that way; and
nothing is computed -- each value is read from a named witness.

Witnesses used:
  STD1892  1892Standard/front_matter.pdf -- Wohlers's text of the 1892
           STANDARD BOOK ("the one to which all other printings were to be
           compared"), set page for page after the original (2013). Where it
           differs from the older justus HTML it reads like a proofread text
           ("fit" for "lit"; Christmas 110 for 118), but it may descend from
           the same keying, so it is NOT counted as independent of FM1892.
  FM1892   1892/Front_Matter_1892.htm -- justus's 1892 front-matter page. It
           prints its OWN copy of the Table of Proper Psalms, keyed apart from
           1892/Psalms_1892.htm (the Wave-13 carrier for that table), which is
           an OCR-grade page with OCR-type errors (3 read as 8: "180").

NOT a witness: 1892Standard/psalter.pdf. It shares the 1892 Psalter carrier's
own slips ("Eqypt", "stretch our her hands"), so the two are one keying, and
where they part (about 470 words, mostly shew/show and judgement/judgment) the
direction of the edit is unknown. Recorded for a scan-based pass (HANDOFF §8).
  SCAN1928 1928/BCP1929.pdf -- the scan of the original 1928 printing (the
           Wave-15 witness), read as page images.
"""

# ---------------------------------------------------------------------------
# 1892 Table of Proper Psalms on Certain Days (carrier: Psalms_1892.htm, built
# by w13_build_extras.py). The carrier is an OCR-grade keying that confuses 3
# and 8 and 0 and 8 and prints line-break hyphens inside day names. Wherever
# it disagrees with the Standard Book, the Standard Book's reading is carried,
# and at every such place FM1892 reads the same. Two of the carrier's readings
# replaced are impossible (Psalms 180 and 190); the other two (148, 132) each
# differ from the witnesses in one figure, as its 180 for 130 does. (Where
# FM1892 and STD1892 disagree
# -- Christmas evening, FM1892 "89, 118, 132" -- the carrier agrees with
# STD1892, so nothing changes there.)
# ---------------------------------------------------------------------------
PROPER_1892 = [
    {"carrier": "Christ-Mas-day |", "witness": "Christmas-day |",
     "why": "line-break hyphen keyed inline with a capital; STD1892 "
            "CHRITMAS-DAY (sic), FM1892 Christmas-day"},
    {"carrier": "Ash-Wednesday | Morning: 6, 32, 38 | Evening: 102, 180, 148",
     "witness": "Ash-Wednesday | Morning: 6, 32, 38 | Evening: 102, 130, 143",
     "why": "3 read as 8 twice (Psalm 180 does not exist); STD1892 and FM1892 "
            "both 102, 130, 143. Resolves the Wave-13 VERIFY '180'"},
    {"carrier": "Easter Day |", "witness": "Easter-day |",
     "why": "STD1892 EASTER-DAY, FM1892 Easter-day"},
    {"carrier": "Ascension-day | Morning: 8, 15, 21 | Evening: 24, 47, 190",
     "witness": "Ascension-day | Morning: 8, 15, 21 | Evening: 24, 47, 108",
     "why": "Psalm 190 does not exist; STD1892 and FM1892 both 24, 47, 108. "
            "Resolves the Wave-13 VERIFY '190'"},
    {"carrier": "Whit-sunday |", "witness": "Whitsunday |",
     "why": "line-break hyphen keyed inline; STD1892 WHITSUNDAY, FM1892 "
            "Whitsunday"},
    {"carrier": "Trinity Sunday |", "witness": "Trinity-Sunday |",
     "why": "STD1892 TRINITY-SUNDAY, FM1892 Trinity-Sunday"},
    {"carrier": "Transfig-uration | Morning: 27, 61, 93 | Evening: 84, 99, 132",
     "witness": "Transfiguration | Morning: 27, 61, 93 | Evening: 84, 99, 133",
     "why": "line-break hyphen keyed inline; and 3 read as 2 -- a valid-looking "
            "number the Wave-13 VERIFY could not see; STD1892 and FM1892 both "
            "84, 99, 133"},
]

# ---------------------------------------------------------------------------
# 1892 Concerning the Service of the Church (carrier: Front_Matter_1892.htm;
# witness: STD1892). The two keyings agree word for word but for these.
# ---------------------------------------------------------------------------
CONCERNING_1892 = [
    {"carrier": "as he shall think lit,", "witness": "as he shall think fit,",
     "why": "l keyed for f (\"lit\" is not a reading); STD1892 \"fit\""},
]
# A disagreement no witness settles: carried as the carrier prints it, flagged.
CONCERNING_1892_VERIFY = [
    {"reading": "the President",
     "verify": "Front_Matter_1892.htm prints \"Prayer for the President of the "
               "United States\"; the Standard Book's keying (1892Standard/"
               "front_matter.pdf) capitalizes \"The President\". Carried as the "
               "carrier prints it; confirm against a scan of the 1892 book"},
]

# ---------------------------------------------------------------------------
# 1928 Concerning the Service of the Church (carrier: Lectionary_1928.pdf
# sheet 1, keyed from a later printing; witness: SCAN1928 p. 4, book p. vii).
# ---------------------------------------------------------------------------
CONCERNING_1928 = [
    {"carrier": "in this Church. and shall", "witness": "in this Church, and shall",
     "why": "keyed period for comma", "page": 4, "book": "vii"},
    {"carrier": "of the Ordinary. may use", "witness": "of the Ordinary, may use",
     "why": "keyed period for comma", "page": 4, "book": "vii"},
    {"carrier": "in this Book. it is not", "witness": "in this Book, it is not",
     "why": "keyed period for comma", "page": 4, "book": "vii"},
]


def apply(text, corrections, where):
    """Apply corrections to `text`; each carrier reading must occur exactly
    once (a stale or ambiguous correction aborts the build)."""
    for c in corrections:
        n = text.count(c["carrier"])
        if n != 1:
            raise SystemExit("w16 witness (%s): %r found %d times"
                             % (where, c["carrier"], n))
        text = text.replace(c["carrier"], c["witness"], 1)
    return text
