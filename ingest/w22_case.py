"""w22_case.py -- machine candidates for LETTER-CASE differences, for the eye.

Workstream C, Phase 2 (by-catch of the full eye pass: 'thine anointed',
'the Red Sea', 'O LORD', 'JEHOVAH' seen on pivot crops where the cell prints
'Anointed', 'Red sea', 'Lord', 'Jehovah'). A cell word is a candidate when the
4400px page OCR, word-aligned, reads the same letters with a different initial
case AND Wave 17's 2400px page OCR prints that form on the same page. LORD/GOD
small capitals are excluded (OCR reads them as LoRD, Lorn ...). Candidates are
cropped (the whole printed row, labelled with the verse and the CELL's word)
for the eye; nothing is taken from OCR.

    python3 ingest/w22_case.py            # -> ingest/w22_case.tsv + <render>/strips/cs_NN.png
"""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w22_align as A
import w22_crops as C

OUT = os.path.join(HERE, 'w22_case.tsv')


def candidates():
    W = A.witness()
    verses, words = A.cell_words()
    m, kind, _ = A.align([A.skel(w['core']) for w in words], [A.skel(t['core']) for t in W])
    w17 = json.load(open(os.path.join(HERE, 'w17_scan_ocr.json')))
    pg = {int(n): '\n'.join(v) for n, v in w17.items()}
    out = []
    for i, w in enumerate(words):
        if m[i] is None:
            continue
        t = W[m[i]]
        a = re.sub(r"[^A-Za-z]", '', w['core'])
        b = re.sub(r"[^A-Za-z]", '', t['core'])
        if not a or a.lower() != b.lower() or a == b or a.upper() in ('LORD', 'GOD', 'LORDS'):
            continue
        if a[0].isupper() == b[0].isupper() or b not in pg.get(t['page'], ''):
            continue
        ps, v, _ = verses[w['v']]
        out.append((ps, v, t['page'], w['core'], t['core'], t))
    return out


def main():
    cand = candidates()
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('# w22_case.tsv -- MACHINE candidates (two page OCRs agree on another initial '
                 'case). Not readings; the eye reads are in w22_eye_2.CASE.\n'
                 '# id\tverse\tscan page\tcell word\tOCR form\n')
        for k, (ps, v, page, a, b, t) in enumerate(cand, 1):
            fh.write('C%02d\t%d:%d\t%d\t%s\t%s\n' % (k, ps, v, page, a, b))
    items = []
    for k, (ps, v, page, a, b, t) in enumerate(cand, 1):
        rb = t['rowbox']
        items.append({'label': 'C%02d %d:%d p%d\ncell word: %s' % (k, ps, v, page, a),
                      'png': C.page_png(page),
                      'rect': [max(0, rb[0] - 40), max(0, rb[1] - 4), rb[2] + 80, rb[3] + 8]})
    for s in range(0, len(items), 20):
        C.strip(items[s:s + 20], 'cs_%02d' % (s // 20))
    print('%d candidates, %d strips' % (len(items), (len(items) + 19) // 20))


if __name__ == '__main__':
    main()


def word_rows(targets, name):
    """Crop the printed row of each (psalm, verse, cell word) target -- every
    occurrence of the word in the verse -- labelled with verse, page and the
    CELL word, for the eye (strip <name>_NN)."""
    W = A.witness()
    verses, words = A.cell_words()
    m, kind, _ = A.align([A.skel(w['core']) for w in words], [A.skel(t['core']) for t in W])
    want = {}
    for ps, v, wd in targets:
        want.setdefault((ps, v), set()).add(wd)
    items = []
    recs, by = C.load()
    for i, w in enumerate(words):
        ps, v, _ = verses[w['v']]
        if (ps, v) not in want or w['core'] not in want[(ps, v)]:
            continue
        if m[i] is not None:
            t = W[m[i]]
            rb, page = t['rowbox'], t['page']
            rect = [max(0, rb[0] - 40), max(0, rb[1] - 4), rb[2] + 80, rb[3] + 8]
            items.append({'label': '%d:%d p%d\ncell word: %s' % (ps, v, page, w['core']),
                          'png': C.page_png(page), 'rect': rect})
        else:
            for it in C.whole_items(by[(ps, v)]):
                it['label'] = it['label'].split('\n')[0] + '\ncell word: ' + w['core']
                items.append(it)
    for s in range(0, len(items), 22):
        C.strip(items[s:s + 22], '%s_%02d' % (name, s // 22))
    return len(items)
