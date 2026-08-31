#!/usr/bin/env python3
"""w10_rows.py — pair each apparatus note with the text it annotates.

Authoring-only; NOT published.

The justus synoptic pages are tables: within one <tr>, the wide cell holds the
liturgical text and the narrow cell holds Wohlers' editorial note about THAT
text. Flattening the page (hc_clean) loses the pairing, which matters for the
American page, where the notes are what separate 1789 from 1892 from 1928
("* 'unto' in 1892 only", "1928: The Epistle. Philippians ii. 9.").

Emits JSON: [{"text": [paragraph, ...], "note": "..." | null}, ...] in page
order, so a builder can apply a delta to the exact paragraph it governs instead
of guessing from marker order.

Usage:
    python3 ingest/w10_rows.py <justus-url> <out.json>
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
sys.path.insert(0, "tools")
import scrape  # noqa: E402

WS = re.compile(r"\s+")
NOTE_CELL = re.compile(r'face="Arial|color="#999999"', re.I)
ROW = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S | re.I)
CELL = re.compile(r"<td\b([^>]*)>(.*?)</td>", re.S | re.I)


def paragraphs(inner):
    s = re.sub(r'<font[^>]*color="#808080"[^>]*>\s*(\[|\]\*?|\*)\s*</font>',
               r"\1", inner, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"</p\s*>|<p\b[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    return [WS.sub(" ", p).strip() for p in s.split("\n") if WS.sub(" ", p).strip()]


def rows(url):
    doc = scrape.fetch(url)
    out = []
    for m in ROW.finditer(doc):
        text, note = [], []
        for cm in CELL.finditer(m.group(1)):
            attrs, inner = cm.group(1), cm.group(2)
            paras = paragraphs(inner)
            if not paras:
                continue
            if NOTE_CELL.search(attrs) or NOTE_CELL.search(inner[:400]):
                note.extend(paras)
            else:
                text.extend(paras)
        if text or note:
            out.append({"text": text, "note": " ".join(note) or None})
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    data = rows(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    annotated = sum(1 for r in data if r["note"])
    print(f"{sys.argv[2]}: {len(data)} rows, {annotated} annotated")
