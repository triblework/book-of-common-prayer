"""wxa_tables.py -- a comparison method for the 1979 lectionary tables
(Workstream A, Phase 1 prototype; read-only, writes no cell).

WHY A DIFFERENT METHOD. The repo renders a table row as one long line of
` | ` fields ("Sunday | Morning Psalms: 146, 147 | ... | Matt. 25:1-13"); the
book prints a grid. A paragraph probe therefore matches 1.5% of rows and says
nothing. The unit of comparison has to be the CITATION IN ITS CELL.

WHAT THE WITNESS IS, PAGE BY PAGE (found here; see the report):
  * pp. 936-995  the Daily Office Lectionary, Year One on even pages and Year
                 Two on odd, set as the 1979 book sets it. COMPARABLE.
  * pp. 996-1001 its Holy Days and Special Occasions -- which the repo's
                 tables/daily-office-lectionary.md does not carry at all.
  * pp. 889-932  NOT the 1979 Sunday lectionary: every page carries the slug
                 "RCL pages for BCP 4/13/07" and is headed "The Revised Common
                 Lectionary". Church Publishing replaced the 1979 table with
                 the RCL (adopted by the Episcopal Church in 2006). This
                 witness cannot speak to tables/eucharistic-lectionary.md.
  * pp. 19-30    NOT the 1979 Calendar: slug "cpg-bcp-calendar.indd ...
                 06/12/08", with commemorations added after 1979. This witness
                 cannot speak to tables/calendar.md either.
The two inserts are run below only as CONTROLS: a method that "verified" a
1979 table against an RCL page would be broken.

THE METHOD (Daily Office Lectionary).
  1. Parse the book's pages into rows. Each row is two printed lines, which
     the text layer keeps intact with runs of spaces between columns:
        "Sunday 146, 147      &      111, 112, 113"
        "Isa. 1:1-9      2 Pet. 3:1-10      Matt. 25:1-18"
     A row's OCCASION is (year from the page's parity, the week heading
     above it, the day label).
  2. Parse the cell into rows keyed the same way (year from `## Year One/Two`,
     week from `### `, day from the first field).
  3. For each cell row, take the book row with the same occasion -- the
     WINDOW is that one printed row, nothing else on the page -- and look up
     each cell citation among that row's fields: (occasion, column, citation)
     -> exact | notation (same after folding dashes, spaces, commas) | glyph
     (same after folding the text layer's 1/I and ]/1 confusions) | differs.
  4. Classify every mismatch and print the list.
SENSITIVITY: before trusting a 99% rate, inject citations the book prints
NOWHERE (a real book name, a chapter it never cites) and citations the book
prints in a DIFFERENT row (a neighbour's Gospel); the method must flag every
one. Both are measured below.

    python3 ingest/wxa_tables.py            # rates, classes, sensitivity
    python3 ingest/wxa_tables.py --list     # + every mismatch
"""
import collections
import difflib
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import wxa_book as B

DOL = os.path.join(WT, 'editions/1979/tables/daily-office-lectionary.md')
EUCH = os.path.join(WT, 'editions/1979/tables/eucharistic-lectionary.md')
CAL = os.path.join(WT, 'editions/1979/tables/calendar.md')
DAYS = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
        'Saturday')


def norm(c):
    """Fold notation only: dashes, spaces, the comma space, a final stop, and
    the 1993 e-text's own spellings of the book's marks ("[*]" for the
    asterisk, "&&" for the ampersand of "95* & 22")."""
    c = c.replace('\u2013', '-').replace('\u2014', '-')
    c = c.replace('[***]', '***').replace('[**]', '**').replace('[*]', '*')
    c = c.replace('&&', '&')
    c = re.sub(r'-+', '-', c)
    c = re.sub(r'\s+', '', c)
    return c.rstrip('.').lower()


def marks(c):
    """Also ignore the asterisks (Invitatory / morning / evening marks)."""
    return norm(c).replace('[]', '').replace('*', '')


def punct(c):
    """Also ignore stops and the comma/semicolon between chapter refs."""
    return marks(c).replace('.', '').replace(';', ',').replace(':', ':')


def glyph(c):
    """Also fold the text layer's own glyph confusions: capital I for the
    digit 1 ("I Thess."), and a closing bracket read as 1 ("[791")."""
    c = punct(c).replace('i', '1')
    return re.sub(r'\[(\d+?)1(?=$|,)', r'[\1]', c)


