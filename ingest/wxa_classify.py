"""wxa_classify.py -- the report's classes for every difference wxa_survey
found, and for every line w19_survey.py --list reported (Workstream A,
Phase 1; read-only).

Reads ingest/wxa_survey.json (run `wxa_survey.py --json` first). Classes:

  a  probe artifact   w19's probe missed a paragraph the book prints
                      verbatim (parallel columns, first-nine-words window)
  c  rubric form      the rubric's own furniture: a final stop the book's
                      italic rubric does not print
  d1 typo             a misspelt word ('acknoledge', 'they' for 'thy')
  d2 register         a traditional-language text keyed with contemporary
                      forms, or the reverse ('you' for 'thee', 'liveth')
  d3 wrong word       a different word, neither typo nor register
  d4 dropped words    up to six words the cell lacks
  d5 extra words      up to six words the cell adds
  d6 word order       the same words, moved
  d7 citation         a numeral in a Scripture citation or page reference
  d8 passage          a swallowed or spliced passage (the 1993 keying's
                      characteristic loss: a run of text gone, often with a
                      fused fragment at the join)
  d9 substituted      a whole text keyed from the wrong rite
  e  furniture        repo headings and editorial notes, the book's
                      'Preface of ...' lines and page references
  f  spelling/space   spelling variant or word division (splendour, for ever)
  g  markup           the e-text's own markup leaked into the cell
                      (&mdash. &N. &V. =x= [[ ]] 3em, end-of-file marker)
  h1 mediant punct    the stop before the mediant, lost in the canticles
  h2 punctuation      a stop that differs from the book's
  x  out of power     the pointing asterisk / colon itself (R11)

    python3 ingest/wxa_classify.py             # counts per class and file
    python3 ingest/wxa_classify.py --w19       # every w19_survey miss
    python3 ingest/wxa_classify.py --items     # every difference, classed
    python3 ingest/wxa_classify.py --phase2    # per file: what Phase 2 changes
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wxa_book as B
import w19_survey

IN = os.path.join(HERE, 'wxa_survey.json')

ARCHAIC = {'thee': 'you', 'thou': 'you', 'thy': 'your', 'thine': 'your',
           'art': 'are', 'hast': 'have', 'hath': 'has', 'liveth': 'lives',
           'reigneth': 'reigns', 'abideth': 'abides', 'calleth': 'calls',
           'giveth': 'gives', 'takest': 'takes', 'unto': 'to',
           'whither': 'where', 'ghost': 'spirit', 'same': 'holy',
           'beseech': 'pray', 'didst': 'did', 'wouldest': 'would'}
SPELLING = {('splendour', 'splendor'), ('worshipped', 'worshiped'),
            ('fulness', 'fullness'), ('toward', 'towards'),
            ('towards', 'toward')}
# paragraph-level verdicts read off the residue by eye (file, first line)
SUBSTITUTED = {('collects-epistles-gospels/lent-1.md', 7),
               ('collects-epistles-gospels/thursday-before-easter.md', 7)}
FURNITURE = {('daily-office/morning-prayer.md', 624),     # repo editorial note
             ('daily-office/evening-prayer.md', 289),     # repo editorial note
             ('holy-communion/holy-communion.md', 549)}   # repo editorial note
PASSAGE = {('holy-communion/holy-communion.md', 129),     # spliced prayer
           ('holy-communion/holy-communion.md', 243),
           ('holy-communion/holy-communion.md', 551),
           ('occasional-offices/burial.md', 230),
           ('occasional-offices/burial.md', 609),
           ('occasional-offices/burial.md', 750),
           ('ordinal/ordering-deacons.md', 11),
           ('ordinal/preface.md', 9)}
MARKUP_PARA = {('occasional-offices/private-baptism.md', 29),  # END OF ...TXT
               ('occasional-offices/public-baptism.md', 375)}  # &LordsPrayer.
NUM = re.compile(r'^(\d+|[ivxl]+)$')


_VOCAB = None


def vocab():
    global _VOCAB
    if _VOCAB is None:
        _VOCAB = set(B.Book().tok)
    return _VOCAB


def fused(c, b):
    """A word the book never prints standing for SEVERAL book words ('thf'
    for 'that ... of', 'Bishodaily'): the scar of a swallowed span."""
    return len(b) >= 2 and any(t not in vocab() for t in c) and \
        not (len(c) == 1 and len(b) == 1)


def op_class(o, rel, line, kind):
    k, c, b = o['class'], o['cell'].split(), o['book'].split()
    if k in ('typo', 'word', 'extra', 'edge-extra') and fused(c, b):
        return 'd8'
    if k in ('extra', 'edge-extra') and any(t not in vocab() for t in c) \
            and len(c) >= 2:
        return 'd8'               # a fused fragment left at a splice
    if k == 'mediant-punct':
        return 'h1'
    if k == 'pointing':
        return 'x'
    if k == 'punct':
        if '[' in c or ']' in c:
            return 'g'
        if kind == 'rubric' and c == ['.'] and o['tag'] == 'delete':
            return 'c'
        return 'h2'
    if k == 'markup':
        return 'g'
    if k == 'compound':
        return 'f'
    if c and b and all(NUM.match(t) for t in c + b):
        return 'd7'
    if any(t in ('page',) for t in b) or 'page' in c:
        return 'e'
    if b[:2] == ['preface', 'of'] or ' '.join(b).startswith('preface of'):
        return 'e'
    if len(c) == 1 and len(b) == 1 and (c[0], b[0]) in SPELLING:
        return 'f'
    if c and b and len(c) <= 3 and len(b) <= 3:
        pair = set(c) | set(b)
        if any(ARCHAIC.get(x) in pair for x in pair):
            return 'd2'
    if k == 'typo':
        return 'd1'
    if k == 'word':
        return 'd3'
    if k == 'dropout':
        return 'd4'
    if k == 'extra':
        return 'd5'
    return 'd8'                  # garble, dropout-long, extra-long, edge-*


def para_classes(r):
    key = (r['file'], r['line'])
    if key in SUBSTITUTED:
        return ['d9']
    if key in FURNITURE:
        return ['e']
    if key in PASSAGE:
        return ['d8']
    if key in MARKUP_PARA:
        return ['g']
    if r['status'] == 'unlocated':
        return ['e'] if r['kind'] == 'heading' else ['d8']
    cls = [op_class(o, r['file'], r['line'], r['kind']) for o in r['ops']]
    # a word dropped in one place and added in another is a move
    drops = [o['book'] for o in r['ops'] if o['class'] == 'dropout']
    adds = [o['cell'] for o in r['ops'] if o['class'] == 'extra']
    if set(drops) & set(adds):
        cls = ['d6' if (o['class'] in ('dropout', 'extra') and
                        (o['book'] in adds or o['cell'] in drops)) else c
               for o, c in zip(r['ops'], cls)]
    return cls


def load():
    return json.load(open(IN))


def counts(R):
    per = collections.Counter()
    paras = collections.Counter()
    files = collections.defaultdict(collections.Counter)
    ex = collections.defaultdict(list)
    for r in R:
        cls = para_classes(r)
        for c in set(cls):
            paras[c] += 1
            files[c][r['file']] += 1
        for i, c in enumerate(cls):
            per[c] += 1
            if len(ex[c]) < 5:
                o = r['ops'][i] if i < len(r['ops']) else None
                ex[c].append('%s:%d %s' % (
                    r['file'], r['line'],
                    ('%r -> %r p%s' % (o['cell'][:30], o['book'][:30], o['page'])
                     if o else '%r p%s' % (r['text'][:40], r['page']))))
    return per, paras, files, ex


def w19_misses(R):
    """Every line w19_survey.py --list reports, with this survey's verdict."""
    res = {(r['file'], r['line']): r for r in R}
    W = B.WTX.pages()
    book_key = w19_survey.key(' '.join(W[k] for k in sorted(W)))
    out = []
    for rel, f in B.cells():
        paras = B.paragraphs(f)
        for i, line in enumerate(open(f, encoding='utf-8').read().split('\n'), 1):
            l = line.strip()
            if len(l) < 60 or l.startswith(('#', '>', '<!--', '|')):
                continue
            if ' '.join(w19_survey.key(l).split()[:9]) in book_key:
                continue
            if rel in ('tables/calendar.md', 'tables/daily-office-lectionary.md',
                       'tables/eucharistic-lectionary.md'):
                out.append((rel, i, 'table', ['table'], l[:40]))
                continue
            pl = max(p[0] for p in paras if p[0] <= i)
            r = res.get((rel, pl))
            if r is None:
                out.append((rel, i, 'exact', ['a'], l[:40]))
            else:
                out.append((rel, i, r['status'], para_classes(r), l[:40]))
    return out


