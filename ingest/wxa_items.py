"""wxa_items.py -- build every keyed correction for the 1979 cells from the
witness, verify each against its page, and write them out as data.

    python3 ingest/wxa_items.py
        -> ingest/wxa_witness_items.py   the keyed items, by group (data only)
        -> ingest/wxa_evidence.json      key -> page, book fragment, cell
                                         fragment, class, verification
        -> ingest/wxa_dropped.json       items NOT made, each with its reason

Nothing here writes a cell. The items are keyed to the BRANCH BASE text of
each cell (git 710f635b...:editions/1979/<file>), never to a live tag.

HOW AN ITEM IS MADE. A paragraph is aligned word for word against the book
(wxa_book / wxa_survey.locate). For a word difference, the cell text between
the two unchanged words that flank it is replaced by the BOOK'S text between
the same two words -- cut from the page text by the script, so no restored
word passes through anyone's hands (and the content filter never sees a
passage). The item's `old` is that stretch of the cell including the two
flanking words, widened word by word until it occurs exactly once in its
paragraph; `new` is the same stretch as the book prints it.

WHAT IS REFUSED (wxa_dropped.json, with the reason):
  glyph     the book's reading is a text-layer glyph confusion (1/I, ]/1)
  case      the change would take letter-case from the file (R11): it alters
            an all-capital word, or brings Lord/God into a text that sets
            the divine Name in small capitals
  pointing  the change touches the mediant (asterisk / spaced colon) (R11)
  hyphen    the book breaks the word at a line end, so cannot say (cf. W17)
  placement the corrected paragraph matches the book, but far from where its
            neighbours stand (a look-alike, e.g. a catechism question)
  unverified the corrected text is not found on the page
  edge      a passage with no agreed word on one side (nothing may move
            outside the damage, so a hand pass is needed)
  needs structuring  the book's span holds rubrics or speaker names (set in
            italic in the PDF) inside part of a paragraph
  markup inside the damaged stretch  group MARKUP must settle it first
  wrap-split word  a hard-wrapped prayer split a word across two lines;
            wxa_reflow.py joins it (no keyed item)
  witness-evident  (DOL) the book's reading is one no printing could have

VERIFICATION. A word item is kept only if, with every correction of its
paragraph made, the corrected stretch and five words either side stand on
the credited page (or the next); a short paragraph must also sit within
three pages of its longer neighbours (a catechism question that matched a
look-alike seven pages on was refused, then found in its place). A passage
is kept only if the whole corrected paragraph then matches the book word
for word. A collect is restored WHOLE from its own slot (day, printing,
place among its 'Or this' alternatives), read off the page by the styled
text: the roman lines after the bold title, to 'Amen.'.
"""
import collections
import difflib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import wxa_book as B
import wxa_survey as S
import wxa_classify as C
import wxa_tables as T

BASE = '710f635b7783f1e8188fa334ec75dca3e43a0220'
OUT_ITEMS = os.path.join(HERE, 'wxa_witness_items.py')
OUT_EV = os.path.join(HERE, 'wxa_evidence.json')
OUT_DROP = os.path.join(HERE, 'wxa_dropped.json')
TABLE_ROWS = S.TABLE_ROWS
MARKUP_CH = re.compile(r'[*=&\[\]<>]')
COMMENT = re.compile(r'<!--.*?-->', re.S)


def base_text(rel):
    return subprocess.run(['git', 'show', '%s:editions/1979/%s' % (BASE, rel)],
                          cwd=WT, capture_output=True, text=True).stdout


def blocks(text):
    """-> [{'line': first line (1-based), 'text': the block's exact text,
    'kind': ...}] -- a block is a run of non-blank lines. A block that is
    only a comment has kind 'comment'."""
    out, cur, start = [], [], None
    lines = text.split('\n')
    for i, line in enumerate(lines + [''], 1):
        if line.strip():
            if not cur:
                start = i
            cur.append(line)
            continue
        if cur:
            t = '\n'.join(cur)
            bare = COMMENT.sub('', t).strip()
            if not bare:
                kind = 'comment'
            elif bare.startswith('#'):
                kind = 'heading'
            elif bare.startswith('>'):
                kind = 'rubric'
            elif ' | ' in bare:
                kind = 'row'
            elif re.match(r'^\*\*[^*]+\*\*', bare):
                kind = 'label'
            else:
                kind = 'prose'
            out.append({'line': start, 'text': t, 'kind': kind})
            cur = []
    return out


def cell_spans(t):
    """Word spans of a block, comments masked (spans keep their offsets)."""
    masked = COMMENT.sub(lambda m: ' ' * len(m.group(0)), t)
    return B.spans(masked)


def norm_book(s):
    s = (s.replace('\u2019', "'").replace('\u2018', "'")
          .replace('\u201c', '"').replace('\u201d', '"'))
    return re.sub(r'[ \t]*\n[ \t]*', ' ', s)


def anchor_of(t):
    return ' '.join(COMMENT.sub('', t).split()[:8])


class Ctx:
    def __init__(self):
        self.bk = B.Book()
        self.items = collections.defaultdict(list)
        self.ev = {}
        self.drop = []
        self.n = collections.Counter()

    def add(self, group, rel, blk, old, new, cls, page, book_frag, extra=None):
        self.n[(group, rel)] += 1
        iid = '%s:%s:%d:%d' % (group, rel, blk['line'], self.n[(group, rel)])
        it = {'id': iid, 'file': rel, 'line': blk['line'],
              'anchor': anchor_of(blk['text']), 'old': old, 'new': new,
              'class': cls, 'page': page}
        if extra:
            it.update(extra)
        self.items[group].append(it)
        self.ev[iid] = {'file': rel, 'line': blk['line'],
                        'anchor': it['anchor'], 'page': page,
                        'book': book_frag, 'cell': old, 'new': new,
                        'class': cls, 'group': group,
                        'check': (extra or {}).get('check', 'verified')}
        return it

    def refuse(self, rel, blk, cls, what, reason, page=None):
        self.drop.append({'file': rel, 'line': blk['line'], 'class': cls,
                          'what': what[:80], 'reason': reason, 'page': page})


def unique_window(t, sp, a, b, mid_new=None):
    """Widen the token window [a, b] (inclusive indices into sp) until the
    cell text it covers occurs exactly once in block t. -> (a, b)."""
    while True:
        s0 = sp[a][1] if a >= 0 else 0
        e0 = sp[b][2] if b < len(sp) else len(t)
        old = t[s0:e0]
        if old and t.count(old) == 1:
            return a, b
        if a <= 0 and b >= len(sp) - 1:
            return a, b
        a = max(-1, a - 1) if a > 0 else a
        b = min(len(sp), b + 1) if b < len(sp) - 1 else b


def make_mid(ctx, t, sp, i1, i2, j1, j2, s_bk, allow_sep=True):
    """Replace cell words [i1, i2) by book words [j1, j2). Prefer swapping
    the whole stretch between the flanking unchanged words (so the book's
    own punctuation comes with it); fall back to the words alone where the
    cell's separators carry markup. -> (old, new, refusal or None)."""
    bk = ctx.bk
    n = len(sp)
    ia, ib = i1 - 1, i2               # flanking cell words (may be -1 / n)
    ja, jb = j1 - 1, j2               # flanking book words
    cs = sp[ia][2] if ia >= 0 else None
    ce = sp[ib][1] if ib < n else None
    if ia >= 0 and ib < n:
        cell_mid = t[cs:ce]
        book_mid = (bk.raw_between(ja, jb))
        if '-\n' in book_mid:
            return None, None, 'hyphen'
        if allow_sep and not MARKUP_CH.search(cell_mid) and \
                ' : ' not in cell_mid and '*' not in book_mid and \
                '_' not in book_mid:
            new_mid = norm_book(book_mid)
            # keep the cell's spacing habit after a stop (two spaces) out:
            new_mid = re.sub(r' {2,}', ' ', new_mid)
            a, b = unique_window(t, sp, ia, ib)
            s0 = sp[a][1] if a >= 0 else 0
            e0 = sp[b][2] if b < n else len(t)
            old = t[s0:e0]
            new = t[s0:cs] + new_mid + t[ce:e0]
            return old, new, None
    # words alone
    if '*' in (bk.raw(j1, j2) if j2 > j1 else '') or (
            i2 > i1 and ' : ' in t[sp[i1][1]:sp[i2 - 1][2]]):
        return None, None, 'pointing'
    if j2 > j1:
        brw = norm_book(bk.raw(j1, j2))
        if '-\n' in bk.raw(j1, j2):
            return None, None, 'hyphen'
    else:
        brw = ''
    if i2 > i1:
        s1, e1 = sp[i1][1], sp[i2 - 1][2]
        if not brw:                   # a deletion: take one separator too
            if i2 < n:
                e1 = sp[i2][1]
            elif i1 > 0:
                s1 = sp[i1 - 1][2]
    else:                             # an insertion before word i1
        if i1 < n:
            s1 = e1 = sp[i1][1]
            brw = brw + ' '
        else:
            s1 = e1 = sp[n - 1][2]
            brw = ' ' + brw
    a, b = unique_window(t, sp, max(-1, i1 - 1), min(n, i2))
    s0 = sp[a][1] if a >= 0 else 0
    e0 = sp[b][2] if b < n else len(t)
    s0, e0 = min(s0, s1), max(e0, e1)
    old = t[s0:e0]
    new = t[s0:s1] + brw + t[e1:e0]
    return old, new, None