LEVELS = (('exact', lambda x: x), ('notation', norm), ('marks', marks),
          ('punct', punct), ('glyph', glyph))
OK = ('exact', 'notation', 'marks', 'punct', 'glyph')


def split_alts(field):
    """'John 11:1-27, or 12:1-10' -> ['John 11:1-27', '12:1-10']"""
    return [x.strip() for x in re.split(r',?\s+or\s+|^or\s+', field)
            if x.strip()]


def key(s):
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()


def head_key(h):
    """'Proper 4 (=Week of 1-12; ...)' and 'Proper 4     Week of the Sunday
    closest to June 1' both key as 'proper 4'; 'Week of 1 Advent' keeps all."""
    k = key(h)
    m = re.match(r'(proper \d+)', k)
    return m.group(1) if m else k


def day_key(d):
    d = key(d.replace('–', ' '))
    return d


# --- the book ---------------------------------------------------------------

LABEL = re.compile(
    r'^((?:Sun|Mon|Tues|Wednes|Thurs|Fri|Satur)day|(?:Dec|Jan)\. \d+|'
    r'Eve of (?:\d )?[A-Z][a-z]+(?: [A-Z][a-z]+)*|Christmas (?:Eve|Day)|'
    r'(?:First|Second) Sunday after Christmas|Holy Name|Epiphany|'
    r'Ash Wednesday|Palm Sunday|Maundy Thursday|Good Friday|Holy Saturday|'
    r'Easter Day|Ascension Day|The Day of Pentecost|Trinity Sunday)\b\s*(.*)$')
BOOKNAME = re.compile(r'^(?:[1-3]\s)?[A-Z][A-Za-z]*\.?$')


def split_citations(field):
    """A reading field the text layer ran together with its neighbour
    ("Jer. 38:1-13 1 Cor. 14:26-33a") -> one string per citation."""
    toks = field.split()
    out, cur = [], []
    i = 0
    while i < len(toks):
        t = toks[i]
        start = False
        if cur and any(':' in c or re.match(r'^\d', c) for c in cur[1:]):
            if re.match(r'^[1-3]$', t) and i + 1 < len(toks) and \
                    re.match(r'^[A-Z][a-z]', toks[i + 1]):
                start = True
            elif re.match(r'^[A-Z][a-z]+\.?$', t) and t not in ('or',):
                start = True
        if start:
            out.append(' '.join(cur))
            cur = []
        cur.append(t)
        i += 1
    if cur:
        out.append(' '.join(cur))
    return out


def day_line(l):
    """-> (label, morning psalms, evening psalms) or None"""
    m = LABEL.match(l)
    if not m or '&' not in l:
        return None
    rest = m.group(2)
    parts = re.split(r'\s{3,}&\s{3,}', rest)
    if len(parts) < 2:
        i = rest.rfind('&')
        parts = [rest[:i], rest[i + 1:]]
    mp, ep = parts[0].strip(), ' '.join(parts[1:]).strip()
    return m.group(1), mp.strip(' -\u2013'), ep


def book_dol():
    """-> [(year, week, day, mp, ep, [reading fields], page)]. A row is the
    day line and every citation line under it (Palm Sunday's two lines,
    Good Friday's 'or' line), up to the next day, heading or footnote."""
    P = B.pages()
    rows, weeks = [], {}
    for k in range(936, 996):
        year = 'one' if k % 2 == 0 else 'two'
        lines = [l.strip() for l in P[k].split('\n') if l.strip()]
        week = weeks.get(year)       # a week can run on from the last page
        i = 0
        while i < len(lines):
            l = lines[i]
            d = day_line(l)
            if d:
                rd, rawl = [], []
                while i + 1 < len(lines):
                    nxt = lines[i + 1]
                    if (day_line(nxt) or nxt.startswith('*')
                            or HEAD.match(nxt)
                            or not re.search(r'\d+:\d|\d+-\d|\d+ ~', nxt)):
                        break
                    rawl.append(re.split(r'\s{3,}', nxt))
                    for x in re.split(r'\s{3,}', nxt):
                        if x.startswith('or '):
                            x = x[3:]
                        for y in split_citations(x):
                            rd.extend(split_alts(y))
                    i += 1
                rows.append((year, week, d[0], d[1], d[2], rd, k, rawl))
            elif HEAD.match(l):
                week = re.split(r'\s{3,}', l)[0] if l.startswith('Proper') else l
                weeks[year] = week
            i += 1
    return rows


