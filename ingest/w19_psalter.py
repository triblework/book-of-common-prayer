"""w19_psalter.py — collate the 1979 Psalter cell against the publisher's file.

Both sides are TEXT -- the carrier is justus's 1993 ASCII e-text, the witness
is Church Publishing's own PDF -- so unlike Waves 17 and 18 this is an exact
collation, not one limited by what OCR can see. Every verse is compared word
for word.

The witness's pages carry their structure in the line breaks, so the psalter is
parsed rather than aligned:

    The Psalter / Book One / First Day: Morning Prayer   <- furniture, dropped
    1   Beatus vir qui non abiit                         <- psalm + incipit
    1 Happy are they who have not walked in the counsel  <- verse, wrapping
    the wicked, *                                           over several lines
    Psalm 1   585                                        <- running foot

Comparison folds typography only: curly quotes to straight, en/em dashes, and
the mediant (the book prints "*", the cell prints " : " by the repo's
convention). Case is folded too -- the PDF's text layer renders the book's
small-capital LORD as "Lord", so this witness cannot testify about that.

Differences are reported here, never applied; w19_witness.py holds what this
wave changes.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells
import w19_witness_text as WT

FIRST, LAST = 585, 808

# Page furniture: running heads and feet, the day/office bands, the book
# divisions. "764   Psalm 119:9, 17" and "608   Psalms 20, 21" are feet too.
FURNITURE = re.compile(
    r'^(The Psalter|Book (One|Two|Three|Four|Five)|\d+|'
    r'\w+[- ]?\w* Day: (Morning|Evening) Prayer|'
    r'(\d+\s+)?Psalms? [\d:,\s]+(\s+\d+)?)$')

# Three heading shapes, all with the number/label separated from the Latin
# incipit by a run of spaces:
#   "1   Beatus vir qui non abiit"          a psalm
#   "18   Part 1   Diligam te, Domine."     a psalm printed in parts
#   "Psalm 18: Part II   Et retribuet mihi" its later part
#   "119   Aleph   Beati immaculati" / "Gimel   Retribue servo tuo"
#                                           Psalm 119's portions. The book
#                                           numbers its verses 1-176 straight
#                                           through, so a portion heading is
#                                           just a heading -- no renumbering.
# "1 Happy are they ..." -- and occasionally "9O Lord, give victory ...",
# where the extractor lost the space after the verse number.
VERSE = re.compile(r'^(\d+) ?(\S.*)$')
PSALM = re.compile(r'^(\d+)\s{2,}(?:Part \d+\s{2,})?(\S.*)$')
PART = re.compile(r'^Psalm (\d+): Part [IVX]+\s{2,}(\S.*)$')
LETTERS = ('Aleph Beth Gimel Daleth He Waw Zayin Heth Teth Yodh Kaph Lamedh '
           'Mem Nun Samekh Ayin Pe Sadhe Qoph Resh Shin Taw').split()
PORTION = re.compile(r'^(%s)\s{2,}(\S.*)$' % '|'.join(LETTERS))


def incipit_like(line):
    """A Latin incipit line: begins with a capital, a handful of words, no
    verse number, and none of the English function words a verse would use."""
    if not line or VERSE.match(line):
        return False
    if not re.match(r'^(Part \d+\s+)?[A-Z\u00c6\u00c8\u00c9]', line):
        return False
    body = re.sub(r'^Part \d+\s+', '', line)
    return (len(body.split()) <= 8
            and not re.search(r'\b(the|and|of|is|are|shall|who|you|your|for'
                              r'|with|that|will|my|his|their|from)\b',
                              body.lower()))


def parse():
    """-> ({psalm: {verse: text}}, {psalm: incipit}, {psalm: page})

    The book's layout varies: a psalm's number and its Latin incipit are
    usually one line ("1   Beatus vir qui non abiit") but sometimes two ("18"
    then "Part 1 Diligam te, Domine."), which is why the bare-number case
    needs a look-ahead rather than being dropped as a page number.
    """
    pgs = WT.pages()
    lines = []
    for n in range(FIRST, LAST + 1):
        for raw in (pgs.get(n) or '').split('\n'):
            lines.append((n, raw.strip()))
    verses, incipits, pages = {}, {}, {}
    ps = v = None
    skip = set()                    # incipit lines already taken by a heading
    for i, (n, line) in enumerate(lines):
        if not line or i in skip:
            continue
        nxt = next((x for _, x in lines[i + 1:i + 3] if x), '')
        m = PART.match(line)
        if m:                                       # "Psalm 18: Part II   ..."
            ps, v = int(m.group(1)), None
            continue
        if PORTION.match(line) and ps == 119:       # just a heading
            v = None
            continue
        bare = re.match(r'^(\d{1,3})$', line)
        if bare and int(bare.group(1)) == ps:
            continue        # a running head repeating the psalm we are inside
        if bare and 1 <= int(bare.group(1)) <= 150 and incipit_like(nxt):
            ps, v = int(bare.group(1)), None
            verses.setdefault(ps, {})
            incipits.setdefault(ps, re.sub(r'^Part \d+\s+', '', nxt))
            pages.setdefault(ps, n)
            skip.add(next(j for j in range(i + 1, i + 3) if lines[j][1]))
            continue
        if FURNITURE.match(line):
            continue
        m = PSALM.match(line)
        if m and incipit_like(m.group(2)):
            ps, v = int(m.group(1)), None
            verses.setdefault(ps, {})
            incipits.setdefault(ps, m.group(2).strip())
            pages.setdefault(ps, n)
            continue
        if ps is None:
            continue
        m = VERSE.match(line)
        if (m and ps == 119 and m.group(1) == '119' and v is not None
                and v != 118):
            # a running head merged into the line beneath it -- but verse 119
            # of Psalm 119 is real, and follows verse 118
            verses[ps][v] += ' ' + m.group(2)
            continue
        if m:
            v = int(m.group(1))
            verses.setdefault(ps, {})[v] = m.group(2)
        elif v is not None:
            verses[ps][v] += ' ' + line
    return verses, incipits, pages


def fold(t, mediant=' : '):
    t = WT.flat(t).replace(mediant, ' * ')
    t = re.sub(r"[^A-Za-z0-9'*]+", ' ', t)
    return re.sub(r'\s+', ' ', t).strip().lower()


def main():
    w_verses, w_incipits, w_pages = parse()
    cells = w17_cells.cells('1979')
    n_w = sum(len(v) for v in w_verses.values())
    n_c = sum(len(v) for v in cells.values())
    print('witness: %d psalms, %d verses; cell: %d psalms, %d verses'
          % (len(w_verses), n_w, len(cells), n_c))

    missing, extra, differ = [], [], []
    for ps in sorted(cells):
        wv = w_verses.get(ps, {})
        for v, text in sorted(cells[ps].items()):
            if v not in wv:
                missing.append((ps, v))
                continue
            if fold(text) != fold(wv[v], mediant=' * '):
                differ.append((ps, v, w_pages.get(ps), text, wv[v]))
        for v in sorted(wv):
            if v not in cells[ps]:
                extra.append((ps, v))
    print('verses the book has and the cell lacks: %d %s' % (len(extra), extra[:8]))
    print('verses the cell has and the book lacks: %d %s' % (len(missing), missing[:8]))
    print('verses whose words differ: %d' % len(differ))
    json.dump([{'psalm': p, 'verse': v, 'page': pg, 'cell': c, 'book': b}
               for p, v, pg, c, b in differ],
              open(os.path.join(HERE, 'w19_psalter_diff.json'), 'w'), indent=1)
    for p, v, pg, c, b in differ[:20]:
        print('  %3d:%-3d p%s\n     cell : %s\n     book : %s' % (p, v, pg, c[:110], b[:110]))
    return differ, w_incipits


if __name__ == '__main__':
    main()
