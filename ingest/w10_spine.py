#!/usr/bin/env python3
"""w10_spine.py — separate Wohlers' editorial apparatus from the propers text.

Wave 10 ingest helper (authoring-only; NOT published).

The justus "Collects, Epistles, and Gospels" pages (the 1549/1552/1559 synoptic
and the 1786/1789/1892/1928 American synoptic) are laid out as a table whose
LEFT cell (width=450, Georgia) holds the liturgical text and whose RIGHT cell
(width=150, Arial, #999999) holds Charles Wohlers' editorial notes — the
per-edition apparatus ("added in 1552", "Psalms are given only in the 1549
Book"), plus his modern verse identifications ("[Romans 13:8-14]").

`hc_clean.py` flattens both columns into one stream. That is fine for reading and
is the proven text path (Waves 4-9), but it means editorial prose sits inline with
Prayer-Book text. This script emits the apparatus column ON ITS OWN, so the
slicer can (a) drop those lines from the text spine and (b) use them as the
per-edition delta record. Nothing here is ever transcribed into a published file.

Output: one apparatus note per line.

Usage:
    python3 ingest/w10_spine.py <justus-url> <out-notes.txt>
"""
import sys, os, re, html

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
sys.path.insert(0, "tools")
import scrape  # noqa: E402  (allow-list + cache)

WS = re.compile(r"\s+")

# The apparatus column is Arial / #999999; the liturgical column is Georgia.
NOTE_CELL = re.compile(r'face="Arial|color="#999999"', re.I)


def note_cells(doc):
    """Yield the inner HTML of every apparatus <td>."""
    for m in re.finditer(r"<td\b([^>]*)>(.*?)</td>", doc, re.S | re.I):
        attrs, inner = m.group(1), m.group(2)
        if NOTE_CELL.search(attrs) or NOTE_CELL.search(inner[:400]):
            yield inner


def flatten(inner):
    s = re.sub(r"<br\s*/?>", " ", inner, flags=re.I)
    s = re.sub(r"</p\s*>|<p\b[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace(" ", " ")
    return [WS.sub(" ", part).strip() for part in s.split("\n")]


def notes(url):
    doc = scrape.fetch(url)
    out = []
    for inner in note_cells(doc):
        text = WS.sub(" ", " ".join(p for p in flatten(inner) if p)).strip()
        if text:
            out.append(text)
    return out


def main(url, out_path):
    lines = notes(url)
    with open(out_path, "w", encoding="utf-8") as fh:
        for line in lines:
            fh.write(line + "\n")
    print(f"{out_path}: {len(lines)} apparatus notes")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