HEAD = re.compile(r'^(Week of |Proper \d|Christmas Day and|The Epiphany and|'
                  r'Holy Week|Easter Week)')


# --- the cell -----------------------------------------------------------------

def cell_dol(path=DOL, text=None):
    """-> [(year, week, day, mp, ep, [readings], line)]"""
    rows, year, week = [], None, None
    src = text.split('\n') if text is not None else open(path, encoding='utf-8')
    for n, line in enumerate(src, 1):
        s = line.strip()
        if s.startswith('## Year '):
            year = s[8:].strip().lower()
        elif s.startswith('### '):
            week = s[4:].strip()
        elif ' | ' in s and not s.startswith('<!--'):
            f = [x.strip() for x in s.split(' | ')]
            day, mp, ep, rd = f[0], '', '', []
            for x in f[1:]:
                if x.startswith('Morning Psalms:'):
                    mp = x.split(':', 1)[1].strip()
                elif x.startswith('Evening Psalms:'):
                    ep = x.split(':', 1)[1].strip()
                elif x.startswith('Psalms:'):
                    mp = x.split(':', 1)[1].strip()
                else:
                    rd.append(x)
            rows.append((year, week, day, mp, ep, rd, n))
    return rows


MATCH = {}          # cell line -> the book row compare() gave it (last run)


def level(cv, bv):
    for name, f in LEVELS:
        if f(cv) == f(bv):
            return name
    return None


def compare(cells, book):
    """-> per-citation results [(cell row, column, cell value, book value,
    verdict)] and the book rows no cell row claimed.

    The WINDOW for a cell row is the one book row with the same occasion
    (year, week, day). Psalms are compared column for column; each reading
    -- each alternative of an 'or' -- must be one of that row's printed
    readings. A cell row whose occasion the book has already used (a week
    heading lost in the e-text, so two weeks' rows sit under one) is tried
    against the same day of the FOLLOWING week and called 'misfiled'."""
    order = [(r[0], head_key(r[1] or '')) for r in book]
    idx = collections.defaultdict(list)
    for r in book:
        idx[(r[0], head_key(r[1] or ''), day_key(r[2]))].append(r)
    used, out = set(), []
    shifted = set()          # cell headings whose rows have run into the next week
    for c in cells:
        k = (c[0], head_key(c[1] or ''), day_key(c[2]))
        cand = [b for b in idx.get(k, []) if id(b) not in used]
        tag = None
        if (c[0], c[1]) in shifted:
            cand = []        # once a heading's rows run on, the rest follow
        if not cand and (idx.get(k) or (c[0], c[1]) in shifted):
            # the next week in the book that has this day free
            wk = [w for w in dict.fromkeys(order) if w[0] == c[0]]
            if (c[0], head_key(c[1] or '')) in wk:
                j = wk.index((c[0], head_key(c[1] or '')))
                for w in wk[j + 1:j + 3]:
                    cc = [b for b in idx.get((w[0], w[1], day_key(c[2])), [])
                          if id(b) not in used]
                    if cc:
                        cand, tag = cc, 'misfiled'
                        break
        if not cand:
            out.append((c, 'row', c[2], None, 'no-row'))
            continue
        b = cand[0]
        used.add(id(b))
        MATCH[c[6]] = b
        if tag:
            shifted.add((c[0], c[1]))
            out.append((c, 'row', c[1], b[1], 'misfiled'))
        for col, cv, bv in (('mp', c[3], b[3]), ('ep', c[4], b[4])):
            if col == 'ep' and not cv and c[3] and not c[4]:
                continue                     # a single "Psalms:" field
            lv = level(cv, bv)
            out.append((c, col, cv, bv, lv or 'differs'))
        bfields = list(b[5])
        claimed = set()
        for j, field in enumerate(c[5]):
            for cv in split_alts(field):
                hit = None
                for i, bv in enumerate(bfields):
                    lv = level(cv, bv)
                    if lv and (hit is None or OK.index(lv) < OK.index(hit[0])):
                        hit = (lv, i, bv)
                if hit:
                    claimed.add(hit[1])
                    out.append((c, 'r%d' % (j + 1), cv, hit[2], hit[0]))
                else:
                    near = max(bfields, key=lambda x: difflib.SequenceMatcher(
                        None, norm(cv), norm(x)).ratio()) if bfields else None
                    out.append((c, 'r%d' % (j + 1), cv, near, 'differs'))
        for i, bv in enumerate(bfields):
            if i not in claimed and not any(
                    r[3] == bv and r[0] is c for r in out):
                out.append((c, 'r?', None, bv, 'cell-lacks'))
    missing = [b for b in book if id(b) not in used]
    return out, missing


