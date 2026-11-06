# Implementation Specification: Transcribing the Entire Book of Common Prayer

**For:** Claude Code (autonomous implementation)
**Repository:** https://github.com/triblework/book-of-common-prayer
**Status of this document:** Full build-out spec, superseding the scope of the
original proof-of-concept brief. The architecture, tooling, format rules, and
licensing guardrails already in the repo are **preserved**; this document
extends them to the whole book and **resolves every open question** in the
handoff brief (§9 of `BCP-EXPANSION-HANDOFF.md`).

Read the whole document before starting. Work in **waves** (§6). Commit on the
`authoring` branch frequently; publish (rebuild the history) only at wave
boundaries. Do not fetch any text that violates §8.

---

## 0. Decisions locked before any bulk work (read first)

These resolve the handoff's open questions. Each is binding unless a later
maintainer overrides it with written rationale.

| # | Question (handoff §9) | Decision |
|---|-----------------------|----------|
| 1 | Editing already-tagged editions | **History becomes a build artifact.** A canonical `authoring` branch holds per-edition source text; `tools/build_history.py` deterministically replays the entire commit/branch/tag graph. Published branches (`main`, `scottish`, `american`) and all tags are **outputs**, regenerated and force-pushed at wave boundaries. See §2. |
| 2 | Depth per service | **Tier 1 = the full printed service body** (rubrics, spoken text, versicles/responses, canticles, creed, suffrages, fixed collects, state prayers). Variable psalms/lessons are pointers. Tier 2 (Psalter, lectionary/calendar, full proper Collects/Epistles/Gospels sets) is stretch. See §3. |
| 3 | Sequencing | **One service family per wave, across all applicable editions**, so each wave lights up that service's cross-edition diffs everywhere at once. Order: migrate → deepen Morning Prayer → Evening Prayer → Litany → Holy Communion → occasional offices → Catechism → Ordinal → front-matter → Collects/Epistles/Gospels → (stretch) Psalter → (stretch) tables. See §6. |
| 4 | Branch tooling parity | **Tools are authored once** on `authoring` and **stamped identically into every commit** by the builder. A tools change triggers a full rebuild; CI asserts a tools-only change leaves `texts/` byte-identical. See §5.4. |
| 5 | 1928 / 1979 sourcing gaps | **Both closed.** 1928 = justus/Satucket clean per-service **HTML** (`/1928/MP.htm`, `/1928/HC.htm`, …), already-allow-listed. 1979 = justus **public-domain ASCII e-text** (`ASCII_1979.htm` → `bcpprayr.txt` et al. / `bcp10.txt`), static, no JavaScript. See §4. |
| 6 | Phase D (1789←1764 merge) | **Skip in canonical history.** Cross-branch `git diff v1764 v1789 -- texts/normalized/holy-communion/holy-communion.md` already exposes the influence; keep the `NOTICE.md` note and add a README demonstration. See §9. |
| 7 | Verification at scale | Machine-readable `authoring/provenance.yaml` per service-edition; `tools/verify_index.py` gate; optional two-pass transcribe/verify; per-edition sign-off before a wave is "done." See §7. |
| 8 | Psalter/lectionary | Stretch. Psalter = one-verse-per-line under `## Psalm N` anchors; tables = normalized long-form, one row per line, stable column order; both excluded from Tier 1. See §10. |

**Why decision 1 is forced, not optional.** Completing early editions' service
sets *necessarily* changes their commits: to make `git diff v1549 v1552 --
texts/normalized/holy-communion/holy-communion.md` render the famous 1549→1552
Communion change, the `v1549` commit must contain 1549's Holy Communion. It does
not today. Adding services "forward" at the current branch tips would place every
edition's Baptism in commits *after* `v1979`, which is nonsensical. So history
**must** be rewritten; the builder is what makes rewriting safe, deterministic,
and repeatable.

---

## 1. Invariants carried forward (do not violate)

These are unchanged from the existing repo and the two briefs. Summarized here;
the authoritative statements live in `CONTRIBUTING.md`, `README.md`, and the
original spec.

1. **Editions are commits and tags, never folders.** No `/1549/` directories in
   the published trees.
2. **Genealogy is branches:** `main` (English) → `scottish` forks at `v1604`,
   `american` forks at `v1662`.
3. **Two spelling trees at every commit:** `texts/original/` (faithful, hand
   authored) and `texts/normalized/` (**generated** by `tools/normalize.py`;
   never hand-edited).
4. **One unit per line** (semantic line breaks); enforced by
   `tools/sentence_split.py` (idempotent, CI-checked).
5. **Light Markdown:** `#` service title, `##` major section, `> ` rubric,
   plain lines for spoken text, `**Priest.** …` bold speaker labels.
6. **UTF-8, LF, no trailing whitespace, single trailing newline.** Long-s (ſ→s)
   and archaic ligatures normalized even in `original/`; u/v, i/j, -ie/-y, thorn,
   doubled consonants kept as printed in `original/`.
7. **Stable section anchors:** reuse identical `##` headings across editions
   where a section persists, so only the *body* diffs; a genuine rename is itself
   a meaningful diff and is allowed.
8. **Normalization is spelling only.** `shew`→`show` allowed; `divers`→`various`
   forbidden. Never change vocabulary, word order, or meaning.
