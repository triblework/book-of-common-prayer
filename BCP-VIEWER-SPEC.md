# Implementation Specification: A Reader's Viewer for the Version-Controlled BCP

**For:** Claude Code (autonomous implementation)
**Repository:** https://github.com/triblework/book-of-common-prayer
**Corpus state:** transcription complete through **Wave 9** (all core services,
English/Scottish/American lines). The viewer builds against the full published
corpus. The data build is **decoupled**: git-only, independent of
`build_history.py` (§3.1, §14). Reference implementation:
`prototype/bcp-viewer-prototype.html`.
**Status of this document:** Full build-out spec for a static, browser-based
**viewer** that sits on top of the repository so that **non-technical readers**
can compare editions of the Book of Common Prayer without touching git. It
consumes the repo's published tags/branches; it does **not** change the
transcription architecture, tooling, format rules, or licensing guardrails —
those are **preserved and inherited** (§1).

Read the whole document before starting. The viewer is a **downstream
projection** of the repository, produced by a deterministic builder, in exactly
the same sense that `texts/normalized/` is a projection of `texts/original/`,
and Markdown-on-GitHub is a projection of the canonical plain text. It adds a
reading surface; it introduces no new source of truth.

---

## 0. Decisions locked before any work (read first)

| # | Question | Decision |
|---|----------|----------|
| 1 | Where does the viewer's data come from? | **A build artifact generated from the published git layer only.** `tools/build_viewer_data.py` reads nothing but the published repository — tags, the three branches, both spelling trees, and `SOURCES.md`/`NOTICE.md`/inline VERIFY — and emits static JSON under `viewer/data/`. It **never** reads the `authoring` branch, `editions.yaml`, or `provenance.yaml`, and it runs **independently of `build_history.py`**. The app is a pure client-side static site that loads that JSON. No backend, no runtime GitHub calls in the happy path (§3, §14). |
| 2 | How many editions can be shown together? | **1, 2, or 3 columns.** The user adds/removes columns and picks an edition per column, filtered to editions that actually contain the selected service (§7). |
| 3 | Two viewing modes? | **Reading mode** (clean parallel columns, aligned at `##` section anchors — the digital analog of Brightman's parallel columns) and **Compare mode** (GitHub-style diff). A single toggle switches between them (§5, §6). |
| 4 | Diff model for >2 columns? | **Base + deltas.** The leftmost column is the neutral **base**; every other column is a two-way diff *against the base* — green where it adds, a red gap where it drops a base line. Scales cleanly to three columns and reads as "how 1552 and 1662 each changed 1549" (§6). |
| 5 | Diff granularity? | **Line-level LCS**, made trivially clean by the repo's one-unit-per-line rule, plus **word-level** highlighting on modified line pairs (the on-screen analog of the repo's `git wdiff` aliases). |
| 6 | Spelling axis? | A global **Original / Modern** toggle, defaulting to **Modern** (`normalized/`) since that is what the README recommends for studying substantive change (§4). |
| 7 | Framework? | **Buildless.** Vanilla ES modules + CSS custom properties, zero runtime dependencies. Matches the project's dependency-light ethos (stdlib + PyYAML) and drops onto GitHub Pages with no toolchain (§14). |
| 8 | Hosting & churn? | **GitHub Pages via an Actions artifact**, not a served branch — so it is immune to the wave-boundary force-pushes of `main`/`scottish`/`american`. Viewer source lives on `authoring` (§14). |

**Why the build-artifact approach is forced, not optional.** A static page
cannot run `git`, and the repo's whole value lives in *git history* — the text
at each tag. Something must extract "service X at tag Y in tree Z" ahead of time.
Doing it at build time (deterministically, from the same tags the repo already
publishes) keeps the viewer offline-capable, rate-limit-free, reproducible, and
philosophically identical to every other generated layer in the project.

---

## 1. Invariants inherited from the repo (do not violate)

The viewer is a **reader**, not an author. It never writes text, never invents
readings, and never becomes a second source of truth.

1. **Git history is the edition axis.** The viewer reads editions from **tags**
   (`v1549` … `v1979`) across the three branches; it does not know or care about
   per-edition folders (there are none).
2. **Two spelling trees.** Every edition exists as `original/` and `normalized/`;
   the viewer surfaces both via one toggle. It never displays a hand-edited
   normalized text — it displays what the repo published.
3. **One unit per line.** Because the repo enforces semantic line breaks, a
   **line** is already a liturgical unit. The viewer treats each line as an
   atomic unit for both reading (one paragraph per unit) and diffing (one row per
   unit). This is what makes the diff view clean without any cleverness.
4. **Light Markdown conventions** (§4) are the parse contract: `#` title,
   `##` section anchor, `> ` rubric, plain line = spoken text, `**Priest.**`
   speaker label, `<!-- … -->` metadata.
5. **Presence/absence is meaningful.** A service absent at an edition (e.g.
   Morning Prayer at Scottish `v1764`) is shown as a deliberate absence, not an
   error (§5.3, §7).
6. **The `BCP 1662` acknowledgment is mandatory** wherever 1662 content is
   displayed (§13). Licensing guardrails (original spec §1 / expansion §8) are
   absolute: the viewer only ever renders text the repo already includes.
7. **VERIFY markers are preserved**, surfaced unobtrusively to the reader rather
   than hidden (§13).
8. **SHAs are not part of the interface.** The viewer keys everything on **tags**
   and services, never commit SHAs, so wave-boundary rebuilds don't break links
   (§9).

---

## 2. What a reader can do (feature summary)

A first-time visitor, with no git knowledge, can:

1. **Pick a service** ("Morning Prayer", "Holy Communion", …) from a friendly
   menu grouped by section of the book (§8).
