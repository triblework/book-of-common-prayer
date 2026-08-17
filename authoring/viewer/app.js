// app.js — the reader's viewer (spec §5–§13). Buildless ES module.
// Loads viewer/data/index.json once, then one service file on demand, and
// renders reading (parallel columns) + compare (base+deltas diff) modes.

import { esc, alignToRef, simil, wordDiffHTML } from "./diff.js";

/* ============================================================ helpers ======= */
const $ = (s) => document.querySelector(s);
const dataURL = (name) => new URL("viewer/data/" + name, document.baseURI).href;
const slug = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
// Only allow http(s)/mailto in hrefs, so a stray SOURCES.md `javascript:` URL
// can never become a click-to-execute link.
const safeUrl = (u) => (u && /^(https?:|mailto:)/i.test(u.trim()) ? u.trim() : null);
const LINE_LABEL = { english: "English", scottish: "Scottish", american: "American" };

/* ============================================================ data ========== */
let INDEX = null; // index.json
let SERVICE = null; // current service payload
const EDMETA = {}; // tag -> edition meta (line/branch/desc/provenance/ack)
const SERVICE_CACHE = {};
const SERVICE_INDEX = {}; // id -> index service entry (present_at, feature_editions, label)

const state = {
  service: null,
  cols: [],
  base: null,
  spelling: "normalized", // normalized | original
  mode: "reading", // reading | compare
  wordDiff: true,
  rubrics: true,
  anchor: null, // current section slug, for the permalink
};

// Per-service anchor -> unique slug map (canonical_anchors can contain entries
// that slugify identically, e.g. "The Exhortation" vs "The Exhortation."). Built
// in loadService so ids/hrefs never collide.
let SLUG_BY_ANCHOR = new Map();
function buildSlugMap(anchors) {
  SLUG_BY_ANCHOR = new Map();
  const used = new Set();
  for (const a of anchors) {
    let base = slug(a) || "sec";
    let s = base, i = 2;
    while (used.has(s)) s = base + "-" + i++;
    used.add(s);
    SLUG_BY_ANCHOR.set(a, s);
  }
}
const slugFor = (a) => SLUG_BY_ANCHOR.get(a) || slug(a);

const PREF_KEY = "bcp-viewer-prefs";
// True only for a real phone-width viewport. A width of 0 (e.g. a hidden/
// not-yet-measured frame) must NOT count as narrow, or the grid would collapse
// to the unified diff off-screen.
const isNarrow = () => {
  const w = window.innerWidth;
  return w > 0 && w <= 640;
};

/* ============================================================ boot =========== */
async function init() {
  try {
    INDEX = await fetch(dataURL("index.json")).then((r) => {
      if (!r.ok) throw new Error("index.json " + r.status);
      return r.json();
    });
  } catch (e) {
    $("#content").innerHTML =
      `<p class="absent-whole">Could not load the viewer data (<code>${esc(String(e))}</code>). ` +
      `Run <code>python tools/build_viewer_data.py --out viewer/data</code> and serve the site root.</p>`;
    return;
  }

  for (const line of INDEX.lines)
    for (const ed of line.editions) EDMETA[ed.tag] = { ...ed, line: line.id, branch: line.branch };
  for (const g of INDEX.service_groups) for (const s of g.services) SERVICE_INDEX[s.id] = s;

  populateServicePicker();
  applyPrefs();

  const url = parseHash();
  const stored = loadStored();
  const startService =
    (url.service && SERVICE_INDEX[url.service] && url.service) ||
    (stored.service && SERVICE_INDEX[stored.service] && stored.service) ||
    firstPopulatedService();
  // With no URL hash, restore the reader's last view (§9.1); the URL always wins.
  const initial = Object.keys(url).length
    ? url
    : (stored.service === startService
        ? { cols: stored.cols, base: stored.base, mode: stored.mode, spelling: stored.spelling }
        : {});

  wireControls();
  const noticeHref = safeUrl(INDEX.notice && INDEX.notice.notice_url);
  if (noticeHref) $("#ack-notice-link").href = noticeHref;

  await loadService(startService, initial);
  window.addEventListener("hashchange", onHashChange);
  window.addEventListener("resize", debounce(render, 150));
}

function firstPopulatedService() {
  for (const g of INDEX.service_groups)
    for (const s of g.services) if (s.present_at.length) return s.id;
  return INDEX.service_groups[0].services[0].id;
}

