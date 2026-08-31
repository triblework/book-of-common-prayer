#!/usr/bin/env python3
"""w10_textspine.py — a spine built from the TEXT column only.

Authoring-only; NOT published.

The justus propers pages are two-column tables: liturgical text on the left,
Charles Wohlers' editorial apparatus on the right. hc_clean.py flattens both into
one stream, and the apparatus frequently QUOTES the text it discusses -- a
reading in full, or a whole collect. Content alone therefore cannot tell a
genuine line from a quoted one, and a filter that tries silently deletes real
text: it removed the Passion Gospels from Palm Sunday and Good Friday, and the
Collects from St. Andrew's and St. Mark's Days, while the fidelity gate stayed
green because every surviving word was still attested.

The only reliable discriminator is which COLUMN a paragraph came from, so this
script keeps the left column and discards the right entirely. No guessing, and
no filter to tune.

Emits the same shape hc_clean does (pilcrow-marked paragraphs become '> '
rubrics), so the existing slicer consumes it unchanged.

Usage:
    python3 ingest/w10_textspine.py <justus-url> <out-spine.md>
"""
import html, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
sys.path.insert(0, "tools")
import scrape  # noqa: E402

WS = re.compile(r"\s+")

# Page furniture in the text column (nav, titles, image captions, footer).
CRUFT = [
    r"^The Book$", r"^of Common Prayer$", r"^The Book of Common Prayer",
    r"^(United|States|England|Scotland|Ireland|Wales|Canada|World)$",
    r"^Collects, Epistles, and Gospels$", r"^from the 15\d\d",
    r"^Return to", r"^Web author", r"Charles Wohlers",
    r"Society of Archbishop Justus", r"^Previous Readings$", r"^Next Readings$",
    r"^Clicking on the image", r"larger \(\d+K",
]
CRUFT_RE = [re.compile(pat, re.I) for pat in CRUFT]
# The columns are distinguished by the cell's own WIDTH: the liturgical column
# is width=450 (sometimes colspan'd), the apparatus column width=150. Sniffing
# the cell CONTENTS for an Arial font misclassifies a text cell that happens to
# contain one, which silently drops a whole occasion.
# The apparatus column is consistently width=150. The liturgical column is 450,
# but the page SPLITS it into two 225-wide halves for some occasions (St. Mark's
# collect lives in such a pair), so anything that is not 150 is text.
NOTE_WIDTH = re.compile(r'width\s*=\s*"?150"?', re.I)
ANY_WIDTH = re.compile(r'width\s*=\s*"?\d+%?"?', re.I)
NOTE_FONT = re.compile(r'face="Arial|color="#999999"', re.I)


def is_note_cell(attrs, inner):
    if NOTE_WIDTH.search(attrs):
        return True
    if ANY_WIDTH.search(attrs):
        return False          # any other declared width is a text column
    return bool(NOTE_FONT.search(attrs) or NOTE_FONT.search(inner[:400]))
CELL = re.compile(r"<td\b([^>]*)>(.*?)</td>", re.S | re.I)


def paragraphs(inner):
    # Grey brackets mark material present in only some books: keep as [x]*.
    s = re.sub(r'<font[^>]*color="#808080"[^>]*>\s*(\[|\]\*?|\*)\s*</font>',
               r"\1", inner, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"</p\s*>|<p\b[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    out = []
    for chunk in s.split("\n"):
        line = WS.sub(" ", chunk).strip()
        if not line:
            continue
        if any(r.search(line) for r in CRUFT_RE):
            continue
        # A pilcrow, where present, introduces a rubric. On some pages the
        # labels are italic instead and carry no pilcrow at all, which is why
        # the slicer treats the "> " prefix as optional.
        line = re.sub(r"^[\u00b6\ufffd]\s*", "> ", line)
        out.append(line)
    return out


def merge_fragments(paras):
    """Rejoin a paragraph the markup split into pieces.

    These pages set a drop-capital in its own span and sometimes break a heading
    after its first word, so a paragraph can arrive as a stub ("O", "The")
    followed by the rest. Rejoining is what hc_clean effectively did; without it
    an occasion heading no longer matches its marker.
    """
    out = []
    for para in paras:
        stub = out and len(out[-1]) <= 5 and not re.search(r"[.!?:;]$", out[-1])
        if stub and not para.startswith(">"):
            joiner = "" if len(out[-1]) == 1 and out[-1].isupper() else " "
            out[-1] = out[-1] + joiner + para
        else:
            out.append(para)
    return out


def build(url):
    doc = scrape.fetch(url)
    lines = []
    for m in CELL.finditer(doc):
        attrs, inner = m.group(1), m.group(2)
        if is_note_cell(attrs, inner):
            continue                      # the apparatus column: discarded
        for para in merge_fragments(paragraphs(inner)):
            lines.append(para)
            lines.append("")
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    text = build(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"{sys.argv[2]}: {len(text.splitlines())} lines (text column only)")