2. **Choose 1–3 editions** to view together, picked from a list grouped by line
   (English / Scottish / American), with editions that lack the chosen service
   greyed out (§7).
3. **Read them side by side** in clean, typeset columns aligned so that the same
   section (e.g. "The Exhortation") sits at the same height across editions
   (§5).
4. **Flip to Compare** to see a GitHub-style diff: additions in muted green,
   removals as red gaps, changed wording highlighted word-by-word (§6).
5. **Switch spelling** between the original period spelling and modernized
   spelling with one toggle (§4).
6. **Jump to any section** via a contents rail; all columns scroll together
   (§8).
7. **Share the exact view** via a permalink that encodes service, editions,
   spelling, mode, and section (§9), and optionally **open the same comparison on
   GitHub** (§9).
8. **See where the text came from** — per-column provenance, retrieval date, the
   `BCP 1662` acknowledgment, and any VERIFY notes (§13).

Non-goals for v1: editing, search across the whole corpus (stretch, §15),
account/state persistence beyond the URL and optional localStorage, and the
Psalter/lectionary tables (they arrive in the repo as stretch work; the viewer
renders them automatically once present).

---

## 3. Data model — the build artifact

### 3.1 `tools/build_viewer_data.py` — decoupled, git-only

A new tool, **deterministic and dependency-light** (stdlib + PyYAML), that reads
**only the published repository** — the same public interface a reader uses. It
does **not** read the `authoring` branch, `editions.yaml`, or `provenance.yaml`,
and it must run to completion on a plain clone that has the tags but no
`authoring` branch. It also runs and deploys **independently of
`build_history.py`** (§14): a viewer rebuild never waits on a history rebuild,
and a history force-push never corrupts a viewer build. Everything the app needs
is derived from git plus the published files.

Algorithm (entirely from the published layer):

```
build_viewer_data(repo, out_dir, check=False, authoring=None):
    tags = git tag --list 'v*'                          # the edition axis
    for branch in (main, scottish, american):
        members[branch] = tags that are ancestors of <branch> tip
        order[branch]   = tags in first-parent order along <branch>
    for tag in tags:
        year = int(tag[1:])                             # 'v1662' -> 1662
        line = earliest branch whose tip has <tag> as ancestor   # english/scottish/american
        desc = annotated tag message                    # git tag -l --format='%(contents)'
        for tree in (original, normalized):
            for service in discovered_services(tag):    # git ls-tree, see below
                text  = git show tag:texts/<tree>/<service>.md   # missing -> {present:false}
                parsed = parse_service_markdown(text)   # §4.1, unchanged
                record(service, tag, tree, parsed)
    services      = union of service paths seen at any tag
    present_at[s] = tags where texts/normalized/<s>.md exists     # presence matrix, OBSERVED
    anchors[s]    = union of ## anchors across editions, in first-seen order
    provenance    = parse_sources_md(repo) + parse_notice_md(repo)   # §13
    emit index.json                          # §3.3
    emit one file per service                # §3.2  (viewer/data/<service-slug>.json)
    if authoring: enrich descriptions / feature-editions from editions.yaml IF present
    if check: rebuild in scratch, assert byte-identical to committed/artifact output
```

- **`discovered_services(tag)`** = `git ls-tree -r --name-only <tag> --
  texts/normalized/` filtered to `*.md`, stripped to service ids. **No hard-coded
  service list** — the corpus is whatever the tags contain (Waves 1–9, complete).
- **Line assignment uses ancestry, not tag-name guessing.** A tag is on the
  earliest branch (english → scottish → american) whose tip has it as an
  ancestor, so shared pre-fork tags (e.g. `v1604`) attach to their originating
  line and the forks (`scottish` from `v1604`, `american` from `v1662`) inherit
  correctly.
- Reads history with `git show <tag>:<path>` / `git ls-tree`, never by checking
  out working trees, so it is safe against a bare or shallow-but-tagged clone.
- **Determinism:** same published tags + same tool ⇒ byte-identical JSON.
  `--check` is the analog of `normalize.py --check`.
- **Optional enrichment (off by default):** `--authoring DIR` may pull nicer
  descriptions or per-service `feature_editions` from `editions.yaml` **if the
  file is present**, but the builder must produce a complete, correct result
  **without it**. The git-only path is the supported default and the one CI runs.

### 3.2 Per-service payload (`viewer/data/daily-office__morning-prayer.json`)

Slug = service id with `/` → `__`. One file per service keeps initial load tiny;
the app lazy-loads only the selected service.

```json
{
  "service": "daily-office/morning-prayer",
  "label": "Morning Prayer",
  "canonical_anchors": ["The Opening Sentences", "The Exhortation", "…"],
  "editions": {
    "v1549": {
      "year": 1549, "line": "english", "branch": "main",
      "trees": {
        "normalized": {
          "present": true,
          "title": "The Order for Morning Prayer, daily throughout the Year.",
          "meta": { "acknowledgment": null, "verify": [ … ] },
          "units": [
            { "anchor": null,                 "kind": "title",   "text": "The Order for Morning Prayer…" },
            { "anchor": "The Lordes Prayer",  "kind": "heading", "text": "The Lordes Prayer" },
            { "anchor": "The Lordes Prayer",  "kind": "rubric",  "text": "Then the Minister shall kneel…" },
            { "anchor": "The Lordes Prayer",  "kind": "text",    "text": "Our Father, which art in heaven…" },
            { "anchor": "The Versicles",      "kind": "speech",  "speaker": "Priest", "text": "O Lord, open thou our lips." }
          ]
        },
        "original": { "present": true, "…": "…" }
      }
    },
    "v1764": { "year": 1764, "line": "scottish", "branch": "scottish",
               "trees": { "normalized": { "present": false }, "original": { "present": false } } }
  }
}
```