9. **Never invent text or transcribe from memory.** Source, then verify against a
   scan; flag doubtful readings with `<!-- VERIFY: … -->` and index them.
10. **Licensing guardrails (§8) are absolute.**

---

## 2. History as a build artifact (resolves handoff §9.5)

### 2.1 Two layers

- **Authoring layer** — a single **orphan branch** named `authoring`. It holds
  the source-of-truth per-edition text plus build metadata. Its directory
  structure is *build input*, unrelated to the published diff layout, so
  per-edition folders here are fine (they never appear on published branches).
- **Published layer** — `main`, `scottish`, `american` and all `vYYYY` tags.
  These are **outputs** of `tools/build_history.py`. Nobody hand-commits to them.

Rationale: rebuilding the whole genealogy requires *every edition's every
service available simultaneously*. A published branch at any commit holds only
one edition's snapshot, so it cannot be the rebuild source. The authoring branch
is that simultaneous store. This is the same philosophy already applied to
`normalized/` (a generated function of `original/`), lifted to the whole history.

### 2.2 Authoring branch layout

```
authoring/                     # (this branch's root; orphan, unrelated to main)
├── editions.yaml              # ordered genealogy + per-edition manifest
├── provenance.yaml            # per service-edition source/verify metadata (§7)
├── editions/
│   ├── 1549/
│   │   ├── daily-office/morning-prayer.md
│   │   ├── daily-office/evening-prayer.md
│   │   ├── holy-communion/holy-communion.md
│   │   └── …                  # only services this edition ADDS or CHANGES
│   ├── 1552/ …
│   ├── 1662/ …
│   ├── 1637/ …                # Scottish/American editions keyed by year too
│   ├── 1764/ …                # (years never collide, per the original spec)
│   └── 1979/ …
└── tools/                     # the canonical tooling, stamped into every commit
    ├── build_history.py
    ├── scrape.py
    ├── sentence_split.py
    ├── normalize.py
    ├── normalization_rules.yaml
    ├── verify_index.py
    └── gen_sources.py          # optional; renders SOURCES.md table from provenance.yaml
```

Also authored once on this branch and stamped into every published commit:
`README.md`, `CONTRIBUTING.md`, `NOTICE.md`, `LICENSE`, `.gitattributes`,
`.gitignore`, `requirements.txt`, `.github/workflows/`. Keep them under
`authoring/repo-root/` (a directory whose contents are copied to the published
root at build time) to separate "files that appear in every published commit"
from "authoring-only files" (`editions.yaml`, `provenance.yaml`, `editions/`).

### 2.3 `editions.yaml` schema

An ordered list encoding the DAG. Example (abbreviated):

```yaml
editions:
  - id: 1549
    year: 1549
    branch: main
    parent: null                 # first commit on main after scaffold
    tag: v1549
    tag_message: "1549 — First Book of Common Prayer (Edward VI)"
    commit_message: "1549 Book of Common Prayer (First Edwardian)"
    present: [daily-office/morning-prayer, daily-office/evening-prayer,
              holy-communion/holy-communion, occasional-offices/baptism, …]
    absent: []                   # services deliberately not in this edition

  - id: 1552
    year: 1552
    branch: main
    parent: 1549
    tag: v1552
    tag_message: "1552 — Second Book of Common Prayer (Edward VI)"
    commit_message: "1552 revision (Second Edwardian)"
    present: [ … ]
    absent: []

  - id: 1637
    year: 1637
    branch: scottish
    branch_from: v1604           # create `scottish` here on first Scottish edition
    parent: 1604
    tag: v1637
    …

  - id: 1764
    year: 1764
    branch: scottish
    parent: 1637
    tag: v1764
    present: [holy-communion/holy-communion]
    absent: [daily-office/morning-prayer, daily-office/evening-prayer,
             the-litany/litany, occasional-offices/baptism, … ]   # Communion-only "Wee Bookie"
    …

  - id: 1789
    year: 1789
    branch: american
    branch_from: v1662
    parent: 1662
    tag: v1789
    …
```

Field semantics:
- `parent` — the edition whose materialized tree this edition starts from
  (inheritance source). For a branch's first edition, also set `branch_from`
  (the **tag** to branch at).
- `present` — services that must resolve to a file at this commit (authored here
  or inherited). The builder **fails** if a `present` service resolves to nothing.
- `absent` — services removed at this edition relative to the parent. The builder
  **deletes** the file (clean deletion diff). Fails if a service is in both lists.

### 2.4 Inheritance / absence model

For each edition, for each service the project tracks:

1. If `authoring/editions/<year>/<service>.md` exists → **use it** (this edition
   authored or changed the service).
2. Else if the service is in this edition's `absent:` → **delete** it from the
   materialized tree (removal shows cleanly in the diff).
3. Else → **inherit** the parent edition's *materialized* file unchanged.
4. After resolution, every service in `present:` must exist and no service in
   `absent:` may exist, or the build fails.

This gives: no duplication for unchanged services (inherit by omission), explicit
auditable drops, and a **full snapshot** materialized at each commit — matching
the original spec's "each edition is a commit snapshotting the same set of files."

