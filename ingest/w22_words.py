"""w22_words.py -- a machine candidate list of WORD differences (by-catch).

Workstream C, Phase 1b. While reading the pointing, the eye met word forms the
1892 cells do not share with the book (99:1 'unpatient' / book 'impatient';
50:20 'satest' / book 'sattest'; 'strong hold(s)' / book 'stronghold(s)').
Wave 17 corrected listed classes only, so this sweeps the whole Psalter for
more. A cell word is a CANDIDATE when the two independent page reads of the
scan agree on a different form at its place:
  * the 4400px page OCR (w22_scan_ocr.json, word-aligned by w22_align), and
  * the 2400px page OCR (Wave 17's w17_scan_ocr.json) prints the same form on
    the same page;
and that form is a real word (it occurs in some psalter cell of any edition, or
in the 4400 record at least twice). Line-end hyphenation is joined first.
Candidates are for the eye; nothing is taken from this list.

    python3 ingest/w22_words.py            # -> prints candidates, writes ingest/w22_words.tsv
    python3 ingest/w22_words.py --strips   # crops of the real-word candidates (wd_NN.png)
"""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells
import w22_align as A

OUT = os.path.join(HERE, 'w22_words.tsv')


def norm(w):
    return re.sub(r"[^a-z]", '', w.lower())


def main():
    W = A.witness()
    verses, words = A.cell_words()
    a_sk = [A.skel(w['core']) for w in words]
    b_sk = [A.skel(t['core']) for t in W]
    m, kind, _ = A.align(a_sk, b_sk)
    w17 = json.load(open(os.path.join(HERE, 'w17_scan_ocr.json')))
    page2400 = {}
    for n, lines in w17.items():
        txt = '\n'.join(lines)
        txt = re.sub(r'-\s*\n\s*', '', txt)
        page2400[int(n)] = collections.Counter(norm(t) for t in txt.split())
    vocab = collections.Counter()
    for ed in ('1662', '1892', '1928', '1979'):
        for p in w17_cells.cells(ed).values():
            for t in p.values():
                vocab.update(norm(x) for x in t.split())
    ocr_vocab = collections.Counter(norm(t['core']) for t in W)
    out = []
    for i, w in enumerate(words):
        if m[i] is None:
            continue
        t = W[m[i]]
        a, b = norm(w['core']), norm(t['core'])
        if not a or not b or a == b:
            continue
        if page2400.get(t['page'], {}).get(b, 0) == 0:
            continue
        if not (vocab.get(b) or ocr_vocab.get(b, 0) >= 2):
            continue
        ps, v, _ = verses[w['v']]
        out.append((ps, v, t['page'], w['core'], t['core'], kind[i]))
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('# w22_words.tsv -- MACHINE candidates only (two page OCRs agree on a form '
                 'the cell does not print). Not readings.\n# verse\tscan page\tcell word\t'
                 'OCR form\talignment\n')
        for r in out:
            fh.write('%d:%d\t%d\t%s\t%s\t%s\n' % r)
    pairs = collections.Counter((norm(r[3]), norm(r[4])) for r in out)
    print('candidates %d (%d distinct cell/OCR pairs)' % (len(out), len(pairs)))
    for (a, b), n in pairs.most_common(80):
        print('  %3d  %s -> %s' % (n, a, b))


def strips():
    """Crop each real-word candidate's printed row for the eye (label: verse,
    page and the CELL word only)."""
    import w22_crops as C
    W = A.witness()
    verses, words = A.cell_words()
    m, kind, _ = A.align([A.skel(w['core']) for w in words], [A.skel(t['core']) for t in W])
    vocab = collections.Counter()
    for ed in ('1662', '1892', '1928', '1979'):
        for p in w17_cells.cells(ed).values():
            for t in p.values():
                vocab.update(norm(x) for x in t.split())
    rows = [l.rstrip('\n').split('\t') for l in open(OUT) if not l.startswith('#')]
    want = {(r[0], r[2]) for r in rows if vocab.get(norm(r[3]))}
    items = []
    for i, w in enumerate(words):
        ps, v, _ = verses[w['v']]
        if m[i] is None or ('%d:%d' % (ps, v), w['core']) not in want:
            continue
        t = W[m[i]]
        rb = t['rowbox']
        items.append({'label': 'W%02d %d:%d p%d\ncell word: %s' % (len(items) + 1, ps, v, t['page'], w['core']),
                      'png': C.page_png(t['page']),
                      'rect': [max(0, rb[0] - 40), max(0, rb[1] - 4), rb[2] + 80, rb[3] + 8]})
    for s in range(0, len(items), 20):
        C.strip(items[s:s + 20], 'wd_%02d' % (s // 20))
    return len(items)


if __name__ == '__main__':
    if '--strips' in sys.argv:
        print(strips(), 'crops')
    else:
        main()