`units` is a flat, ordered list — one entry per source line — carrying its
governing `##` anchor. This single structure serves **both** modes: reading
mode groups units under anchors; compare mode diffs the `text` fields in order.
`kind ∈ {title, heading, rubric, text, speech, note}`; `speech` carries an
optional `speaker`; `note` carries surfaced VERIFY content (§13).

### 3.3 Global index (`viewer/data/index.json`)

```json
{
  "repo": "triblework/book-of-common-prayer",
  "built": "2026-08-14T00:00:00Z",
  "wave_note": "history rebuilt for wave 1",
  "lines": [
    { "id": "english", "label": "English", "branch": "main",
      "editions": [
        { "tag": "v1549", "year": 1549, "label": "1549",
          "desc": "First Book of Common Prayer (Edward VI)" }, "…" ] },
    { "id": "scottish", "…": "…" },
    { "id": "american", "…": "…" }
  ],
  "service_groups": [
    { "label": "The Daily Office",
      "services": [
        { "id": "daily-office/morning-prayer", "label": "Morning Prayer",
          "file": "daily-office__morning-prayer.json",
          "present_at": ["v1549","v1552","v1559","v1604","v1662","v1637","v1929","v1789","v1892","v1928","v1979"] },
        { "id": "daily-office/evening-prayer", "…": "…" } ] },
    { "label": "Holy Communion", "…": "…" }
  ],
  "notice": { "bcp1662_ack": "BCP 1662", "notice_url": "…/NOTICE.md", "sources_url": "…/SOURCES.md" }
}
```

The app loads `index.json` once (small), then one service file on demand.

### 3.4 Where it lives / where it deploys

- **Source of the app:** `authoring/viewer/` (HTML, CSS, JS). It is authoring-
  layer, like the tooling. The reference implementation (§6.2) lives at
  `prototype/bcp-viewer-prototype.html`.
- **Generated data:** `viewer/data/*.json`, produced by the builder from the
  published git layer (§3.1) — not hand-committed.
- **Deployed site:** a GitHub Pages **artifact** built by CI (§14), *not* a
  served branch — so the wave-boundary force-pushes of `main`/`scottish`/
  `american` never touch it, and the deploy is independent of `build_history.py`.

### 3.5 JSON Schema (a deliverable, not assumed)

Author `viewer/data/schema/index.schema.json` and
`viewer/data/schema/service.schema.json` (JSON Schema **draft 2020-12**) that
describe exactly the shapes in §3.2/§3.3. CI validates every emitted file against
them as a **hard gate**, alongside `--check`. Treat the schemas as work to write,
not files that already exist.

---

## 4. Rendering the liturgical Markdown

### 4.1 Parse contract (`parse_service_markdown`, in the builder)

Deterministic, line-oriented, honoring the repo conventions exactly:

| Source line | `kind` | Notes |
|-------------|--------|-------|
| `# …` | `title` | The office title; one per file. |
| `## …` | `heading` | Opens a section; its text becomes the `anchor` for all following units until the next `##`. |
| `> …` | `rubric` | Strip the leading `> `; may repeat across lines (each stays its own unit). |
| `**Speaker.** rest` | `speech` | Capture `speaker`; `text` = the rest. |
| `<!-- BCP 1662 … -->` | *(meta)* | Not a visible unit; sets `meta.acknowledgment = "BCP 1662"`. |
| `<!-- VERIFY: … -->` | *(meta)* | Recorded in `meta.verify[]` and attached to the nearest following unit for margin display (§13). |
| any other non-blank line | `text` | Spoken text / scripture citation line. |
| blank line | *(dropped)* | Structure comes from `kind`/`anchor`, not blank runs. |

The parser runs in the builder (Python), not the browser, so the client receives
clean structured JSON and needs no Markdown parser.

### 4.2 Element → visual mapping (the app)

- `title` → the column's running head (see §5.1); also the sticky context label.
- `heading` → a section header in reading mode; a strong diff anchor in compare
  mode.
- `rubric` → serif **italic** in the muted **rubric red** (`--rubric`). This is
  deliberate: "rubric" *means* red-letter, and rendering the repo's `> ` lines in
  red is the digital re-embodiment of the hand-press convention the source
  encodes. It is a functional signal re-expressed in screen type, not decoration.
- `speech` → the speaker in letterspaced **small caps**, the response text plain,
  on the same visual line.
- `text` → a reading paragraph, one per unit, with generous leading.
- Scripture citations (a `text` unit that is purely a reference, e.g.
  `Psalm 51.3`) → rendered smaller, in `--ink-muted`, right-adjacent or beneath
  its sentence. Detection is a light heuristic in the app (a short line matching a
  book-chapter-verse pattern); it is cosmetic only and never affects diffing.

> **Design principle (state once in the About panel).** The canonical text is
> plain text; Markdown-on-GitHub is one projection; this viewer's typeset HTML is
> another. Each era re-embodies the same structured signals — title, rubric,
> versicle, response — into whatever the current medium affords. The viewer is
> the newest link in that chain, not a "neutral" or "correct" rendering. The
> invariant is the structured text, not any typographic form.

---

## 5. Reading mode (parallel columns)

The scholarly north star is **F. E. Brightman's *The English Rite* (1915)** —
parallel columns of editions read across the page. This mode is its interactive
descendant.

### 5.1 Layout

- 1–3 columns of equal width, each with a fixed **column header**: year, line,
  and tag (e.g. `1662 · English · v1662`), the header underlined in that line's
  accent tint; a small ⓘ opens per-column provenance (§13); the base column (in
  compare mode) is badged "base".
- A shared **section rail** (contents) on the left on wide screens; collapses to
  a top dropdown on narrow screens (§11).
