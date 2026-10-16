"""w22_classify.py -- the machine FIRST PASS over the 1892 pointing: it
classifies, it never supplies.

Workstream C. For every verse of the 1892 cells, from w22_align.json:

  pivot class (one per verse)
    at-pivot   the page OCR shows a mark on the word the cell's mediant follows;
               the OCR's mark class is recorded (':' ';' ',' '.') -- page OCR
               cannot tell ':' from ';' (Wave 17), so this says only that the
               book prints SOME mark there
    no-mark    the pivot word is found on the page but the OCR reads no mark
    unaligned  the pivot word could not be placed on the page

  flags (any number per verse) -- the OCR reads a colon-class mark (':' or
  ';') on ANOTHER word of the verse where the cell prints a weaker stop:
    E-in       inside the verse, where the cell prints no ':' or ';'
    E-end      on the verse's last word, where the cell prints no ':' or ';'
    S-in/S-end the OCR reads ':' where the cell prints ';'
  E and S are the candidates that matter most: a book that prints its colon on
  a different word than the cell. OCR also reads a period or comma as ':'/';'
  (it does so often at a line end), so every flag is a candidate, nothing more.

Every verse then falls in an eye queue:
    Q1  at-pivot ':' and no flag      (machine-consistent; control sample)
    Q2  at-pivot ':' with a flag      (whole-verse crop to the eye)
    Q3  at-pivot ';' ',' '.', no-mark, unaligned (pivot crop, then whole verse)

Writes ingest/w22_firstpass.tsv (one row per verse: the witness record of the
first pass) and prints the counts.

    python3 ingest/w22_classify.py [--psalms=1,23,78]
"""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w22_render as R

ALIGN = os.path.join(R.OUT, 'w22_align.json')
OUT = os.path.join(HERE, 'w22_firstpass.tsv')
COLONS = set(':;')


def classify(r):
    p = r.get('pivot') or {}
    if not p.get('box'):
        pc, om = 'unaligned', ''
    elif p['ocr_mark']:
        pc, om = 'at-pivot', p['ocr_mark'][0]
    else:
        pc, om = 'no-mark', ''
    flags = []
    for o in r['other']:
        oc, cc = set(o['ocr']) & COLONS, set(o['cell']) & COLONS
        if not oc:
            continue
        pos = 'end' if o['last'] else 'in'
        if not cc:
            flags.append(('E-' + pos, o['word'], o['cell'] or '-', o['ocr']))
        elif ':' in oc and cc == {';'}:
            flags.append(('S-' + pos, o['word'], o['cell'], o['ocr']))
    if pc == 'at-pivot' and om == ':':
        q = 'Q2' if flags else 'Q1'
    else:
        q = 'Q3'
    return pc, om, flags, q


def main():
    recs = json.load(open(ALIGN))
    only = None
    for a in sys.argv[1:]:
        if a.startswith('--psalms='):
            only = {int(x) for x in a.split('=', 1)[1].split(',')}
    if only:
        recs = [r for r in recs if r['psalm'] in only]
    rows, tally, fl, q = [], collections.Counter(), collections.Counter(), collections.Counter()
    flagged_verses = collections.Counter()
    per_psalm = collections.defaultdict(lambda: [0, 0, 0])
    for r in recs:
        pc, om, flags, qq = classify(r)
        tally[(pc, om)] += 1
        q[qq] += 1
        for f in flags:
            fl[f[0]] += 1
        for k in sorted({f[0] for f in flags}):
            flagged_verses[k] += 1
        pp = per_psalm[r['psalm']]
        pp[0] += 1
        pp[1] += bool(r['placed'])
        pp[2] += bool((r.get('pivot') or {}).get('box'))
        page = (r.get('pivot') or {}).get('page') or r.get('page') or ''
        rows.append('%d:%d\t%s\t%s\t%s\t%s\t%s' % (
            r['psalm'], r['verse'], page, qq, pc, om or '-',
            ' '.join('%s/%s/%s>%s' % f for f in flags) or '-'))
    if not only:
        with open(OUT, 'w', encoding='utf-8') as fh:
            fh.write('# w22 first pass: verse, scan page, eye queue, pivot class, '
                     'OCR mark at pivot, flags (kind/word/cell mark>OCR mark).\n'
                     '# OCR CLASSIFIES ONLY; no reading is taken from it.\n')
            fh.write('\n'.join(rows) + '\n')
    print('verses %d' % len(recs))
    print('pivot class: ' + ', '.join('%s %s: %d' % (pc, om or '', n)
                                      for (pc, om), n in sorted(tally.items(), key=lambda kv: -kv[1])))
    print('flags (instances): %s' % dict(fl))
    print('flags (verses):    %s' % dict(flagged_verses))
    print('eye queues: %s' % dict(sorted(q.items())))
    weak = {ps: v for ps, v in per_psalm.items() if v[2] < v[0]}
    print('psalms with every pivot located: %d of %d; the rest (psalm: verses, placed, '
          'pivot located): %s' % (len(per_psalm) - len(weak), len(per_psalm),
                                  ' '.join('%d:%d/%d/%d' % ((ps,) + tuple(v))
                                           for ps, v in sorted(weak.items()))))


if __name__ == '__main__':
    main()
