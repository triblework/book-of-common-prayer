#!/usr/bin/env python3
"""w10_slice.py — segment a propers spine into per-occasion cells (Wave 10).

Authoring-only; NOT published. Text flows spine -> script -> file and is never
emitted as model tokens (see the subagent-write-content-filter memory).

Input  : a flat hc_clean.py spine + the apparatus notes from w10_spine.py.
Output : one dict per occasion, with the anchor sections of WAVE10_GUIDE.md §2.

The segmenter is deliberately dumb and explicit (the proven w9_build.py shape):
occasion boundaries come from a caller-supplied list of (slug, start-marker)
pairs, and within a segment only the source's own printed markers are used --
'The Collect.', 'The Epistle. <cite>', 'The Gospel. <cite>', the Introit's
'<Latin incipit>. Psalm <n>.' line, and the 1549 'At Mattins.'/'At Euensong.'
sub-blocks. Anything matching an apparatus note is dropped, so Wohlers'
editorial prose can never reach a transcription.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from w10_cite import canonical, roman_to_int  # noqa: E402

SPINES = os.path.join(HERE, "spines-w10")

# ---------------------------------------------------------------------------
# Line classification
# ---------------------------------------------------------------------------
INTROIT = re.compile(r"^>?\s*(?P<incipit>[A-Z][^.]{2,60})\.\s*(?:Psalm|Ps\.)\s*(?P<num>[ivxlcIVXLC]+|\d+)\.?\s*$")
READING = re.compile(r"^(?P<label>For the Epistle|The Epistle|The Gospel|The Gospell)[.,]?\s+(?P<cite>\S.*)$", re.I)
LABEL_ONLY = re.compile(r"^>?\s*(For the Epistle|The Epistle|The Gospel|The Gospell)\s*[.,]?\s*$", re.I)
COLLECT = re.compile(r"^>\s*The Collect\.?\s*$", re.I)
GLORIA = re.compile(r"^(Glory be to the (father|Father)|As it was in the (begynnyng|beginning))")
SUBHEAD = re.compile(r"^>\s*(At Mattins|At Matins|At Mattyns|At Euensong|At Evensong|"
                     r"At the (First|Firste|Seconde|Second) Communion|At the Communion)\b", re.I)


def load(spine_name, notes_name=None):
    path = os.path.join(SPINES, spine_name)
    lines = [ln.rstrip("\n") for ln in open(path, encoding="utf-8")]
    notes = []
    if notes_name:
        np = os.path.join(SPINES, notes_name)
        if os.path.exists(np):
            notes = [ln.strip() for ln in open(np, encoding="utf-8") if ln.strip()]
    return lines, notes


def is_apparatus(line, notes):
    """True if this spine line is Wohlers' editorial note, not Prayer-Book text."""
    probe = re.sub(r"^>\s*", "", line).strip()
    if not probe:
        return False
    if re.fullmatch(r"\[[^\]]{2,60}\](?:;.*)?", probe):     # [Romans 13:8-14]
        return True
    if re.fullmatch(r"\*.*", probe) and len(probe) < 90:     # footnote markers
        return True
    if probe.startswith(("Psalms are given only", "Initial verse numbers",
                         "Note that punctuation", "In the original, the Epistles",
                         "The translation used is", "The 1928 Book adds dates",
                         "These two rubrics added", "Heading,", "Rubric added",
                         "Prop. (1786) Book only")):
        return True
    return any(probe in note for note in notes)


def strip_brackets(text, keep):
    """Resolve the two kinds of square bracket the justus pages use.

    An EDITION MARKER carries a trailing asterisk -- '[in Advent]*' -- and marks
    words present in only some of the three books:
        keep=True  -> render the bracketed words (this edition has them)
        keep=False -> drop them (this edition does not)

    An EDITORIAL GLOSS has no asterisk -- '[=obstructed]', '[Elijah]' -- and is
    Wohlers' explanation of an archaic word. It is never Prayer-Book text, so it
    is always removed, in every edition.

    Both removals leave exactly one space behind, so neighbouring words are never
    fused (the bug that produced 'letteand').
    """
    marker = re.compile(r"\[\s*([^\]]*?)\s*\]\s*\*")
    text = marker.sub((lambda m: m.group(1)) if keep else (lambda m: " "), text)
    gloss = re.compile(r"\s*\[[^\]]*\]")
    text = gloss.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text.strip()


def segment(lines, notes, marks):
    """marks = [(slug, start-substring), ...] in spine order -> {slug: [lines]}"""
    idx = []
    for slug, marker in marks:
        found = None
        for i, ln in enumerate(lines):
            if marker in ln:
                if idx and i <= idx[-1][1]:
                    continue
                found = i
                break
        if found is None:
            raise SystemExit(f"  !! occasion marker not found: {slug}: {marker!r}")
        idx.append((slug, found))
    out = {}
    for n, (slug, start) in enumerate(idx):
        stop = idx[n + 1][1] if n + 1 < len(idx) else len(lines)
        out[slug] = [ln for ln in lines[start:stop] if not is_apparatus(ln, notes)]
    return out