def differs_class(cv, bv):
    """What kind of disagreement is a 'differs'?"""
    a, b = norm(cv), norm(bv)
    if re.sub(r'\d', '#', a) == re.sub(r'\d', '#', b):
        return 'digit'                  # same shape, a numeral differs
    if a.replace('[', '').replace(']', '') == b.replace('[', '').replace(']', ''):
        return 'brackets'
    if re.sub(r'\(.*?\)', '', a) == re.sub(r'\(.*?\)', '', b):
        return 'parenthesis'
    if a in b or b in a:
        return 'truncated'
    if len(a) > len(b) + 6:
        return 'merged'                 # the cell field carries a neighbour
    return 'other'


# chapters per book, for a PLAUSIBILITY check only (a citation to Mark 23
# cannot be right); never used to supply a reading
CHAPTERS = {'matt': 28, 'mark': 16, 'luke': 24, 'john': 21, 'acts': 28,
            'rom': 16, 'gal': 6, 'eph': 6, 'phil': 4, 'col': 4, 'heb': 13,
            'james': 5, 'jude': 1, 'rev': 22, 'ruth': 4, 'haggai': 2,
            'amos': 9, 'micah': 7, 'joel': 3, 'mal': 4}
ABBR = re.compile(r'^(?:[1-3] )?(Gen|Exod|Lev|Num|Deut|Joshua|Judges|Ruth|Samuel|'
                  r'Kings|Chron|Ezra|Neh|Esther|Job|Prov|Eccles|Song|Isa|Jer|'
                  r'Lam|Ezek|Dan|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Hab|'
                  r'Zeph|Haggai|Zech|Mal|Matt|Mark|Luke|John|Acts|Rom|Cor|Gal|'
                  r'Eph|Phil|Col|Thess|Tim|Titus|Philemon|Heb|James|Pet|Jude|'
                  r'Rev|Wisdom|Ecclus|Baruch|Judith|Tobit|Macc|Esdras)\.? \d')


def malformed(c, col='r'):
    """A citation no printing could have: an unknown or missing book name, a
    letter or a stop inside a number, a double colon, a range that runs
    backwards or overlaps the one before, a chapter past the end of the
    book, run-together text."""
    if c is None:
        return False
    s = c.strip()
    if re.search(r'[a-z]{3,}:', s) or re.search(r'day:', s):
        return True                              # 'onday: 31' run together
    if re.search(r'\d:\d+:|\d\.\d|:[a-z]|\d-\d+:\d', s):
        return True                              # '9:1:24', '9.6b', '65:a.'
    for a, b in re.findall(r'(?<![\d:])(\d+)-(\d+)(?![\d:])',
                           re.sub(r'\d+:', '', s)):
        if int(b) <= int(a):
            return True                          # '1-1', '31-26'
    prev = None
    for part in re.findall(r'(\d+)(?:-(\d+))?', re.sub(r'^.*?\d+:', '', s)):
        lo, hi = int(part[0]), int(part[1] or part[0])
        if prev is not None and lo <= prev and ',' in s and ';' not in s and \
                s.count(':') == 1:
            return True                          # '23:1-17,13-17'
        prev = hi
    if col in ('mp', 'ep') or not re.search(r'[A-Za-z]{2,}', s.replace(' or ', ' ')):
        return False if col in ('mp', 'ep') else col.startswith('r')
    if not ABBR.match(s.replace('Mark.', 'Mark')):
        return True
    if re.search(r'\d[A-Za-z~]\d|\d[SlO]\b|~', s):
        return True
    for a, b in re.findall(r'(?<![\d:])(\d+)-(\d+)(?![\d:])',
                           re.sub(r'\d+:', '', s)):
        if int(b) < int(a) and len(b) >= len(a):
            return True
    m = re.match(r'^(?:[1-3] )?([A-Za-z]+)\.? (\d+)', s)
    if m and m.group(1).lower() in CHAPTERS and \
            int(m.group(2)) > CHAPTERS[m.group(1).lower()]:
        return True
    return False


