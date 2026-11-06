"""w25_gates.py -- Wave 25's gates (R24 apostrophes, R25 possessives); authoring-only.

  1. R24. No cell's text (outside <!-- --> comments) carries a straight mark
     that the rule (w25_witness) calls an apostrophe -- so no cell mixes the
     two forms either.
  2. QUOTATION MARKS. Every straight single mark left in cell text is a
     quotation mark: in each cell they alternate open (before a letter) /
     close (after punctuation) and pair up, except the declared strays
     (STRAYS). Every U+2018 is declared too. A closing quotation mark after a
     letter -- which the rule would have taken for a possessive -- fails here.
  3. CONTAINMENT. Every cell at Wave 25's base (BASE, by full SHA; R18),
     through w25_witness.apply, equals the cell in the work tree; and the two
     differ ONLY in apostrophe characters and the declared possessive s's
     (character for character, same length).
  4. POSSESSIVES. Every possessive of small-capital LORD in the 1892, 1928 and
     1979 cells has the case of its book: 1892 lower-case s (12), 1928 S (11),
     1979 the face of its s's font run in Church Publishing's file (13; re-read
     from the cached PDF by w25_fontruns), each key's line as recorded at the
     base, and every one in the eye record (w25_eye.txt) with the same reading.
  5. NORMALIZATION. tools/normalize.py's word pattern reads a word with U+2019
     as one word, and every cell normalizes to the same text as its base cell
     (possessive keys applied) apart from the apostrophe character.

    python3 ingest/w25_gates.py              # the gates
    python3 ingest/w25_gates.py --selftest   # each gate fails on a case built to break it
"""
import collections, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, 'tools'))
import w25_witness as W

# (edition/cell, the words before the mark) -- marks left as they are (R24 (b))
STRAYS = [('1789/collects-epistles-gospels/advent-4.md', 'speedily help and '),
          ('1892/collects-epistles-gospels/advent-4.md', 'speedily help and '),
          ('1928/collects-epistles-gospels/advent-4.md', 'speedily help and ')]
LEFT = [('1928/occasional-offices/public-baptism.md', 'let us ')]       # U+2018
EXPECT = {'1892': ('s', 12), '1928': ('S', 11), '1979': (None, 13)}
findings = []


def check(label, ok, detail=''):
    print('%s %s %s' % ('ok  ' if ok else 'FAIL', label, '' if ok else '<- %s' % (detail,)))
    if not ok:
        findings.append(label)


