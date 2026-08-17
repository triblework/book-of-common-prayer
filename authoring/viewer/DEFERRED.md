# Viewer — deferred improvements

Tracked here so we circle back. None of these block v1; each has a working,
correct behavior today.

## 1. `canonical_anchors` ordering when the 1979 American Rite II is in view
`tools/build_viewer_data.py::merge_anchor_order` builds the global section order
with an order-preserving greedy merge of every edition's `##` heading sequence.
This is correct for the flagship English comparisons (the 1552 penitential
opening sorts before "The Lordes Prayer"). Side effect: the 1979 BCP's Rite II
carries many uniquely-named sections ("Confession of Sin", "The Invitatory and
Psalter", canticle numbers, …) that have no shared neighbours, so they cluster
near the **top** of the rail whenever 1979 is one of the selected columns. Only
visible when 1979 is in view; the per-section diff itself is unaffected (it keys
on anchor identity, not order).

_Possible fixes to weigh:_ pick a per-view spine (the most-complete selected
edition) and order relative to it; or compute the order over only the
in-view editions at render time rather than globally at build time; or a proper
shortest-common-supersequence over the selected columns.

## 2. Fonts are loaded from the Google Fonts CDN
The spec (§14) prefers self-hosted WOFF2. Today `index.html` links Google Fonts
with `font-display: swap` and a metric-compatible Georgia fallback, and the
colophon names the source. Circle back to vendor the WOFF2 files under
`authoring/viewer/fonts/` and drop the third-party request.

## QA pass — low/latent items deliberately deferred

From the holistic QA pass (two adversarial code reviews + hands-on testing). The
high/medium findings were all fixed; these remain, each low-risk and non-blocking:

- **§6.4 cross-line indicator** — a "English ⇄ American" tag when comparing columns
  on different branches is specced but not implemented. Diff still works.
- **Rubric-only section with Rubrics toggled off** shows an empty band header
  instead of hiding or greying it. Cosmetic.
- **3-column mobile unified diff** (`renderUnified`, `mods` branch) can drop a
  third column's `delgap` and labels the base `−` line with the first comparison's
  year. Mobile is single-column by spec, so effectively unreachable.
- **Dead `ignoreHash` guard** in `onHashChange` — inert today; keep or remove.
- **Builtin validator ignores `$ref` siblings** (`build_viewer_data.py::_validate`).
  Latent: neither schema places keywords beside a `$ref`. The reference
  `jsonschema` validator (used in CI) has no such gap.
- **`--authoring` `feature_editions` enrichment** (`_load_authoring`) collects
  empty lists; off-by-default path, no `editions.yaml` currently defines them.
- **Parser nits**: `>`-without-space is accepted as a rubric (robust, off the
  `> ` contract); multi-line `<!-- VERIFY -->` notes retain embedded newlines.

## 3. Provenance is edition-level, not per-`<edition, service>`
`SOURCES.md`/`NOTICE.md` expose per-edition rows only, so the viewer uses the
spec §13 graceful fallback (edition status + a link to `SOURCES.md`) as the
normal path. If per-service provenance rows are ever added upstream, the builder
and popover can surface them without a schema change (fields already nullable).
