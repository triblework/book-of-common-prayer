"""w21_lexical.py -- lexical candidates, the 1928 cells against both scans
(Workstream B, read-only; writes <render>/align/w21_lexical.json).

Two directions, per verse (alignment from w21_psalter):

  CELL -> SCAN   a word of the cell (as a form: lower case, internal hyphen
                 and apostrophe kept) that NEITHER scan's OCR prints on the
                 verse's aligned book page(s). A word the scan breaks at a line
                 end attests both its hyphenated and its closed form, but only
                 AMBIGUOUSLY; a cell word attested only that way in both scans
                 is reported apart (undecidable on these pages, as Wave 17's
                 1:3 "water-side").
  SCAN -> CELL   a word the scan prints INSIDE the verse's aligned span with no
                 equal partner in the cell (a dropped word, a different
                 reading, or OCR noise). It survives when BOTH scans print the
                 same unpartnered form in the same verse, or when one scan does
                 and the form is a word the 1928 Psalter uses elsewhere while
                 the verse does not use it (a real-word substitution).

Everything here only FINDS readings; each one is then read twice (page OCR +
crop OCR, w21_reads.py) and, where that does not settle it, by eye.
"""
import collections, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w21_psalter as P
CLEAR = collections.Counter()
CLEARALL = set()


def page_forms(A):
    """(book page) -> {'clear': set, 'lb': set} of forms. A word broken at a line
    end attests its hyphenated AND its closed form, ambiguously ('lb'); the
    parts of a hyphenated word printed in the clear are attested too."""
    pf = collections.defaultdict(lambda: {'clear': set(), 'lb': set()})
    for t in A['wtoks']:
        for bp in {t['book'], t.get('book2', t['book'])}:
            d = pf[bp]
            if t['lb']:
                d['lb'].update([t['f'], t['lb_alt']] + t['f'].split('-'))
            else:
                d['clear'].add(t['f'])
                if '-' in t['f']:
                    d['lb'].update(t['f'].split('-'))
    return pf


def twins(f, clear_forms):
    """The other spelling of a compound: hyphen removed, or a hyphenated form
    printed in the clear whose letters are f's."""
    if '-' in f:
        return {f.replace('-', '')}
    return {g for g in clear_forms if '-' in g and g.replace('-', '') == f}


def verse_pages(A, k):
    rows = A['rows']
    for d in (0, -1, 1, -2, 2):
        if 0 <= k + d < len(rows) and rows[k + d]['pages']:
            ps = {p[2] for p in rows[k + d]['pages']}
            return ps if d == 0 else {min(ps) - 1, min(ps), max(ps), max(ps) + 1}
    return set()


def run():
    S = {w: P.build(w) for w in ('1929', '1952')}
    PF = {w: page_forms(S[w]) for w in S}
    verses = S['1929']['verses']
    ct = S['1929']['ctoks']
    vocab = collections.Counter(t['f'] for t in ct)
    global CLEAR
    CLEAR = collections.Counter(t['f'] for w in S for t in S[w]['wtoks'] if not t['lb'])
    global CLEARALL
    CLEARALL = set(CLEAR)
    cell_side, undecidable, scan_side = [], [], []
    for k, (ps, v, text) in enumerate(verses):
        pages = {w: verse_pages(S[w], k) for w in S}
        r29 = S['1929']['rows'][k]
        vforms = {ct[i]['f'] for i in range(r29['c_lo'], r29['c_hi'])}
        for i in range(r29['c_lo'], r29['c_hi']):
            f = ct[i]['f']
            att, contra = {}, {}
            for w in S:
                clear = set().union(*[PF[w][bp]['clear'] for bp in pages[w]]) if pages[w] else set()
                lb = set().union(*[PF[w][bp]['lb'] for bp in pages[w]]) if pages[w] else set()
                att[w] = 'clear' if f in clear else 'lb' if f in lb else None
                contra[w] = sorted(twins(f, clear) & clear)
            rec = dict(psalm=ps, verse=v, word=ct[i]['t'], form=f, ci=i, att=att,
                       contra=contra, pages=sorted(pages['1929'] | pages['1952']))
            if 'clear' in att.values():
                continue
            if any(contra.values()) or not any(att.values()):
                cell_side.append(rec)
            elif '-' in f or any(f == g.replace('-', '') and all(x in vocab for x in g.split('-'))
                                 for g in CLEARALL if '-' in g):
                rec['clear_elsewhere'] = {f: CLEAR[f], (f.replace('-', '') if '-' in f else
                                          next(g for g in CLEARALL if '-' in g and
                                               g.replace('-', '') == f)): 0}
                k2 = [x for x in rec['clear_elsewhere'] if x != f][0]
                rec['clear_elsewhere'][k2] = CLEAR[k2]
                undecidable.append(rec)
        # scan -> cell
        extra = {}
        for w in S:
            A = S[w]; r = A['rows'][k]
            if r['w_lo'] is None or not r['placed']:
                extra[w] = None
                continue
            partnered = {A['map'][i] for i in range(r['c_lo'], r['c_hi'])
                         if A['map'][i] is not None
                         and A['wtoks'][A['map'][i]]['sk'] == A['ctoks'][i]['sk']}
            ex = collections.OrderedDict()
            for j in range(r['w_lo'], r['w_hi']):
                t = A['wtoks'][j]
                if j in partnered or not t['f'] or t['f'] in vforms:
                    continue
                if t['lb'] and t['lb_alt'] in vforms:
                    continue
                ex.setdefault(t['f'], j)
            extra[w] = ex
        if extra['1929'] is None and extra['1952'] is None:
            continue
        both = set(extra['1929'] or {}) & set(extra['1952'] or {})
        for w in S:
            for f, j in (extra[w] or {}).items():
                real = vocab[f] > 0
                if f in both or real:
                    t = S[w]['wtoks'][j]
                    scan_side.append(dict(psalm=ps, verse=v, scan=w, form=f, word=t['t'],
                                          both=f in both, psalter_word=real,
                                          at=[t['scan'], t['side'], t['line'], t['book']],
                                          lb=t['lb']))
    return S, cell_side, undecidable, scan_side


def main():
    S, cs, und, ss = run()
    print('CELL -> SCAN: cell words neither scan attests on the aligned page(s): %d' % len(cs))
    for c in cs:
        print('   %3d:%-3d %-16s pages %s att %s contra %s' % (
            c['psalm'], c['verse'], c['word'], c['pages'], c['att'],
            {w: x for w, x in c['contra'].items() if x}))
    print('hyphen forms attested only at a line break (undecidable on these pages): %d' % len(und))
    for c in und:
        print('   %3d:%-3d %-16s %s  clear in the two scans, whole Psalter: %s' % (
            c['psalm'], c['verse'], c['word'], c['att'], c['clear_elsewhere']))
    nb = collections.Counter((c['scan'], c['both']) for c in ss)
    print('SCAN -> CELL: unpartnered scan words in a verse span: %d (%s)' % (len(ss), dict(nb)))
    json.dump(dict(cell_side=cs, undecidable=und, scan_side=ss),
              open(os.path.join(P.ALIGN_DIR, 'w21_lexical.json'), 'w'), indent=0)


if __name__ == '__main__':
    main()