> **Known limitation (must be controlled by verification, not tooling).**
> Inheritance-by-omission cannot detect a *forgotten* change: if an edition truly
> altered Evening Prayer but no one authored the file, the builder silently
> inherits the parent. Tooling cannot know intent. This is caught by the §7
> sign-off: each edition's `provenance.yaml` records, per service, whether it was
> `transcribed` (fresh from source), `reviewed-unchanged` (confirmed identical to
> parent against a source), or `inherited-unreviewed`. A wave is not "done" while
> any in-scope service is `inherited-unreviewed`.

### 2.5 `tools/build_history.py`

Deterministic, idempotent, dependency-light (stdlib + PyYAML). Algorithm:

```
build_history(authoring_worktree, target_repo, check=False, dry_run=False):
    load editions.yaml (topologically ordered; validate DAG, tags unique)
    create/clean a scratch worktree for the published side
    write the scaffold commit (repo-root files + tools/ + empty texts/ tree)
    for edition in topological_order:
        checkout parent state (branch_from tag for a branch's first edition,
            else the parent edition's commit on the same branch)
        if branch_from: create `branch` at that tag, check it out
        materialize texts/original/ for this edition via §2.4 resolution
        run sentence_split.py over texts/original/   (in place)
        run normalize.py                              (regenerate texts/normalized/)
        stamp repo-root files + tools/ (identical bytes at every commit)
        stage all; commit with commit_message
        create annotated tag `tag` with tag_message
    if check:
        for each edition tag in the LIVE repo:
            assert live tag's texts/ tree == freshly built texts/ tree
        exit nonzero on any mismatch
    elif not dry_run:
        update refs main/scottish/american + all tags to the built graph
        (caller performs: git push --force-with-lease + tag push)
```

Requirements:
- **Determinism:** same authoring input ⇒ identical published `texts/` trees
  (commit timestamps may be pinned from `editions.yaml` or set to a fixed epoch so
  even SHAs are reproducible; pin them, so `--check` can compare trees, not SHAs).
- **`--check` mode:** rebuild in a scratch area and assert every live tag's
  `texts/` tree matches the freshly built one. This is the history-level analog of
  `normalize.py --check`. Runs in a dedicated CI workflow (§5.3), not per-push.
- **`--dry-run`:** build fully, run all checks, print the intended ref updates,
  touch nothing.
- **Safety:** never update live refs until the full build + all local checks pass.

### 2.6 Publishing (force-push) policy

- Rebuild + publish **only at a wave boundary**, never mid-wave.
- Publish sequence: `build_history.py` (no `--check`) → run `normalize.py --check`
  and `sentence_split.py --check texts` on the built tips of all three branches →
  `verify_index.py --check` → `git push --force-with-lease` the three branches →
  delete-and-recreate the twelve tags at their new commits and push them.
- **SHAs are explicitly not part of the interface.** Tags and diffs are. Record
  each rebuild in `NOTICE.md` ("history rebuilt on <date> for wave N") and in the
  README's transcription-status section.
- Once the corpus is essentially complete, the project may **freeze**: stop
  rebuilding and only append genuinely new future scholarship forward. Force-push
  churn is a build-out-phase phenomenon.

### 2.7 One-time migration (Wave 0)

The current history was hand-built forward. Migrate it under the builder without
changing any *text*:

1. Create the orphan `authoring` branch.
2. For each existing tag, `git checkout <tag>` and copy its `texts/original/`
   into `authoring/editions/<year>/` (this captures each edition's current
   materialized state). Then **thin** it: delete any file byte-identical to what
   the parent already provides, so only real per-edition changes remain authored
   (optional but keeps the authoring tree clean; the builder reproduces the rest
   by inheritance).
3. Author `editions.yaml` reproducing the existing genealogy, messages, tags,
   and the current `present:`/`absent:` sets (e.g. `v1764` Morning Prayer absent).
4. Author `provenance.yaml` from the current `SOURCES.md`.
5. Move `tools/`, `README.md`, etc. into the authoring layout.
6. Implement `build_history.py`; run it; assert the rebuilt `texts/` trees match
   the current published `texts/` trees **byte-for-byte** (they must, since no
   text changed). Only tooling/root files may differ if you took the opportunity
   to unify them — if so, confirm that difference is intended and text-neutral.
7. Force-push the rebuilt branches and re-create tags. Announce the one-time
   rewrite.

After Wave 0, **all** content work happens on `authoring` and every published
state is a build output.

---

## 3. Service depth standard (resolves handoff §9.2)

### 3.1 Tiers

- **Tier 1 (the build-out target):** the complete printed body of a service —
  every rubric, every spoken text, all versicles/responses and speaker labels,
  the **full text of fixed canticles** (Venite, Te Deum, Benedictus, Magnificat,
  Nunc Dimittis, etc.), the Creed, the suffrages/lesser litany, the **fixed**
  collects that are part of the office, and the state prayers. Variable material
  read *by reference* — the day's psalms and the two lessons — is represented as a
  rubric pointer, **not** transcribed (its content is Tier 2). Proper collects/
  epistles/gospels are their own service (Wave 10), not part of MP/EP.
- **Tier 2 (stretch, §10):** the Psalter, the lectionary/calendar tables, and the
  full seasonal sets of Collects, Epistles & Gospels.

Adopt Tier 1 as the uniform standard so cross-edition diffs stay aligned: every
edition of a service is transcribed to the same depth, so a diff reflects real
liturgical change, never uneven coverage.

### 3.2 Canonical `##` anchor menus