/* ============================================================ service load === */
async function loadService(id, url = {}) {
  const entry = SERVICE_INDEX[id];
  if (!entry) return;
  if (!SERVICE_CACHE[id]) {
    SERVICE_CACHE[id] = await fetch(dataURL(entry.file)).then((r) => r.json());
  }
  SERVICE = SERVICE_CACHE[id];
  state.service = id;
  buildSlugMap(SERVICE.canonical_anchors);

  const present = entry.present_at;
  // Columns: URL cols (filtered to present) > feature_editions > sensible default.
  let cols = [];
  let dropped = [];
  if (url.cols && url.cols.length) {
    for (const t of url.cols) (present.includes(t) ? cols : dropped).push(t);
  }
  if (!cols.length) cols = pickDefaults(entry);
  cols = cols.filter((t, i) => cols.indexOf(t) === i).slice(0, 3);

  state.cols = cols;
  state.base = url.base && cols.includes(url.base) ? url.base : cols[0];
  if (url.spelling === "original" || url.spelling === "normalized") state.spelling = url.spelling;
  if (url.mode === "compare" || url.mode === "reading") state.mode = url.mode;
  state.anchor = url.anchor || null;

  $("#svc-picker").value = id;
  refreshModeAvailability();
  syncToggleUI();
  render();
  if (url.anchor) whenReady(() => scrollToAnchor(url.anchor));
  if (dropped.length) flashNotice(`Skipped ${dropped.join(", ")} — not in this service.`);
  syncHash();
}

function pickDefaults(entry) {
  const present = entry.present_at;
  if (entry.feature_editions && entry.feature_editions.length)
    return entry.feature_editions.filter((t) => present.includes(t)).slice(0, 3);
  const preferred = ["v1549", "v1552", "v1662"].filter((t) => present.includes(t));
  if (preferred.length >= 2) return preferred;
  // else: earliest, a middle, and latest present edition
  if (present.length <= 3) return present.slice();
  const first = present[0], last = present[present.length - 1];
  const mid = present[Math.floor(present.length / 2)];
  return [first, mid, last].filter((t, i, a) => a.indexOf(t) === i);
}

/* ============================================================ data access ==== */
function treeOf(tag) {
  const ed = SERVICE.editions[tag];
  if (!ed) return null;
  return ed.trees[state.spelling] || ed.trees.normalized;
}
function serviceAbsent(tag) {
  const t = treeOf(tag);
  return !t || !t.present;
}
function titleOf(tag) {
  const t = treeOf(tag);
  if (!t || !t.present) return null;
  const tu = t.units.find((u) => u.kind === "title");
  return tu ? tu.text : t.title;
}
// A `##` (level-2) heading is a section band label; the title is a running head.
// Both are excluded from a section's body. `###`+ sub-headings ARE body content
// (they render inline within their parent section).
const isBandLabel = (u) => u.kind === "title" || (u.kind === "heading" && (u.level || 2) === 2);
// Units under an anchor (null = preamble before the first heading).
function unitsOf(tag, anchor) {
  const t = treeOf(tag);
  if (!t || !t.present) return null;
  return t.units.filter((u) => u.anchor === anchor && !isBandLabel(u));
}
function hasSection(tag, anchor) {
  const u = unitsOf(tag, anchor);
  return u && u.length > 0;
}
function anchorsInView() {
  const anchors = [];
  if (state.cols.some((t) => { const u = unitsOf(t, null); return u && u.length; })) anchors.push(null);
  for (const a of SERVICE.canonical_anchors)
    if (state.cols.some((t) => hasSection(t, a))) anchors.push(a);
  return anchors;
}

/* ============================================================ diff (compare) = */
function unitsForDiff(tag, anchor) {
  let us = unitsOf(tag, anchor);
  if (us === null) return null;
  if (!state.rubrics) us = us.filter((u) => u.kind !== "rubric");
  return us;
}

// Ported from prototype buildSectionGrid (spec §6.2): base + deltas per anchor.
function buildSectionGrid(anchor) {
  const cols = state.cols.map((tag) => {
    const us = unitsForDiff(tag, anchor) || [];
    return { tag, units: us, text: us.map((u) => u.text) };
  });
  const base = cols.find((c) => c.tag === state.base) || cols[0];
  const baseEmpty = base.text.length === 0;
  const ref = baseEmpty ? cols.slice().sort((a, b) => b.text.length - a.text.length)[0] : base;
  const aligns = {};
  for (const c of cols) aligns[c.tag] = alignToRef(ref.text, c.text);

  const rows = [];
  const pushInsertions = (gap) => {
    const seen = [];
    for (const c of cols) {
      const list = aligns[c.tag].insAfter[gap] || [];
      for (const bi of list) {
        const txt = c.text[bi];
        // Merge identical insertions ACROSS columns onto one row, but a line
        // repeated WITHIN a column (e.g. a thrice-said response) needs its own
        // row each time — so only reuse a row this column hasn't filled yet.
        let row = seen.find((r) => r.text === txt && r.by[c.tag] === undefined);
        if (!row) { row = { text: txt, by: {} }; seen.push(row); }
        row.by[c.tag] = bi;
      }
    }
    for (const r of seen) {
      const cells = {};
      for (const c of cols) {
        if (r.by[c.tag] !== undefined) {
          const u = c.units[r.by[c.tag]];
          cells[c.tag] = { type: c.tag === state.base ? "base" : "add", unit: u };
        } else cells[c.tag] = { type: "blank" };
      }
      rows.push({ cells });
    }
  };
  for (let g = 0; g <= ref.text.length; g++) {
    pushInsertions(g);
    if (g === ref.text.length) break;
    const cells = {};
    for (const c of cols) {
      const mi = aligns[c.tag].matched[g];
      if (c.tag === state.base) {
        cells[c.tag] = baseEmpty ? { type: "blank" } : { type: "base", unit: mi >= 0 ? c.units[mi] : base.units[g] };
      } else if (mi >= 0) {
        cells[c.tag] = { type: baseEmpty ? "add" : "eq", unit: c.units[mi] };
      } else {
        cells[c.tag] = baseEmpty
          ? { type: "blank" }
          : { type: "delgap", removed: base.units[g] ? base.units[g].text : ref.text[g], removedUnit: base.units[g] };
      }
    }
    rows.push({ cells });
  }

  // Modified-pair merge -> word-level 'mod' cell (spec §6.2).
  if (state.wordDiff) {
    for (let i = 0; i < rows.length - 1; i++) {
      for (const c of cols) {
        if (c.tag === state.base) continue;
        const cell = rows[i].cells[c.tag];
        if (!cell || cell.type !== "delgap") continue;
        for (let k = i + 1; k < Math.min(rows.length, i + 4); k++) {
          const nxt = rows[k].cells[c.tag];
          if (nxt && nxt.type === "add" && nxt.unit) {
            const baseTxt = cell.removed, colTxt = nxt.unit.text;
            if (simil(baseTxt, colTxt) > 0.4) {
              rows[i].cells[c.tag] = { type: "mod", unit: nxt.unit, html: wordDiffHTML(baseTxt, colTxt) };
              rows[k].cells[c.tag] = { type: "blank" };
            }
            break;
          }
          if (nxt && nxt.type !== "blank") break;
        }
      }
    }
  }
  return rows;
}