def book_frag(bk, j, w=10):
    a, b = max(0, j - w), min(len(bk.tok), j + w)
    return bk.raw(a, b)[:160]


# ---------------------------------------------------------------------------
# prose cells: words, spelling, passages, punctuation, markup blanks

GLYPH = {('1', 'i'), ('i', '1')}
LABELS = ('People', 'Celebrant', 'Bishop', 'Officiant', 'Presenters',
          'Candidate', 'Candidates', 'Parents and Godparents', 'Answer',
          'Deacon', 'Priest', 'Minister', 'Child', 'Parent(s)', 'Leader',
          'Reader', 'Bishops', 'Rector', 'Lector')


def refuse_reason(t, sp, i1, i2, ctoks, btoks):
    pairs = set(zip(ctoks, btoks)) if len(ctoks) == len(btoks) else set()
    if pairs & GLYPH or (ctoks == ['i'] and btoks == ['1']):
        return 'glyph'
    if i2 > i1:
        for k in range(i1, i2):
            w = t[sp[k][1]:sp[k][2]]
            if len(w) > 1 and w.isupper() and w.isalpha():
                return 'case'
    if set(btoks) & {'lord', 'god'} and not set(btoks) <= set(ctoks):
        if re.search(r'\b(LORD|GOD)\b', t) or ' : ' in t:
            return 'case'
    return None


def located_page(bk, s, e):
    return collections.Counter(bk.page[s:e]).most_common(1)[0][0]


# Where in the book each cell's text is printed (pages), so a paragraph is
# not compared with a look-alike in another office. Morning and Evening
# Prayer hold Rite I up to the line that opens Rite II.
RANGES = {
    'front-matter/': [(9, 14), (934, 935)],
    'tables/feasts-and-fasts.md': [(15, 33), (880, 885)],
    'the-litany/': [(148, 155), (548, 551)],
    'holy-communion/': [(316, 409)],
    'occasional-offices/public-baptism.md': [(298, 314)],
    'occasional-offices/private-baptism.md': [(312, 314)],
    'occasional-offices/confirmation.md': [(412, 421)],
    'occasional-offices/matrimony.md': [(422, 438)],
    'occasional-offices/churching.md': [(439, 445)],
    'occasional-offices/visitation-sick.md': [(453, 467)],
    'occasional-offices/burial.md': [(468, 507)],
    'occasional-offices/catechism.md': [(844, 862)],
    'ordinal/': [(509, 555)],
    'prayers-and-thanksgivings/': [(810, 841)],
}
RITE2 = {'daily-office/morning-prayer.md': 624,
         'daily-office/evening-prayer.md': 289}


def within_for(rel, line, head):
    sec = B.section(rel, head)
    if sec:
        return sec
    if rel in RITE2:
        if 'morning' in rel:
            return (36, 74) if line < RITE2[rel] else (74, 102)
        return (61, 74) if line < RITE2[rel] else (108, 126)
    for k, v in RANGES.items():
        if rel.startswith(k):
            return (v[0][0], v[-1][1]) if len(v) == 1 else (v[0][0], v[-1][1])
    return None


def locate_in(bk, rel, line, head, pre, w, post):
    """wxa_survey.locate, held to the pages where this cell's text is."""
    rng = within_for(rel, line, head)
    old = B.section
    if rng:
        B.section = lambda _r, _h: rng
    try:
        return S.locate(bk, rel, head, pre, w, post)
    finally:
        B.section = old


def prose(ctx):
    bk = ctx.bk
    survey = {(r['file'], r['line']): r
              for r in json.load(open(os.path.join(HERE, 'wxa_survey.json')))}
    for rel, _f in B.cells():
        if rel in TABLE_ROWS:
            continue
        text = base_text(rel)
        blks = blocks(text)
        head = None
        body = [i for i, b in enumerate(blks)
                if b['kind'] not in ('heading', 'row', 'comment')]
        placed = {}                      # block index -> located page
        plan = []
        for bi, blk in enumerate(blks):
            if blk['kind'] == 'heading':
                head = blk['text']
                continue
            if blk['kind'] in ('row', 'comment'):
                continue
            t = blk['text']
            sp = cell_spans(t)
            w = [x[0] for x in sp]
            if not w:
                continue
            pre = post = []
            # hard-wrapped prayers: every fragment is read inside its
            # neighbours, or a word on the next line looks "dropped" here
            short = 30 if rel.startswith('prayers-and-thanksgivings/') else 12
            if len(w) < short and bi in body:
                j = body.index(bi)
                if j > 0:
                    pre = [x[0] for x in cell_spans(blks[body[j - 1]]['text'])][-12:]
                if j + 1 < len(body):
                    post = [x[0] for x in cell_spans(blks[body[j + 1]]['text'])][:12]
            r = locate_in(bk, rel, blk['line'], head, pre, w, post)
            if r is None:
                plan.append((bi, blk, sp, None))
                continue
            ratio, s, e, ops = r
            placed[bi] = located_page(bk, s, e) if e > s else bk.page[s]
            plan.append((bi, blk, sp, r))
        pages_list = [placed.get(i) for i in range(len(blks))]

        def near_ok(bi, page):
            """the located page agrees with the nearest located longer
            neighbours (within 3 pages of one of them)"""
            neigh = []
            for d in (-1, 1):
                k = bi + d
                while 0 <= k < len(blks):
                    if pages_list[k] is not None and k in placed and \
                            len(cell_spans(blks[k]['text'])) >= 12:
                        neigh.append(pages_list[k])
                        break
                    k += d
            return not neigh or any(abs(page - p) <= 3 for p in neigh)

        for bi, blk, sp, r in plan:
            t = blk['text']
            key = (rel, blk['line'])
            sv = survey.get(key)
            if key in C.FURNITURE or re.match(r'^-+\(END OF', t.strip()):
                continue                  # repo notes / e-text furniture
            if t.strip() == '&LordsPrayer.':
                lords_prayer(ctx, rel, blk)
                continue
            if r is None:
                if sv and sv['status'] == 'unlocated':
                    ctx.refuse(rel, blk, 'd8', t, 'unlocated', None)
                continue
            ratio, s, e, ops = r
            # book words standing outside the paragraph (the window's spill
            # before its first word or after its last) are not differences
            n_ = len(sp)
            ops = [o for o in ops if not (o[0] == 'insert' and
                                          (o[4] == 0 or o[4] == n_))]
            r = (ratio, s, e, ops)
            diffs = [o for o in ops if o[0] != 'equal']
            page = placed.get(bi)
            # classes, the same way the survey + classifier assign them
            classes = []
            if diffs and sv and sv['status'] == 'diff':
                classes = C.para_classes(sv)
            elif diffs and sv:
                classes = C.para_classes(sv)
            # a short paragraph can match a look-alike elsewhere in the book;
            # a long one anchors itself
            only_blank = diffs and all(set(o[1]) <= {'mdash', '3em'} and not o[2]
                                       or (set(o[1]) & {'mdash', '3em'})
                                       for o in diffs)
            if diffs and len(sp) < 12 and not only_blank and \
                    not near_ok(bi, page):
                for o in diffs:
                    ctx.refuse(rel, blk, 'word', ' '.join(o[1]) + ' -> ' +
                               ' '.join(o[2]), 'placement', page)
                continue
            if diffs:
                passage = any(c in ('d8', 'd9') for c in classes) or (
                    sv and sv['status'] == 'unlocated')
                if passage:
                    passage_item(ctx, rel, blk, sp, r, classes, page)
                else:
                    word_items(ctx, rel, blk, sp, r, sv, page)
            punct_items(ctx, rel, blk, sp, r, page)
            markup_blanks(ctx, rel, blk, sp, r, page)


