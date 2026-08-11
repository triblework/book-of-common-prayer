# The Book of Common Prayer, as Git History

> # 🚧 Work in progress
> **The full texts of the Book of Common Prayer are actively being transcribed
> and added edition by edition — more services are coming soon.** The repository
> structure, tooling, and diff mechanism are complete; today the transcribed
> text centres on **Morning Prayer** (plus the Scottish Communion office). No
> text is ever invented — everything is sourced from faithful public-domain
> transcriptions (see [`SOURCES.md`](SOURCES.md)). See
> [Transcription status](#transcription-status) for what's here and what's next.

A public, version-controlled edition of the **Book of Common Prayer (BCP)** in
which the historical evolution of the book is expressed as **git history** —
so that anyone can see exactly *what changed* between editions using ordinary
git and GitHub diffs.

## The core idea

The edition axis is **git history, not directories.** There are deliberately no
`/1549/` or `/1662/` folders — that would defeat diffing. Instead:

- Each **edition is a commit** that snapshots the *same* set of files with that
  edition's content, marked with an annotated **tag** (`v1549`, `v1552`, …).
- The tradition **branches** in real history, so we model it with git branches:
  the English line (`main`) forks into the **Scottish** line (from 1604) and the
  **American / Episcopal** line (from 1662). The version graph mirrors the
  actual liturgical genealogy.
- A separate axis — **original spelling vs. modernized spelling** — is a
  *representation* present at every commit, modeled as two parallel trees:
  `texts/original/` (faithful period spelling) and `texts/normalized/`
  (modern spelling, generated from the original by `tools/normalize.py`).

The payoff:

```bash
git diff v1549 v1552 -- texts/normalized/daily-office/morning-prayer.md
```

shows precisely how Morning Prayer changed between 1549 and 1552 — and GitHub's
compare view (`/compare/v1549...v1552`) renders the same thing in the browser.

## Genealogy

```mermaid
gitGraph
    commit id: "scaffold"
    commit tag: "v1549"
    commit tag: "v1552"
    commit tag: "v1559"
    commit tag: "v1604"
    branch scottish
    checkout scottish
    commit tag: "v1637"
    commit tag: "v1764"
    commit tag: "v1929"
    checkout main
    commit tag: "v1662"
    branch american
    checkout american
    commit tag: "v1789"
    commit tag: "v1892"
    commit tag: "v1928"
    commit tag: "v1979"
```

*(The Scottish line forks from 1604; the American line forks from 1662. The
American 1789 Communion Office also drew heavily on the Scottish 1764 Office —
see `NOTICE.md`.)*

## Editions

| Year | Line | Branch | Tag | Description |
|-----:|------|--------|-----|-------------|
| 1549 | English | `main` | `v1549` | First Book of Common Prayer (Edward VI). |
| 1552 | English | `main` | `v1552` | Second Edwardian book; adds the penitential introduction to Morning Prayer. |
| 1559 | English | `main` | `v1559` | Elizabethan Settlement. |
| 1604 | English | `main` | `v1604` | Jacobean / Hampton Court revision. |
| 1662 | English | `main` | `v1662` | Restoration; the standard Church of England book. `BCP 1662` |
| 1637 | Scottish | `scottish` | `v1637` | "Laud's Liturgy". |
| 1764 | Scottish | `scottish` | `v1764` | Scottish Communion Office. |
| 1929 | Scottish | `scottish` | `v1929` | Scottish Book of Common Prayer. |
| 1789 | American | `american` | `v1789` | First American book (Protestant Episcopal Church). |
| 1892 | American | `american` | `v1892` | American revision. |
| 1928 | American | `american` | `v1928` | American revision. |
| 1979 | American | `american` | `v1979` | Current American book (public domain). |

## Transcription status

> **🚧 Work in progress.** The full text of every service is actively being
> transcribed and will be added edition by edition — check back soon. The
> repository structure, tooling, and diff mechanism are already complete; the
> text is being filled in against faithful public-domain sources (no text is
> ever invented — see `SOURCES.md`).

The **structure is complete**: all three branches and all twelve tags exist, and
the diff mechanism works end-to-end. The **transcribed text so far** centres on
the **Daily Office (Morning Prayer)** — the richest source of famous
edition-to-edition change — plus the **Scottish Communion** office at 1764/1929
(the 1764 book was Communion-only).

**Coming soon** (in progress): Evening Prayer across all editions, the full Holy
Communion office, the occasional offices (Baptism, Confirmation, Matrimony,
Visitation of the Sick, Burial), the Collects, the Catechism, and the Ordinal;
the Psalter and lectionary tables will follow. Two American tags (`v1928`,
`v1979`) currently carry a documented sourcing gap rather than invented text —
justus offers 1928 only as an OCR scan and the 1979 lives on JavaScript sites the
static scraper can't yet capture — and clean sources for them are being sought.

Progress and per-edition provenance are tracked in `SOURCES.md`. Uncertain
readings are flagged inline with `<!-- VERIFY -->` comments and listed there.

## How to explore the diffs

Clone the repository (tags and branches come with it), then:

```bash
# How Morning Prayer changed from 1549 to 1552 (the famous penitential opening):
git diff v1549 v1552 -- texts/normalized/daily-office/morning-prayer.md

# Compare any two editions on a shared line, whole tree or one service:
git diff v1552 v1662 -- texts/normalized/daily-office/
```

**Readable word-level diffs.** Set up the suggested local aliases once:

```bash
git config diff.prose.wordRegex '[^[:space:]]'
git config alias.wdiff 'diff --word-diff=color'
git config alias.cdiff 'diff --color-words'
```

Then:

```bash
git wdiff v1552 v1662 -- texts/normalized/daily-office/morning-prayer.md
```

**On GitHub**, use the compare view:

```
https://github.com/triblework/book-of-common-prayer/compare/v1552...v1662
```

## `original/` vs. `normalized/` — which to read

- Use **`texts/normalized/`** to study *substantive* change: modern spelling
  removes noise (`haue`/`have`, `shew`/`show`) so real wording changes stand out
  in a diff.
- Use **`texts/original/`** for *textual fidelity*: it preserves the printed
  spelling of each edition (u/v, i/j, -ie/-y, thorn, doubled consonants), with
  only the long-s and archaic ligatures normalized.

`normalized/` is **generated** from `original/` and is never hand-edited — see
`CONTRIBUTING.md`.

## Provenance and licensing

- The **tooling/code** is under the MIT `LICENSE`.
- The **texts** are governed by **`NOTICE.md`**, not the MIT license. It records
  the public-domain status of every included edition and the Crown-rights
  acknowledgment for 1662: **`BCP 1662`**.
- Per-file sources and retrieval dates are in **`SOURCES.md`**.

## Repository layout

```
texts/
  original/     # faithful transcription (period spelling)  -- generated by the builder
  normalized/   # generated modern spelling (do not hand-edit)
tools/
  build_history.py          # replay the whole edition graph (history as a build artifact)
  scrape.py                 # fetch + clean source HTML -> markdown (assistive)
  sentence_split.py         # enforce one-unit-per-line semantic line breaks
  normalize.py              # original/ -> normalized/ via the rules below
  normalization_rules.yaml  # transparent, version-controlled spelling rules
  verify_index.py           # keep inline VERIFY comments in sync with provenance
```

**History is a build artifact.** The published branches and tags you see here are
*outputs*. The source of truth is the orphan **`authoring`** branch (per-edition
text in `editions/`, the genealogy in `editions.yaml`, provenance in
`provenance.yaml`); `tools/build_history.py` deterministically regenerates the
whole `main`/`scottish`/`american` graph and all `vYYYY` tags from it. This is why
completing a service in an *early* edition can change that edition's commit so its
diff renders a real liturgical change. See `CONTRIBUTING.md`. SHAs are not part of
the interface — tags and diffs are.

## Contributing

See **`CONTRIBUTING.md`**. The one rule to internalize: **editions are commits
and tags on the right branch — never per-edition directories** — and never
hand-edit `texts/normalized/`.
