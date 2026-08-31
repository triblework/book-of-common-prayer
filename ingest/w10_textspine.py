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
NOTE_CELL = re.compile(r'face="Arial|color="#999999"', re.I)
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
        # A pilcrow introduces a rubric or an occasion heading.
        line = re.sub(r"^[¶�]\s*", "> ", line)
        out.append(line)
    return out


def build(url):
    doc = scrape.fetch(url)
    lines = []
    for m in CELL.finditer(doc):
        attrs, inner = m.group(1), m.group(2)
        if NOTE_CELL.search(attrs) or NOTE_CELL.search(inner[:400]):
            continue                      # the apparatus column: discarded
        for para in paragraphs(inner):
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