def lords_prayer(ctx, rel, blk):
    """public-baptism.md: the e-text's placeholder `&LordsPrayer.` where the
    book prints the Lord's Prayer in its two forms side by side (p. 311).
    The two columns, rebuilt by wxa_book, become the two paragraphs the repo
    sets elsewhere (traditional, then contemporary)."""
    t = B.pages()[311]
    a = t.find('Our Father, who art in heaven,')
    b = t.find('now and for ever. Amen.', a)
    if a < 0 or b < 0:
        ctx.refuse(rel, blk, 'b', blk['text'], 'not-extracted', 311)
        return
    seg = t[a:b + len('now and for ever. Amen.')]
    i = seg.find('Our Father in heaven,')
    trad = ' '.join(norm_book(seg[:i]).split())
    cont = ' '.join(norm_book(seg[i:]).split())
    for p in (trad, cont):
        if not p.endswith('Amen.'):
            ctx.refuse(rel, blk, 'b', blk['text'], 'not-extracted', 311)
            return
    ctx.add('PASSAGES', rel, blk, blk['text'], trad + '\n\n' + cont, 'b', 311,
            '(the Lord\'s Prayer, both forms, p. 311)', {'structured': True})


def merged_ops(ops):
    """Join differences that sit within two words of each other."""
    out = []
    for o in ops:
        if o[0] == 'equal':
            out.append(list(o))
            continue
        if out and out[-1][0] == 'equal' and len(out[-1][1]) <= 2 and \
                len(out) >= 2 and out[-2][0] != 'equal':
            eq = out.pop()
            prev = out.pop()
            out.append(['replace', prev[1] + eq[1] + o[1],
                        prev[2] + eq[2] + o[2], prev[3], prev[4], o[5]])
            continue
        out.append(list(o))
    return out


def word_items(ctx, rel, blk, sp, r, sv, page):
    bk = ctx.bk
    t = blk['text']
    ratio, s, e, ops = r
    # the survey's classes, matched op by op (same alignment code)
    cls_by = {}
    if sv:
        cl = C.para_classes(sv)
        for o, c in zip(sv['ops'], cl):
            cls_by.setdefault((o['cell'][:60], o['book'][:60]), c)
    cands = []
    for o in merged_ops(ops):
        tag, ctoks, btoks, bpos, i1, i2 = o
        if tag == 'equal':
            continue
        if 'mdash' in ctoks or '3em' in ctoks or 'lordsprayer' in ctoks:
            continue                      # MARKUP blanks, made below
        j1 = bpos
        j2 = bpos + len(btoks)
        c = cls_by.get((' '.join(ctoks)[:60], ' '.join(btoks)[:60]))
        if c is None:
            # a merged op: class of its first part, else typo
            c = next((v for (a, b), v in cls_by.items()
                      if a and a in ' '.join(ctoks)), 'd1')
        if c == 'g' and not ({'mdash', '3em', 'lordsprayer'} & set(ctoks)) \
                and ctoks and btoks:
            # the survey's mechanical rule called a word difference in a
            # paragraph that also holds markup 'markup'; it is a word
            c = 'd1' if difflib.SequenceMatcher(None, ' '.join(ctoks),
                                                ' '.join(btoks)).ratio() >= 0.6 \
                else 'd3'
        if c in ('e', 'x', 'g', 'h1', 'h2', 'c'):
            continue
        # a word the 60-column wrap split across two fragments: the re-flow
        # (wxa_reflow.py) mends it; no item here
        if rel.startswith('prayers-and-thanksgivings/') and \
                (i2 == len(sp) or i1 == 0) and len(btoks) == 1 and \
                len(ctoks) == 1 and btoks[0] != ctoks[0] and \
                (btoks[0].startswith(ctoks[0]) or btoks[0].endswith(ctoks[0])):
            ctx.refuse(rel, blk, c, ctoks[0] + ' -> ' + btoks[0],
                       'wrap-split word (the re-flow joins it)',
                       bk.page[min(bpos, len(bk.page) - 1)])
            continue
        group = 'SPELLING' if c == 'f' else 'WORDS'
        why = refuse_reason(t, sp, i1, i2, ctoks, btoks)
        if why:
            ctx.refuse(rel, blk, c, ' '.join(ctoks) + ' -> ' + ' '.join(btoks),
                       why, bk.page[min(j1, len(bk.page) - 1)])
            continue
        old, new, why = make_mid(ctx, t, sp, i1, i2, j1, j2, s)
        if why:
            ctx.refuse(rel, blk, c, ' '.join(ctoks) + ' -> ' + ' '.join(btoks),
                       why, bk.page[min(j1, len(bk.page) - 1)])
            continue
        cands.append((group, old, new, c, j1, ' '.join(ctoks) + ' -> ' +
                      ' '.join(btoks)))
    # verify each on the paragraph with ALL its corrections made, so that a
    # neighbouring defect does not hide a good correction: the corrected
    # stretch with five words either side stands on the credited page
    fixed = t
    for g, old, new, c, j1, what in cands:
        if fixed.count(old) == 1:
            fixed = fixed.replace(old, new, 1)
    for g, old, new, c, j1, what in cands:
        ok, pg = verify_window(ctx, fixed, new, new, j1)
        if not ok:
            ctx.refuse(rel, blk, c, what, 'unverified', pg)
            continue
        ctx.add(g, rel, blk, old, new, c, pg, book_frag(bk, j1))


def verify_window(ctx, t, old, new, j):
    """Words of the corrected stretch plus five neighbours each side must
    stand, in that order, on the page of book word j or an adjacent page."""
    bk = ctx.bk
    fixed = t if old == new else t.replace(old, new, 1)
    i = fixed.find(new)
    lw = B.words(fixed[:i])[-5:]
    rw = B.words(fixed[i + len(new):])[:5]
    win = lw + B.words(new) + rw
    pg = bk.page[min(j, len(bk.page) - 1)]
    pages = B.pages()
    for k in (pg, pg - 1, pg + 1):
        joined = ' ' + ' '.join(B.words(pages.get(k, '') + ' ' +
                                        pages.get(k + 1, ''))) + ' '
        if ' ' + ' '.join(win) + ' ' in joined:
            return True, k
    return False, pg


def collect_slot(rel, blk):
    """For a block in a collects file: (book title, section range, index of
    this collect among its section's collects) or None."""
    if not rel.startswith('collects-epistles-gospels/'):
        return None
    text = base_text(rel)
    blks = blocks(text)
    title = next((b['text'][2:].strip() for b in blks
                  if b['text'].startswith('# ')), None)
    sec, idx = None, -1
    for b in blks:
        if b['text'].startswith('## The Collect (Contemporary)'):
            sec, idx = (211, 261), -1
            continue
        if b['text'].startswith('## The Collect'):
            sec, idx = (158, 210), -1
            continue
        if b['kind'] in ('prose',) and sec:
            idx += 1
            if b['line'] == blk['line']:
                return title, sec, idx
    return None