/* ============================================================ render ========= */
function lineTint(tag) { return "var(--line-" + EDMETA[tag].line + ")"; }
function gridTemplate() { return state.cols.map(() => "minmax(var(--col-min),1fr)").join(" "); }

const CITE_RE = /^(?:[1-3]\s+)?(?:(?:St\.?|Saint)\s+)?[A-Z][A-Za-z']+\.?\s+[0-9ivxlcdm]+(?:[.:,]\s?[0-9ivxlcdm-]+)*\.?$/;
function isCite(u) { return u.kind === "text" && u.text.trim().length <= 34 && CITE_RE.test(u.text.trim()); }

function verifyMark(notes) {
  const t = esc(notes.join("  •  "));
  return `<a class="verify-mark" tabindex="0" role="note" aria-label="Editorial note (VERIFY): ${t}" title="${t}">❓</a>`;
}
function unitReadingHTML(u) {
  const v = u.verify && u.verify.length;
  const mark = v ? verifyMark(u.verify) : "";
  const vc = v ? " has-verify" : "";
  if (u.kind === "title") return `<p class="u title">${esc(u.text)}</p>`;
  if (u.kind === "heading") return `<p class="u subheading">${esc(u.text)}</p>`; // ###+ sub-heading
  if (u.kind === "note") return `<p class="u note">${esc(u.text)}</p>`;
  if (u.kind === "rubric") return `<p class="u rubric${vc}">${esc(u.text)}${mark}</p>`;
  if (u.kind === "speech")
    return `<p class="u speech${vc}"><span class="speaker">${esc(u.speaker || "")}.</span>${esc(u.text)}${mark}</p>`;
  if (isCite(u)) return `<p class="u cite${vc}">${esc(u.text)}${mark}</p>`;
  return `<p class="u${vc}">${esc(u.text)}${mark}</p>`;
}

function cellClass(cell) {
  let k = "cell " + cell.type;
  const u = cell.unit || cell.removedUnit;
  if (u && u.kind === "rubric") k += " rubric";
  if (u && u.kind === "heading") k += " subhead"; // ###+ sub-heading
  return k;
}
function cellAria(cell, tag) {
  const y = EDMETA[tag].year;
  if (cell.type === "add") return `added in ${y}`;
  if (cell.type === "mod") return `modified in ${y}`;
  if (cell.type === "delgap") return `removed in ${y}; present in the base`;
  return "";
}
function cellInnerHTML(cell) {
  if (cell.type === "blank") return `<span class="sign"></span>`;
  if (cell.type === "delgap")
    return `<span class="sign"></span><span class="removed-line" title="Present in the base edition">${esc(cell.removed)}</span>`;
  const u = cell.unit;
  if (!u) return `<span class="sign"></span>`;
  const v = u.verify && u.verify.length ? verifyMark(u.verify) : "";
  let body;
  if (cell.type === "mod") body = cell.html + v;
  else if (u.kind === "speech") body = `<span class="speaker">${esc(u.speaker || "")}.</span>${esc(u.text)}${v}`;
  else body = esc(u.text) + v;
  return `<span class="sign"></span><span>${body}</span>`;
}

function render() {
  closePop();
  const compare = state.mode === "compare";
  $("#legend").hidden = !compare;
  renderColHeads();
  renderContent();
  renderRail();
  renderContext();
  renderAckBanner();
  syncHash();
  savePrefs();
}

function renderAckBanner() {
  const show = state.cols.some((t) => EDMETA[t] && EDMETA[t].acknowledgment);
  const b = $("#ack-banner");
  if (show && b.dataset.dismissed !== "1") b.hidden = false;
  else if (!show) b.hidden = true;
}

function renderColHeads() {
  const el = $("#colheads");
  el.style.gridTemplateColumns = gridTemplate();
  el.innerHTML = "";
  const present = SERVICE_INDEX[state.service].present_at;
  state.cols.forEach((tag, idx) => {
    const e = EDMETA[tag];
    const isBase = state.mode === "compare" && tag === state.base;
    const div = document.createElement("article");
    div.className = "colhead";
    div.setAttribute("aria-label", `${e.year}, ${LINE_LABEL[e.line]}, ${tag}`);

    // Selector grouped by line, presence-filtered.
    let opts = "";
    for (const line of INDEX.lines) {
      opts += `<optgroup label="${LINE_LABEL[line.id]}">`;
      for (const ced of line.editions) {
        const t = ced.tag;
        const dis = present.includes(t) ? "" : "disabled";
        const sel = t === tag ? "selected" : "";
        const title = present.includes(t) ? "" : ` title="Not in this service"`;
        opts += `<option value="${t}" ${sel} ${dis}${title}>${ced.year} · ${LINE_LABEL[line.id]}${present.includes(t) ? "" : " (absent)"}</option>`;
      }
      opts += `</optgroup>`;
    }
    const ackBadge = e.acknowledgment ? `<span class="ack-badge" title="Reproduced with the required acknowledgment">${esc(e.acknowledgment)}</span>` : "";
    div.innerHTML = `
      <div class="row1"><span class="year">${e.year}</span>
        <span class="tag">${tag}</span>
        ${isBase ? '<span class="basebadge">base</span>' : ""}
        ${ackBadge}
      </div>
      <div class="line">${LINE_LABEL[e.line]} line</div>
      <div class="desc">${esc(e.desc || "")}</div>
      <div class="accent" style="background:${lineTint(tag)}"></div>
      <div class="tools">
        <select aria-label="Edition for column ${idx + 1}" data-col="${idx}">${opts}</select>
        ${state.mode === "compare" && !isBase ? `<button class="mini" data-base="${tag}">set base</button>` : ""}
        <button class="mini" data-prov="${tag}" title="Where this text comes from">ⓘ prov</button>
        ${state.cols.length > 1 ? `<button class="mini" data-remove="${idx}" title="Remove column" aria-label="Remove column ${idx + 1}">✕</button>` : ""}
      </div>`;
    el.appendChild(div);
  });
}

function renderContent() {
  const host = $("#content");
  host.innerHTML = "";
  const tmpl = gridTemplate();

  // Title band (running heads) — rendered in BOTH modes so a title change
  // (e.g. 1662 "The Preface" -> "Concerning the Service of the Church", which is
  // a title, not a `##` heading) is visible in Compare, not only in Reading.
  {
    const tb = document.createElement("div");
    tb.className = "band";
    const cols = document.createElement("div");
    cols.className = "cols";
    cols.style.gridTemplateColumns = tmpl;
    const baseTitle = state.mode === "compare" ? titleOf(state.base) : null;
    state.cols.forEach((tag) => {
      const c = document.createElement("article");
      c.className = "col";
      c.setAttribute("aria-label", `${EDMETA[tag].year} ${LINE_LABEL[EDMETA[tag].line]}`);
      if (serviceAbsent(tag)) {
        c.innerHTML = `<div class="absent-whole">${esc(SERVICE.label)} is not present in the ${EDMETA[tag].year} book.</div>`;
      } else {
        const t = titleOf(tag);
        // In compare, flag a title that differs from the base's.
        const changed = state.mode === "compare" && tag !== state.base && t && t !== baseTitle;
        c.innerHTML = t ? `<p class="u title${changed ? " title-changed" : ""}">${esc(t)}</p>` : "";
      }
      cols.appendChild(c);
    });
    tb.appendChild(cols);
    host.appendChild(tb);
  }

  anchorsInView().forEach((anchor) => {
    const band = document.createElement("section");
    band.className = "band";
    if (anchor !== null) band.id = "sec-" + slugFor(anchor);
    if (anchor !== null) {
      const label = document.createElement("div");
      label.className = "seclabel";
      const n = state.cols.filter((t) => hasSection(t, anchor)).length;
      label.innerHTML = `${esc(anchor)}${n < state.cols.length ? `<span class="anchor-count">in ${n} of ${state.cols.length}</span>` : ""}`;
      band.appendChild(label);
    }

    if (state.mode === "reading") {
      const cols = document.createElement("div");
      cols.className = "cols";
      cols.style.gridTemplateColumns = tmpl;
      state.cols.forEach((tag) => {
        const c = document.createElement("article");
        c.className = "col";
        const us = unitsOf(tag, anchor);
        if (us === null) c.innerHTML = `<div class="absent">service not in this book</div>`;
        else if (us.length === 0) c.innerHTML = `<div class="absent">— not in this edition —</div>`;
        else c.innerHTML = us.map(unitReadingHTML).join("");
        cols.appendChild(c);
      });
      band.appendChild(cols);
    } else if (isNarrow()) {
      band.appendChild(renderUnified(anchor));
    } else {
      const rows = buildSectionGrid(anchor);
      rows.forEach((r) => {
        const cr = document.createElement("div");
        cr.className = "crow";
        cr.style.gridTemplateColumns = tmpl;
        state.cols.forEach((tag) => {
          const cell = r.cells[tag] || { type: "blank" };
          const d = document.createElement("div");
          d.className = cellClass(cell);
          const aria = cellAria(cell, tag);
          if (aria) d.setAttribute("aria-label", aria);
          d.innerHTML = cellInnerHTML(cell);
          cr.appendChild(d);
        });
        band.appendChild(cr);
      });
    }
    host.appendChild(band);
  });
}

// Mobile unified inline diff against the base (spec §11). Each base line is
// emitted once: as context when kept, as "−" when dropped, and as "~" (with a
// word diff) when reworded; comparison-only lines are "+".
function renderUnified(anchor) {
  const wrap = document.createElement("div");
  const rows = buildSectionGrid(anchor);
  const others = state.cols.filter((t) => t !== state.base);
  rows.forEach((r) => {
    const baseCell = r.cells[state.base];
    if (baseCell && baseCell.type === "base") {
      const baseText = baseCell.unit ? baseCell.unit.text : "";
      const dels = [], mods = [];
      others.forEach((t) => {
        const c = r.cells[t];
        if (!c) return;
        if (c.type === "delgap") dels.push(t);
        else if (c.type === "mod") mods.push({ t, c });
      });
      if (mods.length) {
        wrap.appendChild(uniRowText("−", baseText, "del", others[0], baseCell.unit));
        mods.forEach((m) => wrap.appendChild(uniRow("~", m.c.unit, "add", m.t, m.c.html)));
      } else if (dels.length && dels.length === others.length) {
        wrap.appendChild(uniRowText("−", baseText, "del", others.length === 1 ? others[0] : null, baseCell.unit));
      } else {
        wrap.appendChild(uniRow(" ", baseCell.unit, ""));
        dels.forEach((t) => wrap.appendChild(uniRowText("−", baseText, "del", t, baseCell.unit)));
      }
    } else {
      others.forEach((t) => {
        const c = r.cells[t];
        if (c && c.type === "add" && c.unit) wrap.appendChild(uniRow("+", c.unit, "add", t));
        else if (c && c.type === "mod" && c.unit) wrap.appendChild(uniRow("~", c.unit, "add", t, c.html));
      });
    }
  });
  return wrap;
}
function uniRow(sign, unit, cls, tag, html) {
  const d = document.createElement("div");
  d.className = "uni-row " + cls + (unit && unit.kind === "rubric" ? " rubric" : "");
  const hint = tag ? `<span class="uni-colhint">${EDMETA[tag].year}</span>` : "";
  const body = html ? html : unit ? (unit.kind === "speech" ? `<b>${esc(unit.speaker || "")}.</b> ${esc(unit.text)}` : esc(unit.text)) : "";
  d.innerHTML = `<span class="usign">${sign}</span><span>${hint}${body}</span>`;
  return d;
}
function uniRowText(sign, text, cls, tag, unit) {
  const d = document.createElement("div");
  d.className = "uni-row " + cls + (unit && unit.kind === "rubric" ? " rubric" : "");
  const hint = tag ? `<span class="uni-colhint">${EDMETA[tag].year}</span>` : "";
  d.innerHTML = `<span class="usign">${sign}</span><span>${hint}${esc(text)}</span>`;
  return d;
}

function renderRail() {
  const ul = $("#rail-list");
  ul.innerHTML = "";
  const mob = $("#mobile-sections");
  mob.innerHTML = "";
  anchorsInView().forEach((a) => {
    if (a === null) return;
    const s = slugFor(a);
    const n = state.cols.filter((t) => hasSection(t, a)).length;
    const li = document.createElement("li");
    li.setAttribute("role", "option");
    const active = state.anchor === s ? " active" : "";
    li.innerHTML = `<a class="sec${active}" data-slug="${s}" href="#sec-${s}">${esc(a)}<span class="count">${n} of ${state.cols.length}</span></a>`;
    ul.appendChild(li);
    const o = document.createElement("option");
    o.value = s;
    o.textContent = a;
    if (state.anchor === s) o.selected = true;
    mob.appendChild(o);
  });
}

function renderContext() {
  const gh = githubCompareURL();
  const add =
    state.cols.length < 3
      ? `<button class="mini" id="add-col" style="margin-left:.4rem">+ add edition</button>`
      : "";
  const ghLink = gh ? `<a class="gh-link" href="${esc(gh)}" target="_blank" rel="noopener">View on GitHub ↗</a>` : "";
  const summary =
    state.mode === "compare"
      ? "comparing against " + EDMETA[state.base].year + " (base)"
      : "reading · " + (state.spelling === "original" ? "original" : "modern") + " spelling";
  $("#context").innerHTML =
    `<b>${esc(SERVICE.label)}</b> <span class="tri">▸</span> ${summary}${add}${ghLink}`;
}

/* ============================================================ github bridge == */
function githubCompareURL() {
  if (state.cols.length !== 2 || !INDEX.repo) return null;
  const [a, b] = state.cols;
  if (EDMETA[a].branch !== EDMETA[b].branch) return null; // same-branch only (§9.2)
  const lo = EDMETA[a].year <= EDMETA[b].year ? a : b;
  const hi = lo === a ? b : a;
  return `https://github.com/${INDEX.repo}/compare/${lo}...${hi}`;
}

/* ============================================================ provenance ===== */
let openPop = null;
function closePop() {
  if (openPop) { openPop.remove(); openPop = null; document.removeEventListener("click", outside, true); }
}
function outside(e) {
  if (openPop && !openPop.contains(e.target) && !e.target.dataset.prov) closePop();
}
function showProvenance(tag, anchorEl) {
  closePop();
  const e = EDMETA[tag];
  const copyright = e.copyright || "See NOTICE.";
  const crown = /crown/i.test(copyright);
  const statusRow = e.status
    ? `<dt>Status</dt><dd>${esc(e.status)}${e.status === "inherited-unreviewed" ? " — carried forward; not yet re-checked against a source for this edition" : ""}</dd>`
    : "";
  const src = safeUrl(e.source_url);
  const sourcesLink = safeUrl(INDEX.notice && INDEX.notice.sources_url) || "#";
  const srcRow = src
    ? `<dt>Source</dt><dd><a href="${esc(src)}" target="_blank" rel="noopener">${esc(src.replace(/^https?:\/\//, ""))}</a></dd>`
    : `<dt>Source</dt><dd>See <a href="${esc(sourcesLink)}" target="_blank" rel="noopener">SOURCES.md</a></dd>`;
  const pop = document.createElement("div");
  pop.className = "pop";
  pop.setAttribute("role", "dialog");
  pop.setAttribute("aria-label", `Provenance for ${e.year}`);
  pop.innerHTML = `
    <h4>${e.year} · ${LINE_LABEL[e.line]} <span class="status ${crown ? "crown" : "pd"}">${crown ? "Crown / PD" : "Public domain"}</span></h4>
    <dl>
      <dt>Tag</dt><dd>${tag}</dd>
      ${srcRow}
      ${e.retrieved ? `<dt>Retrieved</dt><dd>${esc(e.retrieved)}</dd>` : ""}
      <dt>Copyright</dt><dd>${esc(copyright)}</dd>
      ${statusRow}
    </dl>
    ${e.acknowledgment ? `<div class="ack">Reproduced with the required acknowledgment: <b>${esc(e.acknowledgment)}</b></div>` : ""}
    <p class="caveat">Provenance is edition-level, from the repository's published SOURCES.md / NOTICE.md.</p>`;
  document.body.appendChild(pop);
  const r = anchorEl.getBoundingClientRect();
  pop.style.top = r.bottom + 8 + window.scrollY + "px";
  pop.style.left = Math.max(8, Math.min(r.left, window.innerWidth - pop.offsetWidth - 8)) + "px";
  openPop = pop;
  setTimeout(() => document.addEventListener("click", outside, true), 0);
}

/* ============================================================ about modal ==== */
function showAbout() {
  const ov = document.createElement("div");
  ov.className = "overlay";
  const m = document.createElement("div");
  m.className = "modal";
  m.setAttribute("role", "dialog");
  m.setAttribute("aria-modal", "true");
  m.setAttribute("aria-label", "About this project");
  const built = INDEX.built ? new Date(INDEX.built).toISOString().slice(0, 10) : "";
  const noticeLink = safeUrl(INDEX.notice && INDEX.notice.notice_url) || "#";
  const sourcesLink = safeUrl(INDEX.notice && INDEX.notice.sources_url) || "#";
  m.innerHTML = `
    <button class="icon-btn close-x" aria-label="Close">✕</button>
    <h3>The Book of Common Prayer, in Parallel</h3>
    <p class="beta-note"><b>Beta.</b> This viewer and the underlying texts are still being constructed and
       audited. Coverage is incomplete, some readings are still marked for verification, and both the
       transcription and the interface may change. Please don't cite it as a settled edition yet.</p>
    <p>A reader's window onto a repository that expresses the prayer book's history as
       <b>git history</b>: every edition is a tag, every tradition a branch. Set editions side
       by side and, with one toggle, see exactly what changed — the way a scholar reads
       Brightman's <i>English Rite</i> in parallel columns, but live. This viewer only ever
       shows text the repository has published; it invents nothing.</p>
    <p class="principle">The canonical text is plain text; Markdown-on-GitHub is one projection; this
       viewer's typeset page is another. Each era re-embodies the same signals — title, rubric, versicle,
       response — into whatever the medium affords. Rubrics appear here in red because "rubric" means the
       red letter. The viewer is the newest link in that chain, not a "neutral" rendering.</p>
    <h4>Modern vs. original spelling</h4>
    <p>Read in <i>modern</i> spelling to let substantive change stand out; switch to <i>original</i>
       for the printed spelling of each edition. Both come from the repo — the modern text is generated
       from the original, never hand-edited.</p>
    <h4>Provenance &amp; rights</h4>
    <p>Each column's ⓘ shows where its text came from. The 1662 book is public domain outside the UK and
       Crown copyright within it; it is shown with the required acknowledgment, <b>BCP 1662</b>.
       Editorial uncertainties are surfaced honestly with a <span class="verify-mark">❓</span> marker
       rather than silently corrected.</p>
    <div class="colophon">
       The viewer's <b>code</b> is under the repository's MIT <code>LICENSE</code>; the <b>texts</b> are
       governed by <a href="${esc(noticeLink)}" target="_blank" rel="noopener">NOTICE.md</a>
       (see <a href="${esc(sourcesLink)}" target="_blank" rel="noopener">SOURCES.md</a> for per-edition sources).
       Fonts: EB Garamond &amp; Source Serif 4 via Google Fonts.
       Data built ${built} from <code>${esc(INDEX.repo || "")}</code>.${INDEX.wave_note ? " " + esc(INDEX.wave_note) : ""}
    </div>`;
  document.body.appendChild(ov);
  document.body.appendChild(m);
  const close = () => { ov.remove(); m.remove(); };
  ov.addEventListener("click", close);
  m.querySelector(".close-x").addEventListener("click", close);
  document.addEventListener("keydown", function k(ev) {
    if (ev.key === "Escape") { close(); document.removeEventListener("keydown", k); }
  });
}

/* ============================================================ permalinks ===== */
function syncHash() {
  const p = new URLSearchParams();
  p.set("service", state.service);
  p.set("cols", state.cols.join(","));
  p.set("spelling", state.spelling);
  p.set("mode", state.mode);
  p.set("base", state.base);
  if (state.anchor) p.set("anchor", state.anchor);
  const hash = "#/" + p.toString().replace(/%2C/g, ",").replace(/%2F/g, "/");
  if (location.hash !== hash) history.replaceState(null, "", hash);
}
function parseHash() {
  const h = location.hash.replace(/^#\/?/, "");
  if (!h) return {};
  const p = new URLSearchParams(h);
  const out = {};
  if (p.get("service")) out.service = p.get("service");
  if (p.get("cols")) out.cols = p.get("cols").split(",").filter(Boolean);
  if (p.get("spelling")) out.spelling = p.get("spelling");
  if (p.get("mode")) out.mode = p.get("mode");
  if (p.get("base")) out.base = p.get("base");
  if (p.get("anchor")) out.anchor = p.get("anchor");
  return out;
}
let ignoreHash = false;
async function onHashChange() {
  if (ignoreHash) { ignoreHash = false; return; }
  const url = parseHash();
  if (url.service && url.service !== state.service) return loadService(url.service, url);
  // same service, cols/mode/etc changed externally
  if (url.cols) state.cols = url.cols.filter((t) => SERVICE_INDEX[state.service].present_at.includes(t));
  if (url.base && state.cols.includes(url.base)) state.base = url.base;
  // Base must always be one of the current columns, or the compare grid renders
  // with no neutral base.
  if (!state.cols.includes(state.base)) state.base = state.cols[0];
  if (url.spelling) state.spelling = url.spelling;
  if (url.mode) state.mode = url.mode;
  state.anchor = url.anchor || null;
  refreshModeAvailability();
  syncToggleUI();
  render();
  if (url.anchor) whenReady(() => scrollToAnchor(url.anchor));
}

/* ============================================================ prefs ========== */
function savePrefs() {
  try {
    localStorage.setItem(PREF_KEY, JSON.stringify({
      service: state.service, cols: state.cols, base: state.base,
      spelling: state.spelling, mode: state.mode, wordDiff: state.wordDiff, rubrics: state.rubrics,
    }));
  } catch (e) {}
}
function loadStored() {
  try { return JSON.parse(localStorage.getItem(PREF_KEY)) || {}; } catch (e) { return {}; }
}
function applyPrefs() {
  const s = loadStored();
  if (s.spelling) state.spelling = s.spelling;
  if (typeof s.wordDiff === "boolean") state.wordDiff = s.wordDiff;
  if (typeof s.rubrics === "boolean") state.rubrics = s.rubrics;
}

/* ============================================================ misc UI ======== */
function refreshModeAvailability() {
  const cmp = $("#seg-mode").querySelector('[data-v="compare"]');
  if (state.cols.length < 2) {
    cmp.disabled = true;
    cmp.title = "Add a second edition to compare";
    if (state.mode === "compare") state.mode = "reading";
  } else { cmp.disabled = false; cmp.title = ""; }
}
function syncToggleUI() {
  $("#seg-spelling").querySelectorAll("button").forEach((b) =>
    b.setAttribute("aria-checked", String(b.dataset.v === state.spelling)));
  $("#seg-mode").querySelectorAll("button").forEach((b) =>
    b.setAttribute("aria-checked", String(b.dataset.v === state.mode)));
  $("#opt-word").setAttribute("aria-checked", String(state.wordDiff));
  $("#opt-word").classList.toggle("on", state.wordDiff);
  $("#opt-rubrics").setAttribute("aria-checked", String(state.rubrics));
  $("#opt-rubrics").classList.toggle("on", state.rubrics);
}
// Defer until fonts have loaded so anchor offsets don't shift out from under us.
function whenReady(fn) {
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => requestAnimationFrame(fn));
  else requestAnimationFrame(fn);
}
function scrollToAnchor(anchorSlug) {
  const s = anchorSlug.replace(/^sec-/, "");
  const el = document.getElementById("sec-" + s);
  if (!el) return;
  state.anchor = s;
  syncHash();
  const reduce = window.matchMedia("(prefers-reduced-motion:reduce)").matches;
  // scroll-margin-top (CSS) offsets the sticky header; scrollIntoView is the
  // most broadly-honored API and respects reduced-motion.
  el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  $("#rail-list").querySelectorAll("a.sec").forEach((x) => x.classList.toggle("active", x.dataset.slug === s));
}
let noticeTimer = null;
function flashNotice(msg) {
  let n = $("#flash");
  if (!n) {
    n = document.createElement("div");
    n.id = "flash";
    n.style.cssText =
      "position:fixed;bottom:1rem;left:50%;transform:translateX(-50%);background:var(--ink-soft);color:#F7F4EE;padding:.5rem .9rem;border-radius:var(--radius);font-size:.82rem;z-index:70;box-shadow:0 4px 16px rgba(60,50,35,.2)";
    document.body.appendChild(n);
  }
  n.textContent = msg;
  n.style.opacity = "1";
  clearTimeout(noticeTimer);
  noticeTimer = setTimeout(() => (n.style.opacity = "0"), 3500);
}
function debounce(fn, ms) {
  let t;
  return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}

function populateServicePicker() {
  const sel = $("#svc-picker");
  sel.innerHTML = "";
  for (const g of INDEX.service_groups) {
    const withData = g.services.filter((s) => s.present_at.length);
    if (!withData.length) continue;
    const og = document.createElement("optgroup");
    og.label = g.label;
    for (const s of withData) {
      const o = document.createElement("option");
      o.value = s.id;
      o.textContent = `${s.label} · ${s.present_at.length} ed.`;
      og.appendChild(o);
    }
    sel.appendChild(og);
  }
}

/* ============================================================ wiring ========= */
function wireControls() {
  $("#seg-spelling").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    state.spelling = b.dataset.v;
    syncToggleUI();
    render();
  });
  $("#seg-mode").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b || b.disabled) return;
    if (state.cols.length < 2 && b.dataset.v === "compare") return;
    state.mode = b.dataset.v;
    syncToggleUI();
    render();
  });
  $("#opt-word").addEventListener("click", () => { state.wordDiff = !state.wordDiff; syncToggleUI(); render(); });
  $("#opt-rubrics").addEventListener("click", () => { state.rubrics = !state.rubrics; syncToggleUI(); render(); });
  $("#about-btn").addEventListener("click", showAbout);
  $("#ack-close").addEventListener("click", () => {
    const b = $("#ack-banner"); b.hidden = true; b.dataset.dismissed = "1";
  });
  $("#svc-picker").addEventListener("change", (e) => loadService(e.target.value));

  $("#context").addEventListener("click", (e) => {
    if (e.target.id !== "add-col") return;
    const present = SERVICE_INDEX[state.service].present_at;
    const avail = present.find((t) => !state.cols.includes(t));
    if (avail) { state.cols.push(avail); refreshModeAvailability(); render(); }
  });

  $("#colheads").addEventListener("click", (e) => {
    const t = e.target;
    if (t.dataset.remove !== undefined) {
      const i = +t.dataset.remove;
      const removed = state.cols[i];
      state.cols.splice(i, 1);
      if (state.base === removed) state.base = state.cols[0];
      refreshModeAvailability();
      render();
    } else if (t.dataset.base !== undefined) {
      state.base = t.dataset.base;
      render();
    } else if (t.dataset.prov !== undefined) {
      showProvenance(t.dataset.prov, t);
    }
  });
  $("#colheads").addEventListener("change", (e) => {
    const sel = e.target.closest("select");
    if (!sel) return;
    const i = +sel.dataset.col, val = sel.value;
    if (state.cols.includes(val) && state.cols[i] !== val) {
      const j = state.cols.indexOf(val);
      state.cols[j] = state.cols[i]; // swap to avoid dup
    }
    const wasBase = state.base === state.cols[i];
    state.cols[i] = val;
    if (wasBase) state.base = val;
    render();
  });

  $("#rail-list").addEventListener("click", (e) => {
    const a = e.target.closest("a.sec");
    if (!a) return;
    e.preventDefault();
    scrollToAnchor(a.dataset.slug); // scrollToAnchor updates state.anchor, the hash, and the active class
  });
  $("#mobile-sections").addEventListener("change", (e) => scrollToAnchor(e.target.value));
}

init();
