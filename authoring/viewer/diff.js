// diff.js — vendored line/word diff primitives (~100 lines, no dependencies).
// Ported verbatim from prototype/bcp-viewer-prototype.html (spec §6.2). These
// are the canonical functions; do not "improve" them without re-checking the
// flagship diffs (1549→1552 penitential insertion; 1662 Lord's-Prayer doxology;
// Holy Communion 1549→1552 restructure).

// Escape for BOTH text content and quoted attribute values. Quotes MUST be
// escaped: VERIFY notes and provenance strings flow into title=""/aria-label=""
// attributes, and unescaped " there breaks out of the attribute.
export function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

// Longest-common-subsequence ops over two arrays (a = ref, b = col).
export function lcsOps(a, b) {
  const n = a.length, m = b.length;
  const dp = Array.from({ length: n + 1 }, () => new Int32Array(m + 1));
  for (let i = n - 1; i >= 0; i--)
    for (let j = m - 1; j >= 0; j--)
      dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const ops = [];
  let i = 0, j = 0;
  while (i < n && j < m) {
    if (a[i] === b[j]) { ops.push({ t: "eq", ai: i, bi: j }); i++; j++; }
    else if (dp[i + 1][j] >= dp[i][j + 1]) { ops.push({ t: "del", ai: i }); i++; }
    else { ops.push({ t: "add", bi: j }); j++; }
  }
  while (i < n) { ops.push({ t: "del", ai: i }); i++; }
  while (j < m) { ops.push({ t: "add", bi: j }); j++; }
  return ops;
}

// Align a column's lines to the reference: which ref index each col line matched,
// and which col lines were inserted after each ref gap.
export function alignToRef(refT, colT) {
  const ops = lcsOps(refT, colT);
  const matched = new Array(refT.length).fill(-1);
  const insAfter = {};
  let consumed = 0;
  for (const op of ops) {
    if (op.t === "eq") { matched[op.ai] = op.bi; consumed = op.ai + 1; }
    else if (op.t === "del") { consumed = op.ai + 1; }
    else { (insAfter[consumed] = insAfter[consumed] || []).push(op.bi); }
  }
  return { matched, insAfter };
}

// Token-set Jaccard similarity — separates a reworded line (> 0.40) from a
// wholly replaced one.
export function simil(a, b) {
  const A = new Set(a.toLowerCase().split(/\s+/)), B = new Set(b.toLowerCase().split(/\s+/));
  let inter = 0;
  for (const x of A) if (B.has(x)) inter++;
  return inter / Math.max(1, new Set([...A, ...B]).size);
}

export function tokenize(s) {
  return s.match(/\S+|\s+/g) || [];
}

// Word-level diff for one modified line pair, emitting <ins>/<del> (col side).
export function wordDiffHTML(baseS, colS) {
  const a = tokenize(baseS), b = tokenize(colS);
  const ops = lcsOps(a, b);
  let out = "";
  for (const op of ops) {
    if (op.t === "eq") out += esc(b[op.bi]);
    else if (op.t === "add") out += "<ins>" + esc(b[op.bi]) + "</ins>";
    else out += "<del>" + esc(a[op.ai]) + "</del>";
  }
  return out;
}
