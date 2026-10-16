"""w23_survey.py -- every 1979 paragraph against Church Publishing's file,
word for word (Workstream A, Phase 1; read-only).

w19_survey.py asked one question of each line of 60+ characters: are its
first nine words somewhere in the book? That has three blind spots, each
measured here:

  1. it never looks past word nine, so a defect later in a paragraph passes;
  2. it skips rubrics (`> `), headings, short lines, and the hard-wrapped
     prayers whose "paragraphs" are 60-column fragments;
  3. a parallel-column page (the Lord's Prayer, traditional | contemporary)
     interleaves in the plain extraction, so a correct cell cannot match.

This script aligns EVERY paragraph of every non-Psalter, non-table cell
against the book and reports each difference with the book page. What makes
that fair to a correct cell (each one a measured false miss of the old probe):

  * the book's running feet and producer slugs are dropped, and its
    parallel-column blocks rebuilt left-then-right (w23_book.pages);
  * words are folded (case, accents, ligatures, quotes, dashes, the mediant)
    and the repo's own furniture removed (`> `, `#`, `**People.**`);
  * a paragraph is located by shared 4-grams, then diffed word for word
    against the located stretch (w23_book.Book.align), stray far-off matches
    trimmed;
  * a short paragraph (a question, a response) is located inside its
    neighbours, then diffed alone;
  * a collect is compared with the printing its heading names (traditional
    pp. 158-210, contemporary pp. 211-261), because the 1993 keying's
    traditional collects are sometimes contemporary text;
  * where the words agree, punctuation is compared in a second pass, the
    mediant itself excepted (R11).

Mechanical classes are assigned here (classify()); the report's classes are
assigned by w23_classify.py from the residue this writes.

    python3 ingest/w23_survey.py              # rates, before and after
    python3 ingest/w23_survey.py --list       # + every difference
    python3 ingest/w23_survey.py --json       # + ingest/w23_survey.json
    python3 ingest/w23_survey.py --sensitivity  # mutated-paragraph test
"""
import collections
import difflib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w23_book as B
import w19_survey

OUT = os.path.join(HERE, 'w23_survey.json')
TABLE_ROWS = ('tables/calendar.md', 'tables/daily-office-lectionary.md',
              'tables/eucharistic-lectionary.md')
MARKUP = re.compile(r'=[^=\n]{1,40}=|&N\.|&mdash\.')


def family(rel):
    return rel if rel.startswith('tables/') else rel.split('/')[0]