def whole_collect(ctx, rel, blk, c, page):
    """Replace a damaged collect paragraph whole by the book's collect in the
    same slot (same day, same printing, same place among its 'Or this'
    alternatives), read off the page by book_collect(). The block's first
    words must open the book's collect too, or nothing is made."""
    slot = collect_slot(rel, blk)
    if not slot:
        return False
    title, sec, idx = slot
    title = title.replace("Saint's", "Saints'")
    pg, paras = book_collect(title, sec)
    if not paras:
        return False
    cols = [p for p in paras if not p.startswith('> ')]
    if idx >= len(cols):
        return False
    new = cols[idx]
    t = blk['text']
    def head(x):
        w = B.words(x)
        return (w[1:] if w[:1] == ['o'] else w)[:2]
    if head(t) != head(new):
        return False
    if t.count(t) != 1 or t == new:
        return False
    ctx.add('PASSAGES', rel, blk, t, new, c, pg,
            ' '.join(new.split()[:8]) + ' ...', {'whole_collect': title})
    return True


def passage_item(ctx, rel, blk, sp, r, classes, page):
    """A swallowed or spliced passage: one item from the first difference to
    the last, its new text cut from the book (structured if the book's span
    holds rubrics or speaker labels, which the PDF sets in italic)."""
    bk = ctx.bk
    t = blk['text']
    ratio, s, e, ops = r
    diffs = [o for o in ops if o[0] != 'equal']
    if ratio < 0.4:
        ctx.refuse(rel, blk, 'd8', t, 'unverified', page)
        return
    i1 = diffs[0][4]
    i2 = diffs[-1][5]
    j1 = diffs[0][3]
    last = diffs[-1]
    j2 = last[3] + len(last[2])
    c = 'd9' if 'd9' in classes else 'd8'
    # a collect is restored whole from its own slot in the book
    if whole_collect(ctx, rel, blk, c, page):
        return
    # a restored passage must be held by an agreed word on EACH side, so
    # that nothing outside the damage can move; and its stretch of the cell
    # must carry no markup (that is group MARKUP's to settle first)
    if i1 == 0 or i2 >= len(sp):
        ctx.refuse(rel, blk, c, t, 'edge (no agreed word on one side)', page)
        return
    if MARKUP_CH.search(t[sp[i1 - 1][2]:sp[i2][1]]):
        ctx.refuse(rel, blk, c, t, 'markup inside the damaged stretch', page)
        return
    old, new, why = make_mid(ctx, t, sp, i1, i2, j1, j2, s)
    if why:
        ctx.refuse(rel, blk, c, t, why, page)
        return
    structured = structure(ctx, j1, j2)
    if structured is not None and '\n' in structured and old != t:
        ctx.refuse(rel, blk, c, t, 'needs structuring (rubrics or speakers '
                   'inside part of a paragraph)', page)
        return
    if structured is not None and '\n' in structured:
        # replace the plain cut by the structured one (same words)
        flat = norm_book(bk.raw(j1, j2)) if j2 > j1 else ''
        if flat and flat in new:
            new = new.replace(flat, structured, 1)
    fixed = t.replace(old, new, 1)
    fw = B.words(COMMENT.sub('', fixed))
    rr = S.locate(bk, rel, None, [], fw, [])
    ok = rr is not None and not [o for o in rr[3] if o[0] != 'equal']
    if not ok:
        ctx.refuse(rel, blk, c, t, 'unverified', page)
        return
    ctx.add('PASSAGES', rel, blk, old, new, c, page,
            book_frag(bk, j1), {'structured': '\n' in new})


def structure(ctx, j1, j2):
    """Book words [j1, j2) as repo lines: italic-only lines -> '> rubric';
    a line opening with an italic speaker name -> '**Name.** text'; roman
    lines run together into paragraphs, broken after 'Amen.'. None if the
    page has no style map (a rebuilt column page)."""
    bk = ctx.bk
    if j2 <= j1 or bk.page[j1] != bk.page[j2 - 1]:
        return None
    k = bk.page[j1]
    st = B.styles().get(k)
    if st is None:
        return None
    t = B.pages()[k]
    a, b = bk.span[j1][0], bk.span[j2 - 1][1]
    seg_lines = []
    pos = a
    for line in t[a:b].split('\n'):
        fonts = [st[pos + i] for i, ch in enumerate(line) if not ch.isspace()
                 and st[pos + i]]
        ital = [f.endswith('Italic') for f in fonts]
        seg_lines.append((line.strip(), ital, pos))
        pos += len(line) + 1
    out, para = [], []

    def flush():
        if para:
            out.append(' '.join(para))
            para.clear()
    for line, ital, p0 in seg_lines:
        if not line:
            continue
        if ital and all(ital):
            flush()
            out.append('> ' + norm_book(line))
            continue
        # leading italic run = a speaker name
        n_it = 0
        for f in ital:
            if f:
                n_it += 1
            else:
                break
        if n_it and n_it < len(ital):
            # find the italic prefix text
            cnt, cut = 0, 0
            for i, ch in enumerate(line):
                if not ch.isspace():
                    cnt += 1
                    if cnt == n_it:
                        cut = i + 1
                        break
            name = line[:cut].strip()
            if name in LABELS:
                flush()
                para.append('**%s.** %s' % (name, norm_book(line[cut:].strip())))
                continue
        para.append(norm_book(line))
        if line.endswith('Amen.'):
            flush()
    flush()
    return '\n\n'.join(out)


def punct_items(ctx, rel, blk, sp, r, page):
    """Stops that differ between two words both sides agree on."""
    bk = ctx.bk
    t = blk['text']
    ratio, s, e, ops = r
    for o in ops:
        if o[0] != 'equal':
            continue
        _t, ctoks, btoks, bpos, i1, i2 = o
        for k in range(i1, i2 - 1):
            j = bpos + (k - i1)
            csep = t[sp[k][2]:sp[k + 1][1]]
            bsep = bk.between(j)
            item = sep_item(t, sp, k, csep, bsep, blk['kind'])
            if item:
                old, new, c = item
                grp = {'h1': 'MEDIANT_STOPS', 'h2': 'PUNCT', 'c': 'RUBRIC_STOPS'}[c]
                ctx.add(grp, rel, blk, old, new, c, bk.page[j],
                        book_frag(bk, j, 6))
        # a rubric's final stop (a prose paragraph's last stop is not
        # compared: the 1993 keying sometimes ends a paragraph where the
        # book's sentence runs on, and a stop alone cannot mend that)
        if i2 == len(sp) and i2 > i1 and blk['kind'] == 'rubric':
            j = bpos + (i2 - 1 - i1)
            if j + 1 < len(bk.tok):
                csep = t[sp[-1][2]:]
                bsep = bk.between(j).split('\n')[0]
                if '\n' in bk.between(j):
                    item = sep_item(t, sp, len(sp) - 1, csep, bsep,
                                    blk['kind'], final=True)
                    if item:
                        old, new, c = item
                        grp = {'h1': 'MEDIANT_STOPS', 'h2': 'PUNCT',
                               'c': 'RUBRIC_STOPS'}[c]
                        ctx.add(grp, rel, blk, old, new, c, bk.page[j],
                                book_frag(bk, j, 6))


STOPS = ',;:.?!()[]'


def sig(sep, cell):
    s = sep
    if cell:
        s = re.sub(r'\s:\s', 'M', s)
    else:
        s = s.replace('*', 'M')
    return ''.join(ch for ch in s if ch in STOPS or ch == 'M')


def sep_item(t, sp, k, csep, bsep, kind, final=False):
    if MARKUP_CH.search(csep) or '_' in bsep or '\u2014' in bsep or \
            '--' in csep:
        return None
    a, b = sig(csep, True), sig(bsep, False)
    if a == b:
        return None
    if a.replace('M', '') == b.replace('M', ''):
        return None                       # the mark itself: out of power
    if 'M' in a and 'M' in b:
        # a stop before the mediant the cell lost
        if b.replace('M', '') and a == 'M' and b.endswith('M'):
            stops = b[:-1]
            new_sep = csep.replace(' : ', stops + ' : ', 1)
            w0 = sp[k]
            s0 = w0[1]
            e0 = sp[k + 1][2] if not final else len(t)
            old = t[s0:e0]
            new = t[s0:w0[2]] + new_sep + t[sp[k + 1][1]:e0]
            if t.count(old) != 1:
                return None
            return old, new, 'h1'
        return None
    if 'M' in a or 'M' in b:
        return None                       # next to the mediant: ruling 5(b)
    # ordinary stops: the book's, with the cell's spacing habit
    bs = norm_book(bsep)
    new_sep = re.sub(r'\s+', ' ', bs)
    if final:
        new_sep = new_sep.rstrip()
        s0 = sp[k][1]
        old = t[s0:]
        new = t[s0:sp[k][2]] + new_sep
        c = 'c' if kind == 'rubric' else 'h2'
    else:
        s0, e0 = sp[k][1], sp[k + 1][2]
        old = t[s0:e0]
        new = t[s0:sp[k][2]] + new_sep + t[sp[k + 1][1]:e0]
        c = 'h2'
    if '"' in new_sep or "'" in new_sep or '"' in csep or "'" in csep:
        return None                       # quotation marks: not compared
    if t.count(old) != 1 or old == new:
        return None
    return old, new, c


