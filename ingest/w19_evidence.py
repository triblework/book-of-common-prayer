"""w19_evidence.py — evidence for every Wave-19 correction, from the book itself.

For each correction, the corrected reading is looked up in Church Publishing's
PDF (w19_witness_text.py) and the page and surrounding sentence are recorded.
The witness's text layer is exact, so there is no second machine read to take,
as there was for the scans in Waves 17-18: what stands in for it is this
lookup, which fails loudly if a correction cannot be found in the book.

    python3 ingest/w19_evidence.py        # writes ingest/w19_evidence.json
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w19_witness as W
import w19_witness_text as WT
import w19_cells

OUT = os.path.join(HERE, 'w19_evidence.json')

# What to look for in the book for each correction that is not a plain
# substring of it (a fragment that spans the mediant, or a deletion).
PROBE = {
    (78, 58): 'They grieved him with their hill-altars',
    (135, 11): 'Og, the king of Bashan',
    (150, 6): 'praise the Lord. Hallelujah!',
    (118, 25): 'Hosannah, Lord, hosannah!',
}


def probe(text):
    """Fold the repo's mediant and the LORD small-capital convention away."""
    t = text.replace(' : ', ' ').replace(' * ', ' ')
    t = re.sub(r'\bLORD\b', 'Lord', t)
    return re.sub(r'\s+', ' ', t).strip()


def main():
    pgs = WT.pages()
    rec, missing = [], []

    def look(kind, key, reading, note=''):
        hits = WT.find(probe(reading), pgs)
        if not hits:
            missing.append((kind, key, reading[:60]))
            return
        page, ctx = hits[0]
        rec.append({'kind': kind, 'where': key, 'reading': reading,
                    'page': page, 'book': ctx.strip(), 'note': note})

    for (n, v), (_was, now) in sorted(W.VERSES.items()):
        look('psalm-verse', '%d:%d' % (n, v), PROBE.get((n, v), now))
    for was, (now, count) in sorted(W.HEADINGS.items()):
        look('psalm-heading', was, now, '%d psalm(s)' % count)
    for rel, subs in sorted(w19_cells.EDITS.items()):
        for _old, new in subs:
            first = re.sub(r'^> ', '', new.strip().split('\n')[0])
            look('cell', rel.replace('editions/1979/', ''), first)

    json.dump(rec, open(OUT, 'w'), indent=1)
    print('%d readings evidenced; %d not found in the book' % (len(rec), len(missing)))
    for m in missing:
        print('  MISSING %s %s %r' % m)
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