def chars(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def classify(tag, c, b, text, first, last):
    """One mechanical class for a word-level difference."""
    cs, bs = ' '.join(c), ' '.join(b)
    if 'mdash' in c or (MARKUP.search(text) and tag in ('delete', 'replace')
                        and len(c) <= 3 and len(b) <= 3):
        return 'markup'
    if c and b and ''.join(c) == ''.join(b):
        return 'compound'          # first fruits / firstfruits, line-end hyphen
    if tag == 'replace' and len(c) == 1 and len(b) == 1:
        return 'typo' if chars(cs, bs) >= 0.6 else 'word'
    if tag == 'replace' and len(c) <= 3 and len(b) <= 3:
        return 'typo' if chars(cs, bs) >= 0.6 else 'word'
    if tag == 'delete' and (first or last) and len(c) <= 4:
        return 'edge-extra'        # a label/number the book prints elsewhere
    if tag == 'insert' and (first or last):
        return 'edge-short'        # the paragraph ends/begins differently
    if tag == 'insert':
        return 'dropout' if len(b) <= 6 else 'dropout-long'
    if tag == 'delete':
        return 'extra' if len(c) <= 6 else 'extra-long'
    return 'garble'                # a long replace: swallowed or corrupted text


def pclass(c, b):
    """Class of a punctuation-only difference."""
    if '*' in c or '*' in b:
        return 'pointing'            # the mediant itself: out of power (R11)
    return 'punct'


def locate(bk, rel, head, pre, w, post):
    """Align a paragraph's words w (with up to 12 neighbouring words either
    side, pre/post, for a short paragraph) -> Book.align's result for w."""
    ctx = pre + w + post
    r = (bk.align(ctx, within=B.section(rel, head))
         if len(ctx) >= bk.n else None)
    if r is not None and (pre or post):
        # the neighbours said WHERE; now diff the paragraph alone
        # against that stretch of the book (a few words either side)
        lo_, hi_ = len(pre), len(pre) + len(w)
        pos = [o[3] + (i - o[4]) for o in r[3] if o[0] == 'equal'
               for i in range(o[4], o[5]) if lo_ <= i < hi_]
        if pos:
            got = bk.align_window(w, max(0, min(pos) - 4),
                                  min(len(bk.tok), max(pos) + 5))
            r = got[1] if got else None
            if r is not None:
                bk.exact = [(r[1], r[2])] if r[0] == 1.0 else []
        else:
            r = bk.align(w, within=B.section(rel, head)) \
                if len(w) >= bk.n else None
    return r


def sensitivity(n=300, seed=1979):
    """Mutate paragraphs the book prints verbatim and count how many the
    survey then flags: a word the book prints NOWHERE, a word the book does
    print (elsewhere), a dropped word, two words swapped, a comma made a
    semicolon."""
    import random
    rnd = random.Random(seed)
    bk = B.Book()
    vocab = sorted(set(bk.tok))
    pool = []
    for rel, f in B.cells():
        if rel in TABLE_ROWS:
            continue
        head = None
        for ln, kind, text in B.paragraphs(f):
            if kind == 'heading':
                head = text
                continue
            if kind == 'row' or text.startswith('<!--'):
                continue
            w = B.words(B.cell_text(text, kind))
            if len(w) >= 12:
                pool.append((rel, head, kind, text, w))
    exact = []
    for item in pool:
        rel, head, kind, text, w = item
        r = locate(bk, rel, head, [], w, [])
        if r and not [o for o in r[3] if o[0] != 'equal']:
            exact.append(item)
    sample = rnd.sample(exact, min(n, len(exact)))
    res = collections.Counter()
    for rel, head, kind, text, w in sample:
        i = rnd.randrange(2, len(w) - 2)
        muts = {
            'nowhere': w[:i] + ['zqxv'] + w[i + 1:],
            'elsewhere': w[:i] + [rnd.choice([v for v in vocab[:4000]
                                              if v != w[i]])] + w[i + 1:],
            'dropped': w[:i] + w[i + 1:],
            'swapped': w[:i] + [w[i + 1], w[i]] + w[i + 2:]
            if w[i] != w[i + 1] else None,
        }
        for name, mw in muts.items():
            if mw is None:
                continue
            res[(name, 'n')] += 1
            r = locate(bk, rel, head, [], mw, [])
            if r is None or [o for o in r[3] if o[0] != 'equal']:
                res[(name, 'flagged')] += 1
        if ', ' in text:
            j = text.index(', ')
            mt = text[:j] + '; ' + text[j + 2:]
            res[('comma->semicolon', 'n')] += 1
            ct = B.ptoks(B.cell_text(mt, kind), cell=True)
            r = locate(bk, rel, head, [], w, [])
            if r and bk.exact:
                pd = min((bk.punct(ct, a, z) for a, z in bk.exact), key=len)
                if pd:
                    res[('comma->semicolon', 'flagged')] += 1
    print('SENSITIVITY (%d paragraphs the book prints verbatim, mutated):'
          % len(sample))
    for name in ('nowhere', 'elsewhere', 'dropped', 'swapped',
                 'comma->semicolon'):
        print('  %-18s %3d / %3d flagged' % (name, res[(name, 'flagged')],
                                             res[(name, 'n')]))


def main(show=False, dump=False):
    bk = B.Book()
    pg = B.pages()
    # --- before: w19_survey's own probe, per family -----------------------
    before = collections.Counter()
    book_key = w19_survey.key(' '.join(B.WTX.pages()[k]
                                       for k in sorted(B.WTX.pages())))
    for rel, f in B.cells():
        fam = family(rel)
        for line in open(f, encoding='utf-8'):
            line = line.strip()
            if (len(line) < 60 or line.startswith(('#', '>', '<!--', '|'))):
                continue
            probe = ' '.join(w19_survey.key(line).split()[:9])
            before[(fam, probe in book_key)] += 1

    # --- after: every paragraph aligned ------------------------------------
    rates = collections.Counter()
    residue = []
    classes = collections.Counter()
    for rel, f in B.cells():
        if rel in TABLE_ROWS:
            continue
        fam = family(rel)
        head = None
        paras = B.paragraphs(f)
        body = [i for i, (_l, k, t) in enumerate(paras)
                if k not in ('heading', 'row') and not t.startswith('<!--')]
        for pi, (ln, kind, text) in enumerate(paras):
            if kind == 'heading':
                head = text
            if kind == 'row':
                continue
            w = B.words(B.cell_text(text, kind))
            if not w:
                continue
            # A short paragraph (a question, a response, a versicle) is
            # aligned inside its neighbours, so that it is compared with the
            # right place in the book and not with the first look-alike.
            pre = post = []
            if len(w) < 12 and kind != 'heading' and pi in body:
                j = body.index(pi)
                if j > 0:
                    a = paras[body[j - 1]]
                    pre = B.words(B.cell_text(a[2], a[1]))[-12:]
                if j + 1 < len(body):
                    a = paras[body[j + 1]]
                    post = B.words(B.cell_text(a[2], a[1]))[:12]
            grp = {'prose': 'para', 'label': 'para'}.get(kind, kind)
            if text.startswith('<!--'):
                continue                   # a provenance comment, not text
            r = locate(bk, rel, head, pre, w, post)
            if r is None:
                # no usable anchor (short, or only very common 4-grams):
                # is the word sequence in the book at all?
                hit = bk.find_short(w)
                rates[(fam, grp, 'exact' if hit is not None else
                       'unlocated')] += 1
                if hit is None:
                    residue.append({'file': rel, 'line': ln, 'kind': kind,
                                    'status': 'unlocated', 'page': None,
                                    'text': text[:70], 'ops': []})
                    classes['unlocated'] += 1
                continue
            ratio, s, e, ops = r
            diffs = [o[:4] for o in ops if o[0] != 'equal']
            if not diffs:
                # words agree: compare punctuation too
                ct = B.ptoks(B.cell_text(text, kind), cell=True)
                # the same words may stand in several places (the Lord's
                # Prayer): compare against the one that agrees best
                pd = min((bk.punct(ct, a, z) for a, z in (bk.exact or [(s, e)])),
                         key=len)
                if not pd:
                    rates[(fam, grp, 'exact')] += 1
                    continue
                items = []
                for t, c, b, p in pd:
                    k = pclass(c, b)
                    # the comma/semicolon the canticles lost before the mediant
                    nxt = bk.ptok[p + len(b):p + len(b) + 1]
                    if k == 'punct' and t == 'insert' and nxt == ['*']:
                        k = 'mediant-punct'
                    classes[k] += 1
                    pgno = bk.page[s]
                    items.append({'class': k, 'tag': t, 'cell': ' '.join(c),
                                  'book': ' '.join(b), 'page': pgno,
                                  'at': ' '.join(bk.ptok[max(0, p - 4):p + 5])})
                only = set(i['class'] for i in items)
                status = 'pointing' if only == {'pointing'} else 'punct'
                rates[(fam, grp, status)] += 1
                residue.append({'file': rel, 'line': ln, 'kind': kind,
                                'status': status, 'page': bk.page[s],
                                'text': text[:70], 'ops': items})
                continue
            if ratio < 0.5:
                rates[(fam, grp, 'unlocated')] += 1
                classes['unlocated'] += 1
                residue.append({'file': rel, 'line': ln, 'kind': kind,
                                'status': 'unlocated', 'page': bk.page[s],
                                'ratio': round(ratio, 3),
                                'text': text[:70], 'ops': []})
                continue
            rates[(fam, grp, 'diff')] += 1
            items = []
            plain = [o[:4] for o in ops]
            for i, (t, c, b, p) in enumerate(diffs):
                first = plain.index((t, c, b, p)) == 0
                last = plain.index((t, c, b, p)) == len(plain) - 1
                k = classify(t, c, b, text, first, last)
                classes[k] += 1
                items.append({'class': k, 'tag': t, 'cell': ' '.join(c)[:60],
                              'book': ' '.join(b)[:60],
                              'page': bk.page[min(p, len(bk.page) - 1)],
                              'at': bk.context(p, 3, 3)})
            residue.append({'file': rel, 'line': ln, 'kind': kind,
                            'status': 'diff', 'page': bk.page[s],
                            'ratio': round(ratio, 3),
                            'text': text[:70], 'ops': items})

    fams = sorted(set(f for f, _ in before) | set(k[0] for k in rates))
    print('BEFORE (w19_survey probe: lines >= 60 chars, first 9 words)')
    print('%-36s %6s %6s %7s' % ('family', 'found', 'not', 'rate'))
    for fam in fams:
        h, m = before[(fam, True)], before[(fam, False)]
        if h + m:
            print('%-36s %6d %6d %6.1f%%' % (fam, h, m, 100.0 * h / (h + m)))
    print('\nAFTER (every paragraph, whole-paragraph word diff; '
          'punctuation checked where words agree)')
    print('%-36s %-8s %6s %6s %6s %6s %7s' % ('family', 'kind', 'exact',
                                            'punct', 'diff', 'unloc', 'exact%'))
    tot = collections.Counter()
    for fam in fams:
        for grp in ('para', 'rubric', 'heading'):
            n = {s: rates[(fam, grp, s)] for s in
                 ('exact', 'punct', 'diff', 'unlocated')}
            n['exact'] += rates[(fam, grp, 'pointing')]
            if not sum(n.values()):
                continue
            for s, v in n.items():
                tot[(grp, s)] += v
            print('%-36s %-8s %6d %6d %6d %6d %6.1f%%'
                  % (fam, grp, n['exact'], n['punct'], n['diff'],
                     n['unlocated'], 100.0 * n['exact'] / sum(n.values())))
    for grp in ('para', 'rubric', 'heading'):
        n = {s: tot[(grp, s)] for s in ('exact', 'punct', 'diff', 'unlocated')}
        n['exact'] += sum(rates[(f, grp, 'pointing')] for f in fams)
        print('%-36s %-8s %6d %6d %6d %6d %6.1f%%'
              % ('TOTAL', grp, n['exact'], n['punct'], n['diff'],
                 n['unlocated'], 100.0 * n['exact'] / max(1, sum(n.values()))))
    print('\nmechanical classes of the differences:')
    for k, v in classes.most_common():
        print('  %-14s %5d' % (k, v))
    if show:
        for r in residue:
            print('\n%s:%d [%s/%s] p%s %s' % (r['file'], r['line'], r['kind'],
                                           r['status'], r['page'], r['text']))
            for o in r['ops']:
                print('    %-12s %-8s cell=%r book=%r p%s' % (
                    o['class'], o['tag'], o['cell'], o['book'], o['page']))
    if dump:
        json.dump(residue, open(OUT, 'w'), indent=1)
        print('\nwrote %s (%d paragraphs)' % (os.path.relpath(OUT), len(residue)))


if __name__ == '__main__':
    if '--sensitivity' in sys.argv:
        sensitivity()
    else:
        main('--list' in sys.argv, '--json' in sys.argv)