def parse_cell(block, want_introit):
    """Pull the anchor sections out of one occasion's lines."""
    cell = {"heading": None, "introit": None, "collect": [], "epistle": None,
            "gospel": None, "second": {}, "lessons": [], "rubrics": []}
    cell["heading"] = re.sub(r"^>\s*", "", block[0]).strip()
    scope = cell            # current target: the occasion, or its 2nd Communion
    mode = None
    # On these pages everything printed BEFORE the first 'The Collect.' is the
    # Introit block: the proper psalm, its Gloria, and the rubrics that belong
    # to it ('And so must every Introite be ended.'). An edition that has no
    # Introit prints none of it, so skip the lot rather than let stray rubrics
    # leak forward.
    seen_collect = False
    for raw in block[1:]:
        line = raw.rstrip()
        if not line.strip():
            continue
        bare = re.sub(r"^>\s*", "", line).strip()

        m = SUBHEAD.match(line)
        if m:
            head = m.group(1).lower()
            if "seconde" in head or "second communion" in head:
                cell["second"] = {"introit": None, "collect": [],
                                  "epistle": None, "gospel": None}
                scope = cell["second"]
            elif "matt" in head or "mat" in head or "evensong" in head or "euensong" in head:
                mode = "lessons"
                cell["lessons"].append(bare)
                continue
            mode = None
            continue

        if want_introit and scope.get("introit") is None:
            mi = INTROIT.match(line)
            if mi:
                num = mi.group("num")
                if not num.isdigit():
                    num = str(roman_to_int(num))
                scope["introit"] = f"{mi.group('incipit').strip()}. Psalm {num}"
                mode = "introit"
                continue

        if COLLECT.match(line):
            mode = "collect"
            seen_collect = True
            continue

        if not want_introit and not seen_collect:
            continue

        mr = READING.match(bare)
        if mr:
            slot = "gospel" if mr.group("label").lower().startswith("the gosp") else "epistle"
            scope[slot] = {"cite": mr.group("cite").strip(),
                           "for_the": mr.group("label").lower().startswith("for the")}
            mode = slot
            continue
        if LABEL_ONLY.match(line):
            lbl = LABEL_ONLY.match(line).group(1).lower()
            slot = "gospel" if lbl.startswith("the gosp") else "epistle"
            scope[slot] = scope.get(slot) or {"cite": None,
                                              "for_the": lbl.startswith("for the")}
            mode = slot
            continue

        if mode == "lessons":
            cell["lessons"].append(bare)
            continue
        if mode == "collect":
            if GLORIA.match(bare):
                continue
            if line.startswith(">"):
                cell["rubrics"].append(bare)
                continue
            scope["collect"].append(bare)
            continue
        if mode in ("epistle", "gospel") and scope.get(mode) and not scope[mode]["cite"]:
            # 1637 prints the citation on its own line beneath the label.
            if re.match(r"^[0-9A-Za-z][^ ]{0,12}\.?\s*[0-9ivxlcIVXLC]", bare) and len(bare) < 40:
                scope[mode]["cite"] = bare
            elif line.startswith(">"):
                cell["rubrics"].append(bare)
            continue
        if line.startswith(">") and mode is None:
            cell["rubrics"].append(bare)
    return cell


def render(cell, title, edition, want_introit, keep_bracket):
    """Emit the markdown for one <occasion, edition> cell."""
    parts = [f"# {title}", ""]

    def cite_block(anchor, slot):
        if not slot or not slot.get("cite"):
            return
        parts.append(f"## {anchor}")
        parts.append("")
        if slot.get("for_the"):
            parts.append("> For the Epistle.")
            parts.append("")
        parts.append(canonical(slot["cite"]))
        parts.append("")

    if want_introit and cell.get("introit"):
        parts += ["## The Introit", "", cell["introit"], ""]
    if cell["collect"]:
        parts.append("## The Collect")
        parts.append("")
        for para in cell["collect"]:
            parts.append(strip_brackets(para, keep_bracket))
            parts.append("")
    for rub in cell["rubrics"]:
        parts.append("> " + strip_brackets(rub, keep_bracket))
        parts.append("")
    cite_block("The Epistle", cell.get("epistle"))
    cite_block("The Gospel", cell.get("gospel"))

    sec = cell.get("second") or {}
    if sec:
        if want_introit and sec.get("introit"):
            parts += ["## The Introit (Second Communion)", "", sec["introit"], ""]
        if sec.get("collect"):
            parts.append("## The Collect (Second Communion)")
            parts.append("")
            for para in sec["collect"]:
                parts.append(strip_brackets(para, keep_bracket))
                parts.append("")
        cite_block("The Epistle (Second Communion)", sec.get("epistle"))
        cite_block("The Gospel (Second Communion)", sec.get("gospel"))

    if want_introit and cell.get("lessons"):
        parts += ["## The Proper Lessons", ""]
        for les in cell["lessons"]:
            parts.append("> " + strip_brackets(les, keep_bracket))
            parts.append("")

    text = "\n".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def write_cell(edition, slug, text):
    dest = os.path.join(HERE, "..", "editions", edition,
                        "collects-epistles-gospels", f"{slug}.md")
    dest = os.path.abspath(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(text)
    return dest


def add_amen(paragraph):
    """Apply the 1559 apparatus note, only where the collect lacks an Amen."""
    text = paragraph.rstrip()
    if re.search(r"\bAmen\.?$", text):
        return paragraph
    return text.rstrip(".").rstrip() + ". Amen."
