# Wave 12 — the four deferred sections: source survey + one open decision

> ## DECISIONS — LOCKED (maintainer ruling, 2026-09-01)
>
> **1. The Penitential Office gets its OWN slug** —
> `occasional-offices/penitential-office.md`, present 1892 and 1928, NOT mapped
> onto `occasional-offices/commination`. The Commination stays `absent:` in the
> American line from 1789. The Commination→Penitential relationship is an
> *occasion* relationship, not a textual one (it keeps the first day of Lent and
> Psalm 51 and drops the name, all eight curses and their responses), so it is
> recorded in **NOTICE.md**, not asserted as a diff on one slug.
>
> **2. The Sea forms carry their psalms as a CITATION POINTER, not in full.**
> The CoE page prints 98 psalm-verse paragraphs; the Psalter is a deferred wave,
> so transcribing them here would pre-empt it and duplicate the text later. This
> follows the Wave-10 "citation only" precedent: the anchor is identical whether
> it later holds a citation or a full text, so a deepening pass throws nothing
> away.
>
> **2a. Refinement, decided from repo precedent (not a new policy).** Ruling 2
> covers the **Sea forms**, where whole psalms are appended as devotional
> material. It does NOT cover **Psalm 51 in the Penitential Office**, which is
> the structural core of that service. The repo already answered this case: the
> existing `occasional-offices/commination.md` transcribes Psalm 51 **in full**
> under a `## The Psalm` anchor (Wave 6, published). The Penitential Office
> follows that precedent and carries Psalm 51 in full.
>
> This is deliberate, and it is what makes the two Ash Wednesday services
> comparable — which is the whole reason for recording their occasion
> relationship in NOTICE.md rather than collapsing them onto one slug.
>
> Do not re-litigate either ruling; this is the durable record.


Authoring-only. These four were excluded from Wave 11 by the maintainer's locked
ruling (`WAVE11_SCOPING.md`) as "each its own future wave". This is that wave.

## 1. Presence, from the edition indexes

| section | 1662 | 1637 | 1789 | 1892 | 1928 | 1979 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| Forms of Prayer to be used at Sea | x | — | x | x (shares the 1789 page) | **—** | — |
| A Penitential Office for Ash-Wednesday | — | — | — | x | x (**on the Litany page**) | — |
| Prayer to be used in Families | — | — | x | x (shares the 1789 page) | x | — |
| A Prayer and Thanksgiving to Almighty God | — | — | x | x (shares the 1789 page) | — | — |

Evidence, not assumption:
- **1928 drops the Sea forms.** Its index carries 75 hrefs and *none* matches
  `sea`. It does carry `Family_Prayer.htm` and `Litany.htm#Penitential`.
- **1928 moves the Penitential Office to the Litany page** (`Litany.htm#Penitential`),
  where 1892 prints it with Prayers and Thanksgivings — a placement change to
  record, exactly like the Wave-11 migrations.
- **1892 shares 1789's pages** for Sea / Family Prayer / Prayer and Thanksgiving
  (its index links `../1789/...`), the same pattern as the propers. Whether 1892
  is textually identical must be confirmed per section, not assumed.
- **1979 carries none of the four.** The PD e-text set has no "at Sea", no
  "Family Prayer", no "Thanksgiving to Almighty God"; its "Penitential" hits are
  the Eucharist's Penitential Order and penitential psalms, a different thing.
- **CONFIRM BEFORE BUILDING:** whether the Sea forms are a 1662 addition (absent
  1549–1604) — the CoE has them at 1662, but the English 1549–1604 indexes were
  not reachable this pass (the justus 1662 index URL 404s). Do not assert it.

## 2. Sources

| edition | source | note |
|---|---|---|
| 1662 | CoE `…/book-common-prayer/prayers-be-used-sea` | different class vocabulary from the P&T page — see §4 |
| 1789 | `1789/Prayer_at_Sea_1789.htm`, `Family_Prayer_1789.htm`, `Prayer&Thanksgiving_1789.htm` | not yet fetched |
| 1892 | links to the 1789 pages; Penitential Office on the cached `Pray&Thanks_1892.htm` | already parsed — see §4 |
| 1928 | `1928/Family_Prayer.htm`, `1928/Litany.htm#Penitential` | Family Prayer not yet fetched |

## 3. THE OPEN DECISION — the Penitential Office and the Commination

The American line **drops the Commination at 1789** (`absent:` in editions.yaml;
1892/1928/1979 inherit the absence), and a **Penitential Office for
Ash-Wednesday appears at 1892**. Same liturgical slot. Is it the Commination's
successor (same slug, so the American revision reads as a diff) or a distinct
service (its own slug)?

Measured, not guessed — 1662 Commination vs the 1892 Penitential Office:

| marker | 1662 Commination | 1892 Penitential Office |
|---|:-:|:-:|
| the word "Commination" | 1 | **0** |
| "Cursed is he" — the denounced curses | **8** | **0** |
| congregational Amen responses | 20 | 2 |
| Psalm 51 (Miserere) | 1 | 1 |
| appointed for the first day of Lent | 1 | 1 |
| whole-text word overlap | — | 0.33 |

So it keeps the **occasion** and **Psalm 51**, and drops the Commination's entire
defining content. See §5 for the options and the recommendation.

## 4. Parsing notes (structural discriminators)

- **The Penitential Office is already parsed.** `w11_spine.extract('1892')`
  drops exactly 10 blocks at the `EXCLUDE` cut; those blocks *are* this office,
  correctly classified (2 title, 3 rubric, and the Psalm). Emitting them is
  nearly free.
- **The CoE Sea page uses a different class vocabulary** from the P&T page:
  `vlpsalm` (98), `vlnormal` (26), `vlrubric` (18), `vlitemheading` (2),
  `bcpitalicheading` (1) — and **no `bcprubricheading` at all**, which is what
  `w11_spine`'s `coe` style keys titles on. Extend the style before reusing it,
  or it will yield zero titles.
- **SCOPE FLAG — psalms.** The Sea forms carry **98 psalm-verse paragraphs**.
  The Psalter is a deferred wave; transcribing these psalms here would pre-empt
  it and duplicate text later. Decide whether the Sea forms carry their psalms in
  full or as a pointer (the Wave-10 "citation only" precedent applies cleanly).

## 5. Options for §3 — (a) ACCEPTED (see the locked decision at the top)

**(a) Its own slug** — `occasional-offices/penitential-office.md`, present 1892+,
with the relationship to the Commination recorded in NOTICE. *Recommended.*
The repo's own rule is "never force a non-descendant onto a historic slug to
manufacture a diff". Nothing that makes a Commination a Commination survives:
the name, all eight curses and their responses are gone. A `v1662→v1892` diff on
one slug would render as "the Commination lost its content", which reads as a
revision of one service rather than what happened — one service dropped in 1789,
another supplied for the same day three editions later.

**(b) The commination slug** — 1892 restores `occasional-offices/commination.md`
with the Penitential Office's text. Makes the American revision a single visible
diff and keeps one file per liturgical slot. But it asserts a textual descent the
measurements do not support, and it would have the service reappear at 1892
after being explicitly `absent:` at 1789 — a restoration the books did not make.

**Recommendation: (a).** The Commination→Penitential relationship is real but it
is an *occasion* relationship, not a textual one, so NOTICE.md is the right place
to record it — the same treatment already given to the Wave-11 relocations.


## 6. FINDING — 1979 promotes six prayers out of the 1928 Family Prayer

Measured while surveying `family-1928`. Six of its titles coincide with slugs
created at 1979 in Wave 11, and the texts confirm real descent (Jaccard overlap
of the bodies, each against the correct 1979 cell):

| 1928 Family Prayer | 1979 cell | overlap |
|---|---|:-:|
| For Quiet Confidence | `for-quiet-confidence` | **1.00** |
| For Those We Love | `for-those-we-love` | **1.00** |
| For the Absent | `for-the-absent` | 0.98 |
| For Joy in God's Creation | `for-joy-in-gods-creation` | 0.94 |
| For Guidance | `for-guidance-2` | **1.00** |
| For a Birthday | `for-a-birthday-2` | 0.92 |

So 1979 **promoted** these out of Family Prayer into its main Prayers and
Thanksgivings section. Wave 11 gave them their own 1979 slugs, which was correct
on the evidence available then — their ancestor lived in a section Wave 11 had
excluded. **No Wave-11 defect:** the two initially-low scores (0.22, 0.26) were
an artifact of comparing against the wrong twin where 1979 prints two prayers
under one title; against the `-2` cell both match.

**Decision (precedent, not a new ruling): keep them where each book prints
them.** The 1928 prayers stay in `occasional-offices/family-prayer.md`; the 1979
cells keep their own `prayers-and-thanksgivings/` slugs. Moving the 1928 prayers
onto the 1979 paths to manufacture a `v1928->v1979` diff would assert that the
1928 book printed them in Prayers and Thanksgivings, which it does not — the
same error option (c) would have made in Wave 11. **Record the promotion in
NOTICE.md**, alongside the other relocations.

## 7. File scheme

Four files in the existing `occasional-offices/` family, each an office-like
section with `##` anchors — matching how this repo already treats the
Commination, Churching and the other occasional offices:

| file | editions |
|---|---|
| `occasional-offices/prayers-at-sea.md` | 1662, 1789, 1892 |
| `occasional-offices/penitential-office.md` | 1892, 1928 |
| `occasional-offices/family-prayer.md` | 1789, 1892, 1928 |
| `occasional-offices/prayer-and-thanksgiving.md` | 1789, 1892 |

One file per service (not per prayer as in Wave 11) because these are offices
with internal structure, not independent occasional prayers.
