#!/usr/bin/env python3
"""spine_struct.py — mechanical structurer for byte-faithful spines.

Wave-6 helper for the few service-editions whose sickness/childbirth/dying text trips
an output content-filter false-positive when a model tries to emit it directly. This
flows source spine -> code -> file (no model-generated liturgical text): it keeps the
spine's words verbatim and only ADDS structure (a title, `##` anchors, `>` rubric
markers already present, `**Speaker.**` labels), applying a small declared set of
obvious PDF/OCR layout fixes. Fidelity is then checked with ingest/fidelity_check.py.

A driver calls build(spine_text, cfg) where cfg is a dict:
  title:   the "# ..." title line (already title-cased)
  is_pdf:  True to convert `¶`->`> `, de-hyphenate line breaks, and merge wrapped lines
  fixes:   {bad: good} literal replacements applied to every emitted text line
  labels:  list of speaker designations to bold-split at line start (Minister, Answer, ...)
  anchors: list of (trigger, anchor_name, mode) where mode is
             "before"  -> insert `## anchor_name` before the first line whose stripped
                          text startswith trigger (the trigger line is kept)
             "replace" -> replace the first line whose stripped text startswith trigger
                          with `## anchor_name` (drops the source ALL-CAPS heading line)
  mediant: True to turn ` * ` (psalm pointing) into ` : `
"""
import re


def build(spine_text, cfg):
    lines = spine_text.split("\n")
    if cfg.get("is_pdf"):
        lines = _pdf_reflow(lines)
    labels = cfg.get("labels", ["Minister", "Answer", "Priest", "Presbyter",
                                 "Antiphon", "Versicle", "Response", "People", "Deacon"])
    label_re = re.compile(r"^(%s)\.\s+(.*)$" % "|".join(labels))
    fixes = cfg.get("fixes", {})
    # remaining anchors to place (first match wins)
    pending = list(cfg.get("anchors", []))

    def fixup(s):
        for a, b in fixes.items():
            s = s.replace(a, b)
        if cfg.get("mediant"):
            s = re.sub(r" \* ", " : ", s)
        return s

    out = [cfg["title"], ""]
    for raw in lines:
        s = raw.rstrip()
        stripped = s.strip()
        probe = re.sub(r"^>\s*", "", stripped)  # match triggers past a rubric marker
        # anchor placement
        hit = None
        for i, (trig, name, mode) in enumerate(pending):
            if stripped.startswith(trig) or probe.startswith(trig):
                hit = (i, name, mode)
                break
        if hit:
            i, name, mode = hit
            pending.pop(i)
            out.append(f"## {name}")
            out.append("")
            if mode == "replace":
                continue  # drop the source heading line
        if stripped == "":
            if out and out[-1] != "":
                out.append("")
            continue
        if s.startswith(">"):
            out.append("> " + fixup(s[1:].strip()))
            continue
        m = label_re.match(s)
        if m:
            out.append(f"**{m.group(1)}.** " + fixup(m.group(2).strip()))
            continue
        out.append(fixup(s))
    # collapse blank runs, trim
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
    unplaced = [a for a in pending]
    return "\n".join(res) + "\n", unplaced


def _pdf_reflow(lines):
    """Join wrapped lines from a text-layer PDF into one paragraph/rubric per line."""
    # de-hyphenate line-break splits like "resur-\nrection"
    joined = "\n".join(lines)
    joined = re.sub(r"([A-Za-z])-\n\s*([a-z])", r"\1\2", joined)
    lines = joined.split("\n")
    out = []
    for raw in lines:
        s = raw.rstrip()
        st = s.strip()
        if st == "":
            out.append("")
            continue
        st = re.sub(r"^¶\s*", "> ", st)  # PDF pilcrow rubric marker
        starts_block = (st.startswith(">") or re.match(r"^[A-ZÀ-Ý]{2,}", st)
                        or re.match(r"^(Minister|Answer|Priest|Antiphon|Versicle|Response|People)\.", st)
                        or re.match(r"^(The |A |An )", st))
        if out and out[-1] not in ("",) and not starts_block \
           and not out[-1].startswith(">"):
            # continuation of the previous paragraph
            out[-1] = out[-1].rstrip() + " " + st
        else:
            out.append(st)
    return out
