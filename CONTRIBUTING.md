# Contributing

Thank you for helping build a version-controlled Book of Common Prayer. Please
read this before opening a pull request — the repository's whole value depends
on a few conventions being followed exactly.

## The core model: editions are commits, not folders

**Never add per-edition directories** (no `/1549/`, no `/1662/`). The edition
axis *is* git history:

- Each **edition** is a single **commit** that snapshots the *same* set of files
  with that edition's content, and is marked with an annotated **tag**
  (`v1549`, `v1552`, …).
- Real liturgical genealogy is modeled with **branches**:
  - `main` — the English line (1549 → 1552 → 1559 → 1604 → 1662).
  - `scottish` — forks from `v1604` (1637 → 1764 → 1929).
  - `american` — forks from `v1662` (1789 → 1892 → 1928 → 1979).
- Original vs. modernized spelling is a *representation*, present at every
  commit as two parallel trees: `texts/original/` and `texts/normalized/`.

This is what makes `git diff v1552 v1662 -- texts/normalized/daily-office/morning-prayer.md`
and the GitHub compare view show exactly how a service changed between editions.

## History is a build artifact — work on the `authoring` branch

The published branches (`main`, `scottish`, `american`) and every `vYYYY` tag are
**generated outputs**. You do not hand-commit to them. All content work happens on
the orphan **`authoring`** branch, and `tools/build_history.py` deterministically
replays the whole commit/branch/tag graph from it.

Why: completing an early edition's services necessarily *changes that edition's
commit* (so `git diff v1549 v1552` can render a real liturgical change), which
means history must be rewritten. A deterministic builder makes that safe and
repeatable. This is the same philosophy already applied to `texts/normalized/`
(a generated function of `texts/original/`), lifted to the whole history.

The `authoring` branch holds:

```
editions.yaml      # the genealogy: editions, branches, parents, tags, present/absent
provenance.yaml    # per <service, edition> source + verify metadata (sign-off status)
editions/<year>/   # only the service text a given edition ADDS or CHANGES
repo-root/         # files copied verbatim into every published commit (README, LICENSE, …)
tools/             # the canonical tooling, stamped identically into every commit
```

An edition inherits every service it does not itself author; a service it drops is
listed in that edition's `absent:` (a clean removal diff). Run the builder to
verify your change reproduces the live history before publishing:

```bash
python3 tools/build_history.py --authoring . --live-repo . --check   # must be green
```

Publishing (rebuild + force-push of the three branches and all tags) happens only
at a **wave boundary**, never mid-wave — see the spec §2.6. SHAs are explicitly
**not** part of the interface; tags and diffs are.

## Text format conventions (make diffs readable)

1. **One unit per line ("semantic line breaks").** Each sentence, versicle,
   response, or rubric goes on its own line. This is the single most important
   rule — git diffs by line. `tools/sentence_split.py` enforces it; run it on
   every file before committing.
2. **Light Markdown structure:**
   - `#` = office/service title (e.g. `# The Order for Morning Prayer`).
   - `##` = major sections within a service.
   - **Rubrics** (spoken-word instructions) → blockquote lines beginning `> `.
   - **Spoken text** → plain lines.
   - **Speaker labels** → bold prefix on the same line, e.g. `**Priest.** …`,
     `**Answer.** …`.
   - Never hard-wrap within a unit; one logical unit = one line, however long.
3. **Encoding & whitespace:** UTF-8, LF endings, no trailing whitespace, a
   single trailing newline at EOF. Normalize long-s (ſ→s) and archaic ligatures
   even in `original/`; keep everything else (u/v, i/j, -ie/-y, doubled
   consonants, thorn) as printed.
4. **Stable anchors:** keep section headings identical in wording across
   editions wherever the section persists, so only the *body* diffs. A genuine
   rename between editions is itself a meaningful diff — allow it.

## Never hand-edit `texts/normalized/`

`texts/normalized/` is **generated** from `texts/original/` by
`tools/normalize.py` using `tools/normalization_rules.yaml`. To change the
normalized text you either edit the original, or improve the rules — then
regenerate:

```bash
python3 tools/normalize.py            # regenerate normalized/ from original/
python3 tools/normalize.py --check    # CI: fail if normalized/ is stale
```

Normalization is **spelling only** — never change vocabulary, word order, or
meaning (`shew`→`show` is fine; `divers`→`various` is forbidden). Rule changes
are reviewed as diffs to `normalization_rules.yaml`.

## How to add or change a service (on `authoring`)

1. **Check out `authoring`.** Never edit `texts/` on a published branch — it is
   regenerated.
2. **Add or edit `editions/<year>/<service>.md`** to that edition's state. Author
   only what the edition *adds or changes*; unchanged services are inherited
   automatically. To drop a whole service, list it in that edition's `absent:` in
   `editions.yaml` (a clean removal diff) rather than leaving a stub.
3. **Update `editions.yaml`** if you added an edition, changed the genealogy, or
   changed a `present:`/`absent:` set.
4. **Record provenance** in `provenance.yaml`: the source URL, retrieval date,
   verifier, and `status` (`transcribed` / `reviewed-unchanged` /
   `inherited-unreviewed`). Flag doubtful readings inline with
   `<!-- VERIFY: ... -->` and add a matching `verify_items` entry.
5. **Verify the rebuild** reproduces the live history and the indexes are in sync:
   ```bash
   python3 tools/verify_index.py --root . --check
   python3 tools/build_history.py --authoring . --live-repo . --check
   ```
6. **Commit to `authoring`.** Publishing (the force-push of the regenerated
   branches and tags) is a separate, wave-boundary step run by a maintainer — see
   the spec §2.6.

`tools/sentence_split.py` and `tools/normalize.py` are run *for* you by the
builder when it materializes each commit; you do not commit generated
`texts/normalized/` by hand.

## Licensing guardrails (mandatory)

Only include texts that are clearly free to reproduce. **Do not** add Common
Worship (2000), the Church of Ireland 2004 book, or modern Canadian/Australian/
other 20th–21st-century non-US revisions. Add a source host to
`tools/scrape.py`'s allow-list only after confirming licensing. When in doubt,
skip the text and note the omission in `SOURCES.md`. See `NOTICE.md` for the
per-edition copyright status and the `BCP 1662` acknowledgment.

## Handy local git aliases

```bash
git config diff.prose.wordRegex '[^[:space:]]'
git config alias.wdiff 'diff --word-diff=color'
git config alias.cdiff 'diff --color-words'
```
