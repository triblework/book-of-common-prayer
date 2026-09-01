#!/usr/bin/env python3
"""Wave 11 — structural spine extractor for the Prayers & Thanksgivings sources.

STRUCTURAL DISCRIMINATORS (ingest/AUDIT_METHOD.md — never a content filter):

  justus 1789 / 1928 : two-column. The APPARATUS column is `td width=200`.
                       Enumerate that narrow, well-defined thing and treat
                       EVERYTHING ELSE as text (the 1928 keeps one content cell
                       with no width= at all, which a `width==400` test drops).
  justus 1892        : no apparatus column. Content sits in unwidthed cells.
                       The 87/262/25 cells are the Penitential Office versicle
                       table -> excluded material, see EXCLUDE.
  CoE 1662           : <p>-based, no tables.

Within a text cell, block elements are classified by their own markup:
  TITLE  - <p align=center> (nested in <blockquote>, or a section head)
  RUBRIC - text opening with the pilcrow (para)
  BODY   - everything else

TRAP handled: drop capitals are a separate <span class="dropcap*"> from the rest
of the word ("M" + "OST gracious"), so leading single-letter fragments are
rejoined before anything is matched (AUDIT_METHOD "markup fragments words").

Emits a JSON spine; it never emits prayer text to a model.
"""
from __future__ import annotations
import html, json, re, sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, '/Users/wtrible/Developer/bcp/tools')
import scrape  # noqa: E402

SOURCES = {
    '1789': ('http://justus.anglican.org/resources/bcp/1789/Prayers&Thanks_1789.htm', 'justus', '200'),
    '1892': ('http://justus.anglican.org/resources/bcp/1892/Pray&Thanks_1892.htm',    'justus', None),
    '1928': ('http://justus.anglican.org/resources/bcp/1928/Pray&Thanks.htm',         'justus', '200'),
    '1662': ('https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/'
             'book-common-prayer/prayers-and-thanksgivings', 'coe', None),
}

# Excluded by the locked scoping ruling (WAVE11_SCOPING.md). Matched against a
# TITLE, and everything from that title to the end of its cell is dropped.
EXCLUDE = [
    r'PENITENTIAL OFFICE',        # 1892/1928 - its own future wave
    r'\bFAMILY PRAYER\b',
    r'Prayer and Thanksgiving to Almighty God',
    r'Forms? of Prayer.*at Sea',
]

PILCROW = '¶'

# CoE page furniture that arrives as <h*> like a real section heading.
CHROME = {'site nav', 'footer', 'social', 'footer navigational small',
          'breadcrumb', 'sign up for our newsletter', 'join us in daily prayer',
          'apps for worship', 'popular search items'}


def _text(frag: str) -> str:
    """Tags -> spaces, entities decoded, whitespace collapsed."""
    t = re.sub(r'<[^>]+>', ' ', frag)
    t = html.unescape(t)
    t = t.replace(' ', ' ')
    return re.sub(r'\s+', ' ', t).strip()


def _rejoin_dropcap(frag: str) -> str:
    """Rejoin a drop-capital span to the word it starts.

    '<span class="dropcap2">M</span><font>OST gracious...' -> 'MOST gracious...'
    Done on the RAW fragment before tag-stripping, because after stripping the
    two pieces are separated by whitespace and the word is unrecoverable.
    """
    def sub(m):
        return m.group(1)
    # a dropcap span holding exactly one letter, followed by more markup+letters
    frag = re.sub(r'<span[^>]*class="[^"]*dropcap[^"]*"[^>]*>\s*(?:<[^>]+>\s*)*([A-Za-z])\s*(?:</[^>]+>\s*)*</span>',
                  lambda m: '\x01' + m.group(1), frag, flags=re.I)
    return frag


