"""w23_book.py -- the 1979 witness as a token stream, and a paragraph aligner.

Shared by w23_survey.py, w23_flags.py and w23_tables.py. Read-only: nothing
here writes a cell.

THE WITNESS is Church Publishing's PDF of the 1979 book (w19_witness_text.py
extracts its text layer page by page; PDF page == book page). Three things
this module does to that text, each because the plain extraction would make
a correct cell look wrong:

  * RUNNING FEET. The last line of a page is its running foot ("Morning
    Prayer II   97", "Psalm 9   598") or a producer's slug ("RCL pages for
    BCP  4/13/07 ...", "cpg-bcp-calendar.indd ..."). Dropped, so a paragraph
    that straddles a page is not broken by them.
  * PARALLEL COLUMNS. About twenty prose pages set two texts side by side --
    the Lord's Prayer traditional | contemporary, chiefly. The plain
    extraction interleaves them line by line. Those blocks are rebuilt from
    pypdf's layout-mode extraction (cached, gitignored, in ingest/.cache/),
    left column then right, and used ONLY where the rebuilt page has exactly
    the plain page's bag of words -- so no word is gained or lost by it.
  * FOLDING. Comparison is on words: case-folded (R11: the text layer
    cannot say LORD from Lord), accents and ligatures folded (ae for the
    ligature, fi for its ligature), quotes, dashes, the pointing asterisk
    and the repo's mediant colon all dropped. Punctuation is compared in a
    separate, second pass (punct_ops), never mixed into the word diff.
"""
import collections
import difflib
import glob
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w19_witness_text as WTX

LAYOUT = os.path.join(HERE, '.cache', 'w23_layout.json')   # gitignored
# Pages that are tables (the 2008 Calendar insert, the Golden Number/Easter
# tables, the 2007 RCL insert, the Daily Office Lectionary): never
# column-split -- the table comparison reads them its own way.
TABLE_PAGES = set(range(19, 31)) | set(range(875, 1002))
# Producer slugs that mark pages substituted after 1979 (see w23_tables).
SLUG = re.compile(r'RCL pages for BCP|cpg-bcp-calendar\.indd')
FOOT = re.compile(r'^\s*(\d+\s{2,}\S.*|.*\S\s{2,}\d+)\s*$')


def layout_pages():
    if os.path.exists(LAYOUT):
        return {int(k): v for k, v in json.load(open(LAYOUT)).items()}
    import pypdf
    r = pypdf.PdfReader(WTX.SRC)
    out = {}
    for i, p in enumerate(r.pages, 1):
        try:
            out[i] = p.extract_text(extraction_mode='layout') or ''
        except Exception:                          # an empty page
            out[i] = ''
    os.makedirs(os.path.dirname(LAYOUT), exist_ok=True)
    json.dump(out, open(LAYOUT, 'w'))
    return out


def strip_furniture(text):
    """Drop the producer slug and the running foot (the last real line)."""
    lines = [l for l in text.split('\n') if not SLUG.search(l)]
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and FOOT.match(lines[-1]):
        lines.pop()
    return '\n'.join(lines)


def fold_chars(t):
    t = (t.replace('æ', 'ae').replace('Æ', 'Ae')
          .replace('ﬁ', 'fi').replace('ﬂ', 'fl')
          .replace('’', "'").replace('‘', "'")
          .replace('“', '"').replace('”', '"'))
    t = unicodedata.normalize('NFKD', t)
    return ''.join(c for c in t if not unicodedata.combining(c))


def words(t):
    """-> the folded word tokens of a text."""
    return re.findall(r'[a-z0-9]+', fold_chars(t).lower())


WORD = re.compile(r'[^\W_]+')


def spans(t):
    """-> [(folded word, start, end)] over the ORIGINAL text t, giving the
    same word list as words(t) but with each word's character span, so a
    correction can be cut from (and put back into) the real text."""
    out = []
    for m in WORD.finditer(t):
        for w in re.findall(r'[a-z0-9]+', fold_chars(m.group()).lower()):
            out.append((w, m.start(), m.end()))
    return out


PTOK = re.compile(r'[a-z0-9]+|[,;:.?!()\[\]]|\*')


def ptoks(t, cell=False):
    """-> words AND punctuation, for the second (punctuation) pass. The
    mediant -- the book's asterisk, the repo's spaced colon -- becomes one
    token, '*', on both sides; markdown emphasis in a cell is removed first."""
    t = fold_chars(t).lower()
    if cell:
        t = re.sub(r'\*+(?=\S)|(?<=\S)\*+', '', t)   # **Label.** *or*
        t = t.replace(' : ', ' * ')
    return PTOK.findall(t)


