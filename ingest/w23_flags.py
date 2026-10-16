"""w23_flags.py -- every open 1979 VERIFY flag, and what Church Publishing's
file can say about it (Workstream A, Phase 1; read-only).

For each inline flag in editions/1979: the file, line, the quoted reading,
the flag's own question (its template), and the witness's verdict:

  RESOLVABLE     the book prints what the flag says is missing or doubtful,
                 on a page of the 1979 text (page + a short fragment given)
  CONFIRMS       the book prints the flagged reading as the cell has it
  OUT OF POWER   the question is not one this witness can answer: it is a
                 representation decision of this repo, or it concerns pages
                 this file does NOT carry in their 1979 form (the Sunday
                 lectionary, pp. 889-931, is replaced by the 2007 RCL
                 insert; see w23_tables.py), or it turns on letter-case or
                 pointing (R11)

    python3 ingest/w23_flags.py            # summary + every flag
"""
import collections
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w23_book as B
import w23_tables as T

# the quoted reading may itself hold an apostrophe ('All Saint's Day'), so it
# ends at the quote that is followed by the flag's own separator
FLAG = re.compile(r"<!-- VERIFY:?\s*'(.*?)'(\s*(?:\u2014|;).*?)-->", re.S)
TRAD, CONT = (158, 210), (211, 261)


def template(rest):
    r = re.sub(r"'[^']*'", "'X'", rest).strip(' ;—-')
    if 'three reading sets' in r:
        return 'three-year'
    if 'contemporary-language collect for this day is absent' in r:
        return 'absent-contemporary'
    if 'traditional-language collect for this day is absent' in r:
        return 'absent-traditional'
    if 'COLLECT LINEAGE' in r:
        return 'lineage'
    if 'citation fields' in r or 'loses page 889' in r:
        return 'euch-table'
    if 'readings where this office' in r or 'merges a reading line' in r:
        return 'dol-table'
    return 'other'


def title_of(path):
    for line in open(path, encoding='utf-8'):
        if line.startswith('# '):
            return line[2:].strip()
    return ''


def find_in(needle, rng):
    """-> (page, context) of the first hit of needle within pages rng."""
    P = B.WTX.pages()
    n = B.WTX.flat(needle).lower()
    for k in range(rng[0], rng[1] + 1):
        t = B.WTX.flat(P.get(k, ''))
        i = t.lower().find(n)
        if i >= 0:
            return k, t[i:i + 160]
    return None, None


def collect_after(title, rng):
    """The first words the book prints after a day's title in a section."""
    P = B.WTX.pages()
    for k in range(rng[0], rng[1] + 1):
        t = B.WTX.flat(P.get(k, ''))
        m = re.search(re.escape(title) + r'(?:\s+[A-Z][a-z]+ \d+)?\s+', t)
        if m:
            rest = t[m.end():]
            # a rubric may stand between title and collect
            rest = re.sub(r'^The Proper Liturgy for this day is on page \d+\.\s*',
                          '', rest)
            return k, ' '.join(rest.split()[:8])
    return None, None


def main():
    flags = []
    for f in sorted(glob.glob(os.path.join(WT, 'editions/1979/**/*.md'),
                              recursive=True)):
        rel = os.path.relpath(f, os.path.join(WT, 'editions/1979'))
        text = open(f, encoding='utf-8').read()
        for m in FLAG.finditer(text):
            line = text[:m.start()].count('\n') + 1
            flags.append((rel, line, m.group(1), m.group(2), f))
    book_rows = T.book_dol()
    out = []
    for rel, line, reading, rest, path in flags:
        t = template(rest)
        verdict, page, frag = 'OUT OF POWER', None, ''
        if t == 'three-year':
            # the readings live in the Lectionary, which this file replaces
            p, ctx = find_in(reading, TRAD)
            page = p
            frag = ('title printed as cited' if p else
                    'title NOT found as cited in pp. 158-210')
            if not p:
                p2, ctx2 = find_in(reading.replace("Saint's", "Saints'"), TRAD)
                if p2:
                    frag = "title printed 'All Saints'' (p%d)" % p2
        elif t in ('absent-contemporary', 'absent-traditional'):
            rng = CONT if t == 'absent-contemporary' else TRAD
            p, first = collect_after(reading, rng)
            if p is None:
                p, first = collect_after(title_of(path), rng)
            verdict, page = ('RESOLVABLE (new text: ruling)', p) if p else (
                'NOT FOUND', None)
            frag = 'book begins: %s' % (first or '?')
        elif t == 'lineage':
            p, ctx = find_in(reading, TRAD)
            page = p
            frag = ('the book prints %s with its date rule; the placement at '
                    'this slug is the repo\'s' % reading)
        elif t == 'euch-table':
            frag = ('pp. 889-932 of this file are the 2007 RCL, not the 1979 '
                    'table')
        elif t == 'dol-table':
            # locate the flagged occasion in the book's rows
            cell = [c for c in T.cell_dol() if abs(c[6] - (line - 1)) <= 1
                    or c[6] == line - 1]
            hit = None
            if cell:
                c = cell[0]
                for b in book_rows:
                    if (b[0] == c[0] and T.head_key(b[1] or '') ==
                            T.head_key(c[1] or '') and T.day_key(b[2]) ==
                            T.day_key(c[2])):
                        hit = b
                        break
            if 'merges a reading line' in rest:
                _res, missing = T.compare(T.cell_dol(), book_rows)
                lost = [b for b in missing if b[0] == 'one' and
                        T.head_key(b[1] or '') == 'proper 4']
                if lost:
                    verdict, page = 'RESOLVABLE (table: ruling)', lost[0][6]
                    out.append((rel, line, reading, t, verdict, page,
                                'the book prints Proper 4 %s; the cell has '
                                'none of these rows (the heading swallowed '
                                'them)' % ', '.join(b[2] for b in lost)))
                    continue
            if hit:
                verdict, page = 'RESOLVABLE (table: ruling)', hit[6]
                frag = 'book row %s / %s: %s & %s | %s' % (
                    hit[1], hit[2], hit[3], hit[4], '; '.join(hit[5]))
            else:
                verdict = 'NOT LOCATED (prototype)'
        out.append((rel, line, reading, t, verdict, page, frag))
    by = collections.Counter((o[3], o[4].split(' (')[0]) for o in out)
    print('%d flags' % len(out))
    for k, v in sorted(by.items()):
        print('  %-22s %-14s %3d' % (k[0], k[1], v))
    print()
    for o in out:
        print('%s:%d  [%s] %s  p%s  %r  -- %s' % (o[0], o[1], o[3], o[4],
                                                o[5], o[2][:50], o[6][:110]))


if __name__ == '__main__':
    main()