Anchors are a **superset menu per service family**, listed in canonical order.
An edition includes the anchors it actually has; a section's presence/absence and
any rename are themselves meaningful diffs. **Keep the exact spelling below**
(including the archaic `## The Lordes Prayer`) for continuity with the existing
slice.

**Morning Prayer** (`daily-office/morning-prayer.md`) — extend the existing
opening anchors; do not rename them:

```
## The Opening Sentences
## The Exhortation
## The General Confession
## The Absolution
## The Lordes Prayer
## The Versicles
## Venite
## The Psalms                 (rubric pointer; body is Tier 2)
## The First Lesson           (rubric pointer)
## Te Deum Laudamus
## Benedicite
## The Second Lesson          (rubric pointer)
## Benedictus
## Jubilate Deo
## The Apostles' Creed
## The Suffrages
## The Collect for the Day
## The Collect for Peace
## The Collect for Grace
## The Anthem                 (1662+; "In Quires and Places where they sing…")
## A Prayer for the King's Majesty
## A Prayer for the Royal Family
## A Prayer for the Clergy and People
## A Prayer of St. Chrysostom
## The Grace
```

Notes: 1549 titles the office **Matins** and is markedly simpler (opens at the
Lord's Prayer; several state prayers and the closing set are absent). The
1549→1552 addition of the whole penitential opening is the flagship diff and is
already demonstrated. The state prayers differ sharply between the English and
American lines (the American line has no prayers for the Crown) — that divergence
is exactly what the branch diffs should show.

**Evening Prayer** (`daily-office/evening-prayer.md`) — mirrors MP:

```
## The Opening Sentences
## The Exhortation
## The General Confession
## The Absolution
## The Lordes Prayer
## The Versicles
## The Psalms                 (pointer)
## The First Lesson           (pointer)
## Magnificat
## Cantate Domino
## The Second Lesson          (pointer)
## Nunc Dimittis
## Deus Misereatur
## The Apostles' Creed
## The Suffrages
## The Collect for the Day
## The Collect for Peace
## The Collect for Aid against all Perils
## (state prayers as in MP)
## A Prayer of St. Chrysostom
## The Grace
```

**The Litany** (`the-litany/litany.md`): title, the invocations, the
deprecations, the obsecrations, the intercessory suffrages, the Agnus/Kyrie
close, the concluding prayers. Anchor at `## The Litany` plus `## The Prayers`;
the litany body is long, single-response prose — one petition per line.

**Holy Communion** (`holy-communion/holy-communion.md`) — the crown jewel for
diffs (the 1549→1552 restructuring, the moving Gloria, the words of
administration, and the Black Rubric are the tradition's most dramatic changes).
Menu (canonical order; positions deliberately fixed so a *moved* section shows as
a delete+insert):

```
## The Lord's Prayer          (1549 opening)
## The Collect for Purity
## The Introit                (1549 proper psalm; later dropped)
## The Summary of the Law     (American line)
## Kyrie Eleison
## Gloria in Excelsis         (1549 position — early)
## The Collects
## The Collect for the King
## The Epistle
## The Gospel
## The Nicene Creed
## The Sermon
## The Offertory
## The Prayer for the Whole State of Christ's Church
## The Exhortations
## The Invitation
## The General Confession
## The Absolution
## The Comfortable Words
## The Sursum Corda
## The Preface
## The Proper Prefaces
## Sanctus
## The Prayer of Humble Access
## The Prayer of Consecration
## The Communion              (administration + words of delivery)
## The Lord's Prayer          (post-communion, 1552+)
## The Prayer of Oblation
## The Prayer of Thanksgiving
## Gloria in Excelsis         (1552 position — near the end)
## The Blessing
## The Rubrics                (incl. the 1552/1662 Declaration on Kneeling — "Black Rubric")
```

Because Gloria and the Lord's Prayer legitimately appear at **different
positions** in different editions, keep both anchor occurrences in the menu; an
edition populates whichever position it uses, leaving the other absent. The diff
then reads as the section moving — which is historically exactly what happened.

**Occasional offices** (`occasional-offices/*.md`): give each a small stable
anchor set following the service's printed structure, e.g. Baptism →
`## The Introduction`, `## The Exhortation`, `## The Gospel`, `## The Thanksgiving`,
`## The Vows`, `## The Blessing of the Water` (1662+), `## The Baptism`,
`## The Reception`, `## The Lord's Prayer`, `## The Final Exhortation`. Confirm
the exact set against 1549 and 1662 at transcription and record it once so all
editions of that office reuse it.

### 3.3 What "done" means for a service-edition

A `<service, edition>` cell is **done** when: sourced from an allow-listed source
(§4/§8); transcribed to Tier 1 depth using the canonical anchors; passes
`sentence_split.py --check` and normalizes cleanly; every doubtful reading is
`<!-- VERIFY -->`-flagged and indexed; and `provenance.yaml` records the source
URL, retrieval date, verifier, and status (§7).

---

## 4. Sourcing map, extended (resolves handoff §9.1)

Primary source remains **justus.anglican.org/resources/bcp/** (Charles Wohlers /
Society of Archbishop Justus), already allow-listed. Cross-check against
Wikimedia Commons / Library of Congress / Wikisource page scans where useful.
The existing per-edition URL patterns in the handoff §6 stand. The two additions
below **close the gaps the handoff left open** — both texts are available as
clean, freely-reusable, allow-listed sources.

### 4.1 American 1928 — GAP CLOSED (clean HTML on justus)

The handoff assumed 1928 existed only as an image/OCR PDF. It does not: justus
serves the **Satucket (Wohlers) formatted text edition** as clean per-service
HTML under `/resources/bcp/1928/`, e.g. `MP.htm` (Daily Morning Prayer),
`HC.htm` (Holy Communion), with the index at `BCP_1928.htm`. These are the same
class of clean HTML the existing `scrape.py` already handles for 1789/1892. Host
is already allow-listed.

- **Licensing:** the underlying 1928 US text is public domain (US editions were
  PD on publication). The Satucket distribution permits electronic
  redistribution provided no fee is charged and its header is retained; since we
  produce a *derivative transcription of a PD work* in our own format, record
  Satucket/Wohlers provenance in `provenance.yaml`/`SOURCES.md` and preserve the
  attribution note in `NOTICE.md`.
- **Cross-check:** the justus `1928Standard/bcp1928std.pdf` (Updike Standard
  Book facsimile) and St. Peter's AOC PDFs for visual verification of doubtful
  readings.
- **Action:** remove the "not transcribed this pass" note for 1928 from
  `SOURCES.md` and schedule 1928 in every wave like any other American edition.

### 4.2 American 1979 — GAP CLOSED (public-domain ASCII e-text on justus)

The handoff's blocker was that the 1979 lives on JavaScript SPAs
(`bookofcommonprayer.net`) and day-generated pages. But justus also hosts the
long-standing **public-domain ASCII e-text** of the 1979 book, which is static
plain text the existing stdlib scraper can capture:

- Index: `/resources/bcp/ASCII_1979.htm`, which links the eleven-part set
  (`BCPINFO.TXT`, … `BCPSALT1.TXT`, `BCPSALT2.TXT`, `BCPPRAYR.TXT`, …) and the
  single-file `bcp10.txt`; e.g. `/resources/bcp/bcpprayr.txt`.
- **Licensing:** the e-text header states it is **in the public domain** and
  explicitly permits copying, distribution, derivative works, reformatting, and
  extracts. (It asks that its own header not be redistributed with altered
  e-texts — trivially satisfied, since we record provenance separately and do not
  embed their header.)
- **Cross-check:** the Wikisource transcription of *Book of common prayer (TEC,
  1979).pdf* and the Wikimedia Commons PDF (both add-only, allow-list after
  confirming as PD scans/transcriptions).
- **Ingestion note:** this source is **plain text, not HTML**, so the HTML→
  Markdown path in `scrape.py` does not apply. Add a small **text-ingest mode**
  to `scrape.py` (`--text`) that fetches the `.txt`, preserves significant line
  breaks, strips the license header and page-furniture, and emits rough Markdown
  for `sentence_split.py`/human verification. The e-text notes that line breaks
  are significant and fixed-width — treat blank-line runs as paragraph breaks and
  do not reflow.
- **Rite I vs Rite II:** the 1979 uniquely has two rites. Represent **Rite I** in
  the persistent office files (it is the traditional-language rite continuous with
  the earlier tradition, so its diff against 1928 is the meaningful one) and add
  **Rite II** as a clearly separated `## Rite Two` section within the same file
  (or a sibling section set), so the dramatic modernization ("Lord, open our lips
  / And our mouth shall proclaim your praise") is visible without corrupting the
  cross-edition Rite-I diff. Decide and document this once; keep it consistent.
- **Action:** remove the "not transcribed this pass" note for 1979 from
  `SOURCES.md`.

### 4.3 Allow-list changes required

Add hosts to `scrape.py`'s `ALLOWED_HOSTS` **only after confirming licensing**,
via a reviewed diff, with a comment recording why. For this build-out the only
likely additions beyond the current set are `en.wikisource.org` (PD transcription
cross-check) and — if used — `github.com`/`raw.githubusercontent.com` for the
`bcponline/BCP-Source` 1979 HTML (confirm its license first; prefer the justus PD
e-text as the primary and treat any GitHub source as corroboration only). Do
**not** add the JavaScript SPA hosts.

### 4.4 Editions still excluded (unchanged)

Common Worship (2000), Church of Ireland 2004, other modern non-US revisions, and
the English 1928 "Deposited Book" (no confirmed clean PD source; keep omitted and
noted). See §8.

---

## 5. Tooling (extend, don't rewrite) — resolves handoff §9.4

### 5.1 New: `tools/build_history.py`
Per §2.5. The one substantial new component.

### 5.2 New: `authoring/editions.yaml`, `authoring/provenance.yaml`
Per §2.3 and §7. `provenance.yaml` is the machine-readable source of truth for
per service-edition provenance and sign-off status.

### 5.3 New: `tools/verify_index.py`
`--check` fails if any inline `<!-- VERIFY: … -->` in `texts/` is not indexed in
`provenance.yaml` (or `SOURCES.md`), and vice versa. Cheap; runs per-push.

### 5.4 New (optional): `tools/gen_sources.py`
Renders the tabular sections of `SOURCES.md` from `provenance.yaml` so provenance
never drifts from content (same discipline as `normalize.py`). Prose notes in
`SOURCES.md` stay hand-written between generated markers. If adopted, add a
`--check` to CI.

### 5.5 New (only if 1928 cross-check needs it): `tools/ocr_pdf.py`
A tesseract-based OCR path for image-only PDFs, gated strictly behind human
verification. **Likely unnecessary** now that 1928/1979 have clean text sources;
include only if a future edition genuinely has no text source. If added, keep it
out of the default pipeline and never let OCR output reach a commit unverified.

### 5.6 Extend: `tools/scrape.py`
Add the `--text` ingest mode (§4.2). Keep the custom wildcard-aware robots
matcher, the caching, the ≥1s rate limit, and the allow-list mechanism exactly as
they are. Adding a host stays a reviewed, licensing-confirmed diff.

### 5.7 Unchanged: `sentence_split.py`, `normalize.py`, `normalization_rules.yaml`
Extend `normalization_rules.yaml` only additively as new spellings appear (each
addition is a reviewable diff; a rules change triggers a full rebuild because it
changes `normalized/` history-wide — expected and fine). Keep the `protect` list
guarding proper nouns and intentionally archaic terms. Watch for new
false-positives as vocabulary widens (e.g. verb forms, Latin canticle incipits —
add Latin incipits like *Venite*, *Te Deum*, *Magnificat*, *Nunc Dimittis*,
*Benedicite*, *Jubilate*, *Cantate*, *Deus Misereatur* to `protect`).

### 5.8 Branch tooling parity (the actual §9.4 answer)
There is **no per-branch tooling drift** because tooling is authored once on
`authoring` and the builder stamps the identical `tools/` (and root docs) into
every commit on every branch. A tools change is a history-wide rebuild. Add a CI
assertion (§5.9) that a tools-only change leaves every tag's `texts/` tree
byte-identical.

### 5.9 CI
- **Per-push** (existing, on every branch): `normalize.py --check`,
  `sentence_split.py --check texts`, plus new `verify_index.py --check` and (if
  adopted) `gen_sources.py --check`.
- **Rebuild workflow** (new; manual dispatch and/or on a `rebuild` label, not
  per-push because it is heavy): `build_history.py --check` — rebuild in a scratch
  area and assert every live tag's `texts/` tree equals the freshly built tree.
  This is the guarantee that published history is exactly what the authoring
  branch produces.

---

## 6. Sequencing — the wave plan (resolves handoff §9.3)

Each wave transcribes **one service family to Tier 1 across every applicable
edition**, then rebuilds and publishes once. Within a wave, work edition-by-
edition on `authoring`; the per-service cross-edition diffs appear together when
the wave publishes.

| Wave | Scope | Notes |
|-----:|-------|-------|
| **0** | Migrate to the builder (§2.7) | No text changes. Byte-identical rebuild. Gate: `build_history.py --check` green. |
| **1** | **Deepen Morning Prayer to full Tier 1**, all editions | Establishes the depth template every later service copies. Preserve existing opening anchors; only *add* sections. This is the reference implementation of a Tier-1 service. |
| **2** | Evening Prayer, all editions | Parallels MP; sources already known. Cheapest large win. |
| **3** | The Litany, all applicable editions | Long single-response prose; one petition per line. |
| **4** | **Holy Communion**, all editions | The highest-value diffs (1549→1552 restructure, moving Gloria, words of administration, Black Rubric). Expect the most anchors and the richest history. |
| **5** | Baptism + Confirmation | Public & Private Baptism where distinct; 1662 adds Baptism of Riper Years. |
| **6** | Matrimony + Visitation of the Sick + Burial (+ Churching, Commination where present) | American line drops the Commination — model as `absent:`. |
| **7** | Catechism | Grows across editions (1604 adds the sacraments section). |
| **8** | Ordinal | See §6.1 on the 1549 nuance. |
| **9** | Front-matter (Preface, Of Ceremonies, Concerning the Service, Ratification) | Rich English/American divergence; 1662 adds its Preface. |
| **10** | Collects, Epistles & Gospels (proper sets) | Large; Tier 2-adjacent. Represent one collect/epistle/gospel unit per file section, stable per-Sunday anchors. |
| **13** | *(stretch)* Psalter | §10. One verse per line. |
| **14** | *(stretch)* Lectionary / calendar tables | §10. Normalized long-form. |

Rationale for deepening MP first rather than going breadth-first at shallow depth:
the acceptance criterion is *consistent depth so cross-edition diffs stay
aligned*. Leaving MP shallow while adding other services wide would bake in uneven
coverage. Wave 1 fixes the template; everything after copies it. (If a maintainer
prefers a breadth-first demonstration, Evening Prayer at the current shallow depth
is the documented alternative — but then schedule a later "deepen all offices"
pass, and record the temporary depth inconsistency.)

### 6.1 Presence matrix (encode into `editions.yaml`; confirm at transcription)

`✓` present · `—` absent · `?` confirm against source during the wave. Notes
follow the table. This is the **starting declaration**; the transcriber confirms
each cell against the actual source and corrects `editions.yaml` as needed.

| Service | 1549 | 1552 | 1559 | 1604 | 1662 | 1637 | 1764 | 1929 | 1789 | 1892 | 1928 | 1979 |
|---------|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
| Morning Prayer | ✓¹ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Evening Prayer | ✓¹ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| The Litany | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Holy Communion | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Baptism | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Confirmation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Matrimony | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Visitation of the Sick | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Burial | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Churching of Women | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ? | ✓ | ✓ | ✓ | ? |
| Commination | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ? | — | — | — | — |
| Catechism | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Ordinal | ?² | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Front-matter | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ?³ | ✓ | ✓ | ✓ | ✓ | ✓ |

Notes:
1. 1549 titles the offices **Matins**/**Evensong** and is structurally simpler
   (the office title heading itself differs — a legitimate diff).
2. The Ordinal was published separately in **1550** and bound in from 1552; the
   1549 book proper did not contain it. Decide once whether to represent it at
   1549 (from the 1550 Ordinal) or first at 1552, and record the decision in
   `NOTICE.md`. justus provides `Bishops/Priests/Deacons_1549.htm`.
3. The 1764 "Wee Bookie" is Communion-only; almost everything is `absent:`. It
   may carry a title page / minimal front-matter — confirm and represent
   faithfully (prefer absence over a stub for whole missing services).
4. The 1929 Scottish full book contains the whole set, but the repo's Scottish
   line currently centers the **Communion** (the 1764/1929 sourcing). Decide per
   wave whether to expand 1929 beyond Communion; if not this pass, mark the
   others `inherited-unreviewed` and note the scope in `SOURCES.md` rather than
   inventing text. The Scottish MP/EP diverge from the English line and are worth
   doing, but are lower priority than completing the English and American lines.

---

## 7. Verification at scale (resolves handoff §9.7)

### 7.1 `provenance.yaml` (machine-readable)

One record per `<service, edition>`:

```yaml
- edition: 1552
  service: daily-office/morning-prayer
  source_url: http://justus.anglican.org/resources/bcp/1552/MP_1552.htm
  retrieved: 2026-08-10
  cross_check: [ commons scan URL or PDF, … ]
  status: transcribed            # transcribed | reviewed-unchanged | inherited-unreviewed
  verifier: <agent-or-person id>
  verify_items:
    - anchor: "The Opening Sentences"
      note: "source prints 'Psalm ii.'; verse is 51:3 — likely li→ii printer error"
```

- `status: transcribed` — authored fresh from a source and verified against a
  scan.
- `status: reviewed-unchanged` — confirmed byte-appropriate-identical to the
  parent against a source (a real, checked "no change this edition").
- `status: inherited-unreviewed` — inherited by omission, not yet checked. **A
  wave is not done while any in-scope cell is `inherited-unreviewed`.**

`verify_index.py --check` keeps inline `<!-- VERIFY -->` comments and
`provenance.yaml` `verify_items` in sync (fails if either references something the
other lacks). `gen_sources.py` (optional) renders the `SOURCES.md` tables from
this file.

### 7.2 Two-pass transcribe/verify (recommended for scale)

For each `<service, edition>`:
1. **Transcriber pass:** `scrape.py` first-pass → format to §3 conventions →
   Tier-1 anchors → `sentence_split.py` → `normalize.py`.
2. **Adversarial verify pass (independent):** diff the transcription against an
   *independent* source (a page scan on Commons/LoC/Wikisource, or the
   cross-check PDF) and file `<!-- VERIFY -->` items for every discrepancy;
   confirm the anchor set and section order; confirm no invented text and no
   memory-sourced content.
3. **Resolution:** a lead resolves VERIFY items, sets `status`, records
   `verifier`. Only then does the cell count toward wave completion.

Cleaning obvious transcription noise (stray mid-sentence periods, OCR triples like
"synnne") is allowed; changing a genuine reading is not. When a reading is
uncertain, flag it — never guess.

### 7.3 Carry-forward VERIFY items already known
Preserve and resolve the existing items (1552 `Psalm ii`/`Jerem. ii`; 1559
missing "O"; 1637 `Ps. 28`; 1764 `Matth. vi. 9. 20`; 1929 `Acts 20. 85`; 1789
citation OCR damage) as those services are deepened.

---

## 8. Licensing guardrails (mandatory — unchanged, restated)

Include only clearly free-to-reproduce texts. **Included:** 1549/1552/1559/1604
(English, PD); **1662** (PD outside the UK, Crown copyright within the UK —
reproduce with the `BCP 1662` acknowledgment in every 1662 file header and in
`NOTICE.md`); Scottish 1637/1764/1929 (PD); American 1789/1892/1928/1979 (US
editions PD on publication; 1979 explicitly PD). **Excluded, on every branch:**
Common Worship (2000), Church of Ireland 2004, modern Canadian/Australian/other
20th–21st-c. non-US revisions, and the English 1928 "Deposited Book" (no
confirmed clean PD source). When in doubt, **skip and note in `SOURCES.md`**.
Add a `scrape.py` host only after confirming licensing, via a reviewed diff.

---

## 9. Phase D (1789 ← 1764 Communion) — resolved (handoff §9.6)

**Do not** model this as a merge in canonical history. Reasons: a merge commit's
diff is muddier than a linear branch; and the influence is already fully
inspectable via a **cross-branch diff**, which works regardless of graph shape:

```bash
git diff v1764 v1789 -- texts/normalized/holy-communion/holy-communion.md
```

Keep the existing `NOTICE.md` genealogical-influence note, and add a short
README subsection ("The Scottish influence on the American rite") that shows the
command above. This delivers the scholarly payoff with zero added graph
complexity. Revisit only if a maintainer specifically wants the merge topology
and can add it without disturbing the linear per-edition diffs.

---

## 10. Psalter & tables (stretch) — resolved (handoff §9.8)

- **Psalter** (`psalter/psalter.md`, Wave 13): one **verse per line**; `## Psalm
  N` anchors in order; keep the printed verse numbering. The English/1662 line
  uses the **Coverdale** psalter; the American line's psalter differs (note the
  divergence — it is a real, interesting diff). Because the psalter is long, keep
  it a single file per the layout, or split per fifty psalms if file size
  matters; decide once and keep stable.
- **Lectionary / calendar tables** (Wave 14): tables diff poorly as rendered
  Markdown. Represent as **normalized long-form**, one entry per line with a
  stable column order, e.g. `Advent 1 | Morning: Isaiah 1 | Evening: Isaiah 2`,
  so a changed cell is a one-line diff. Keep a stable row order (liturgical
  calendar order). These remain **out of Tier 1**; they are the last thing built.

---

## 11. Acceptance criteria

Carried forward and extended. The build-out is complete when:

**Structure & mechanism (already met, keep green):**
- [ ] `main` has `v1549 v1552 v1559 v1604 v1662`; `scottish` has `v1637 v1764
      v1929`; `american` has `v1789 v1892 v1928 v1979`.
- [ ] For any two editions on a shared line, `git diff <tagA> <tagB> --
      texts/normalized/…` is a clean, unit-level diff.
- [ ] `texts/normalized/` is exactly reproducible from `texts/original/`
      (`normalize.py --check`, CI).
- [ ] Every text file is idempotent under `sentence_split.py` (CI).
- [ ] `NOTICE.md`/`SOURCES.md` document provenance for every included edition; no
      §8-excluded text is present; `BCP 1662` appears.
- [ ] README renders the genealogy `gitGraph`, the editions table, and the
      explore-diffs guide.

**New — builder & parity:**
- [ ] Published history is exactly what `build_history.py` produces from
      `authoring` (`build_history.py --check`, CI rebuild workflow).
- [ ] A tools-only change leaves every tag's `texts/` tree byte-identical
      (asserted by the rebuild workflow).
- [ ] `verify_index.py --check` passes: inline `<!-- VERIFY -->` items and
      `provenance.yaml` are in sync.

**New — per service-edition "done" (per §3.3, §7):**
- [ ] Every in-scope `<service, edition>` cell is Tier-1 depth, sourced from an
      allow-listed source, with `provenance.yaml` status `transcribed` or
      `reviewed-unchanged` (no `inherited-unreviewed` in a completed wave).
- [ ] The wave's flagship diffs render as intended, at minimum:
  - MP 1549→1552 shows the added penitential introduction (already met).
  - HC 1549→1552 shows the Communion restructuring and the moved Gloria.
  - HC across 1552/1559/1662 shows the Black Rubric appear / vanish / return.
  - MP/EP `main` vs `american` shows the state-prayers divergence.
  - `git diff v1764 v1789 -- …/holy-communion.md` shows the Scottish→American
    Communion borrowing (§9).

**New — gaps closed:**
- [ ] 1928 and 1979 Daily Office (and their wave-scoped services) are transcribed
      from the §4 sources, not carried-forward stubs; the "not transcribed this
      pass" notes are removed from `SOURCES.md`.

---

## 12. Risks & mitigations

- **Force-push churn on a public repo.** Mitigate: SHAs are declared not part of
  the interface; rebuild only at wave boundaries; `--dry-run` + full local checks
  before any ref update; loud rebuild notes; freeze when the corpus is complete.
- **Silent inheritance hiding a real change.** Mitigate: the `present:` build
  gate, the `status` field, and the "no `inherited-unreviewed` in a done wave"
  rule (§2.4, §7.1). Tooling cannot detect intent; verification must.
- **`normalize.py` false-positives as vocabulary widens.** Mitigate: extend
  `protect` (esp. Latin incipits and proper nouns) additively; every rules change
  is a reviewable diff and a full rebuild.
- **Source drift / link rot.** Mitigate: `scrape.py` caches to `scrape-cache/`;
  `provenance.yaml` records retrieval dates; prefer justus PD sources; keep
  cross-check scans referenced.
- **1979 Rite I/Rite II conflation** corrupting cross-edition diffs. Mitigate:
  fix the Rite-I-in-office-files / Rite-II-as-separate-section convention once
  (§4.2) and keep it consistent.
- **Scope creep into copyrighted modern books.** Mitigate: §8 is absolute; the
  allow-list is add-only with licensing confirmation.

---

## 13. First actions for the implementing agent

1. Read this spec, `BCP-EXPANSION-HANDOFF.md`, `CONTRIBUTING.md`, and the current
   `tools/`.
2. Execute **Wave 0** (§2.7): stand up `authoring`, `editions.yaml`,
   `provenance.yaml`, `build_history.py`; prove a byte-identical rebuild;
   force-push; announce.
3. Execute **Wave 1** (deepen Morning Prayer to Tier 1) as the depth template,
   using §3.2 anchors and §7 verification.
4. Proceed wave by wave (§6), publishing once per wave, keeping CI green.

Prefer correctness over speed. Source, verify against a scan, flag uncertainty
with `<!-- VERIFY -->` — never invent text.
