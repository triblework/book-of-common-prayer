"""wxa_dol_extra.py -- the Daily Office Lectionary's Holy Days and Special
Occasions tables (book pp. 996-1001), transcribed from the CARRIER (justus's
1993 e-text, bcplectn.txt, `<page 996>` onward) and verified against the
WITNESS by the A3 window method. A silent absence: the repo's
tables/daily-office-lectionary.md stops at Proper 29 and records no gap.

    python3 ingest/wxa_dol_extra.py
        -> scratchpad/render/a/dol-holy-days.md   (NOT editions/; a ruling
           decides whether it is appended to the cell)

Row shape follows the 1928 tables/proper-lessons.md (`Morning 1:` ...),
with the 1979 table's psalm fields:
  Occasion (date) | Morning Psalms: .. | Morning 1: .. | Morning 2: .. |
                    Evening Psalms: .. | Evening 1: .. | Evening 2: ..
An Eve has evening fields only. The e-text's `*or*` is `or`, its `[*]`
the book's `*`, its `--` the repo's `-`; a footnote is its own row
(`Footnote | ...`), as R13 set for the 1662 Kalendar.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wxa_book as B
import wxa_tables as T

SRC = glob.glob('/Users/wtrible/Developer/bcp/scrape-cache/'
                'justus.anglican.org_resources_bcp_bcplectn.txt.*.html')[0]
OUT = ('/private/tmp/claude-501/-Users-wtrible-Developer-bcp--claude-worktrees-'
       'bcp-wave-20-coordinator-5838d5/ff7c7f54-263d-4ce2-ac10-c0c8399ab47d/'
       'scratchpad/render/a/dol-holy-days.md')


def etext_entries():
    lines = open(SRC, encoding='latin-1').read().split('\n')
    start = next(i for i, l in enumerate(lines) if l.strip() == '<page 996>')
    sect, out, cur, notes = None, [], None, []
    for l in lines[start:]:
        s = l.rstrip()
        if s.startswith('-----') or 'END OF' in s:
            break
        if s.strip() in ('<Holy Days>', '<Special Occasions>'):
            sect = s.strip()[1:-1]
            continue
        if not s.strip() or s.strip().startswith('<page'):
            continue
        if re.match(r'^\s*\[\*+\]', s):
            notes.append((sect, s.strip()))
            continue
        if not s.startswith(' '):
            if cur and cur['lines'] and not s.rstrip().endswith(':') and \
                    re.search(r'\d', s) and ';' not in s.split(' ')[0]:
                cur['lines'][-1] += ' ' + s.strip()      # a wrapped line
                continue
            name = s.strip().rstrip(':')
            cur = {'sect': sect, 'name': name, 'lines': []}
            out.append(cur)
            continue
        if cur is not None:
            cur['lines'].append(s.strip())
    return out, notes


def fix(v):
    v = v.replace('*or*', 'or').replace('[**]', '**').replace('[*]', '*')
    v = re.sub(r'-{2,}', '-', v)
    v = re.sub(r':\s+(?=\d)', ':', v)
    v = re.sub(r',(?=\S)', ', ', v)
    return re.sub(r'\s+', ' ', v).strip()


def rows(entries):
    out = []
    for e in entries:
        name = e['name']
        if ';' in name:
            n, d = [x.strip() for x in name.split(';', 1)]
            occ = '%s (%s)' % (n, d)
        else:
            occ = name
        ls = [l for l in e['lines']]
        fields = [occ]
        labels = (('Morning Psalms', 'Morning 1', 'Morning 2'),
                  ('Evening Psalms', 'Evening 1', 'Evening 2'))
        for li, l in enumerate(ls[:2]):
            parts = [fix(p) for p in l.split(';')]
            if not any(parts):
                continue                                 # an Eve's ';;'
            lab = labels[li]
            for k, p in enumerate(parts[:3]):
                if p:
                    fields.append('%s: %s' % (lab[k], p))
        out.append((e['sect'], occ, ' | '.join(fields), len(ls) > 2))
    return out


def book_text():
    P = B.WTX.pages()
    return '\n'.join(B.strip_furniture(P[k]) for k in range(996, 1002))


CITE = re.compile(r'(?:[1-3] )?[A-Z][a-z]+\.? \d+:[\d\-\u2013,ab() ]+\d[ab]?\)?')


def verify(rws):
    """Each citation of a row must stand in the book NEAR ITS OCCASION: the
    window opens at the occasion's name (or, where the two-column page
    splits the name across lines, at the row's first lesson) and runs 420
    characters -- about one printed entry."""
    flat = B.WTX.flat(book_text())
    nflat = T.norm(flat).replace('*', '')
    found, missing, tot = 0, [], 0
    for r in rws:
        nm = re.sub(r'\s*\(.*\)$', '', r[1])
        a = flat.find(nm)
        fields = [f.split(':', 1)[1].strip() for f in r[2].split(' | ')[1:]]
        cits = [c for f in fields for c in re.split(r'\s+or\s+', f)]
        if a >= 0:
            win = T.norm(flat[a:a + 420]).replace('*', '')
        else:
            first = next((c for c in cits if re.match(r'^[1-3]? ?[A-Z]', c)), None)
            j = nflat.find(T.norm(first).replace('*', '')) if first else -1
            win = nflat[max(0, j - 120):j + 300] if j >= 0 else ''
        for cit in cits:
            tot += 1
            c = T.norm(cit).replace('*', '')
            if c and c in win:
                found += 1
            else:
                missing.append((r[1], cit))
    return tot, found, missing


def book_citations_not_in_etext(rws):
    """Citations the book prints on pp. 996-1001 that no e-text row has --
    the entries the 1993 keying lost."""
    flat = B.WTX.flat(book_text())
    have = set(T.norm(c).replace('*', '') for r in rws
               for f in r[2].split(' | ')[1:]
               for c in re.split(r'\s+or\s+', f.split(':', 1)[1]))
    out = []
    for m in CITE.finditer(flat):
        c = m.group(0).strip().rstrip(',')
        n = T.norm(c).replace('*', '')
        if n not in have and not any(n in h or h in n for h in have):
            out.append(c)
    return out


def main():
    entries, notes = etext_entries()
    rws = rows(entries)
    out = ['## Holy Days', '']
    sect = 'Holy Days'
    for s, occ, row, extra in rws:
        if s != sect:
            out += ['## ' + s, '']
            sect = s
        out += [row, '']
    for s, n in notes:
        out += ['Footnote | ' + fix(n.lstrip('[*]* ').strip()) if False else
                'Footnote | ' + fix(n), '']
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write('\n'.join(out).rstrip() + '\n')
    tot, found, missing = verify(rws)
    print('e-text entries: %d (%d Holy Days, %d Special Occasions); '
          'footnotes %d' % (len(rws), sum(1 for r in rws if r[0] == 'Holy Days'),
                            sum(1 for r in rws if r[0] != 'Holy Days'), len(notes)))
    print('verified against pp. 996-1001: %d/%d citations found in their '
          'occasion\'s window (%.1f%%)' % (found, tot, 100.0 * found / max(1, tot)))
    for m in missing:
        print('  NOT FOUND  %-40s %s' % m)
    lost = book_citations_not_in_etext(rws)
    print('book citations no e-text row carries (%d) -- the entries the keying '
          'lost: %s' % (len(lost), lost))
    print('wrote %s' % OUT)


if __name__ == '__main__':
    main()
