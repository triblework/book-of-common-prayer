# Wave 11 guide — Prayers and Thanksgivings: anchors, slugs, presence

Authoring-only. The scoping ruling is in `WAVE11_SCOPING.md` (option (b), four
sections excluded) and is LOCKED. This file records the **anchor menu and the
slug list once**, so every edition build agrees.

## Anchor menu (per file — a file is ONE prayer)

```
# <Title as that edition prints it>      <- h1, the printed title; renames are diffs
> <rubric>                               <- the printed rubric, if any
<body lines>                             <- one sentence per line (sentence_split)
```

A single `#` title and no `##` sections: one prayer per file makes the section
anchor redundant, and keeps a rename (e.g. "In the time of any common Plague of
Sickness" -> "In Time of great Sickness and Mortality") a clean one-line diff.
Where a book prints two forms under one head, the second is its own file with a
`-2` slug and keeps its own printed label (`Or this.` / `(ii)`).

## Untitled prayers — the bracket convention

Some books print a prayer with **no title at all** (the 1559 prayer for the
clergy runs straight on from the one before it with a drop capital; the 1928
Collects are six untitled texts under one shared rubric). A file still needs an
`#` heading to be an anchor, but putting the 1662 printed title there would
fabricate a heading the book does not have — and would make the 1559->1662
heading diff vanish, which is a false claim of continuity.

Convention: the heading carries the conventional name **in square brackets**,
and the cell carries an inline `<!-- VERIFY -->` recording that the source
prints the prayer untitled. Brackets already mean "editorial, not printed"
elsewhere in this repo.

    # [A Prayer for the Clergy and People]
    <!-- VERIFY: 'untitled' - the 1559 source prints this prayer with no title -->

## The state-prayer migration (evidence-based, decided this wave)

At **1559 / 1604 / 1637** Morning Prayer ends at `## The Collect for Grace`; the
sovereign / royal-family / clergy / Ember prayers are printed **after the
Litany**, and so belong to this family. At **1662** those same prayers appear as
MP anchors (`## A Prayer for the King's Majesty`, `## A Prayer for the Royal
Family`, `## A Prayer for the Clergy and People`) and are **not** in the
separate "Prayers and Thanksgivings" section.

So the state prayers are `present:` here at 1559/1604/1637 and `absent:` from
1662 onward. That absence is a **relocation, not a deletion** — the text
continues, in `daily-office/morning-prayer.md`, which already carries it.
**Record this in NOTICE.md**, next to the 1552–1637 inline-placement note.

## Slug list

Lineage keys the slug, not the printed wording; a rename is a heading diff on
the same slug. `-2` marks a second form printed under the same head.

### Occasional prayers — the 1552 core
| slug | 1552 | 1559 | 1604 | 1637 | 1662 | 1789 | 1892 | 1928 | 1979 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `for-rain` | x | x | x | x | x | x | x | x | x (#43) |
| `for-fair-weather` | x | x | x | x | x | x | x | x | — |
| `in-time-of-dearth-and-famine` | x | x | x | x | x | x | x | x | — |
| `in-time-of-dearth-and-famine-2` | x (`Or thus`) | — | — | — | x (`(ii)`) | — | — | — | — |
| `in-time-of-war-and-tumults` | x | x | x | x | x | x | x | x | — |
| `in-time-of-plague` | x | x | x | x | x | x* | x* | x* | — |
| `prayer-after-the-former` | — | ? | x | x | x | — | — | — | — |

`*` the American line renames it "In Time of great Sickness and Mortality" —
same slug, heading diff. `?` at 1559 = the open VERIFY on `O God, whose nature
and property…` (WAVE11_SCOPING.md §1); do not resolve by inference.

### State prayers — 1559/1604/1637 only, then migrate to MP (above)
`for-the-sovereign` (1559 Queen's Majesty -> 1604/1637 King's Majesty — a
heading+text diff on one slug) · `for-the-royal-family` (1604+, per the source's
`[prayer added 1604]`) · `for-the-clergy-and-people` · `in-the-ember-weeks`
(1637 + 1662)

### 1662 additions
`in-the-ember-weeks` / `in-the-ember-weeks-2` (two forms) ·
`for-the-high-court-of-parliament` · `for-all-conditions-of-men`
(carries the `*This to be said when any desire the Prayers of the Congregation`
rubric, which the CoE page marks up as a heading but which is a rubric)

### Thanksgivings — added 1604 (see WAVE11_SCOPING.md §1)
`thanksgiving-general` (1662+) · `thanksgiving-for-rain` ·
`thanksgiving-for-fair-weather` · `thanksgiving-for-plenty` ·
`thanksgiving-for-peace-and-deliverance` ·
`thanksgiving-for-restoring-publick-peace` (1662+) ·
`thanksgiving-for-deliverance-from-plague` · `thanksgiving-for-deliverance-2`
(the `Or this` second form, 1604/1637)

**Note the `for-rain` / `thanksgiving-for-rain` split.** Every book prints "For
Rain" twice — once as a prayer, once as a thanksgiving. They are different
texts and MUST NOT collapse onto one slug. Same for fair weather.

### American additions (1789 -> 1928)
1789: `for-those-to-be-admitted-into-holy-orders` ·`for-a-sick-person` ·
`for-a-sick-child` · `for-a-person-going-to-sea` · `for-a-person-under-affliction` ·
`for-malefactors-after-condemnation` · `thanksgiving-women-after-childbirth` ·
`thanksgiving-for-recovery-from-sickness` · `thanksgiving-for-safe-return-from-sea`
· `thanksgiving-for-deliverance-from-sickness`

1892 adds: `for-congress` · `for-the-convention`† · `for-unity` · `for-missions` ·
`for-fruitful-seasons` · `thanksgiving-for-childs-recovery`

1928 adds: `for-a-state-legislature` · `for-courts-of-justice` · `for-our-country` ·
`for-the-church` · `for-the-increase-of-the-ministry` · `in-time-of-calamity` ·
`for-the-army` · `for-the-navy` · `memorial-days` ·
`for-schools-colleges-universities` · `for-religious-education` · `for-children` ·
`for-those-about-to-be-confirmed` · `for-christian-service` · `for-social-justice` ·
`for-every-man-in-his-work` · `for-the-family-of-nations` · `for-prisoners` ·
`a-bidding-prayer` · `thanksgiving-for-fruits-of-the-earth`

† **`for-the-convention` is NOT 1789.** The 1789 page prints it, but that page's
own apparatus column says `This prayer and rubric added in 1845`. It therefore
belongs at 1892, and is `absent:` at 1789. This is the single most important
apparatus-licensed delta on the American side — the page would otherwise put an
1845 prayer into the 1789 book.

## 1979 — crosswalk rules (Wave-10 Decision C, restated)

1979 prints **70 Prayers + 11 Thanksgivings** in 7 subsections. The great
majority are **new** and take their own slugs. Map to a historic slug **only on
demonstrable lineage**, never to manufacture a diff:

- continues a historic prayer -> **same slug** (modernization reads as a diff)
- drops one -> `absent:`
- genuinely new -> **its own slug**

Candidate lineages to confirm one by one against both texts before mapping
(record each decision, kept or rejected, in `WAVE11_1979_CROSSWALK.md`):
#2 For all Sorts and Conditions of Men -> `for-all-conditions-of-men`;
#43 For Rain -> `for-rain`; #9 For Clergy and People -> `for-the-clergy-and-people`;
#21 For Courts of Justice -> `for-courts-of-justice`;
#31 For Schools and Colleges -> `for-schools-colleges-universities`;
Thanksgiving #1 A General Thanksgiving -> `thanksgiving-general`.
**Contested, do not map without checking:** #20 "For Congress or a State
Legislature" merges two 1928 slugs into one text; Thanksgiving #9 "For the
Harvest" vs `thanksgiving-for-plenty`; Thanksgiving #10 "For the Gift of a
Child" vs `thanksgiving-women-after-childbirth`; Thanksgiving #11 "For the
Restoration of Health" vs `thanksgiving-for-recovery-from-sickness`.

## Excluded (locked ruling) — slice off deliberately
1662 *Forms of Prayer to be used at Sea*; the 1892/1928 *Penitential Office*;
*Family Prayer*; the 1789 *Prayer and Thanksgiving to Almighty God*.

**The 1928 `COLLECTS.` sub-block IS IN SCOPE (decided 2026-09-01).** It is six
collects under one shared rubric, printed inside Prayers and Thanksgivings, and
absent from 1789/1892 — so it is a clean 1928 insert. They are occasional
collects, not propers (nothing ties them to a Sunday or Holy Day), so they do
not belong to `collects-epistles-gospels/`. They are printed **untitled**, so
their slugs are incipit-derived and each file's `#` title is the shared section
head with an ordinal, with the shared rubric carried on every one:
`collect-peace-i-leave-with-you` · `collect-assist-us-mercifully` ·
`collect-grant-we-beseech-thee` · `collect-direct-us-o-lord` ·
`collect-fountain-of-all-wisdom` · `collect-promised-to-hear-petitions`

## Sources
See `WAVE11_SCOPING.md` §2. Parser: `ingest/w11_spine.py` — structural
discriminators per page, documented in its docstring. justus over **http**.
