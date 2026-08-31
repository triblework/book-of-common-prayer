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
COLLECT = re.compile(r"^>?\s*The Collects?\.?\s*$", re.I)
# Only these two phrasings denote a reading shared with another day.
# A looser pattern also matched general directions ("The sixth Sunday,
# if there be so many..."), stealing a section and orphaning a real
# citation.
CROSSREF_RE = re.compile(r"(?:the same (?:that is )?appo[iy]nted|&c\.? as upon)", re.I)
GLORIA = re.compile(r"^(Glory be to the (father|Father)|As it was in the (begynnyng|beginning))")
SUBHEAD = re.compile(r"^>?\s*(At Mattins|At Matins|At Mattyns|At Euensong|At Evensong|"
                     r"At the (First|Firste|Seconde|Second) Communion|At the Communion)\b", re.I)


def _norm(text):
    return re.sub(r"\s+", " ", re.sub(r"^>\s*", "", text)).strip()


def load(spine_name, notes_name=None, textcol_name=None):
    """Spine lines, apparatus notes, and (if available) the TEXT-column set.

    The apparatus quotes the text it discusses, so content alone cannot tell a
    genuine line from a quoted one. `textcol` is the set of paragraphs that
    actually came from the liturgical column (built by w10_textspine.py), and it
    is the authority: a line present there is never apparatus, however much of
    some note it happens to match.
    """
    path = os.path.join(SPINES, spine_name)
    lines = [ln.rstrip("\n") for ln in open(path, encoding="utf-8")]
    notes = []
    if notes_name:
        np = os.path.join(SPINES, notes_name)
        if os.path.exists(np):
            notes = [ln.strip() for ln in open(np, encoding="utf-8") if ln.strip()]
    textcol = ""
    if textcol_name is None and spine_name.startswith("1549_"):
        textcol_name = "text_" + spine_name[len("1549_"):]
    if textcol_name:
        tp = os.path.join(SPINES, textcol_name)
        if os.path.exists(tp):
            # One normalized blob: hc_clean splits a paragraph at <br> where the
            # column builder joins it, so exact line membership would miss. What
            # matters is only whether the words came from the text column.
            textcol = _norm(" ".join(
                ln for ln in open(tp, encoding="utf-8") if ln.strip()))
    return lines, notes, textcol


def is_apparatus(line, notes, textcol=""):
    """True if this spine line is Wohlers' editorial note, not Prayer-Book text.

    A STRUCTURAL line -- an occasion heading, 'The Collect.', or a reading label
    with its citation -- is always real Prayer-Book text and is never apparatus.
    This guard matters: the apparatus column sometimes QUOTES a reading in full,
    beginning with the very citation line it discusses ("The Gospell. Matt. xxvi.
    xxvii. AND it came to passe..."), and the substring test below would then
    suppress the genuine line. That silently dropped the Passion Gospels from
    Palm Sunday and Good Friday.
    """
    probe = re.sub(r"^>\s*", "", line).strip()
    if not probe:
        return False
    if READING.match(probe) or LABEL_ONLY.match(line) or COLLECT.match(line):
        return False
    if textcol and len(probe) > 24 and _norm(line) in textcol:
        return False          # these words came from the liturgical column
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


def segment(lines, notes, marks, textcol=""):
    """marks = [(slug, start-substring), ...] in spine order -> {slug: [lines]}"""
    idx = []
    for slug, marker in marks:
        # Markers and lines are compared without the "> " rubric prefix, so the
        # same mark table works against hc_clean's output and the text-column
        # spine (whose pages mark labels with italics, not pilcrows).
        probe_marker = re.sub(r"^>\s*", "", marker)
        found = None
        for i, ln in enumerate(lines):
            if probe_marker in re.sub(r"^>\s*", "", ln):
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
        out[slug] = [ln for ln in lines[start:stop]
                     if not is_apparatus(ln, notes, textcol)]
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

        mr = READING.match(bare)
        if mr:
            slot = "gospel" if mr.group("label").lower().startswith("the gosp") else "epistle"
            scope[slot] = {"cite": mr.group("cite").strip(),
                           "for_the": mr.group("label").lower().startswith("for the")}
            mode = slot
            seen_collect = True
            continue
        if LABEL_ONLY.match(line):
            lbl = LABEL_ONLY.match(line).group(1).lower()
            slot = "gospel" if lbl.startswith("the gosp") else "epistle"
            scope[slot] = scope.get(slot) or {"cite": None,
                                              "for_the": lbl.startswith("for the")}
            mode = slot
            seen_collect = True
            continue

        # Everything before the first STRUCTURAL marker (a Collect label or a
        # reading label) is the Introit block. Skip it for the books that print
        # no Introit -- but only here, after the reading labels have had their
        # chance, since several Holy Week days carry readings and NO collect.
        if not want_introit and not seen_collect:
            continue

        if mode == "lessons":
            cell["lessons"].append(bare)
            continue
        if mode == "collect":
            if GLORIA.match(bare):
                continue
            if line.startswith(">"):
                # Some days print no collect of their own but a CROSS-REFERENCE
                # to another day's ("God, which, &c. as upon witsonday."). That
                # cross-reference is the printed text, so it stands as the
                # collect rather than being dropped as a rubric.
                if re.search(r"&c\.?\s*as upon|as upon (the )?\w", bare, re.I):
                    scope["collect"].append(bare)
                else:
                    cell["rubrics"].append(bare)
                continue
            scope["collect"].append(bare)
            continue
        if (mode in ("epistle", "gospel") and scope.get(mode)
                and not scope[mode]["cite"] and CROSSREF_RE.search(bare)):
            # Some days appoint no citation of their own but refer to another
            # day's reading. That cross-reference IS the printed text.
            scope[mode]["crossref"] = bare
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
        if not slot or not (slot.get("cite") or slot.get("crossref")):
            return
        parts.append(f"## {anchor}")
        parts.append("")
        if slot.get("for_the"):
            parts.append("> For the Epistle.")
            parts.append("")
        if slot.get("cite"):
            parts.append(canonical(slot["cite"]))
        else:
            parts.append("> " + slot["crossref"])
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
