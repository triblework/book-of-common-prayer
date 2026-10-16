"""w23_dol_extra.py -- the Daily Office Lectionary's Holy Days and Special
Occasions tables (book pp. 996-1001), transcribed from the CARRIER (justus's
1993 e-text, bcplectn.txt, `<page 996>` onward) and verified against the
WITNESS by the A3 window method. A silent absence: the repo's
tables/daily-office-lectionary.md stops at Proper 29 and records no gap.

    python3 ingest/w23_dol_extra.py
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
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w23_book as B
import w23_tables as T

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


MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December')
CELL = 'tables/daily-office-lectionary-holy-days.md'


def book_entries():
    """The book's Holy Days and Special Occasions (pp. 996-1001), from the
    layout-mode text (the two office columns keep their places): ->
    [{'sect', 'name', 'date', 'mp': [fields], 'ep': [fields], 'page'}]."""
    L = B.layout_pages()
    out, notes, sect = [], [], 'Holy Days'
    for k in range(996, 1002):
        lines = B.strip_furniture(L[k]).split('\n')
        hdr = next((l for l in lines if 'Morning Prayer' in l and
                    'Evening Prayer' in l), None)
        mx = hdr.find('Morning Prayer') if hdr else 27
        ex = hdr.find('Evening Prayer') if hdr else 60
        cur = None
        for l in lines + ['']:
            st = l.strip()
            if st in ('Holy Days', 'Special Occasions'):
                sect = st
                cur = None
                continue
            if 'Morning Prayer' in l and 'Evening Prayer' in l:
                continue
            if re.match(r'^\*+ ', st):
                notes.append(st)
                continue
            if not st:
                cur = None
                continue
            chunks = [(m.start(), m.group(0)) for m in
                      re.finditer(r'\S+(?: \S+)*', l)]
            if cur is None:
                cur = {'sect': sect, 'name': [], 'mp': [], 'ep': [], 'page': k}
                out.append(cur)
            for x, txt in chunks:
                col = 'name' if x < mx - 3 else 'mp' if x < ex - 3 else 'ep'
                if col != 'name' and txt.startswith('or ') and cur[col]:
                    cur[col][-1] += ' ' + txt
                else:
                    cur[col].append(txt)
    for e in out:
        nm = ' '.join(e['name'])
        m = re.search(r'\b(%s) \d+$' % '|'.join(MONTHS), nm)
        e['date'] = m.group(0) if m else None
        e['name'] = (nm[:m.start()].strip() if m else nm).replace('\u2019', "'")
    return out, notes


def ekey(n):
    n = n.lower().replace('saint ', 'st. ').replace('ss. ', 'st. ')
    n = n.replace('&', 'and').replace('tranfiguration', 'transfiguration')
    return re.sub(r'[^a-z]+', ' ', n).strip()


def e_fields(e):
    """An e-text entry's (mp, ep) field lists."""
    out = []
    for l in e['lines'][:2]:
        parts = [fix(p) for p in l.split(';')]
        out.append([p for p in parts if p])
    while len(out) < 2:
        out.append([])
    if e['lines'] and not any(fix(p) for p in e['lines'][0].split(';')):
        out = [[], out[1] if len(e['lines']) > 1 else []]
    return out


def bfix(v):
    v = v.replace('\u2013\u2013', '-').replace('\u2013', '-').replace('\u2014', '-')
    v = re.sub(r'-{2,}', '-', v)
    v = re.sub(r'(?<=\d) (?=\d)', '', v)
    return re.sub(r'\s+', ' ', v).strip()


def row_text(name, date, mp, ep):
    occ = '%s (%s)' % (name, date) if date else name
    f = [occ]
    for lab, vals in (('Morning', mp), ('Evening', ep)):
        if not vals:
            continue
        f.append('%s Psalms: %s' % (lab, vals[0]))
        for i, v in enumerate(vals[1:3], 1):
            f.append('%s %d: %s' % (lab, i, v))
    return ' | '.join(f)