def markup_blanks(ctx, rel, blk, sp, r, page):
    """`&mdash.` / `&3em.` / an em dash where the book prints a blank: the
    book's own blank (its underscores, or N.) between the same two words."""
    bk = ctx.bk
    t = blk['text']
    ratio, s, e, ops = r
    for o in ops:
        tag, ctoks, btoks, bpos, i1, i2 = o
        if tag == 'equal' or not ({'mdash', '3em'} & set(ctoks)):
            continue
        if ctoks[-1] in ('mdash', '3em') and i2 == len(sp) and i1 > 0 and \
                len(ctoks) == 1:
            # the blank ends the paragraph: the book's text after the last
            # agreed word, to the end of its line
            ja = bpos - 1
            tail = bk.between(ja).split('\n')[0]
            if re.search(r'_+', tail):
                s0 = sp[i1 - 1][1]
                old = t[s0:]
                new = t[s0:sp[i1 - 1][2]] + norm_book(tail).rstrip()
                if t.count(old) == 1:
                    ctx.add('MARKUP', rel, blk, old, new, 'g', bk.page[ja],
                            book_frag(bk, ja, 6), {'pattern': '&mdash.'})
                    continue
            ctx.refuse(rel, blk, 'g', ' '.join(ctoks), 'no-blank-in-book',
                       bk.page[bpos])
            continue
        if len(ctoks) != 1 or btoks:
            # a blank folded in with other words: leave to WORDS/PASSAGES
            ctx.refuse(rel, blk, 'g', ' '.join(ctoks), 'markup-with-words',
                       bk.page[bpos])
            continue
        # flanking words
        if i1 == 0 or i2 >= len(sp):
            continue
        ja = bpos - 1
        cell_mid = t[sp[i1 - 1][2]:sp[i2][1]]
        book_mid = norm_book(bk.between(ja))
        if not re.search(r'_+|\bN\.', book_mid):
            ctx.refuse(rel, blk, 'g', cell_mid, 'no-blank-in-book', bk.page[ja])
            continue
        a, b = unique_window(t, sp, i1 - 1, i2)
        s0, e0 = sp[a][1], sp[b][2]
        old = t[s0:e0]
        new = t[s0:sp[i1 - 1][2]] + re.sub(r' {2,}', ' ', book_mid) + t[sp[i2][1]:e0]
        ctx.add('MARKUP', rel, blk, old, new, 'g', bk.page[ja],
                book_frag(bk, ja, 6), {'pattern': '&mdash.'})


# ---------------------------------------------------------------------------
# markup patterns that change no word (normalized to book/repo conventions)

MARKUP_RULES = [
    # (name, regex on a line, replacement function)
    ('=x=', re.compile(r'=(\S(?:[^=\n]{0,58}\S)?)='), lambda m: m.group(1)),
    ('&N.', re.compile(r'&N\.'), lambda m: 'N.'),
    ('&V./&R.', re.compile(r'&([VR])\.'), lambda m: m.group(1) + '.'),
    ('**X* :', re.compile(r'^\*\*([A-Za-z ,()]+)\* : ', re.M),
     lambda m: '**%s.** ' % m.group(1)),
    ('*X* label', re.compile(r'^\*([A-Z][A-Za-z ]+)\*  ', re.M),
     lambda m: '**%s.** ' % m.group(1)),
    ('[[', re.compile(r'\[\[(?=\S)'), lambda m: ''),
    (']]', re.compile(r'(?<=\S)\]\]'), lambda m: ''),
    ('stray >', re.compile(r'(?<=[a-z])>$', re.M), lambda m: ''),
]


def markup(ctx):
    for rel, _f in B.cells():
        if rel.startswith('tables/'):
            continue
        text = base_text(rel)
        for blk in blocks(text):
            if blk['kind'] == 'comment':
                continue
            t = blk['text']
            bare = COMMENT.sub('', t)
            furniture = t.strip() in ('<An Outline', 'of the Faith>')
            comments = [(m.start(), m.end()) for m in COMMENT.finditer(t)]
            for name, rx, fn in MARKUP_RULES:
                if furniture:
                    break
                for m in rx.finditer(t):
                    if any(a <= m.start() < b for a, b in comments):
                        continue
                    # a blank item (&mdash. -> the book's blank) that already
                    # takes this mark away covers it
                    covered = False
                    for it in ctx.items.get('MARKUP', []):
                        if it['file'] != rel or it['line'] != blk['line'] or \
                                it.get('pattern') != '&mdash.':
                            continue
                        p0 = t.find(it['old'])
                        if p0 >= 0 and p0 <= m.start() and \
                                m.end() <= p0 + len(it['old']):
                            covered = True
                    if covered:
                        continue
                    # key: the mark with the word on each side (never the
                    # bare mark), widened until it occurs once
                    s0, e0 = m.start(), m.end()
                    ps = t.rfind(' ', 0, max(0, s0 - 1))
                    s0 = ps + 1 if s0 > 0 else 0
                    ne = t.find(' ', e0 + 1)
                    e0 = ne if ne > 0 else len(t)
                    while t.count(t[s0:e0]) != 1 and (s0 > 0 or e0 < len(t)):
                        if s0 > 0:
                            s0 = t.rfind(' ', 0, s0 - 1) + 1
                        if e0 < len(t):
                            ne = t.find(' ', e0 + 1)
                            e0 = ne if ne > 0 else len(t)
                    old = t[s0:e0]
                    rel_m = m.start() - s0
                    new = old[:rel_m] + fn(m) + old[rel_m + len(m.group(0)):]
                    if t.count(old) != 1:
                        ctx.refuse(rel, blk, 'g', old, 'markup-not-unique')
                        continue
                    ctx.add('MARKUP', rel, blk, old, new, 'g', None,
                            '(markup: %s)' % name, {'pattern': name})
            # whole blocks that are e-text furniture
            if re.match(r'^-+\(END OF \w+\.TXT\)-+$', t.strip()) or \
                    t.strip() in ('<An Outline', 'of the Faith>'):
                ctx.add('MARKUP', rel, blk, t, '', 'g', None,
                        '(e-text furniture)', {'pattern': 'furniture'})


# ---------------------------------------------------------------------------
# the eight absent collects, and the flags they close

ABSENT = {
    'advent-4.md': ('Fourth Sunday of Advent', 'trad'),
    'epiphany-8.md': ('Eighth Sunday after the Epiphany', 'trad'),
    'epiphany-6.md': ('Sixth Sunday after the Epiphany', 'cont'),
    'lent-4.md': ('Fourth Sunday in Lent', 'cont'),
    'st-andrew.md': ('Saint Andrew', 'cont'),
    'st-james.md': ('Saint James', 'cont'),
    'st-simon-st-jude.md': ('Saint Simon and Saint Jude', 'cont'),
    'easter-even.md': ('Holy Saturday', 'cont'),
}


