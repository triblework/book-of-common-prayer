"""w25_witness.py -- Wave 25's changes to the cells, as data plus one transform.
Authoring-only. Applied file -> file by `python3 ingest/w25_witness.py`
(idempotent); `--check` reports what it would change and writes nothing.

1. R24 (maintainer, 2026-11-06: "Curly, all cells"): every apostrophe in
   every cell is U+2019. `curl(text)` sets it, outside <!-- --> comments
   (whose straight single quotes delimit VERIFY keys). THE RULE that tells an
   apostrophe from a quotation mark (R24 (a)): a straight mark directly after
   a letter is an apostrophe, whatever follows (don't; Apostles' Creed); after
   a digit, it is one when a letter follows (1500's); a mark NOT after a
   letter or digit is a quotation mark and is left alone (1979's ten pairs of
   single quotation marks; the stray before "deliver" in three Advent 4
   collects). No closing quotation mark in the corpus follows a letter
   (checked by w25_gates: every quotation mark left is paired, or listed).

2. R23/R25: the possessive of small-capital LORD, where its s is read from a
   book. POSSESSIVES lists every such possessive in the 1892, 1928 and 1979
   cells -- the ones that change and the ones that were checked and stay --
   each with the case of its s as the book prints it and the evidence:

     1892  the 11 Psalter verses (Wave 24, w24_eye.txt) and the Churching
           office's psalm (this wave, w25_eye.txt): lower-case s;
     1928  the 11 Psalter verses: a small-capital S in both printings, which
           R23's encoding sets as S -- no change (w25_eye.txt);
     1979  13 places: the face of the s's font run in Church Publishing's file
           (w25_fontruns.py), with an eye read of the rendered page agreeing
           (w25_eye.txt) -- R11 reopened for the possessive (R25).

   A possessive is located by the words before it, exactly once in its cell;
   only the case of its s is set. Its line at the base is recorded and checked.

Order: the possessive keys, then curl() -- they touch different characters,
so the order does not matter, and w25_gates proves the composition: Wave 25's
base cells (BASE, by full SHA, R18) through apply() equal the cells.
"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WB = os.path.dirname(HERE)
BASE = '4bdec46ea27a94e17d74b7b448f4973351d6dc33'   # authoring at the start of Wave 25
APOS = '’'
COMMENT = re.compile(r'<!--.*?-->', re.S)
POSS = re.compile(r"(?<![A-Za-z])LORD['’]([Ss])(?![A-Za-z])")


def _curl_span(t):
    out = []
    for i, c in enumerate(t):
        if c == "'":
            a = t[i - 1] if i else ''
            b = t[i + 1] if i + 1 < len(t) else ''
            if a.isalpha() or (a.isdigit() and b.isalpha()):
                c = APOS
        out.append(c)
    return ''.join(out)


def curl(text):
    """R24: every apostrophe outside comments -> U+2019; quotation marks stay."""
    out, k = [], 0
    for m in COMMENT.finditer(text):
        out.append(_curl_span(text[k:m.start()]))
        out.append(m.group(0))
        k = m.end()
    out.append(_curl_span(text[k:]))
    return ''.join(out)


def straight_apostrophes(text):
    """-> [(offset, context)] of straight marks the rule calls apostrophes
    (outside comments). Empty for a cell that follows R24."""
    masked = COMMENT.sub(lambda m: '\0' * len(m.group(0)), text)
    cur = _curl_span(masked)
    return [(i, text[max(0, i - 20):i + 10]) for i, (a, b) in enumerate(zip(masked, cur)) if a != b]


# (edition, cell, line, the words before, the s as the book prints it, evidence)
# 'line' is the line at Wave 25's base; 'before' must end exactly where LORD begins.
P1892 = [(ps_v, 's', 'w24_eye.txt (scan)') for ps_v in
         ('11:4', '22:28', '24:1', '27:16', '56:10', '113:3', '115:16', '116:16', '118:23',
          '137:4', '147:11')]
POSSESSIVES = [
    # 1892: the Churching office's psalm -- CHANGES (R23)
    ('1892', 'occasional-offices/churching.md', 29, 'the courts of the ', 's',
     '1892 Standard Book scan p331 (book p. 303), eye: lower-case s (w25_eye.txt)'),
    # 1979: font run + eye (R25). Nine CHANGE S -> s; Burial CHANGES s -> S;
    # three are checked and stay S.
    ('1979', 'psalter/psalms-1-50.md', 307, 'oly temple; : the ', 's', 'PDF p596 Sabon-Roman'),
    ('1979', 'psalter/psalms-1-50.md', 707, 'l be known as the ', 's', 'PDF p612 Sabon-Roman'),
    ('1979', 'psalter/psalms-1-50.md', 731, ' The earth is the ', 's', 'PDF p613 Sabon-Roman'),
    ('1979', 'psalter/psalms-1-50.md', 863, 'rry and await the ', 's', 'PDF p619 Sabon-Roman'),
    ('1979', 'psalter/psalms-1-50.md', 879, 'erstanding of the ', 's', 'PDF p619 Sabon-Roman'),
    ('1979', 'psalter/psalms-1-50.md', 1051, '11 But the ', 's', 'PDF p626 Sabon-Roman'),
    ('1979', 'psalter/psalms-51-100.md', 897, '8 For in the ', 's', 'PDF p691 Sabon-Roman'),
    ('1979', 'psalter/psalms-101-150.md', 745, 'of heavens is the ', 'S', 'PDF p758 Sabon-RomanSC'),
    ('1979', 'psalter/psalms-101-150.md', 787, 'the courts of the ', 'S', 'PDF p760 Sabon-RomanSC'),
    ('1979', 'psalter/psalms-101-150.md', 845, '23 This is the ', 's', 'PDF p762 Sabon-Roman'),
    ('1979', 'psalter/psalms-101-150.md', 1685, 'shall we sing the ', 's', 'PDF p792 Sabon-Roman'),
    ('1979', 'occasional-offices/churching.md', 93, 'the courts of the ', 'S', 'PDF p442 Sabon-RomanSC'),
    ('1979', 'occasional-offices/burial.md', 235, 'O tarry thou the ', 'S', 'PDF p478 Sabon-RomanSC'),
]
# 1928: the eleven Psalter verses, small-capital S in both printings (no change).
P1928 = ('11:4', '22:28', '24:1', '27:16', '56:10', '113:3', '115:16', '116:16', '118:23',
         '137:4', '147:11')


def cell_path(ed, rel):
    return os.path.join(WB, 'editions', ed, rel)


def set_possessives(ed, rel, text):
    """Apply the POSSESSIVES keys for one cell -> (text, [changes]). A key is
    located by the words before it, exactly once in the WHOLE cell (so a gate
    may apply it to a cell with its inline flags set aside); its recorded line
    is checked by w25_gates against Wave 25's base, not used to locate it."""
    changes = []
    for e, r, n, before, want, ev in POSSESSIVES:
        if (e, r) != (ed, rel):
            continue
        hits = [m for m in POSS.finditer(text) if text[:m.start()].endswith(before)]
        if len(hits) != 1:
            raise SystemExit('%s/%s: %d possessives after %r (stale key)' % (ed, rel, len(hits), before))
        m = hits[0]
        if m.group(1) != want:
            text = text[:m.start(1)] + want + text[m.end(1):]
            changes.append((text.count('\n', 0, m.start()) + 1, m.group(1), want, ev))
    return text, changes