- Comfortable reading measure (~58–64 characters) per column in the 1-column
  case; columns narrow as more are added but never below a legibility floor
  (§10.3), after which the layout switches to horizontal scroll or drops to the
  responsive fallback (§11).

### 5.2 Anchor alignment

Reading mode aligns columns at **`##` section boundaries**, not pixel-by-pixel:
when section "The Exhortation" begins, every column that has it starts that
section at the same vertical offset; within a section, each column's units flow
naturally at their own length. Implementation: render the union of anchors (in
`canonical_anchors` order) as aligned row-groups; each column fills its cell for
that anchor or shows the absence placeholder (§5.3). This keeps equivalent
sections legible side by side without forcing artificial line-for-line lockstep.

### 5.3 Absence

- **Whole service absent at an edition** (e.g. MP at `v1764`): that edition is
  not selectable for the service (greyed in the picker, §7). If somehow selected
  via a stale permalink, its column shows a quiet full-column notice:
  *"Morning Prayer is not present in the 1764 book (Communion Office only)."*
- **Section absent at an otherwise-present edition** (e.g. the whole penitential
  opening in 1549): the aligned row-group shows a faint placeholder
  *"— not in this edition —"* in `--ink-faint`, so the *addition* in the next
  edition is visible even in reading mode, and the sections below stay aligned.

### 5.4 Synchronized scrolling

A **Sync scroll** toggle (default on): scrolling any column keeps the others'
current section aligned by anchor (snap-to-nearest-anchor sync, not pixel sync,
to avoid drift between unequal texts). Clicking a section in the rail scrolls all
columns to that anchor. Off = independent scroll for close reading of one column.

---

## 6. Compare mode (GitHub-style diff)

### 6.1 Base + deltas (the multi-column model)

- The **leftmost column is the base** and renders as neutral reading text (no
  color). A "make base" control on any header lets the reader re-anchor.
- Each **non-base column** is a two-way diff **against the base**:
  - a unit present in this column but not the base → **addition**: green cell;
  - a base unit not present in this column → **removal**: shown as a **red gap**
    (an empty, faintly hatched cell carrying a `−` and, on hover, the removed
    text) at the aligned row, so the base line it corresponds to is obvious;
  - a unit present in both → neutral, aligned across all columns.
- With **1 column**, Compare is disabled (nothing to compare) and the toggle is
  greyed with a tooltip: *"Add a second edition to compare."*
- With **2 columns**, this degrades to a classic split diff (base = "before").
- With **3 columns**, both comparison columns carry their own color relative to
  the shared base — the reader sees, at a glance, how *each* later edition
  diverged from the earliest. This is more legible for three-way work than
  GitHub's two-pane view, while staying visually familiar.

### 6.2 Algorithm (canonical; the prototype is the reference implementation)

`prototype/bcp-viewer-prototype.html` is the **reference implementation** for the
diff engine and the §10 design tokens. The client diff MUST reproduce its
behavior; the construction below is that behavior written out — including the
hard case (a base edition that lacks a whole section, e.g. the 1549 penitential
opening), which naive "each column vs base" code gets wrong.

Diffing is done **per `##` section anchor** (headings are strong anchors that
keep alignment sectioned and prevent cross-section drift):

```
buildSectionGrid(anchor, cols, base):
    for each column c: c.text = [ unit.displayText for unit in units(c, anchor) ]   # [] if absent
    baseEmpty = (base.text.length == 0)
    ref = baseEmpty ? (comparison column with the most units) : base                # the spine
    for each column c: align[c] = alignToRef(ref.text, c.text)     # line-level LCS/Myers ops
    rows = []
    for g in 0 .. ref.text.length:
        emitInsertions(g)      # units mapped "after g ref items" across ALL cols,
                               # grouped so an identical inserted line shares one row
        if g == ref.text.length: break
        for each column c:
            m = align[c].matched[g]                    # index in c matched to ref[g], or -1
            if c is base:  cell = baseEmpty ? blank : {base,  ref[g]}
            elif m >= 0:   cell = baseEmpty ? {add, c[m]} : {eq, c[m]}   # eq only if == base line
            else:          cell = baseEmpty ? blank      : {delgap, removed: base[g]}
        push row(cells)
    mergeModifiedPairs(rows)   # word-level, see below
    return rows
```

**Modified-pair merge (word highlighting).** After the grid is built, a base row
whose comparison column `c` is `delgap`, followed within a few rows by an `add`
in the same `c` whose text is **similar** (token-set Jaccard **> 0.40**), is
merged into one `mod` cell for `c` carrying a word-diff of `base[g]` vs the added
line; the moved `add` becomes `blank`. Word diff = a line-level LCS over
whitespace-preserving tokens, emitting `<ins>`/`<del>`. The 0.40 gate separates a
reworded line from a wholly replaced one (a replaced rubric stays a clean
`delgap` + `add`, not a `mod`). This is the screen analog of the repo's
`--word-diff` aliases.

**Cell semantics (relative to base):** `base` neutral reference · `eq` neutral
(comparison equals base) · `add` green (in comparison, not base) · `delgap` red
hatch showing the removed base text (in base, dropped by comparison) · `mod`
green with inline `<ins>/<del>` · `blank` faint gap for alignment. Headings
render as section separators spanning the grid so the diff stays skimmable.

Dependency-light: a vendored ~100-line Myers/LCS module (as in the prototype), no
framework, no build step. The prototype's `lcsOps`, `alignToRef`, `simil`,
`wordDiffHTML`, and `buildSectionGrid` are the canonical functions to port.

### 6.3 Diff options (quiet, secondary controls)