def book_collect(title, rng):
    """-> (page, [paragraph texts]) for a day's collect(s) as the book prints
    them: the roman lines after the bold title, to 'Amen.'; an italic
    'Or this' and the next collect are kept, as the repo keeps them."""
    P = B.pages()
    st = B.styles()
    for k in range(rng[0], rng[1] + 1):
        t = P.get(k, '')
        f = st.get(k)
        lines = t.split('\n')
        pos = 0
        offs = []
        for ln in lines:
            offs.append(pos)
            pos += len(ln) + 1
        for li, ln in enumerate(lines):
            if not (ln.strip() == title or re.match(
                    re.escape(title) + r'\s{2,}[A-Z][a-z]+ \d+$', ln.strip())):
                continue
            if f is None:
                return k, None
            paras, cur, mode = [], [], 'seek'
            for lj in range(li + 1, len(lines)):
                l2 = lines[lj].strip()
                if not l2:
                    continue
                o = offs[lj]
                fonts = [f[o + i] for i, ch in enumerate(lines[lj])
                         if not ch.isspace() and f[o + i]]
                if not fonts:
                    continue
                n_it = sum(1 for x in fonts if x.endswith('Italic'))
                kind = ('i' if n_it >= 0.8 * len(fonts) else
                        'b' if all(x.endswith('Bold') for x in fonts) else 'r')
                if re.match(r'^The (Proper )?Liturgy .*page \d+\.$', l2):
                    kind = 'i'
                if l2 == 'Amen.' and cur:
                    kind = 'r'            # set apart, in whatever face
                if kind == 'b':
                    break
                if kind == 'i':
                    if l2.startswith('Or this') and not cur and paras:
                        paras.append('> ' + norm_book(l2))
                        continue
                    if mode == 'seek':
                        continue          # 'The Proper Liturgy ... page 283.'
                    break                 # 'Preface of ...'
                if re.match(r'^(January|February|March|April|May|June|July|'
                            r'August|September|October|November|December) \d+$', l2):
                    continue
                mode = 'text'
                cur.append(norm_book(l2))
                if l2.endswith('Amen.'):
                    paras.append(' '.join(cur))
                    cur = []
            if cur:
                return k, None
            return k, paras
    return None, None


def collects(ctx):
    for fn, (title, which) in sorted(ABSENT.items()):
        rel = 'collects-epistles-gospels/' + fn
        text = base_text(rel)
        blks = blocks(text)
        rng = (211, 261) if which == 'cont' else (158, 210)
        page, paras = book_collect(title, rng)
        if not paras:
            ctx.refuse(rel, blks[0], 'collect', title, 'not-extracted', page)
            continue
        body = '\n\n'.join(paras)
        if which == 'cont':
            blk = [b for b in blks if b['kind'] != 'comment'][-1]
            # keyed to the paragraph's last word, so a correction elsewhere in
            # that collect (group WORDS) cannot make it stale
            m = re.search(r'\S+\s*$', blk['text'])
            old = m.group(0)
            if blk['text'].count(old) != 1:
                ctx.refuse(rel, blk, 'collect', old, 'not-unique', page)
                continue
            new = old.rstrip() + '\n\n## The Collect (Contemporary)\n\n' + body
        else:
            blk = next(b for b in blks if b['text'] == '## The Collect (Contemporary)')
            old = blk['text']
            new = '## The Collect\n\n' + body + '\n\n' + old
        # verify: every paragraph's words are in the book, on that page
        ok = all(' '.join(B.words(p)) in ' '.join(B.words(B.pages()[page] + ' ' +
                                                         B.pages().get(page + 1, '')))
                 for p in paras)
        if not ok:
            ctx.refuse(rel, blk, 'collect', title, 'unverified', page)
            continue
        ctx.add('PASSAGES', rel, blk, old, new, 'b', page,
                ' '.join(paras[0].split()[:8]) + ' ...',
                {'closes': title, 'collect': which})
        # the flag it closes
        fl = [b for b in blks if b['kind'] == 'comment' and
              'collect for this day is absent' in b['text']]
        if len(fl) == 1:
            ctx.add('PASSAGES', rel, fl[0], fl[0]['text'], '', 'flag', page,
                    '(flag closed by the restored collect)',
                    {'closes_flag': title})


# ---------------------------------------------------------------------------
# headings keyed wrong (the slug is never moved, R5)

HEADINGS = [
    ('prayers-and-thanksgivings/for-the-oppresed.md', 'For the Oppressed'),
    ('collects-epistles-gospels/all-saints.md', "All Saints' Day"),
]


def headings(ctx):
    for rel, book_title in HEADINGS:
        text = base_text(rel)
        blk = next(b for b in blocks(text) if b['kind'] == 'heading')
        rng = (810, 841) if rel.startswith('prayers') else (158, 210)
        hit = None
        for k in range(rng[0], rng[1] + 1):
            for ln in B.pages().get(k, '').split('\n'):
                lt = re.sub(r'^\d+\.\s*', '', ln.strip())   # "35. For the ..."
                lt = re.split(r'\s{2,}', lt)[0]               # "... November 1"
                if lt.replace('\u2019', "'").lower() == book_title.lower():
                    hit = (k, lt)
                    break
            if hit:
                break
        if not hit:
            ctx.refuse(rel, blk, 'heading', book_title, 'unverified')
            continue
        # the book's own spelling, read off the page by the script
        page, printed = hit
        frag = printed
        new = '# ' + printed.replace('\u2019', "'")
        ctx.add('HEADINGS', rel, blk, blk['text'], new, 'heading', page,
                frag[:120], {'slug_kept': rel})


# ---------------------------------------------------------------------------
# the Daily Office Lectionary

def dol(ctx):
    rel = 'tables/daily-office-lectionary.md'
    text = base_text(rel)
    lines = text.split('\n')
    blks = {b['line']: b for b in blocks(text)}
    book = T.book_dol()
    cells = T.cell_dol(text=text)
    res, missing = T.compare(cells, book)
    ctx.dol_closes = dol_rows(ctx, text, res, missing, book)
    xmas(ctx, text, res)
    in_rows = set()
    for it in ctx.items.get('DOL_ROWS', []):
        a = it['line']
        in_rows.update(range(a, a + it['old'].count('\n') + 1))
    disputes = []
    by_line = collections.defaultdict(list)
    for r in res:
        by_line[r[0][6]].append(r)
    bad_rows = set(r[0][6] for r in res if r[4] in ('misfiled', 'no-row'))
    for ln, rs in sorted(by_line.items()):
        blk = blks.get(ln)
        if blk is None:
            continue
        t = blk['text']
        row = rs[0][0]
        for r in rs:
            _c, col, cv, bv, verdict = r
            if verdict in ('exact', 'notation', 'glyph') or cv is None or bv is None:
                continue
            if ln in bad_rows or ln in in_rows:
                continue
            if row[0] == 'two' and T.head_key(row[1] or '') == \
                    'christmas day and following' and col in ('r2', 'r3'):
                continue                      # DOL_XMAS
            bpage = T.MATCH[ln][6] if ln in T.MATCH else None
            if verdict in ('marks', 'punct'):
                grp = 'DOL_MARKS' if verdict == 'marks' else 'DOL_FIX'
                new_v = dol_value(bv, cv)
                field_item(ctx, grp, rel, blk, cv, new_v, verdict, row, bv,
                           bpage)
            elif verdict == 'differs':
                j = T.judge(cv, bv, col)
                merged = (len(re.findall(r'[A-Z][a-z]+\.? \d', cv)) > 1 or
                          re.search(r'day:|\d{4,}', cv))
                if merged:
                    continue                  # a merged row: DOL_ROWS
                if j == 'cell-evident':
                    field_item(ctx, 'DOL_FIX', rel, blk, cv, dol_value(bv, cv),
                               'cell-evident', row, bv, bpage)
                elif j == 'disputed':
                    disputes.append((ln, row, col, cv, bv))
                else:
                    ctx.refuse(rel, blk, 'dol', '%s -> %s' % (cv, bv),
                               j, row[6] if False else None)
    return disputes, res, missing, book, cells


OK_V = ('exact', 'notation', 'marks', 'punct', 'glyph')


def book_row_text(b):
    """A book row in the repo's row form. The book's '----' (no psalm) is an
    empty field, as the repo already prints it."""
    def ps(v):
        v = dol_value(v, '')
        return '' if re.fullmatch(r'[-\u2013\u2014 ]*', v) else v
    fields = []
    for line in b[7]:
        for x in line:
            x = x.strip()
            if x.startswith('or ') and fields:
                fields[-1] += ' ' + dol_value(x, '')
            else:
                fields.append(dol_value(x, ''))
    fields = [f for f in fields if not re.fullmatch(r'[-\u2013\u2014 ]*', f)]
    return ' | '.join([b[2], 'Morning Psalms: ' + ps(b[3]),
                       'Evening Psalms: ' + ps(b[4])] + fields), len(b[7]) > 1