def main():
    R = load()
    if '--w19' in sys.argv:
        ms = w19_misses(R)
        tally = collections.Counter()
        for rel, i, st, cls, frag in ms:
            dom = sorted(set(cls))
            tally[' '.join(dom)] += 1
            if st != 'table':
                print('%s:%d  %-8s %-14s %s' % (rel, i, st, ','.join(dom), frag))
        tab = collections.Counter(rel for rel, i, st, c, f in ms if st == 'table')
        print('\ntable rows (A3): %s' % dict(tab))
        print('w19 misses: %d; by class set: %s' % (len(ms), dict(tally)))
        return
    if '--phase2' in sys.argv:
        # what Phase 2 would change, per file: differences (not paragraphs)
        cols = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'f', 'h1', 'h2', 'c',
                'g', 'd8', 'd9']
        tab = collections.defaultdict(collections.Counter)
        for r in R:
            cls = para_classes(r)
            if r['status'] == 'unlocated' or set(cls) & {'d8', 'd9'}:
                # a passage is one item, however many ops it shows
                for c in set(cls) & {'d8', 'd9'}:
                    tab[r['file']][c] += 1
                continue
            for c in cls:
                tab[r['file']][c] += 1
        print('%-58s ' % 'file' + ' '.join('%3s' % c for c in cols) + '  fix')
        tot = collections.Counter()
        for f in sorted(tab):
            row = tab[f]
            n = sum(row[c] for c in cols[:11])
            if not any(row[c] for c in cols):
                continue
            tot.update(row)
            print('%-58s ' % f[:58] + ' '.join('%3d' % row[c] for c in cols)
                  + '  %3d' % n)
        print('%-58s ' % 'TOTAL' + ' '.join('%3d' % tot[c] for c in cols)
              + '  %3d' % sum(tot[c] for c in cols[:11]))
        return
    if '--items' in sys.argv:
        for r in R:
            cls = para_classes(r)
            for i, c in enumerate(cls):
                o = r['ops'][i] if i < len(r['ops']) else None
                print('%-3s %s:%d [%s] %s' % (c, r['file'], r['line'], r['kind'],
                      '%r -> %r p%s' % (o['cell'][:40], o['book'][:40], o['page'])
                      if o else '%r' % r['text'][:50]))
        return
    per, paras, files, ex = counts(R)
    print('%-4s %6s %6s' % ('cls', 'diffs', 'paras'))
    for c in sorted(per):
        print('%-4s %6d %6d   files: %s' % (c, per[c], paras[c],
              ', '.join('%s %d' % (f.split('/')[-1], n)
                        for f, n in files[c].most_common(6))))
        for e in ex[c]:
            print('        e.g. ' + e)
    fam = collections.defaultdict(collections.Counter)
    for r in R:
        for c in set(para_classes(r)):
            fam[r['file'].split('/')[0] if not r['file'].startswith('tables')
                else r['file']][c] += 1
    print('\nparagraphs per family x class:')
    allc = sorted(per)
    print('%-28s ' % '' + ' '.join('%4s' % c for c in allc))
    for f in sorted(fam):
        print('%-28s ' % f[:28] + ' '.join('%4d' % fam[f][c] for c in allc))


if __name__ == '__main__':
    main()
