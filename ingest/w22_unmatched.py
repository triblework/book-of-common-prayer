"""w22_unmatched.py -- the eye pass over the cell words the alignment left
unmatched (R21: 'word forms the alignment left unmatched get an eye pass of
their own').

Workstream C, Phase 2. w22_align maps 43,987 of 44,712 cell words to a page
word; the other 725 (585 runs of consecutive words, in 471 verses) are words
the page OCR damaged, split, merged or dropped -- or words the BOOK prints
differently. Each run is cropped from the page: every printed row from the
matched word before it to the matched word after it, full column width (a
verse-initial run also takes the row above, for the drop capital). The label
gives the verse, scan page and the run's CELL words, so the eye can say
whether the book prints them so. The eye reads are keyed in w22_eye_2.UNMATCHED.

    python3 ingest/w22_unmatched.py      # -> ingest/w22_unmatched.tsv + <render>/strips/um_NN.png
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w22_align as A
import w22_crops as C

OUT = os.path.join(HERE, 'w22_unmatched.tsv')
PER_H = 4500          # two columns of ~2250px


def runs():
    W = A.witness()
    verses, words = A.cell_words()
    m, kind, _ = A.align([A.skel(w['core']) for w in words], [A.skel(t['core']) for t in W])
    out, cur = [], []
    for i, w in enumerate(words):
        if m[i] is None:
            if cur and (cur[-1] + 1 != i or words[cur[-1]]['v'] != w['v']):
                out.append(cur); cur = []
            cur.append(i)
        elif cur:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    res = []
    for r in out:
        p = r[0] - 1
        while p >= 0 and m[p] is None:
            p -= 1
        n = r[-1] + 1
        while n < len(words) and m[n] is None:
            n += 1
        tp = W[m[p]] if p >= 0 else None
        tn = W[m[n]] if n < len(words) else None
        ps, v, _ = verses[words[r[0]]['v']]
        res.append({'ps': ps, 'v': v, 'words': [words[i]['core'] + words[i]['mark'] for i in r],
                    'prev': tp, 'next': tn,
                    'start': r[0] == 0 or words[r[0] - 1]['v'] != words[r[0]]['v']})
    return res


def rect(run):
    tp, tn = run['prev'], run['next']
    anchor = tn or tp
    page = anchor['page']
    boxes = []
    if tp and tp['page'] == page:
        boxes.append(tp['rowbox'])
    if tn and tn['page'] == page:
        boxes.append(tn['rowbox'])
    if tp and tn and tp['page'] != tn['page']:
        boxes = [tn['rowbox']]
    top = min(b[1] for b in boxes) - 6
    bot = max(b[1] + b[3] for b in boxes) + 6
    if run['start'] and (not tp or tp['page'] != page):
        top -= 90
    if bot - top > 520:                     # never more than ~6 rows
        top = max(top, (tn['rowbox'][1] if tn else bot) - 430)
    left = min(b[0] for b in boxes) - 120
    right = max(b[0] + b[2] for b in boxes) + 40
    return page, [int(max(0, left)), int(max(0, top)), int(right - left), int(bot - top)]


def main():
    rs = runs()
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('# w22_unmatched.tsv -- cell words the alignment left unmatched (machine list; '
                 'eye reads in w22_eye_2.UNMATCHED).\n# id\tverse\tscan page\tcell words\n')
        items = []
        for k, r in enumerate(rs, 1):
            page, rc = rect(r)
            fh.write('U%03d\t%d:%d\t%d\t%s\n' % (k, r['ps'], r['v'], page, ' '.join(r['words'])))
            lab = ' '.join(r['words'])
            if len(lab) > 30:
                lab = lab[:28] + '..'
            items.append({'label': 'U%03d %d:%d p%d\n%s' % (k, r['ps'], r['v'], page, lab),
                          'png': C.page_png(page), 'rect': rc})
    groups, cur, h = [], [], 0
    for it in items:
        if cur and h + it['rect'][3] > PER_H:
            groups.append(cur); cur, h = [], 0
        cur.append(it); h += it['rect'][3] + 12
    if cur:
        groups.append(cur)
    for k, g in enumerate(groups):
        C.strip(g, 'um_%02d' % k, cols=2)
    json.dump([[i['label'].split(' ')[0] for i in g] for g in groups],
              open(os.path.join(C.STRIPS, 'um_index.json'), 'w'))
    print('%d runs (%d words), %d strips' % (len(rs), sum(len(r['words']) for r in rs), len(groups)))


if __name__ == '__main__':
    main()
