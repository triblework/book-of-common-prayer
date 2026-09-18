"""w19_survey.py — how much of the rest of the 1979 text matches the book.

Wave 19 collated the Psalter verse by verse and repaired seven named defects
elsewhere. This measures what a further pass would face: for every other 1979
cell, what share of its paragraphs can be found verbatim in Church
Publishing's file. A paragraph that cannot be found is not necessarily wrong
-- it may be re-wrapped, or a rubric the book prints differently -- but the
rate is a fair guide to where the keying is clean and where it is not.

    python3 ingest/w19_survey.py [--list]
"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w19_witness_text as WT_

SKIP = ('psalter/',)


def key(t):
    t = WT_.flat(t)
    t = re.sub(r'\bLORD\b', 'Lord', t)
    t = t.replace(' : ', ' ').replace(' * ', ' ')   # the mediant, either mark
    return re.sub(r'\s+', ' ', re.sub(r"[^a-z0-9 ]", ' ', t.lower()))


def main(show=False):
    pgs = WT_.pages()
    book = key(' '.join(pgs[k] for k in sorted(pgs)))
    per = {}
    for f in sorted(glob.glob(os.path.join(WT, 'editions/1979/**/*.md'),
                              recursive=True)):
        rel = os.path.relpath(f, os.path.join(WT, 'editions/1979'))
        if rel.startswith(SKIP):
            continue
        fam = rel.split('/')[0]
        hit = miss = 0
        for line in open(f, encoding='utf-8'):
            line = line.strip()
            if (len(line) < 60 or line.startswith(('#', '>', '<!--', '|'))):
                continue
            probe = ' '.join(key(line).split()[:9])
            if probe and probe in book:
                hit += 1
            else:
                miss += 1
                if show:
                    print('  MISS %-46s %s' % (rel, line[:90]))
        a, b = per.get(fam, (0, 0))
        per[fam] = (a + hit, b + miss)
    tot = [0, 0]
    print('%-32s %8s %8s %7s' % ('family', 'found', 'not', 'rate'))
    for fam in sorted(per):
        h, m = per[fam]
        tot[0] += h; tot[1] += m
        print('%-32s %8d %8d %6.1f%%' % (fam, h, m, 100.0 * h / max(1, h + m)))
    print('%-32s %8d %8d %6.1f%%' % ('TOTAL', tot[0], tot[1],
                                     100.0 * tot[0] / max(1, sum(tot))))


if __name__ == '__main__':
    main('--list' in sys.argv)
