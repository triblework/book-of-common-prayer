"""w18_mediant.py — does the witness print a mediant where the carrier does?

For every verse of the 1662 Psalter cell, take the word the carrier's mediant
follows (its "pivot"), find that word in the aligned span of the Annexed-Book
page OCR, and look for a mark on it or on the word after it. Three outcomes:

    agree      the witness prints a mark at the same pivot
    unread     the pivot word is not legible in the page OCR, or carries no
               mark there -- page OCR at 4400px still loses about one line in
               twenty on this scan, so this is NOT evidence of absence
    absent     the carrier prints no mediant at all in that verse

Only `absent` is a finding; `unread` verses are re-read line by line
(w18_read.py) when they are few enough to matter, and are otherwise reported as
what they are: verses this pass could not settle. ':' and ';' are treated as
one mark class throughout -- Wave 17 established that page OCR cannot tell them
apart, and this pass makes no claim about which of the two is printed.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from w18_psalter import skel

ALIGN = os.path.join(HERE, 'w18_align.json')


def pivot(text):
    """The word the carrier's mediant follows, and its word offset."""
    i = text.find(' : ')
    if i < 0:
        return None, None
    words = re.findall(r"[A-Za-z']+", text[:i])
    return (skel(words[-1]), len(words)) if words else (None, None)


def like(a, b):
    """OCR-tolerant skeleton match: one is a prefix or suffix of the other."""
    if not a or not b:
        return False
    if a == b:
        return True
    short, long = (a, b) if len(a) <= len(b) else (b, a)
    return len(short) >= 4 and (long.startswith(short) or long.endswith(short))


def classify(row):
    piv, off = pivot(row['carrier'])
    if piv is None:
        return 'absent', None
    toks = row['witness'].split()
    n_car = len(row['carrier'].split())
    want = off * len(toks) / float(max(1, n_car))     # expected position
    best, best_d = None, 1e9
    for i, t in enumerate(toks):
        w = re.sub(r"[^A-Za-z]", '', t)
        if w and like(skel(w), piv) and abs(i - want) < best_d:
            best, best_d = i, abs(i - want)
    if best is None:
        return 'unread', None
    tail = ' '.join(toks[best:best + 2])
    return ('agree' if re.search(r'[:;]', tail) else 'unread'), best


def sample(rows, n=30, seed=18):
    """Re-read a deterministic sample of `unread` verses line by line at
    4400px, to show what the page OCR was failing on. Prints one line each."""
    import random
    import w18_read
    pool = [r for r in rows
            if r['anchored'] and 0.6 <= r['ratio'] <= 1.8
            and classify(r)[0] == 'unread']
    random.Random(seed).shuffle(pool)
    hit = miss = 0
    for r in pool[:n]:
        got = w18_read.read_line(r['page'], r['carrier'], span=2, before=1)
        mark = bool(re.search(r'[:;]', got['second']))
        hit, miss = hit + mark, miss + (not mark)
        print('  %3d:%-3d p%-4d mediant=%-5s %s'
              % (r['psalm'], r['verse'], r['page'], mark, got['second'][:100]))
    print('sample of %d unread verses: mediant legible on re-read %d, still not %d'
          % (len(pool[:n]), hit, miss))


def main():
    rows = json.load(open(ALIGN))
    tally, flagged = {'agree': 0, 'unread': 0, 'absent': 0, 'loose': 0}, []
    for r in rows:
        if not r['anchored'] or not 0.6 <= r['ratio'] <= 1.8:
            tally['loose'] += 1
            continue
        kind, _ = classify(r)
        tally[kind] += 1
        if kind != 'agree':
            flagged.append({'psalm': r['psalm'], 'verse': r['verse'],
                            'page': r['page'], 'kind': kind})
    json.dump(flagged, open(os.path.join(HERE, 'w18_mediant_flags.json'), 'w'),
              indent=0)
    print('verses %d: agree %d, unread %d, absent %d, span too loose %d'
          % (len(rows), tally['agree'], tally['unread'], tally['absent'],
             tally['loose']))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--sample':
        sample(json.load(open(ALIGN)),
               int(sys.argv[2]) if len(sys.argv) > 2 else 30)
    else:
        main()