def head_text(b):
    """'Proper 11     Week of the Sunday closest to July 20' -> the repo's
    '### Proper 11 (Week of the Sunday closest to July 20)'."""
    P = B.pages()
    for ln in P[b[6]].split('\n'):
        ln = ln.strip()
        if T.head_key(ln) == T.head_key(b[1] or '') and ln.startswith(b[1]):
            parts = re.split(r'\s{2,}', ln)
            if len(parts) == 2:
                return '### %s (%s)' % (parts[0], parts[1])
            return '### ' + ln
    return '### ' + (b[1] or '')


def dol_rows(ctx, text, res, missing, book):
    """Row-level repairs, each a block item:
      * a lost week heading is put back before the first row of that week
        (the cell had filed the week's rows under the week before);
      * a merged row (two or more printed rows run together by the 1993
        keying, or a row the e-text flagged) is replaced by the book rows it
        swallowed: the row compare() gave it plus every unclaimed book row
        up to the next claimed one;
      * any other unclaimed book row is inserted before the next cell row;
      * the flags on those rows close with them."""
    rel = 'tables/daily-office-lectionary.md'
    blks = {b['line']: b for b in blocks(text)}
    verdict = collections.defaultdict(set)
    shape = collections.defaultdict(set)
    for r in res:
        verdict[r[0][6]].add(r[4])
        if r[4] == 'differs' and r[2] and r[3]:
            shape[r[0][6]].add(T.differs_class(r[2], r[3]))
    match = dict(T.MATCH)
    by_book = {id(b): l for l, b in match.items()}
    missing_ids = set(id(b) for b in missing)
    order = book
    pos = {id(b): i for i, b in enumerate(order)}
    closes = 0
    done_book = set()
    # rows in order
    cell_lines = sorted(match)
    misfiled_seen = set()
    for l in cell_lines:
        blk = blks.get(l)
        if not blk:
            continue
        b = match[l]
        t = blk['text']
        crows = [c for c in T.cell_dol(text=text) if c[6] == l]
        n_cell = len(crows[0][5]) if crows else 0
        n_book = len(b[7][0]) if b[7] else 0
        merged = ('VERIFY' in t or re.search(r'day:|\d{4,}', t) or
                  'merged' in shape[l] or
                  ('cell-lacks' in verdict[l] and n_cell != n_book))
        # 1. a lost heading: first row of a misfiled run
        if 'misfiled' in verdict[l]:
            wk = (b[0], T.head_key(b[1] or ''))
            if wk not in misfiled_seen:
                misfiled_seen.add(wk)
                prefix = t.split(' | ')[0] + ' | '
                if t.count(prefix) == 1:
                    ctx.add('DOL_ROWS', rel, blk, prefix,
                            head_text(b) + '\n\n' + prefix, 'lost-heading',
                            b[6], 'heading %s, p. %d' % (b[1], b[6]))
        # 2. a merged row: replaced by the rows it swallowed
        if merged:
            same = [x for x in order if x[0] == b[0]]
            i = same.index(b)
            run = [b]
            for nb in same[i + 1:]:
                if id(nb) in missing_ids:
                    run.append(nb)
                else:
                    break
            texts = []
            review = False
            for rb in run:
                tx, multi = book_row_text(rb)
                review = review or multi
                texts.append(tx)
                done_book.add(id(rb))
            # keep a lost heading the run crosses
            out = []
            prev_w = T.head_key(b[1] or '')
            for rb, tx in zip(run, texts):
                if T.head_key(rb[1] or '') != prev_w:
                    out.append(head_text(rb))
                    prev_w = T.head_key(rb[1] or '')
                out.append(tx)
            new = '\n\n'.join(out)
            nfl = t.count('<!-- VERIFY')
            closes += nfl
            ctx.add('DOL_ROWS', rel, blk, t, new, 'merged-row', b[6],
                    'book rows %s, p. %d' % (', '.join(
                        '%s/%s' % (T.head_key(x[1] or ''), x[2]) for x in run),
                        b[6]), {'flags_closed': nfl, 'review': review})
    # 3. unclaimed book rows not taken by a merged row: insert before the
    #    next claimed row's cell line
    for nb in order:
        if id(nb) not in missing_ids or id(nb) in done_book:
            continue
        same = [x for x in order if x[0] == nb[0]]
        i = same.index(nb)
        nxt = next((x for x in same[i + 1:] if id(x) in by_book), None)
        if not nxt:
            ctx.refuse(rel, {'line': 0}, 'dol-row', '%s/%s/%s' % (
                nb[0], nb[1], nb[2]), 'no anchor row', nb[6])
            continue
        l = by_book[id(nxt)]
        blk = blks[l]
        prefix = blk['text'].split(' | ')[0] + ' | '
        tx, multi = book_row_text(nb)
        head = ''
        if T.head_key(nb[1] or '') != T.head_key(nxt[1] or ''):
            head = ''
        ctx.add('DOL_ROWS', rel, blk, prefix, tx + '\n\n' + prefix, 'lost-row',
                nb[6], 'book row %s/%s, p. %d' % (nb[1], nb[2], nb[6]),
                {'review': multi})
        done_book.add(id(nb))
    # 4. flag blocks that stand alone (the merged Proper 4 heading)
    for l, blk in blks.items():
        if blk['kind'] == 'comment' and 'VERIFY' in blk['text']:
            if 'merges a reading line into this week heading' in blk['text']:
                ctx.add('DOL_ROWS', rel, blk, blk['text'], '', 'flag', None,
                        '(flag closed: the heading is restored)',
                        {'flags_closed': 1})
                closes += 1
        if blk['kind'] == 'heading' and '(=' in blk['text']:
            yr = 'one' if text.find('## Year Two') < 0 or \
                text.find(blk['text']) < text.find('## Year Two') else 'two'
            hb = next((b for b in book if b[0] == yr and
                       T.head_key(b[1] or '') == T.head_key(blk['text'][4:])), None)
            if hb:
                ctx.add('DOL_ROWS', rel, blk, blk['text'], head_text(hb),
                        'heading', hb[6], 'heading %s, p. %d' % (hb[1], hb[6]))
    return [closes]


def xmas(ctx, text, res):
    """Year Two, Christmas Day and Following: rows that print Year One's
    Epistle and Gospel (the Old Testament lesson is Year Two's). Fields are
    paired by column with the book's row for the same occasion."""
    rel = 'tables/daily-office-lectionary.md'
    blks = {b['line']: b for b in blocks(text)}
    for c in T.cell_dol(text=text):
        if c[0] != 'two' or T.head_key(c[1] or '') != 'christmas day and following':
            continue
        b = T.MATCH.get(c[6])
        if not b or not b[7] or len(b[7][0]) != len(c[5]) or len(b[7]) > 1:
            continue
        blk = blks.get(c[6])
        for j in (1, 2):
            if j >= len(c[5]):
                continue
            cv, bv = c[5][j], b[7][0][j]
            if T.level(cv, bv):
                continue
            field_item(ctx, 'DOL_XMAS', rel, blk, cv, dol_value(bv, cv),
                       'year-two-xmas', c, bv, b[6])


CIT = re.compile(r'^(?:([1-3]) )?([A-Z][a-z]+)\.? (\d+):(\d+)[ab]?(?:-(?:(\d+):)?(\d+))?')


def parse_cit(c):
    m = CIT.match((c or '').strip())
    if not m:
        return None
    bookn = (m.group(1) or '') + m.group(2)[:3].lower()
    ch, v1 = int(m.group(3)), int(m.group(4))
    ch2 = int(m.group(5)) if m.group(5) else ch
    v2 = int(m.group(6)) if m.group(6) else v1
    return bookn, ch, v1, ch2, v2