def _split_columns(lay):
    """Rebuild 2-column blocks of a layout page as left-then-right. Returns
    None if the page has no such block."""
    lines = lay.split('\n')
    votes = collections.Counter()
    for l in lines:
        for m in re.finditer(r'\S( {5,})\S', l):
            if m.start(1) > 12:
                votes[m.end(1)] += 1
    if not votes:
        return None
    # the column's left edge: the leftmost start that several lines share
    starts = sorted(x for x, n in votes.items() if n >= 2)
    if not starts:
        return None
    x = starts[0]

    def splits(l):
        if len(l) <= x:
            return None
        left, right = l[:x], l[x:]
        if not right.strip() or not left.strip():
            return None
        if left[-1] != ' ' or not re.search(r' {3,}$', left):
            return None
        return left.rstrip(), right.strip()

    out, block, changed = [], [], False
    for l in lines + ['']:
        s = splits(l)
        if s:
            block.append(s)
            continue
        if len(block) >= 2:
            out.extend(b[0] for b in block)
            out.extend(b[1] for b in block)
            changed = True
        else:
            out.extend(a + '   ' + b for a, b in block)
        block = []
        out.append(l)
    return '\n'.join(out) if changed else None


_PAGES = None


def pages():
    """-> {page: text} with feet dropped and parallel columns rebuilt."""
    global _PAGES
    if _PAGES is not None:
        return _PAGES
    plain = WTX.pages()
    lay = layout_pages()
    out, rebuilt = {}, []
    for k in sorted(plain):
        t = plain[k]
        if k not in TABLE_PAGES and lay.get(k):
            s = _split_columns(lay[k])
            if s is not None and (collections.Counter(words(strip_furniture(s)))
                                  == collections.Counter(words(strip_furniture(t)))):
                t = s
                rebuilt.append(k)
        out[k] = strip_furniture(t)
    _PAGES = out
    pages.rebuilt = rebuilt
    return out


_STYLE = None


def styles():
    """-> {page: [font of each character of pages()[page]] or None}. The
    PDF's runs name their font (Sabon-Roman text, Sabon-Italic rubrics and
    speaker names, Sabon-RomanSC small capitals, Sabon-Bold titles); the
    non-space characters of the runs are matched one for one against the
    page text. A page whose order cannot be matched (a rebuilt
    parallel-column page) gets None -- no style is guessed there."""
    global _STYLE
    if _STYLE is not None:
        return _STYLE
    cache = os.path.join(HERE, '.cache', 'w23_styles.json')
    if os.path.exists(cache):
        raw = json.load(open(cache))
    else:
        import pypdf
        r = pypdf.PdfReader(WTX.SRC)
        raw = {}
        for i, p in enumerate(r.pages, 1):
            runs = []

            def v(text, cm, tm, fd, fs):
                if text:
                    runs.append([((fd or {}).get('/BaseFont') or '?')
                                 .lstrip('/'), text])
            try:
                p.extract_text(visitor_text=v)
            except Exception:
                runs = []
            raw[str(i)] = runs
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        json.dump(raw, open(cache, 'w'))
    pg = pages()
    out = {}
    for k, t in pg.items():
        runs = raw.get(str(k), [])
        chars = [(f, c) for f, txt in runs for c in txt if not c.isspace()]
        fonts = [None] * len(t)
        j = 0
        ok = True
        for i, c in enumerate(t):
            if c.isspace():
                continue
            while j < len(chars) and chars[j][1] != c:
                # tolerate a few characters the runs carry that the page
                # text does not (feet, slugs are at the end anyway)
                j += 1
                if j - i > 200:
                    break
            if j >= len(chars) or chars[j][1] != c:
                ok = False
                break
            fonts[i] = chars[j][0]
            j += 1
        out[k] = fonts if ok else None
    _STYLE = out
    return out