def apply(ed, rel, text):
    """Wave 25 on one cell's text: the possessive keys, then R24's curl()."""
    text, _ = set_possessives(ed, rel, text)
    return curl(text)


def cells(root=WB):
    for p in sorted(glob.glob(os.path.join(root, 'editions', '*', '**', '*.md'), recursive=True)):
        rel = os.path.relpath(p, os.path.join(root, 'editions'))
        ed, r = rel.split('/', 1)
        yield ed, r, p


def main():
    check = '--check' in sys.argv
    n_files = n_curl = 0
    poss = []
    for ed, rel, p in cells():
        t = open(p, encoding='utf-8').read()
        t2, ch = set_possessives(ed, rel, t)
        poss += [(ed, rel) + c for c in ch]
        t3 = curl(t2)
        k = sum(1 for a, b in zip(t2, t3) if a != b)
        if t3 != t:
            n_files += 1
            n_curl += k
            if not check:
                open(p, 'w', encoding='utf-8').write(t3)
    for c in poss:
        print('possessive  %s/%s:%d  %s -> %s  (%s)' % c)
    print('%s: %d apostrophes set to U+2019 in %d cells; %d possessives set' % (
        'would change' if check else 'changed', n_curl, n_files, len(poss)))


if __name__ == '__main__':
    main()
