#!/usr/bin/env python3
"""Wave 12 — structural spine for the four deferred sections.

Reuses w11_spine's stack-based block parser (which already handles the
drop-capital and unclosed-<p> traps) and adds the two things Wave 12 needs.

1. PAIRED EDITION COLUMNS. Two justus pages print 1789 and 1892 SIDE BY SIDE in
   narrow cells labelled "1789 BCP:" / "1892 BCP:", with shared material in the
   wide cell. This is NOT an apparatus column:
     - treating the narrow cells as apparatus DELETES the text outright;
     - treating every cell as text CONFLATES two editions into one reading that
       no book ever printed.
   So a paired cell is selected by its own label and the label is stripped. The
   two texts genuinely differ, so 1892 is not simply "the 1789 page shared".

2. PSALMS AS POINTERS. Per the locked ruling (WAVE12_SCOPING.md), psalm bodies
   inside the Sea forms are NOT transcribed here — the Psalter is its own wave.
   A psalm unit keeps its heading and carries its citation, nothing more.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w11_spine as W

scrape = W.scrape

# name -> (url, style, apparatus_width)
SOURCES = {
 'sea-1662':     ('https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/'
                  'book-common-prayer/prayers-be-used-sea', 'coe', None),
 'sea-1789':     ('http://justus.anglican.org/resources/bcp/1789/Prayer_at_Sea_1789.htm', 'justus', '200'),
 'family-1789':  ('http://justus.anglican.org/resources/bcp/1789/Family_Prayer_1789.htm', 'justus', '200'),
 'family-1928':  ('http://justus.anglican.org/resources/bcp/1928/Family_Prayer.htm', 'justus', '200'),
 'thanks-1789':  ('http://justus.anglican.org/resources/bcp/1789/Prayer&Thanksgiving_1789.htm', 'justus-paired', None),
 'penitential-1892': ('http://justus.anglican.org/resources/bcp/1892/Pray&Thanks_1892.htm', 'justus', None),
 'penitential-1928': ('http://justus.anglican.org/resources/bcp/1928/Litany.htm', 'justus', '200'),
}

PAIR_RE = re.compile(r'^\s*(1789|1892)\s*BCP\s*:\s*', re.I)

# Some sources bundle a section inside a bigger page. SLICE is the INVERSE of
# Wave 11's EXCLUDE: keep from the first matching heading to the end (or to the
# next START, where one is given), instead of dropping it.
SLICE = {
 'penitential-1892': (r'PENITENTIAL OFFICE', None),
 'penitential-1928': (r'PENITENTIAL OFFICE|A Penitential Office', None),
}
CHROME_W = {'14', '41', '59', '100'}


def _cells(s, apparatus_width, keep_narrow=False):
    out = []
    for m in re.finditer(r'<td([^>]*)>(.*?)</td>', s, re.S | re.I):
        attrs, inner = m.group(1), m.group(2)
        w = re.search(r'width="?(\d+)', attrs, re.I)
        w = w.group(1) if w else None
        if w in CHROME_W:
            continue
        if apparatus_width is not None and w == apparatus_width:
            continue
        if len(W._text(inner)) < 40:
            continue
        out.append((w, inner))
    return out


def extract(name: str, edition: str | None = None):
    """Return (blocks, note). `edition` selects a side of a paired-column page."""
    url, style, appw = SOURCES[name]
    s = scrape.fetch(url)
    blocks = []
    if style == 'coe':
        i = s.lower().find('forms of prayer to be used at sea')
        if i < 0:
            i = s.lower().find('prayers to be used at sea')
        blocks = W._blocks_from_html(W._coe_promote_inline_titles(s[i:]), style='coe')
    else:
        for w, inner in _cells(s, appw):
            txt = W._text(inner)
            m = PAIR_RE.match(txt)
            if m:
                # a paired edition column: keep it only for its own edition
                if edition and m.group(1) != edition:
                    continue
                inner = re.sub(r'(1789|1892)\s*BCP\s*:\s*', '', inner, count=1, flags=re.I)
            blocks.extend(W._blocks_from_html(inner, style='justus'))
    # keep only the bundled section, where this source carries one
    if name in SLICE:
        start_pat, end_pat = SLICE[name]
        first = next((i for i, (k, t) in enumerate(blocks)
                      if re.search(start_pat, t, re.I)), None)
        if first is None:
            raise SystemExit(f"ABORT {name}: section heading {start_pat!r} not found "
                             f"-- the page changed; do not fall back to the whole page.")
        last = len(blocks)
        if end_pat:
            last = next((i for i, (k, t) in enumerate(blocks)
                         if i > first and re.search(end_pat, t, re.I)), len(blocks))
        blocks = blocks[first:last]

    # strip a paired label that survived inside a block
    cleaned = []
    for k, t in blocks:
        t2 = PAIR_RE.sub('', t)
        if edition and PAIR_RE.match(t) and PAIR_RE.match(t).group(1) != edition:
            continue
        cleaned.append((k, t2))
    return cleaned, None


if __name__ == '__main__':
    from collections import Counter
    for name in sys.argv[1:] or list(SOURCES):
        ed = '1789' if name.endswith('1789') else ('1892' if '1892' in name else None)
        b, _ = extract(name, ed)
        print(f"##### {name} (edition={ed}): {Counter(k for k,_ in b)}")
        for k, t in b:
            if k in ('title', 'section'):
                print(f"    [{k[:5]:5s}] {t[:74]}")