def base(ed, rel):
    r = subprocess.run(['git', 'show', '%s:editions/%s/%s' % (W.BASE, ed, rel)], cwd=WT,
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def masked(t):
    return W.COMMENT.sub(lambda m: '\0' * len(m.group(0)), t)


def quote_marks(t):
    """-> [(offset, 'open'|'close'|'?')] of straight marks left in cell text."""
    m = masked(t)
    out = []
    for i, c in enumerate(m):
        if c != "'":
            continue
        a = m[i - 1] if i else ' '
        b = m[i + 1] if i + 1 < len(m) else ' '
        if b.isalpha() and not a.isalnum():
            out.append((i, 'open'))
        elif not a.isalnum() and not b.isalnum():
            out.append((i, 'close'))
        else:
            out.append((i, '?'))
    return out


def gate_texts(texts, bases, runs_faces):
    """All five gates over {(ed, rel): text}; -> nothing (records findings)."""
    # 1. R24
    bad = [(ed + '/' + rel, W.straight_apostrophes(t)[0][1]) for (ed, rel), t in texts.items()
           if W.straight_apostrophes(t)]
    n_curly = sum(masked(t).count(W.APOS) for t in texts.values())
    check('R24: no straight apostrophe in any cell (%d cells; %d apostrophes, all U+2019)'
          % (len(texts), n_curly), not bad, bad[:3])
    # 2. quotation marks
    qbad, nq = [], 0
    for (ed, rel), t in texts.items():
        key = ed + '/' + rel
        qs = quote_marks(t)
        stray = [i for i, k in qs if any(key == s and t[:i].endswith(w) for s, w in STRAYS)]
        rest = [(i, k) for i, k in qs if i not in stray]
        nq += len(rest)
        if [k for _i, k in rest] != ['open', 'close'] * (len(rest) // 2) or len(rest) % 2:
            qbad.append((key, [(k, t[max(0, i - 15):i + 5]) for i, k in rest][:4]))
        for i, c in enumerate(masked(t)):
            if c == '‘' and not any(key == s and t[:i].endswith(w) for s, w in LEFT):
                qbad.append((key, 'undeclared U+2018 at %d' % i))
    found = sum(1 for (ed, rel), t in texts.items() for s, w in STRAYS if ed + '/' + rel == s
                and any(t[:i].endswith(w) for i, _k in quote_marks(t)))
    check('quotation marks: %d straight marks left, all paired open/close; %d declared strays'
          % (nq, found), not qbad and found == len(STRAYS), qbad[:3])
    # 3. containment
    moved, extra = [], []
    keyed = {(e, r): [] for e, r, *_ in W.POSSESSIVES}
    for (ed, rel), t in texts.items():
        b = bases.get((ed, rel))
        if b is None:
            moved.append((ed, rel, 'no base cell'))
            continue
        if W.apply(ed, rel, b) != t:
            moved.append((ed, rel, 'base + Wave 25 != cell'))
        if len(b) != len(t):
            extra.append((ed, rel, 'length'))
            continue
        for i, (x, y) in enumerate(zip(b, t)):
            if x == y or (x, y) == ("'", W.APOS):
                continue
            if (ed, rel) in keyed and {x, y} == {'s', 'S'} and t[max(0, i - 5):i] in ('LORD’',):
                keyed[(ed, rel)].append(i)
                continue
            extra.append((ed, rel, i, x, y))
    n_keys = sum(len(v) for v in keyed.values())
    check('containment: base %s + Wave 25 == every cell (%d cells)' % (W.BASE[:8], len(texts)),
          not moved, moved[:3])
    check('nothing else moved: only apostrophes and %d possessive s\'s differ from the base'
          % n_keys, not extra and n_keys == 11, extra[:3])
    # 4. possessives
    eye = {}
    for ln in open(os.path.join(HERE, 'w25_eye.txt'), encoding='utf-8'):
        if ln.startswith('#') or not ln.strip():
            continue
        f = ln.rstrip('\n').split('\t')
        eye[(f[1], f[0])] = f[4]
    pbad = []
    for ed, (want, n) in EXPECT.items():
        got = [(rel, m) for (e, rel), t in texts.items() if e == ed
               for m in W.POSS.finditer(W.COMMENT.sub('', t))]
        if len(got) != n:
            pbad.append((ed, 'count %d, want %d' % (len(got), n)))
        if want:
            wrong = [rel for rel, m in got if m.group(1) != want or m.group(0)[4] != W.APOS]
            if wrong:
                pbad.append((ed, 'case/form', wrong[:3]))
    for e, rel, n, before, want, ev in W.POSSESSIVES:
        t = texts[(e, rel)]
        hits = [m for m in W.POSS.finditer(t) if t[:m.start()].endswith(before)]
        if len(hits) != 1 or hits[0].group(1) != want:
            pbad.append((e, rel, before, 'cell'))
        bl = (bases.get((e, rel)) or '').split('\n')
        if n > len(bl) or not any(bl[n - 1][:m.start()].endswith(before)
                                   for m in W.POSS.finditer(bl[n - 1])):
            pbad.append((e, rel, n, 'line at base'))
        if e == '1979':
            face = runs_faces.get((rel, before))
            if face is None or ('S' if face.endswith('RomanSC') else 's') != want \
                    or face not in ev:
                pbad.append((e, rel, before, 'font run %s' % face))
    # every key and every 1928 verse is in the eye record, with the same reading
    for e, rel, n, before, want, ev in W.POSSESSIVES:
        if 'psalter' in rel:
            place = runs_faces.get(('page', rel, before))
        elif e == '1892':
            place = rel.split('/')[-1].replace('.md', '')
        else:
            place = '%s:%d' % (rel.split('/')[-1].replace('.md', ''), n)
        r = eye.get((e, place))
        if r is None or r[-1] != want:
            pbad.append((e, rel, before, 'eye record %s' % place))
    for v in W.P1928:
        r = eye.get(('1928', 'Ps ' + v))
        if r is None or r[-1] != 'S':
            pbad.append(('1928', v, 'eye record'))
    check('possessives: 1892 LORD’s x12, 1928 LORD’S x11, 1979 13 by font run and eye',
          not pbad, pbad[:4])
    # 5. normalization
    import normalize as N
    rules = N.load_rules(__import__('pathlib').Path(WT, 'tools', 'normalization_rules.yaml'))
    nz = N.Normalizer(rules)
    one = N._WORD_RE.fullmatch('LORD’s') is not None
    nbad = []
    for (ed, rel), t in texts.items():
        b = bases.get((ed, rel))
        if b is None:
            continue
        b2, _ = W.set_possessives(ed, rel, b)
        if nz.normalize_text(t).replace(W.APOS, "'") != nz.normalize_text(b2).replace(W.APOS, "'"):
            nbad.append((ed, rel))
    check('normalization: a U+2019 word is one word, and every cell normalizes as its base '
          'did, apart from the character', one and not nbad, (one, nbad[:3]))


def faces():
    """{(rel, before): face of the s} and {('page', rel, before): eye-record place} for 1979."""
    import w25_fontruns as F
    R = F.runs()
    pages = {int(k): F.chars(v) for k, v in R.items()}
    out = {}
    for e, rel, n, before, want, ev in W.POSSESSIVES:
        if e != '1979':
            continue
        pg = int(re.search(r'PDF p(\d+)', ev).group(1))
        t, f = pages[pg]
        want_b = F.letters(before)[-10:]
        hit = [i for i in (m.start() for m in re.finditer(r"Lord['’]s", t))
               if F.letters(t[max(0, i - 40):i]).endswith(want_b)
               and all('RomanSC' in f[j] for j in range(i + 1, i + 4))]
        out[(rel, before)] = F.short(f[hit[0] + 5]) if len(hit) == 1 else None
        if 'psalter' in rel:
            # the eye record names Psalter places by verse; find it from the cell
            t2 = open(W.cell_path(e, rel), encoding='utf-8').read().split('\n')
            ps = v = None
            for i, ln in enumerate(t2[:n]):
                m = re.match(r'^## Psalm (\d+)', ln)
                if m:
                    ps = int(m.group(1))
            mv = re.match(r'^(\d+) ', t2[n - 1])
            out[('page', rel, before)] = 'Ps %d:%s' % (ps, mv.group(1) if mv else '1')
    return out


def load():
    texts, bases = {}, {}
    for ed, rel, p in W.cells():
        texts[(ed, rel)] = open(p, encoding='utf-8').read()
        bases[(ed, rel)] = base(ed, rel)
    return texts, bases


def main():
    texts, bases = load()
    gate_texts(texts, bases, faces())
    print('w25 gates: %d anomalies' % len(findings))
    return 1 if findings else 0


def selftest():
    texts, bases = load()
    fc = faces()
    cases = []
    k = ('1892', 'psalter/psalms-1-50.md')
    t = dict(texts); t[k] = texts[k].replace(W.APOS, "'", 1)
    cases.append(('a straight apostrophe in one cell', t, {'R24'}))
    k2 = ('1979', 'psalter/psalms-1-50.md')
    t = dict(texts); t[k2] = texts[k2].replace('LORD’s', 'LORD’S', 1)
    cases.append(('a 1979 possessive set against its font run', t, {'possessives', 'containment'}))
    k3 = ('1662', 'daily-office/morning-prayer.md')
    t = dict(texts); t[k3] = texts[k3].replace(' and ', ' und ', 1)
    cases.append(('a word changed', t, {'containment', 'nothing else'}))
    k4 = ('1979', 'daily-office/morning-prayer.md')
    t = dict(texts); t[k4] = texts[k4].replace("praise.'", 'praise.', 1)
    cases.append(('a quotation mark dropped', t, {'quotation'}))
    ok = True
    for name, tt, want in cases:
        del findings[:]
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            gate_texts(tt, bases, fc)
        hit = {w for w in want if any(f.startswith(w) or w in f for f in findings)}
        print('selftest %-48s fails: %s' % (name, sorted(hit) == sorted(want)))
        ok &= sorted(hit) == sorted(want)
    del findings[:]
    print('selftest: %s' % ('all gates sensitive' if ok else 'NOT SENSITIVE'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(selftest() if '--selftest' in sys.argv else main())