def judge(cv, bv, col='r'):
    """Who is wrong in a 'differs'?"""
    cm, bm = malformed(cv, col), malformed(bv, col)
    if cm and not bm:
        return 'cell-evident'
    if bm and not cm:
        return 'witness-evident'
    if cm and bm:
        return 'both-malformed'
    return 'disputed'


def sensitivity(cells, book, n=200, seed=1979):
    """Inject citations the book prints nowhere, and citations it prints in
    another row; count how many the method flags."""
    rnd = random.Random(seed)
    printed = set()
    for b in book:
        for x in [b[3], b[4]] + list(b[5]):
            printed.add(norm(x))
    good = [c for c in cells if len(c[5]) == 3]
    nowhere = flagged1 = 0
    for c in rnd.sample(good, n):
        cit = c[5][0]
        m = re.match(r'^(.*?)(\d+):(.*)$', cit)
        if not m:
            continue
        for bump in (97, 89, 83, 79):
            fake = '%s%d:%s' % (m.group(1), int(m.group(2)) + bump, m.group(3))
            if norm(fake) not in printed:
                break
        else:
            continue
        nowhere += 1
        row = (c[0], c[1], c[2], c[3], c[4], [fake] + c[5][1:], c[6])
        res, _ = compare([row], book)
        if any(r[2] == fake and r[4] not in OK for r in res) or \
                not any(r[2] == fake for r in res):
            flagged1 += 1
    moved = flagged2 = 0
    for c in rnd.sample(good, n):
        other = rnd.choice(good)
        if norm(other[5][2]) == norm(c[5][2]):
            continue
        moved += 1
        row = (c[0], c[1], c[2], c[3], c[4], c[5][:2] + [other[5][2]], c[6])
        res, _ = compare([row], book)
        moved_in = other[5][2]
        if any(r[2] in split_alts(moved_in) and r[4] not in OK for r in res) \
                or not any(r[2] in split_alts(moved_in) for r in res):
            flagged2 += 1
    return nowhere, flagged1, moved, flagged2


# --- the controls: the substituted pages -------------------------------------

def control_euch():
    """The repo's 1979 Sunday rows against the 2007 RCL pages, by the same
    window rule: each citation looked up in the RCL page text between the
    occasion's name and the next occasion. Expected to fail often."""
    P = B.pages()
    years = {'A': range(889, 899), 'B': range(899, 911), 'C': range(911, 933)}
    text = {}
    for y, rng in years.items():
        text[y] = '\n'.join(P[k] for k in rng)
    year, tot, hit = None, 0, 0
    for line in open(EUCH, encoding='utf-8'):
        s = line.strip()
        if s.startswith('## Year '):
            year = s[8:].strip()
        elif s.startswith('## '):
            year = None
        elif year and ' | ' in s:
            f = [x.strip() for x in s.split(' | ')]
            occ = f[0]
            t = text[year]
            first = occ.split()[0]
            i = t.find(occ.split(' (')[0][:18])
            win = t[i:i + 600] if i >= 0 else ''
            for x in f[1:]:
                for cit in re.split(r'\s+or\s+|,\s+(?=[A-Z1-3])', x.replace(
                        'Psalm:', '').strip()):
                    if not re.search(r'\d', cit):
                        continue
                    tot += 1
                    if win and norm(cit) in norm(win):
                        hit += 1
    return tot, hit


def control_cal():
    """The repo's 1979 Kalendar notes against the 2008 calendar pages."""
    P = B.pages()
    txt = B.WTX.flat(' '.join(B.WTX.pages()[k] for k in range(19, 31)))
    txt = re.sub(r'\s+', ' ', txt)
    tot = hit = 0
    later = 0
    for line in open(CAL, encoding='utf-8'):
        m = re.search(r'Kalendar Note: (.*)$', line.strip())
        if not m or m.group(1).strip() in ('—', ''):
            continue
        tot += 1
        note = m.group(1).strip()
        if key(note) in key(txt):
            hit += 1
    # rows the 2008 pages fill that the 1979 cell leaves empty
    cellempty = sum(1 for l in open(CAL, encoding='utf-8')
                    if 'Kalendar Note: —' in l)
    return tot, hit, cellempty