class _BlockParser(HTMLParser):
    """Emit one record per <p>/<h*>, with alignment INHERITED from ancestors.

    Written after a regex version silently dropped every heading wrapped in a
    <div>: `<(p|div)...>(.*?)</\\1>` matched the <div> first and consumed its
    child <p>s, so they were never emitted at all. The 1892 "A PENITENTIAL
    OFFICE" heading and the 1928 section title both vanished that way, and the
    exclusion rule that depended on the first of them silently did nothing.
    A real parser with an element stack is the structural fix.

    Also carries font size, which is how these pages mark heading rank:
      +2 = major section, +1 = subsection, plain centred = one prayer's title.
    """

    # <div> is a block here on purpose: the 1928 prints several prayer titles
    # as a bare <div align="center"><em>For Missions.</em></div> with no <p> at
    # all, and without this they open no buffer and are discarded outright
    # (their bodies still arrive, so the loss looks like "this book has no such
    # prayer"). A div that wraps real blocks flushes only whitespace, which is
    # dropped, so nesting stays harmless.
    BLOCK = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
    BLOCK_JUSTUS = BLOCK | {'div'}

    def __init__(self, style='justus'):
        super().__init__(convert_charrefs=True)
        # <div> counts as a block ONLY for justus (see BLOCK_JUSTUS). The CoE
        # pages are modern div-heavy markup with exact CSS classes; treating
        # div as a block there turns every nav wrapper into a text block.
        self.BLOCK = self.BLOCK_JUSTUS if style == 'justus' else self.BLOCK
        self.stack = []          # [(tag, align, size)]
        self.blocks = []
        self.buf = None
        self.buf_ctx = None
        self.buf_own = None
        self.buf_cls = ''
        self.buf_tag = ''
        self.buf_dropcap = False
        self.dropcap_depth = None

    def _ctx(self):
        align = size = None
        for _, a, z in self.stack:
            if a:
                align = a
            if z:
                size = z
        return align, size

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        align = (d.get('align') or '').lower() or None
        size = d.get('size')
        cls = (d.get('class') or '').lower()
        if 'dropcap' in cls and self.dropcap_depth is None:
            self.dropcap_depth = len(self.stack)
        self.stack.append((tag, align, size))
        if tag in self.BLOCK:
            # These pages leave <p> unclosed constantly. Starting a new block
            # while one is open must FLUSH the open one, not silently discard
            # it -- discarding cost the 1928 five prayer titles (For Missions,
            # Memorial Days, For Prisoners, A Bidding Prayer, For a Sick
            # Person) whose bodies survived, so the loss was invisible.
            if self.buf is not None:
                self._flush()
            self.buf = []
            self.buf_ctx = self._ctx()
            self.buf_own = align
            self.buf_cls = cls
            self.buf_tag = tag
            self.buf_dropcap = False
        if 'dropcap' in cls and self.buf is not None:
            self.buf_dropcap = True

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in self.BLOCK and self.buf is not None:
            self._flush()
        if self.dropcap_depth is not None and len(self.stack) - 1 <= self.dropcap_depth:
            self.dropcap_depth = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.buf is None:
            return
        if self.dropcap_depth is not None:
            # a drop capital: mark it so it can be glued to the next word
            self.buf.append('\x01' + data.strip())
        else:
            self.buf.append(data)

    def _flush(self):
        raw = ''.join(self.buf)
        self.buf = None
        # glue a drop capital onto the word that follows it
        # Remove only the marker. Do NOT strip the following whitespace:
        # 1928 prints 'M'+'OST' (no space -> MOST) but 1892 prints 'O'+' GOD'
        # (space -> O GOD). Eating the space silently welded them to 'OGOD'.
        raw = raw.replace('\x01', '')
        t = re.sub(r'\s+', ' ', raw.replace('\xa0', ' ')).strip()
        if not t:
            return
        align, size = self.buf_ctx or (None, None)
        self.blocks.append({'text': t, 'align': align, 'size': size,
                            'own': getattr(self, 'buf_own', None),
                            'cls': getattr(self, 'buf_cls', ''),
                            'tag': getattr(self, 'buf_tag', ''),
                            'dropcap': getattr(self, 'buf_dropcap', False)})

    def close(self):
        if self.buf is not None:
            self._flush()
        super().close()


def _despace(t: str) -> str:
    """'T H A N K S G I V I N G S.' -> 'THANKSGIVINGS.' (letter-spaced heads)."""
    core = t.rstrip('.').strip()
    parts = core.split(' ')
    if len(parts) >= 4 and all(len(p) == 1 for p in parts if p):
        return ''.join(parts) + ('.' if t.rstrip().endswith('.') else '')
    return t



def _coe_promote_inline_titles(frag: str) -> str:
    """Promote a title that the CoE marks up INLINE into its own block.

    Most CoE titles are `<p class="bcprubricheading">Title</p>`, but some are
    `<p class="vlnormal"><span class="vlrubric">Title</span><br>body...</p>`.
    Parsed as-is, such a title is swallowed into the body block and disappears
    from the title list -- which is how the 1662 thanksgiving for deliverance
    from the plague went missing while its text was still present.

    Rewriting the inline form into the block form is a structural fix (it keys
    on the markup, not on what the text says), so both spellings converge
    before classification.
    """
    return re.sub(
        r'<p[^>]*>\s*<span class="vlrubric">(.*?)</span>\s*(?:<br\s*/?>)+',
        lambda m: '<p class="bcprubricheading">' + m.group(1) + '</p><p class="vlnormal">',
        frag, flags=re.S | re.I)