class Book:
    """The whole book as one word stream, with each word's page."""

    def __init__(self, n=4, skip=()):
        pg = pages()
        self.tok, self.page, self.span = [], [], []
        for k in sorted(pg):
            if k in skip:
                continue
            sp = spans(pg[k])
            w = [x[0] for x in sp]
            assert w == words(pg[k]), 'span tokenizer disagrees on p%d' % k
            self.tok.extend(w)
            self.page.extend([k] * len(w))
            self.span.extend((x[1], x[2]) for x in sp)
        # the punctuation stream, and for each word its index in it
        self.ptok, self.wpos = [], []
        for k in sorted(pg):
            if k in skip:
                continue
            for t in ptoks(pg[k]):
                if t[0].isalnum():
                    self.wpos.append(len(self.ptok))
                self.ptok.append(t)
        assert len(self.wpos) == len(self.tok)
        self.joined = ' ' + ' '.join(self.tok) + ' '
        self.n = n
        self.idx = collections.defaultdict(list)
        for i in range(len(self.tok) - n + 1):
            self.idx[tuple(self.tok[i:i + n])].append(i)
        self.ngrams = set(self.idx)

    def candidates(self, toks, top=3, maxfreq=60, within=None):
        n = self.n
        vote = collections.Counter()
        for i in range(len(toks) - n + 1):
            pos = self.idx.get(tuple(toks[i:i + n]))
            if not pos or len(pos) > maxfreq:
                continue
            for p in pos:
                if within and not within[0] <= self.page[p] <= within[1]:
                    continue
                vote[(p - i) // 8] += 1
        return [b * 8 for b, _v in vote.most_common(top)]

    def align(self, toks, within=None):
        """-> best (ratio, start, end, opcodes) of toks against the book, or
        None if no anchor is found. opcodes: (tag, cell words, book words,
        book position, cell index from, cell index to). The best candidate is
        the one with the most words matched; stray one- and two-word matches
        at either end of the window (a far-off "amen") are trimmed before the
        diff is taken."""
        best = None
        self.exact = []                 # every window the words match exactly
        for off in self.candidates(toks, top=8, within=within):
            got = self.align_window(toks, max(0, off - 30),
                                    min(len(self.tok), off + len(toks) + 30))
            if got is None:
                continue
            key, res = got
            if res[0] == 1.0 and (res[1], res[2]) not in self.exact:
                self.exact.append((res[1], res[2]))
            if best is None or key > best[0]:
                best = (key, res)
        return best[1] if best else None

    def align_window(self, toks, lo, hi):
        """Diff toks against book words [lo, hi). -> ((matched, ratio),
        (ratio, start, end, opcodes)) or None."""
        win = self.tok[lo:hi]
        sm = difflib.SequenceMatcher(None, toks, win, autojunk=False)
        blocks = [b for b in sm.get_matching_blocks() if b.size]
        while len(blocks) > 1 and blocks[0].size < 3 and (
                blocks[1].b - blocks[0].b - blocks[0].size
                > 2 * (blocks[1].a - blocks[0].a - blocks[0].size) + 3):
            blocks.pop(0)
        while len(blocks) > 1 and blocks[-1].size < 3 and (
                blocks[-1].b - blocks[-2].b - blocks[-2].size
                > 2 * (blocks[-1].a - blocks[-2].a - blocks[-2].size) + 3):
            blocks.pop()
        if not blocks:
            return None
        s = lo + blocks[0].b
        e = lo + blocks[-1].b + blocks[-1].size
        # a short unmatched head or tail (a typo in the first or last
        # word) is set against the book's words there, not left over
        head = blocks[0].a
        tail = len(toks) - blocks[-1].a - blocks[-1].size
        if 0 < head <= 3:
            s = max(0, s - head)
        if 0 < tail <= 3:
            e = min(len(self.tok), e + tail)
        sm2 = difflib.SequenceMatcher(None, toks, self.tok[s:e],
                                      autojunk=False)
        r = sm2.ratio()
        matched = sum(b.size for b in sm2.get_matching_blocks())
        ops = [(t, toks[i1:i2], self.tok[s + j1:s + j2], s + j1, i1, i2)
               for t, i1, i2, j1, j2 in sm2.get_opcodes()]
        return (matched, r), (r, s, e, ops)

    def punct(self, toks, s, e):
        """Punctuation differences of a paragraph whose WORDS match the book
        at words [s, e). -> [(tag, cell tokens, book tokens)]"""
        a = self.wpos[s]
        b = self.wpos[e - 1] + 1
        # widen by punctuation only -- never into the next or previous word
        lo, hi = a, b
        while lo > 0 and a - lo < 2 and not self.ptok[lo - 1][0].isalnum():
            lo -= 1
        while (hi < len(self.ptok) and hi - b < 2
               and not self.ptok[hi][0].isalnum()):
            hi += 1
        win = self.ptok[lo:hi]
        sm = difflib.SequenceMatcher(None, toks, win, autojunk=False)
        ops = sm.get_opcodes()
        out = []
        for i, (t, i1, i2, j1, j2) in enumerate(ops):
            if t == 'equal':
                continue
            c, w = toks[i1:i2], win[j1:j2]
            # the window's own margin before the first word / after the last
            if t == 'insert' and (i == 0 or i == len(ops) - 1):
                continue
            out.append((t, c, w, lo + j1))
        return out

    def find_short(self, toks):
        """A short paragraph (no usable 4-gram anchor): is the word sequence
        in the book at all? -> word position or None"""
        i = self.joined.find(' ' + ' '.join(toks) + ' ')
        if i < 0:
            return None
        return self.joined[:i].count(' ')

    def raw(self, a, b):
        """The book's own text from word a to word b-1 (b > a), whitespace
        made single spaces; spans pages if it must (feet already dropped)."""
        pg = pages()
        out, k0 = [], self.page[a]
        start = self.span[a][0]
        for k in range(self.page[a], self.page[b - 1] + 1):
            t = pg.get(k, '')
            s0 = start if k == self.page[a] else 0
            e0 = self.span[b - 1][1] if k == self.page[b - 1] else len(t)
            out.append(t[s0:e0])
        return re.sub(r'\s+', ' ', ' '.join(out)).strip()

    def raw_between(self, a, b):
        """The book's exact text after word a and before word b (b > a),
        across a page turn if need be (feet already dropped)."""
        pg = pages()
        ka, kb = self.page[a], self.page[b]
        if ka == kb:
            return pg[ka][self.span[a][1]:self.span[b][0]]
        out = [pg[ka][self.span[a][1]:]]
        for k in range(ka + 1, kb):
            out.append(pg.get(k, ''))
        out.append(pg[kb][:self.span[b][0]])
        return '\n'.join(out)

    def between(self, a):
        """The book's text between word a and word a+1 (its separator)."""
        pg = pages()
        if self.page[a] == self.page[a + 1]:
            t = pg[self.page[a]]
            return t[self.span[a][1]:self.span[a + 1][0]]
        return (pg[self.page[a]][self.span[a][1]:] + ' ' +
                pg[self.page[a + 1]][:self.span[a + 1][0]])

    def context(self, pos, before=4, after=4):
        return ' '.join(self.tok[max(0, pos - before):pos + after])


# --- cells ---------------------------------------------------------------

VERIFY = re.compile(r'<!-- VERIFY.*?-->', re.S)


def paragraphs(path):
    """-> [(first line number, kind, text)] for a cell. A paragraph is a run
    of non-blank lines; VERIFY comments are removed (line numbers kept).
    kind: heading | rubric | label | row | prose."""
    raw = open(path, encoding='utf-8').read()
    # blank out VERIFY comments but keep their newlines, so numbers hold
    raw = VERIFY.sub(lambda m: '\n' * m.group(0).count('\n'), raw)
    out, cur, start = [], [], None
    for i, line in enumerate(raw.split('\n') + [''], 1):
        if line.strip():
            if not cur:
                start = i
            cur.append(line.strip())
            continue
        if cur:
            text = ' '.join(cur)
            if text.startswith('#'):
                kind = 'heading'
            elif text.startswith('>'):
                kind = 'rubric'
            elif ' | ' in text:
                kind = 'row'
            elif re.match(r'^\*\*[^*]+\*\*', text):
                kind = 'label'
            else:
                kind = 'prose'
            out.append((start, kind, text))
            cur = []
    return out


def cell_text(text, kind):
    """The words a paragraph contributes, with the repo's own furniture
    removed: heading hashes, the rubric marker, a speaker label, the mediant
    colon."""
    t = text
    # the repo's speaker label (**People.**, and the malformed **People* :
    # that 85 lines carry) is the book's roman label with no stop
    # (a one-letter label, Q. A. V. R., keeps its stop, as the book does)
    t = re.sub(r'^\*\*([^*]+?)\.?\*\*?( :)?\s',
               lambda m: m.group(1) + ('. ' if len(m.group(1)) == 1 else ' '),
               t)
    if kind == 'heading':
        t = t.lstrip('#').strip()
    if kind == 'rubric':
        t = t.lstrip('>').strip()
    return t


# Where the book prints what a heading in a cell introduces, when that is
# known and matters: the collects are printed twice, traditional (pp. 158-210)
# and contemporary (pp. 211-261), and the 1993 keying's traditional collects
# are sometimes contemporary text with a traditional ending -- so a free
# alignment would compare them with the wrong printing.
SECTION = {
    'collects-epistles-gospels': [('(Contemporary)', (211, 261)),
                                  ('The Collect', (158, 210))],
}


def section(rel, heading):
    for key, rng in SECTION.get(rel.split('/')[0], []):
        if key in (heading or ''):
            return rng
    return None


def cells(families=None, skip=('psalter/',)):
    base = os.path.join(WT, 'editions/1979')
    for f in sorted(glob.glob(os.path.join(base, '**/*.md'), recursive=True)):
        rel = os.path.relpath(f, base)
        if rel.startswith(skip):
            continue
        if families and rel.split('/')[0] not in families:
            continue
        yield rel, f