def main(show=False):
    book = book_dol()
    cells = cell_dol()
    res, missing = compare(cells, book)
    v = collections.Counter(r[4] for r in res)
    tot = sum(v.values())
    print('DAILY OFFICE LECTIONARY (pp. 936-995): %d book rows parsed, %d cell '
          'rows' % (len(book), len(cells)))
    print('  per field (occasion, column, citation): %d compared' % tot)
    for k in OK + ('differs', 'cell-lacks', 'misfiled', 'no-row'):
        print('    %-11s %5d  %5.1f%%' % (k, v[k], 100.0 * v[k] / max(1, tot)))
    ok = sum(v[k] for k in OK)
    print('  match (exact..glyph): %.1f%%' % (100.0 * ok / max(1, tot)))
    rows_ok = collections.Counter()
    for r in res:
        rows_ok[r[0][6]] = rows_ok[r[0][6]] or 0
    bad_rows = set(r[0][6] for r in res if r[4] not in OK)
    print('  rows fully matching: %d of %d (%.1f%%)' % (
        len(cells) - len(bad_rows), len(cells),
        100.0 * (len(cells) - len(bad_rows)) / len(cells)))
    print('  book rows no cell row claims: %d' % len(missing))
    dc = collections.Counter(differs_class(r[2], r[3]) for r in res
                             if r[4] == 'differs' and r[2] and r[3])
    print('  "differs" by shape: %s' % dict(dc))
    notat = collections.Counter()
    for r in res:
        if r[4] == 'notation':
            a, b = r[2], r[3]
            if ('–' in b) != ('–' in a):
                notat['en-dash span'] += 1
            elif a.replace(' ', '') == b.replace(' ', ''):
                notat['spacing'] += 1
            else:
                notat['other'] += 1
    print('  "notation" by kind: %s' % dict(notat))
    # who is wrong, where the row is the right row (not misfiled/merged)
    bad = set(r[0][6] for r in res if r[4] in ('misfiled', 'no-row'))
    jd = collections.Counter()
    for r in res:
        if r[4] == 'differs' and r[0][6] not in bad:
            jd[judge(r[2], r[3], r[1])] += 1
    print('  "differs" in correctly-filed rows, by who is evidently wrong: %s'
          % dict(jd))
    n1, f1, n2, f2 = sensitivity(cells, book)
    print('  SENSITIVITY: citations printed nowhere: %d/%d flagged; a '
          "neighbour's Gospel moved in: %d/%d flagged" % (f1, n1, f2, n2))
    t, h = control_euch()
    print('\nCONTROL -- eucharistic-lectionary.md vs the 2007 RCL pages 889-932: '
          '%d/%d citations found near their occasion (%.1f%%). Not a 1979 '
          'witness; the rate measures the RCL, not the cell.' % (h, t, 100.0 * h / max(1, t)))
    t, h, e = control_cal()
    print('CONTROL -- calendar.md notes vs the 2008 calendar pages 19-30: %d/%d '
          'found verbatim (%.1f%%); %d dates the 1979 cell leaves empty.'
          % (h, t, 100.0 * h / max(1, t), e))
    if show:
        print('\nMISMATCHES (cell line, occasion, column: cell -> book, verdict)')
        for r in res:
            if r[4] in OK:
                continue
            c = r[0]
            extra = (' [%s; %s]' % (differs_class(r[2], r[3]),
                                     judge(r[2], r[3], r[1]))) if (
                r[4] == 'differs' and r[2] and r[3]) else ''
            print('  L%-5d %s / %s / %s  %s: %r -> %r  %s%s' % (
                c[6], c[0], (c[1] or '')[:30], c[2], r[1], r[2], r[3], r[4], extra))
        print('\nMARKS / PUNCT / GLYPH (same citation, different marks):')
        for r in res:
            if r[4] in ('marks', 'punct', 'glyph'):
                print('  L%-5d %s: %r -> %r  %s' % (r[0][6], r[1], r[2], r[3], r[4]))
        print('\nBOOK ROWS NO CELL ROW CLAIMS:')
        for b in missing:
            print('  p%d %s / %s / %s' % (b[6], b[0], b[1], b[2]))


if __name__ == '__main__':
    main('--list' in sys.argv)