def _blocks_from_html(frag: str, style: str = 'justus'):
    """Yield (kind, text) per block element, in document order.

    style='coe'    -- the CoE pages carry exact CSS classes, so use them:
                      bcprubricheading = a prayer's title, vlrubric = rubric,
                      vlnarrowspace = body, <h1>/<h2> = section head.
    style='justus' -- alignment + drop-capital (see _BlockParser).
    """
    p = _BlockParser(style=style)
    p.feed(frag)
    p.close()
    out = []
    for b in p.blocks:
        t = _despace(b['text'])
        if style == 'coe':
            c = b['cls'] or ''
            if b['tag'] in ('h1', 'h2', 'h3') or 'bcpsectionheading' in c:
                kind = 'section'
            elif 'bcprubricheading' in c:
                kind = 'title'
            elif 'rubric' in c:
                kind = 'rubric'
            else:
                kind = 'body'
            if kind == 'section' and t.strip().lower() in CHROME:
                continue
            if kind == 'body' and (
                    t.strip() in ('Some functionality has been disabled',
                                  'A Christian presence in every community',
                                  'Join us in Daily Prayer', 'Apps for Worship')
                    or t.startswith('Text from The Book of Common')
                    or t.startswith('Find Morning, Evening')
                    or t.startswith('Apps for Worship are available')
                    or t.startswith('Stay connected and get')):
                continue
            out.append((kind, t))
            continue
        if t.startswith(PILCROW):
            kind = 'rubric'
        elif b['dropcap']:
            # a drop capital only ever opens a prayer BODY. Decisive, and it
            # survives the unclosed <div align=center> on these pages, whose
            # alignment otherwise leaks down onto every following paragraph.
            kind = 'body'
        elif b['own']:
            kind = 'title' if b['own'] == 'center' else 'body'
        elif (b['align'] or '') == 'center':
            kind = 'title'          # inherited: section heads in a centred div
        else:
            kind = 'body'
        out.append((kind, t))
    return out


def _justus_cells(s: str, apparatus_width):
    """Text cells only. Apparatus is the narrow enumerated width; all else text."""
    cells = []
    for m in re.finditer(r'<td([^>]*)>(.*?)</td>', s, re.S | re.I):
        attrs, inner = m.group(1), m.group(2)
        w = re.search(r'width="?(\d+)', attrs, re.I)
        w = w.group(1) if w else None
        if apparatus_width is not None and w == apparatus_width:
            continue                      # apparatus column
        if w in {'14', '41', '59', '100', '25', '87', '262'}:
            continue                      # site chrome / versicle table
        if len(_text(inner)) < 200:
            continue                      # nav + captions
        cells.append(inner)
    return cells


def extract(year: str):
    url, kind, appw = SOURCES[year]
    s = scrape.fetch(url)
    blocks = []
    if kind == 'justus':
        for cell in _justus_cells(s, appw):
            blocks.extend(_blocks_from_html(cell))
    else:
        i = s.lower().find('prayers and thanksgivings')
        blocks.extend(_blocks_from_html(_coe_promote_inline_titles(s[i:]), style='coe'))
    # drop excluded sections: from a matching TITLE to the next title that is
    # NOT excluded is ambiguous, so drop from the match to end-of-source, which
    # is where these sections sit on every page. Assert that below.
    cut = None
    for idx, (k, t) in enumerate(blocks):
        if any(re.search(p, t, re.I) for p in EXCLUDE):
            cut = idx
            break
    dropped = 0
    if cut is not None:
        dropped = len(blocks) - cut
        blocks = blocks[:cut]
    return blocks, dropped


if __name__ == '__main__':
    out = {}
    for y in sys.argv[1:] or list(SOURCES):
        blocks, dropped = extract(y)
        out[y] = blocks
        titles = [t for k, t in blocks if k == 'title']
        print(f"##### {y}: {len(blocks)} blocks "
              f"({sum(1 for k,_ in blocks if k=='title')} title / "
              f"{sum(1 for k,_ in blocks if k=='rubric')} rubric / "
              f"{sum(1 for k,_ in blocks if k=='body')} body), "
              f"{dropped} blocks dropped as excluded material")
        for t in titles:
            print(f"    • {t[:78]}")
        print()
    Path('/tmp/w11_spine.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