def second_check(disputes, book, cells):
    """For each numeral dispute: (a) the other year's same occasion (the
    psalms are the same in both years), (b) the same citation elsewhere in
    the book's table and in the cell, (c) continuity with the row before and
    after in the same column of the book."""
    idx = {(b[0], T.head_key(b[1] or ''), T.day_key(b[2])): b for b in book}
    seq = collections.defaultdict(list)
    for b in book:
        seq[b[0]].append(b)
    allb = collections.Counter(T.norm(x) for b in book for x in [b[3], b[4]] + b[5])
    allc = collections.Counter(T.norm(x) for c in cells for x in [c[3], c[4]] + c[5])
    cidx = {(c[0], T.head_key(c[1] or ''), T.day_key(c[2])): c for c in cells}
    out = []
    for ln, row, col, cv, bv in disputes:
        res = {'line': ln, 'occasion': '%s / %s / %s' % (row[0], row[1], row[2]),
               'column': col, 'cell': cv, 'book': bv, 'checks': {}}
        oy = 'two' if row[0] == 'one' else 'one'
        other = idx.get((oy, T.head_key(row[1] or ''), T.day_key(row[2])))
        cother = cidx.get((oy, T.head_key(row[1] or ''), T.day_key(row[2])))
        if col in ('mp', 'ep') and other:
            # the psalms are the same in both years: does each source agree
            # with ITSELF across the two years, and with the other source?
            ov = other[3] if col == 'mp' else other[4]
            cov = (cother[3] if col == 'mp' else cother[4]) if cother else None
            b_self = T.punct(ov) == T.punct(bv)
            c_self = cov is not None and T.punct(cov) == T.punct(cv)
            res['checks']['other_year'] = (
                'neither' if b_self and c_self else
                'book' if b_self or (cov is not None and T.punct(cov) == T.punct(bv))
                else 'cell' if c_self or T.punct(ov) == T.punct(cv) else 'neither')
        res['checks']['elsewhere'] = {
            'cell_reading_in_book': allb[T.norm(cv)],
            'book_reading_in_book': allb[T.norm(bv)] - 1,
            'cell_reading_in_cell': allc[T.norm(cv)] - 1}
        if col.startswith('r'):
            me = idx.get((row[0], T.head_key(row[1] or ''), T.day_key(row[2])))
            if me:
                s_ = seq[row[0]]
                i = s_.index(me)
                pc, cc, bc = None, parse_cit(cv), parse_cit(bv)
                verdict = []
                for nb in (s_[i - 1] if i > 0 else None,
                           s_[i + 1] if i + 1 < len(s_) else None):
                    if not nb:
                        continue
                    for x in nb[5]:
                        px = parse_cit(x)
                        if not px or not (cc or bc):
                            continue
                        for name, pv in (('cell', cc), ('book', bc)):
                            if not pv or px[0] != pv[0]:
                                continue
                            if nb is s_[i - 1] and (px[3], px[4] + 1) == (pv[1], pv[2]):
                                verdict.append(name)
                            if nb is not s_[i - 1] and (pv[3], pv[4] + 1) == (px[1], px[2]):
                                verdict.append(name)
                res['checks']['continuity'] = sorted(set(verdict)) or 'none'
        ck = res['checks']
        sup = []
        if ck.get('other_year') in ('book', 'cell'):
            sup.append(ck['other_year'])
        if isinstance(ck.get('continuity'), list):
            sup.extend(ck['continuity'])
        e = ck['elsewhere']
        if e['cell_reading_in_book'] and not e['book_reading_in_book']:
            sup.append('cell')
        if e['book_reading_in_book'] and not e['cell_reading_in_book'] and \
                not e['cell_reading_in_cell']:
            sup.append('book')
        res['supports'] = ('book' if sup and set(sup) == {'book'} else
                           'cell' if sup and set(sup) == {'cell'} else
                           'split' if sup else 'none')
        out.append(res)
    return out


def dol_value(bv, cv):
    """The book's citation in the repo's notation: the en-dash span as '-'
    (R13 keeps the extent, the repo writes its hyphen); the book's marks."""
    v = bv.replace('\u2013\u2013', '-').replace('\u2013', '-').replace('\u2014', '-')
    v = re.sub(r'-{2,}', '-', v)
    v = re.sub(r'(?<=\d) (?=\d)', '', v)          # the layer's '12:1-1 4'
    v = re.sub(r' +(?=\*)', '', v)                 # '72 **'
    v = re.sub(r'([;,])(?=[^\s])', r'\1 ', v)       # a dropped space
    return v.strip()


def field_item(ctx, grp, rel, blk, cv, new_v, cls, row, bfrag, page=None):
    """Key a citation by its field separators (' | ', ': ', ' or ', the
    line's end), so it is never a bare substring."""
    t = blk['text']
    rx = re.compile(r'(?:(?<= \| )|(?<=: )|(?<= or ))' + re.escape(cv) +
                    r'(?= \| | or |,? or |$|\n)', re.M)
    hits = list(rx.finditer(t))
    if len(hits) != 1:
        ctx.refuse(rel, blk, cls, cv, 'field-not-unique')
        return
    m = hits[0]
    s0 = max(0, m.start() - 3)
    e0 = min(len(t), m.end() + 3)
    old = t[s0:e0]
    if t.count(old) != 1:
        ctx.refuse(rel, blk, cls, cv, 'field-not-unique')
        return
    new = t[s0:m.start()] + new_v + t[m.end():e0]
    if old == new:
        return
    ctx.add(grp, rel, blk, old, new, cls, page,
            '%s / %s / %s: %s' % (row[0], row[1], row[2], bfrag))


def main():
    ctx = Ctx()
    prose(ctx)
    markup(ctx)
    collects(ctx)
    headings(ctx)
    disputes, res, missing, book, cells = dol(ctx)
    checked = second_check(disputes, book, cells)
    # a dispute the second check settles for the book becomes an item in
    # its own group (off unless ruling 10 says the check is enough); fields
    # are paired by column with the book row compare() gave the cell row
    rel = 'tables/daily-office-lectionary.md'
    text = base_text(rel)
    blks = {b['line']: b for b in blocks(text)}
    for d in checked:
        if d['supports'] != 'book':
            continue
        b = T.MATCH.get(d['line'])
        c = next((x for x in cells if x[6] == d['line']), None)
        if not b or not c:
            continue
        if d['column'] in ('mp', 'ep'):
            bv = b[3] if d['column'] == 'mp' else b[4]
        else:
            j = int(d['column'][1:]) - 1
            if not b[7] or len(b[7]) > 1 or j >= len(b[7][0]) or \
                    len(b[7][0]) != len(c[5]):
                continue
            bv = b[7][0][j]
        if T.norm(bv) != T.norm(d['book']):
            continue                          # the pairing disagrees: leave it
        field_item(ctx, 'DOL_DISPUTED', rel, blks[d['line']], d['cell'],
                   dol_value(bv, d['cell']), 'dispute-book', c, bv, b[6])
    # page for DOL items: the book row's page
    pg_of = {}
    for r in res:
        pass
    groups = {g: v for g, v in ctx.items.items()}
    with open(OUT_ITEMS, 'w', encoding='utf-8') as f:
        f.write('"""wxa_witness_items.py -- GENERATED by wxa_items.py; do not '
                'edit by hand.\n\nEvery keyed correction for the 1979 cells, '
                'by group. Each item: id, file, line (of its\nparagraph at the '
                'branch base), anchor (that paragraph\'s first words), old (the\n'
                'reading replaced, exactly once in its paragraph), new, class, '
                'page.\n"""\n\nITEMS = ')
        import pprint
        f.write(pprint.pformat(groups, width=100, sort_dicts=False))
        f.write('\n')
    json.dump(ctx.ev, open(OUT_EV, 'w'), indent=1, ensure_ascii=False)
    json.dump({'dropped': ctx.drop,
               'dol_disputes': checked},
              open(OUT_DROP, 'w'), indent=1, ensure_ascii=False)
    tot = collections.Counter()
    for g, v in sorted(groups.items()):
        cl = collections.Counter(i['class'] for i in v)
        print('%-14s %4d  %s' % (g, len(v), dict(cl)))
    dr = collections.Counter((d['class'], d['reason']) for d in ctx.drop)
    print('dropped: %d  %s' % (len(ctx.drop), dict(dr)))
    print('DOL disputes for second check: %d  supports: %s' % (
        len(checked), dict(collections.Counter(c['supports'] for c in checked))))
    print('DOL_ROWS flags closed: %d' % sum(getattr(ctx, 'dol_closes', [])))


if __name__ == '__main__':
    main()
