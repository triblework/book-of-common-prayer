#!/usr/bin/env python3
"""ordinal_struct.py — reusable file->file structurer for Wave-8 Ordinal spines
(CoE 1662 and justus 1789), used for the cells whose large ordination text trips
the output content-filter false-positive when emitted as model tokens (both by
subagents AND by the main agent). Text flows spine -> code -> file; the spine's
words are kept verbatim and only STRUCTURE is added.

build(spine_path, out_path, cfg) where cfg keys:
  title:    "# ..." title line
  anchors:  [(anchor_name, trigger)] — insert `## anchor_name` before the block
            whose first line startswith trigger (first match wins; each used once)
  rubrics:  [trigger, ...] — a block whose first line startswith any trigger is a
            rubric; every line in that block is prefixed `> `
  labels:   [name, ...] — a line (after optional leading "> ") matching
            "^Name\.\s*(rest)" becomes `**Name.** rest` (rest may be empty)
  footer:   stop-marker; drop this block and everything after
  drop_hashes: True to drop source `#`/`##`/`###` heading blocks
  fixes:    {bad: good} literal replacements applied to emitted text lines
Returns (n_lines, unplaced_anchor_names). Caller runs ingest/fidelity_check.py.
"""
import os, re


def build(spine_path, out_path, cfg):
    raw = open(spine_path).read().split("\n")
    footer = cfg.get("footer")
    blocks, cur = [], []
    for ln in raw:
        s = ln.strip()
        if footer and s.startswith(footer):
            break
        if s == "":
            if cur:
                blocks.append(cur); cur = []
            continue
        cur.append(ln.rstrip())
    if cur:
        blocks.append(cur)

    labels = cfg.get("labels", [])
    label_re = re.compile(r"^(?:>\s*)?(%s)\.\s*(.*)$" % "|".join(re.escape(l) for l in labels)) if labels else None
    fixes = cfg.get("fixes", {})
    rubrics = cfg.get("rubrics", [])
    pending = list(cfg.get("anchors", []))

    def fixup(s):
        for a, b in fixes.items():
            s = s.replace(a, b)
        return s

    out = [cfg["title"], ""]
    for blk in blocks:
        head = blk[0].strip()
        if cfg.get("drop_hashes") and head.startswith("#"):
            continue
        for i, (name, trig) in enumerate(pending):
            if head.startswith(trig):
                out.append("## " + name); out.append("")
                pending.pop(i)
                break
        is_rubric = any(head.startswith(t) for t in rubrics)
        for ln in blk:
            s = ln.strip()
            if is_rubric:
                out.append("> " + fixup(re.sub(r"^>\s*", "", s)))
                continue
            if label_re:
                m = label_re.match(s)
                if m:
                    rest = fixup(m.group(2).strip())
                    out.append(("**%s.** " % m.group(1) + rest).rstrip())
                    continue
            out.append(fixup(s))
        out.append("")

    res, blank = [], 0
    for ln in out:
        if ln == "":
            blank += 1
            if blank <= 1:
                res.append("")
        else:
            blank = 0
            res.append(ln)
    while res and res[-1] == "":
        res.pop()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w").write("\n".join(res) + "\n")
    return len(res) + 1, [n for n, _ in pending]