def build():
    """-> (cell text, evidence list, flags list, report counts)"""
    import w23_items as I
    entries, notes = etext_entries()
    book, bnotes = book_entries()
    by = {}
    for e in entries:
        nm = e['name'].split(';')[0].strip()
        by.setdefault(ekey(nm), e)
    lines = ['# Holy Days and Special Occasions', '',
             '<!-- 1979 (public domain). The Daily Office Lectionary\'s tables '
             'for Holy Days and Special Occasions (book pp. 996-1001). Carrier: '
             'justus bcplectn.txt; witness: Church Publishing\'s PDF. -->', '']
    ev, flags, counts = [], [], collections.Counter()
    sect = None
    for b in book:
        if b['sect'] != sect:
            sect = b['sect']
            lines += ['## ' + sect, '']
        bmp = [bfix(x) for x in b['mp']]
        bep = [bfix(x) for x in b['ep']]
        e = by.get(ekey(b['name']))
        src = 'witness'
        mp, ep = bmp, bep
        name = b['name']
        row_flags = []
        if e is not None:
            emp, eep = e_fields(e)
            pairs = list(zip(emp, bmp)) + list(zip(eep, bep))
            agree = sum(1 for c, w in pairs if T.level(c, w))
            if pairs and agree >= len(pairs) / 2 and len(emp) == len(bmp) \
                    and len(eep) == len(bep):
                src = 'carrier'
                mp, ep = [], []
                for ev_l, bk_l, out in ((emp, bmp, mp), (eep, bep, ep)):
                    for fi, (c, w) in enumerate(zip(ev_l, bk_l)):
                        lv = T.level(c, w)
                        if not lv and re.sub(r'[,\s]', '', T.norm(c)) == \
                                re.sub(r'[,\s]', '', T.norm(w)):
                            lv = 'punct'          # a comma, as the book sets it
                        if lv:
                            out.append(c if lv in ('exact', 'notation', 'marks',
                                                   'glyph') else w)
                            if lv == 'punct':
                                counts['punct-from-witness'] += 1
                        else:
                            j = T.judge(c, w, 'mp' if fi == 0 else 'r')
                            if j == 'cell-evident':
                                out.append(w)
                                counts['carrier-evident-fixed'] += 1
                            elif j == 'witness-evident':
                                out.append(c)
                                counts['witness-evident-kept'] += 1
                            else:
                                out.append(c)
                                row_flags.append((c, w))
                                counts['disputed-flagged'] += 1
                ename = e['name'].split(';')[0].strip()
                if ekey(ename) == ekey(name):
                    name = I.keep_cell_case(ename, name)
            else:
                counts['carrier-damaged-row-from-witness'] += 1
        else:
            counts['witness-supplied-row'] += 1
        if src == 'witness':
            counts['rows-from-witness'] += 1
        else:
            counts['rows-from-carrier'] += 1
        row = row_text(name, b['date'], mp, ep)
        lines.append(row)
        for c, w in row_flags:
            note = ("the witness (Church Publishing's PDF, p. %d) prints '%s'; "
                    "no second check settles it; carried as the e-text prints "
                    "it (R11 addendum)" % (b['page'], w))
            lines.append("<!-- VERIFY: '%s'; %s -->" % (c, note))
            flags.append((row.split(' | ')[0], c, note))
        lines.append('')
        ev.append({'row': row.split(' | ')[0], 'source': src, 'page': b['page'],
                   'etext_entry': e['name'] if e else None})
    for n in bnotes:
        lines += ['Footnote | ' + n, '']
        ev.append({'row': 'Footnote', 'source': 'witness+carrier',
                   'page': 1001, 'etext_entry': n})
    return '\n'.join(lines).rstrip() + '\n', ev, flags, counts, entries, book


def main():
    text, ev, flags, counts, entries, book = build()
    out = OUT
    if '--write' in sys.argv:
        out = os.path.join(os.path.dirname(HERE), 'editions/1979', CELL)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(text)
    json.dump({'cell': CELL, 'rows': ev, 'flags': flags, 'counts': counts},
              open(os.path.join(HERE, 'w23_dol_extra_evidence.json'), 'w'),
              indent=1, ensure_ascii=False)
    print('book entries %d; e-text entries %d' % (len(book), len(entries)))
    print('counts: %s' % dict(counts))
    print('flags: %d' % len(flags))
    # the field check: every written field against the book's entry for the
    # same occasion, by column (the layout parse keeps the columns)
    import w23_tables as T2
    bkby = {ekey(b['name']): b for b in book}
    tot = ok = 0
    differ = []
    for l in text.split('\n'):
        if ' | ' not in l or l.startswith('Footnote'):
            continue
        f = l.split(' | ')
        occ = re.sub(r'\s*\(.*\)$', '', f[0])
        b = bkby.get(ekey(occ))
        vals = {x.split(':', 1)[0]: x.split(':', 1)[1].strip() for x in f[1:]}
        bm = [bfix(x) for x in b['mp']] if b else []
        be = [bfix(x) for x in b['ep']] if b else []
        want = {}
        for lab, vv in (('Morning', bm), ('Evening', be)):
            if vv:
                want[lab + ' Psalms'] = vv[0]
                for i, v in enumerate(vv[1:3], 1):
                    want['%s %d' % (lab, i)] = v
        for k2, v in vals.items():
            tot += 1
            if k2 in want and (T2.level(v, want[k2]) or re.sub(r'[,\s]', '', T2.norm(v))
                               == re.sub(r'[,\s]', '', T2.norm(want[k2]))):
                ok += 1
            else:
                differ.append((occ, k2, v, want.get(k2)))
    print('field check of the written table against the book, column by column: '
          '%d/%d fields agree' % (ok, tot))
    for d in differ:
        print('  DIFFERS  %s / %s: %r (book %r)' % d)
    # the A3 check, on what is written: every citation near its occasion
    rws = [(None, l.split(' | ')[0], l, False) for l in text.split('\n')
           if ' | ' in l and not l.startswith('Footnote')]
    tot, found, missing = verify(rws)
    print('A3 check of the written table against pp. 996-1001: %d/%d (%.1f%%)'
          % (found, tot, 100.0 * found / max(1, tot)))
    for m in missing:
        print('  NOT FOUND  %-40s %s' % m)
    print('wrote %s' % out)


if __name__ == '__main__':
    main()
