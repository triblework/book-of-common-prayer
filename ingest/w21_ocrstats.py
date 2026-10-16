"""w21_ocrstats.py -- what the Psalter page OCR records are worth (Workstream B,
Phase 1). Read-only: reads ingest/w21_<pdf>_ocr.json and the 1928 Psalter
cells; writes nothing.

    python3 ingest/w21_ocrstats.py 1952 1929

Per record:
  * book page for every half (from the printed folio, a bare number on the
    last or first line), and the scan->book offset it implies;
  * lines per book page (distribution), halves with 0 lines;
  * suspicious gaps: a vertical gap between consecutive lines >= 1.8x that
    page's median pitch, NOT beside a heading line (a psalm or day heading
    sits in extra space) -- an upper bound on dropped lines;
  * word recall against the cells: for every word type, min(count in cells,
    count in OCR), summed, over the cells' token count. A dropped line loses
    its words, so 1 - recall bounds the loss (OCR misreadings count too);
  * merged lines: a line box >= 1.6x the page's median line height is two
    printed lines Vision fused into one (usually garbled); a crop re-read
    recovers them (checked on scan 204L), so Phase 2 re-reads every one;
  * mediant marks read: '*' and the glyphs Vision substitutes for a small
    raised asterisk (", ', bullet), against the cells' 2,508 verses.
"""
import collections, json, os, re, statistics, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w17_cells

HEAD = re.compile(r"^(Psalms? \d|Psalm\s*\S|The \w+ Day|THE \w+ DAY|Morning Prayer|Evening Prayer|"
                  r"BOOK [IVX]+|The Psalter|or Psalms|D?ay [\dIlı]|[A-Z' ]{6,}\.?$)")


# book page = 2*scan - OFF (left half), +1 (right half); read off the folios
# (w21_ocrstats prints the check). The Psalter is pp. 345-525 in both books
# ("The End of the Psalter." p. 525; p. 526 blank, looked at; p. 527 the
# Ordinal's half-title).
OFF = {'1952': 62, '1929': 40}
FIRST_PAGE, LAST_PAGE = 345, 525


def book_page(which, scan, side):
    return 2 * int(scan) - OFF[which] + (side == 'R')


def toks(s):
    s = s.replace('’', "'").replace('‘', "'")
    return re.findall(r"[a-z]+(?:'[a-z]+)?", s.lower())


def stats(which):
    rec = json.load(open(os.path.join(HERE, 'w21_%s_ocr.json' % which)))
    per, empty, gaps, folios, offs = [], [], 0, {}, collections.Counter()
    tall = 0
    ocr_words = collections.Counter()
    stars = other = 0
    for n in sorted(rec, key=int):
        r = rec[n]
        for side in 'LR':
            L = r[side]
            if not FIRST_PAGE <= book_page(which, n, side) <= LAST_PAGE:
                continue
            if not L:
                empty.append('%s%s' % (n, side)); continue
            per.append(len(L))
            fol = [l[0].strip() for l in (L[-1], L[0]) if re.fullmatch(r'\d{3}', l[0].strip())]
            if fol:
                b = int(fol[0]); folios['%s%s' % (n, side)] = b
                offs[(b - (2 * int(n) if side == 'L' else 2 * int(n) + 1))] += 1
            hs = sorted(l[4] for l in L)
            tall += sum(1 for l in L if l[4] >= 1.6 * hs[len(hs) // 2])
            ys = [l[2] for l in L]
            pitch = [b - a for a, b in zip(ys, ys[1:])]
            if len(pitch) > 3:
                med = statistics.median(pitch)
                for k, p in enumerate(pitch):
                    # not the running head (first line), not the folio (last),
                    # not beside a heading: those sit in extra space by design
                    if k == 0 or k + 1 == len(pitch):
                        continue
                    if p >= 1.8 * med and not (HEAD.match(L[k][0]) or HEAD.match(L[k + 1][0])):
                        gaps += 1
            for l in L:
                if HEAD.match(l[0]) or re.fullmatch(r'\s*\d+\s*', l[0]):
                    continue
                t = re.sub(r'(\w)- *$', r'\1', l[0])
                ocr_words.update(toks(l[0]))
                stars += l[0].count('*')
                other += len(re.findall(r'["“”•\'](?= [a-z])', l[0]))
    return rec, per, empty, gaps, folios, offs, ocr_words, stars, other, tall


def main(whiches):
    cells = w17_cells.cells('1928')
    text = ' '.join(cells[p][v] for p in cells for v in cells[p])
    cw = collections.Counter(toks(text.replace('-', ' ')))
    N = sum(cw.values())
    for which in whiches:
        rec, per, empty, gaps, folios, offs, ow, stars, other, tall = stats(which)
        dist = collections.Counter(per)
        rec_ = sum(min(c, ow[w]) for w, c in cw.items()) / float(N)
        print('== %s: scan pages in record %d (%s-%s); Psalter pp. %d-%d = %d book pages, %d with text' % (
            which, len(rec), min(rec, key=int), max(rec, key=int), FIRST_PAGE, LAST_PAGE,
            LAST_PAGE - FIRST_PAGE + 1, len(per)))
        print('   halves with 0 lines: %s' % (empty or 'none'))
        print('   lines per half: min %d, median %d, max %d; distribution %s' % (
            min(per), statistics.median(per), max(per), sorted(dist.items())))
        print('   folios read %d; scan->book offset (book - 2*scan[+1]) %s' % (len(folios), dict(offs)))
        print('   suspicious gaps (>=1.8x pitch, not at a heading): %d' % gaps)
        print('   merged lines (box >= 1.6x median height): %d' % tall)
        print('   word recall vs the cells: %.2f%% of %d tokens' % (100 * rec_, N))
        print('   asterisks read %d, quote/bullet glyphs before a word %d; cells have 2508 verses'
              % (stars, other))


if __name__ == '__main__':
    main(sys.argv[1:] or ['1952', '1929'])