- **Word highlighting** on/off (default on).
- **Rubrics** on/off in the diff (default on): some readers want to compare only
  spoken text and treat rubric churn as noise. Off = rubric units excluded from
  the diff sequence (still shown greyed for context).
- **Spelling** (§4) applies here too: comparing in `normalized/` isolates
  substantive change; comparing in `original/` shows spelling change as well —
  exactly the README's guidance, made a live toggle.

### 6.4 Cross-line diffs

Diffing is pure text; it does not care whether the two editions share a branch.
So English `v1662` vs American `v1928` "just works." The picker still groups by
line for orientation, and the compare header notes when columns are on different
lines (e.g. a small "English ⇄ American" tag), because a cross-line diff mixes
genealogical distance with edition change — worth signalling, not preventing.

---

## 7. Column & edition selection

- Each column has an **edition selector**: a menu grouped by line
  (English / Scottish / American), each entry showing year + one-line description
  from `index.json`.
- Entries whose tag is **not in the service's `present_at`** are **disabled**
  with a reason on hover (e.g. *"Not in the 1764 Communion Office"*). This is the
  presence matrix, surfaced.
- **Add column** (up to 3) / **remove column** controls; reorder by drag or
  arrows (order matters — the leftmost is the compare base).
- Sensible defaults on first load for a service: the two or three editions whose
  diff is most illustrative (e.g. Morning Prayer → `v1549`, `v1552`, `v1662`;
  Holy Communion → `v1549`, `v1552`, `v1662`). Defaults live in `index.json` as
  an optional `feature_editions` per service so they are data, not code.

---

## 8. Section / navigation

- **Service picker** (primary control): grouped by `service_groups` from
  `index.json` (The Daily Office, The Litany, Holy Communion, Occasional Offices,
  …). Selecting a service loads its JSON and resets columns to defaults (§7).
- **Section rail:** the union of the selected editions' `##` anchors, in
  `canonical_anchors` order. Clicking scrolls all columns to that anchor (§5.4).
  An anchor present in some editions but not others is still listed, with a faint
  count (e.g. "The Exhortation · in 11 of 12").
- **Sticky context strip:** as the reader scrolls, a slim strip shows the current
  service and section, so deep in a long office they always know where they are.

---

## 9. State, permalinks, and the GitHub bridge

### 9.1 URL state (shareable, tag-keyed, SHA-free)

All view state lives in the URL so any view is a link a non-technical reader can
paste to a friend:

```
#/service=daily-office/morning-prayer&cols=v1549,v1552,v1662&spelling=normalized&mode=compare&base=v1549&anchor=the-exhortation
```

- `cols` is an ordered list of tags (order = column order; `cols[0]` = base
  unless `base` overrides).
- `anchor` is a slug of the `##` heading; on load the app scrolls to it.
- Unknown/stale tags degrade gracefully (drop the column, show a small notice)
  rather than erroring — important because tags are stable but presence can widen
  between waves.
- Optional `localStorage` remembers the reader's last view and their
  spelling/sync preferences (this is a real deployed site, so storage is fine).

### 9.2 GitHub bridge (optional, secondary)

When exactly two columns on the **same branch** are shown, offer a discreet
"View on GitHub ↗" that deep-links the repo's compare view, bridging the friendly
viewer to the underlying mechanism for the curious:

```
https://github.com/triblework/book-of-common-prayer/compare/v1549...v1552
```

Hidden for cross-branch pairs (GitHub compare across lines is noisier and off the
viewer's happy path).

---

## 10. Design system

**Direction:** traditional but modern. A quiet, book-like, light-mode surface —
warm parchment paper, warm near-black ink, a muted oxblood for rubrics, and
desaturated sage/rose for diffs so the comparison never turns into the harsh neon
of a raw code diff. Serif-forward throughout, with letterspaced small caps for
structural labels. It should feel like a well-set scholarly edition that happens
to be interactive — not a web app wearing a serif.

### 10.1 Color tokens (light mode)

```css
:root {
  /* Paper — warm off-whites */
  --paper:          #F5F1E8;  /* page background (parchment) */
  --paper-raised:   #FAF7F0;  /* columns / cards */
  --paper-sunken:   #ECE6D9;  /* wells, gutters, section rail */
  --gutter:         #E8E1D3;  /* diff line-number / marker gutter */

  /* Ink — warm near-blacks and grays (never pure #000) */
  --ink:            #2A2621;  /* primary reading text */
  --ink-soft:       #4B463C;  /* secondary text, headings’ subordinate parts */
  --ink-muted:      #837B6C;  /* captions, tags, citations */
  --ink-faint:      #A79E8C;  /* placeholders, “not in this edition” */

  /* Rules */
  --rule:           #E0D8C7;  /* hairlines */
  --rule-strong:    #CFC5AE;  /* column dividers, header underlines */

  /* Rubric — muted oxblood (“red letter”) */
  --rubric:         #9A4632;

  /* Accent — quiet slate-indigo, distinct from rubric to avoid confusion */
  --accent:         #445069;  /* links, active toggle, focus */
  --accent-hover:   #333D52;

  /* Diff — desaturated so it sits on parchment */
  --add-bg:         #E4EBDD;  /* addition cell */
  --add-bg-word:    #CBDABB;  /* added word highlight */
  --add-text:       #33422A;
  --add-sign:       #5D7A49;  /* the “+” marker */
  --del-bg:         #F0E2DC;  /* removal cell */
  --del-bg-word:    #E3C6BD;  /* removed word highlight */
  --del-text:       #5C342B;
  --del-sign:       #A05A49;  /* the “−” marker */
  --gap-bg:         #F3EEE4;  /* empty aligned cell (with faint hatch) */

  /* Line-accent tints (column header underlines) */
  --line-english:   #6B6250;
  --line-scottish:  #4C5B63;
  --line-american:  #5A5147;
}
```

Contrast intent: all body/diff **text** meets WCAG AA on its background; the
washes are backgrounds, never the sole signal (see §12). Tokens are tunable —
these are the locked defaults, not sacred hexes.

### 10.2 Typography

Serif-forward, oldstyle numerals on (they suit `Psalm 51.3`-style citations),
common ligatures on for reading text (off inside diff cells so word alignment
stays honest).

```css
:root {
  /* Reading text: modern, calm, screen-legible transitional serif */
  --font-reading: "Source Serif 4", "Spectral", Georgia, "Times New Roman", serif;
  /* Display / titles / headings: a Garamond-class face for liturgical air */
  --font-display: "EB Garamond", "Cardo", "Source Serif 4", Georgia, serif;
  /* Micro-UI labels (optional): a quiet humanist sans, or reuse the serif in small caps */
  --font-ui:      "Public Sans", "Inter", system-ui, sans-serif;

  --fs-title:   1.55rem;  /* office title */
  --fs-section: 1.05rem;  /* ## headings, letterspaced small caps */
  --fs-body:    1.02rem;  /* reading text */
  --fs-rubric:  0.98rem;  /* rubric italic */
  --fs-cite:    0.82rem;  /* scripture citations */
  --fs-label:   0.74rem;  /* small-caps structural labels */

  --lh-body:    1.55;
  --measure:    62ch;     /* single-column reading measure */
}
```

Recommended pairing (locked default): **reading = Source Serif 4** for its
strong small-size legibility, **display = EB Garamond** for the traditional
liturgical note. Alternatives, all OFL/free and appropriate, are **Cardo** (a
scholarly face designed for biblical/medieval texts — very BCP), **Spectral**,
and **Newsreader**. Rubrics render in `--font-reading` **italic**, `--rubric`
color. Speaker labels and `##` section labels render in **letterspaced small
caps** (`font-variant: small-caps; letter-spacing: 0.06em;`).

### 10.3 Layout & motion tokens

```css
:root {
  --col-min:      21rem;   /* legibility floor before horizontal-scroll fallback */
  --col-gap:      1.25rem;
  --rail-w:       15rem;
  --header-h:     3rem;    /* sticky top controls */
  --context-h:    2.25rem; /* sticky section strip */
  --radius:       4px;     /* restrained; this is a book, not a dashboard */
  --shadow:       0 1px 0 var(--rule);  /* hairline “lift”, no drop shadows */
  --motion:       120ms ease;  /* quick, quiet; disabled under reduced-motion */
}
```

Chrome is minimal: hairline rules over boxes, no heavy shadows, small radii,
generous whitespace. Transitions are short and subtle and fully suppressed under
`prefers-reduced-motion` (§12).

### 10.4 Wireframe (desktop, compare mode, three columns)

```
┌───────────────────────────────────────────────────────────────────────────┐
│  The Book of Common Prayer, in Parallel        [Modern ▾] [ Reading | Compare ]│  ← header
├──────────┬────────────────────────────────────────────────────────────────┤
│ SECTIONS │  Morning Prayer ▸ The Exhortation                               │  ← context strip
│          ├───────────────────┬───────────────────┬────────────────────────┤
│ Opening… │ 1549 · v1549 base │ 1552 · v1552      │ 1662 · v1662           │  ← column headers
│ Exhort…  ├───────────────────┼───────────────────┼────────────────────────┤
│ Confess… │  Our Father,      │ + Dearly beloved  │ + Dearly beloved       │
│ Absol…   │  which art in…    │ + brethren, the…  │ + brethren, the…       │
│ Lord’s…  │                   │ + Scripture mov…  │ + Scripture mov… judge │  ← word hi-lite
│ Versic…  │  ─ (neutral) ─    │   Our Father, …   │   Our Father, …        │
└──────────┴───────────────────┴───────────────────┴────────────────────────┘
        base neutral · adds green in each comparison · removals as red gaps
```

---

## 11. Responsive & mobile

- **≥ 1024px:** up to 3 columns side by side; section rail visible.
- **640–1024px:** up to 2 columns; rail collapses to a top dropdown.
- **< 640px:** **1 column**; editions become a horizontal switcher (chips). In
  **Compare** on mobile the split-column grid is impractical, so the diff renders
  as a **unified inline diff** against the base (interleaved +/− lines, GitHub's
  unified view), which is the natural one-column form of §6's model.
- Column width never drops below `--col-min`; if selected columns can't all fit
  above that floor, the container becomes horizontally scrollable with the base
  column pinned, rather than crushing the text.

---

## 12. Accessibility (first-class, not a pass)

- **Color is never the only signal.** Every addition/removal carries a text
  marker (`+` / `−`) and an ARIA label ("added in 1552", "removed after 1549");
  word highlights are backed by `<ins>`/`<del>` semantics.
- **Contrast:** body and diff text meet WCAG AA on their washes; the tokens above
  are chosen to satisfy this — re-check if retuned.
- **Keyboard:** all controls (spelling, mode, column add/remove/reorder,
  section rail, base-picker) are reachable and operable by keyboard with visible
  `--accent` focus rings; the section rail is an ARIA listbox; toggles are ARIA
  switches.
- **Semantics:** columns are `<article>`s with accessible names ("1662, English,
  v1662"); sections are landmarks; the diff grid uses roles that let a screen
  reader read a column linearly (reading order = source order).
- **Motion:** `prefers-reduced-motion` disables all transitions and any
  scroll-sync animation (jumps instead of animates).
- **Zoom / reflow:** usable to 200% zoom; the responsive fallbacks (§11) are the
  reflow story.

---

## 13. Provenance, licensing, and VERIFY

The viewer must carry the repo's scholarly and licensing commitments to the
reader — it is a publication surface, so the obligations travel with it.

Provenance is sourced **from the published layer only** (§3.1), never from
`authoring/provenance.yaml`.

- **`BCP 1662` acknowledgment.** Whenever a 1662 column is displayed, its header
  and its provenance popover show **`BCP 1662`**, and the site colophon records
  it. This is non-negotiable and driven by the `NOTICE.md` entry **plus** a hard
  rule keyed on the `v1662` tag (belt and braces).
- **Per-column provenance** (the ⓘ on each header): source URL and retrieval date
  parsed from the published **`SOURCES.md`** table, and the edition's copyright
  status from **`NOTICE.md`**, keyed by `<edition, service>`. Transcription
  `status` (`transcribed` / `reviewed-unchanged` / `inherited-unreviewed`) is
  surfaced when derivable from `SOURCES.md`; an `inherited-unreviewed` service
  shows a small honest caveat ("carried forward; not yet re-checked against a
  source for this edition").
- **Graceful fallback (required).** If a `<edition, service>` row is missing from
  `SOURCES.md`, the popover shows the edition-level `NOTICE.md` status plus a link
  to `SOURCES.md` rather than failing or inventing a citation; if status isn't
  derivable, the badge is omitted rather than guessed. A v1 viewer therefore works
  even where per-cell provenance is sparse.
- **VERIFY markers.** A `<!-- VERIFY: … -->` note renders as an unobtrusive
  margin marker (a small superscript ❓ or a dotted underline) on its unit; hover
  / focus reveals the note. Readers see the scholarship's honesty; the text is
  never silently "corrected."
- **Colophon / About panel:** what the project is (the §0 core idea, in plain
  language for non-technical readers), the original-vs-modern distinction and when
  to use each, links to `NOTICE.md` and `SOURCES.md`, and the design principle
  from §4.2. No license overreach: the viewer's *code* is under the repo's MIT
  `LICENSE`; the *texts* are governed by `NOTICE.md` — say so.
- **Excluded texts never appear**, because the viewer only ever renders tags the
  repo published; the builder has no capacity to fetch anything else.

---

## 14. Tech stack, hosting, and CI/deploy

- **Stack:** buildless — semantic HTML, CSS custom properties (§10 tokens), and
  vanilla ES modules. No framework, no bundler required. One small vendored diff
  module (§6.2). Fonts self-hosted (WOFF2) or from a privacy-respecting CDN; the
  colophon notes the font source.
- **Repo placement:** app source on `authoring` under `authoring/viewer/`;
  generated data under `viewer/data/` via the builder.
- **Deploy:** GitHub **Pages served from an Actions artifact**
  (`actions/upload-pages-artifact` → `actions/deploy-pages`) — **not** a
  `gh-pages` branch and **not** `/docs` on `main`. Nothing is committed to a
  served branch, so the wave-boundary force-pushes of the content branches can't
  clobber or race the site, and the viewer deploy is its own job on its own
  trigger, independent of `build_history.py`.
- **Base path — decide once.** A **project page** serves under the subpath
  `https://triblework.github.io/book-of-common-prayer/`, so all asset URLs and
  every `fetch('viewer/data/…')` MUST be **relative / base-path-aware** or they
  404. A **custom domain** (or a `triblework.github.io` user page) serves at root
  and avoids this. Default assumption: **project page + relative paths.** If a
  custom domain is chosen, set it in the workflow and the app base accordingly.
- **Runtime:** all diffing is client-side; the served payload is static
  HTML/CSS/JS + the prebuilt `viewer/data/*.json`. Fonts self-hosted (WOFF2) or
  from a privacy-respecting CDN; the colophon notes the font source.
- **Workflow `.github/workflows/viewer.yml`** (concrete):
  1. `actions/checkout` with `fetch-depth: 0` and `fetch-tags: true` (needs all
     tags + branch tips for ancestry);
  2. `pip install -r requirements.txt` (PyYAML);
  3. `python tools/build_viewer_data.py --out viewer/data` (git-only, §3.1);
  4. `python tools/build_viewer_data.py --check` (byte-stable rebuild gate);
  5. validate every emitted JSON against `viewer/data/schema/*.json` (§3.5) —
     hard gate;
  6. assemble the site (copy `authoring/viewer/` + `viewer/data/` into a publish
     dir);
  7. `upload-pages-artifact` → `deploy-pages`.
  **Triggers:** `push` on `'v*'` tags, `workflow_dispatch`, and (optionally)
  `workflow_run` after the publish workflow — so the live viewer tracks the
  published corpus. It runs **independently of the history-rebuild workflow**.

---

## 15. Performance

- **Lazy loading:** `index.json` on start (small); one service file on demand.
  A service file is a handful of editions × two trees of short liturgical text —
  well within a fast single fetch.
- **Client diff cost** is trivial at these lengths (tens to low hundreds of units
  per service); no need to precompute pairs. Memoize computed diffs per
  `(service, base, cols, spelling, options)` for instant mode/scroll toggling.
- **Caching:** `Cache-Control` on the static JSON; optional `localStorage` of the
  last view and preferences.
- **Stretch — corpus search:** a prebuilt lightweight index (service + edition +
  unit text) enabling "find this phrase across editions" is a natural later
  addition; out of v1 scope, but the per-service JSON already contains everything
  such an index would need.

---

## 16. Acceptance criteria

**Data & fidelity**
- [ ] `tools/build_viewer_data.py` emits `index.json` + one file per service from
      the published tags in both trees; `--check` proves byte-identical output on
      rebuild.
- [ ] The builder runs to completion against a **plain clone with tags and no
      `authoring` branch present** (decoupled, git-only), and never reads
      `editions.yaml`/`provenance.yaml` on the default path.
- [ ] Genealogy (line grouping; fork inheritance for `scottish`/`american`) is
      derived from **git ancestry** and matches the published branches; the
      presence matrix is **observed** from which files exist at each tag.
- [ ] The two JSON Schemas exist and **every emitted file validates** against them
      in CI.
- [ ] Every unit in the viewer traces to a real repo line; the viewer invents no
      text and displays no edition the tags don't contain.
- [ ] The presence matrix is honored: editions lacking a service are disabled in
      the picker and show the absence notice if force-linked.

**Core experience**
- [ ] A reader can pick a service, choose 1–3 editions, and read them in aligned
      parallel columns with rubrics in muted red and sections aligned at anchors.
- [ ] Toggling Compare shows a GitHub-style diff: base neutral, additions green,
      removals as red gaps, modified lines word-highlighted; it scales correctly
      to 2 and 3 columns on a shared base; it is disabled for 1 column.
- [ ] The Original/Modern toggle switches both modes between `original/` and
      `normalized/` and defaults to Modern.
- [ ] **Flagship diffs reproduce the prototype:** MP `v1549 → v1552` shows the
      added penitential introduction as a clean insertion; MP's 1662 Lord's-Prayer
      doxology shows as a targeted addition; and — the corpus being complete
      through Wave 9 — **at least one Holy Communion diff** (`v1549 → v1552`
      restructure / moved Gloria, or the Black Rubric) renders correctly.
      Word-highlighting fires on a modified line and **not** on a full replace.

**Navigation & sharing**
- [ ] The section rail jumps all columns to an anchor; sections stay aligned
      across columns while scrolling (banded/anchor alignment as in the
      prototype); a permalink round-trips service, columns, base, spelling, mode,
      and anchor, and degrades gracefully on stale tags.
- [ ] The two-column same-branch "View on GitHub" link opens the correct
      `/compare/vA...vB` view.

**Design, a11y, provenance**
- [ ] The visual matches §10: warm parchment, warm near-black ink, muted oxblood
      rubrics, desaturated sage/rose diffs, serif-forward with small-caps labels;
      no harsh pure-black or neon-diff.
- [ ] Diffs are legible without color (markers + ARIA); AA contrast holds;
      keyboard-navigable; reduced-motion respected; usable at 200% zoom and on a
      < 640px screen (single column; unified inline diff in Compare).
- [ ] Provenance renders from published `SOURCES.md`/`NOTICE.md`; a missing source
      row degrades to the `NOTICE.md` status + a `SOURCES.md` link (never a failure
      or an invented citation); `BCP 1662` appears wherever 1662 content shows;
      VERIFY notes surface in the margin; the colophon states the code (MIT) vs
      text (`NOTICE.md`) distinction.

**Deploy**
- [ ] CI builds data, passes the determinism and schema gates, and deploys the
      static site to Pages as an artifact, untouched by content-branch
      force-pushes.

---

## 17. Risks & mitigations

- **History force-pushes at wave boundaries** could serve stale viewer data.
  *Mitigate:* the viewer keys on **tags** (stable) not SHAs; the Pages build runs
  after each wave publish; `wave_note` in `index.json` and the colophon show when
  the data was built.
- **Three-column diff overwhelm.** *Mitigate:* the base+deltas model keeps the
  base clean and confines color to the comparison columns; word highlighting and
  rubric-inclusion are toggleable; default to 2 columns on first load.
- **Anchor misalignment when editions rename a section.** *Mitigate:* alignment
  uses `canonical_anchors` order; a genuine rename is shown as a section
  appearing/disappearing (a real, meaningful diff), and headings anchor the LCS
  in compare mode.
- **Unequal transcription depth mid-build-out** (a service deep in one edition,
  shallow in another) makes diffs look lopsided. *Mitigate:* the provenance
  popover shows `status`; an `inherited-unreviewed` badge warns the reader; the
  viewer never hides the gap.
- **Font loading / FOUT** harming the book feel. *Mitigate:* self-host WOFF2,
  `font-display: swap` with metric-compatible fallbacks (Georgia), preloaded
  reading face.
- **Scope creep toward an "app."** *Mitigate:* v1 is a reader; editing, auth, and
  corpus search are explicitly out (§2, §15). The chrome stays hairline-quiet by
  design.

---

## 18. First actions for the implementing agent

1. Read this spec, `README.md`/`CONTRIBUTING.md`/`SOURCES.md`/`NOTICE.md`, and
   **open `prototype/bcp-viewer-prototype.html`** — treat it as the reference for
   the diff engine (§6.2) and the §10 design tokens. Do not redesign it.
2. Author the two JSON Schemas (§3.5).
3. Implement `tools/build_viewer_data.py` on the **git-only** path (§3.1). Prove
   it on a **bare clone with tags and no `authoring` branch**; make `--check`
   byte-stable; validate the output against the schemas. This is the load-bearing
   piece — get the data model right before any UI.
4. Port the prototype onto real `viewer/data/*.json`: keep its tokens and diff
   behavior; wire **reading mode** (anchor-aligned columns, rubric styling,
   spelling toggle) and **compare mode** (base+deltas grid, word highlighting).
   Verify MP `v1549 → v1552` and one Holy Communion diff.
5. Add navigation (section rail, sticky context), tag-keyed permalinks, the
   GitHub bridge, provenance/VERIFY surfacing (from `SOURCES.md`/`NOTICE.md`, with
   fallback), and the colophon.
6. Accessibility and responsive passes (§11, §12); then wire the **independent**
   Pages CI workflow (§14), settling the base-path decision.

Prefer correctness and fidelity over features. The viewer must never become a
second source of truth: it renders what the repository published, and nothing
else.
