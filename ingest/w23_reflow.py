"""w23_reflow.py -- re-flow the hard-wrapped Prayers and Thanksgivings
(ruling 8). Run alone it is a dry run (prints what it would join, writes
nothing); w23_witness.expected() calls reflow() for stage 3, and
`w23_apply.py --stage 3 --write` writes the re-flowed cells (commit 3).

All 81 prayers-and-thanksgivings cells carry the 1993 e-text's 60-column
wrap as paragraph breaks (a blank line after every wrapped line), so each
published "paragraph" is a fragment and a word can be split across two
(`seed` / `time`). The re-flow joins consecutive prose blocks into one
paragraph until a block ends a prayer -- its last word is `Amen.` (the
e-text's `=Amen.=` too) -- or a heading, rubric or comment intervenes. A
wrapped line that ends inside a word the book prints whole is noted (it is
a WORDS item already, e.g. `seed` + `time` = `seedtime`).

Each joined paragraph is then aligned word for word against the book: the
dry run reports how many join into paragraphs the book prints verbatim.

    python3 ingest/w23_reflow.py                 # per-file counts, base text
    python3 ingest/w23_reflow.py --after-groups  # after every keyed group
"""
import collections
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w23_items as I

END = re.compile(r'(=?Amen\.=?|Amen\.\)?)\s*$')


def reflow(text, book_words=None):
    """-> (new text, breaks joined, paragraphs before, paragraphs after).
    Where the wrap split a word (`seed` | `time`), and the book prints the
    joined word in that place (`seedtime`, the words either side agreeing),
    the two halves are joined without a space."""
    bl = I.blocks(text)
    out_blocks, run = [], []
    joined = 0
    glued = []

    def join(parts):
        acc = parts[0].strip()
        for p in parts[1:]:
            p = p.strip()
            if book_words:
                lw = I.B.words(acc)[-2:]
                rw = I.B.words(p)[:2]
                if len(lw) == 2 and len(rw) == 2:
                    spaced = ' %s %s %s %s ' % (lw[0], lw[1], rw[0], rw[1])
                    glue = ' %s %s%s %s ' % (lw[0], lw[1], rw[0], rw[1])
                    if glue in book_words and spaced not in book_words:
                        glued.append(lw[1] + rw[0])
                        acc = acc + p
                        continue
            acc = acc + ' ' + p
        return acc

    def flush():
        nonlocal joined
        if run:
            joined += len(run) - 1
            out_blocks.append(join([b['text'] for b in run]))
            run.clear()
    for b in bl:
        if b['kind'] != 'prose':
            flush()
            out_blocks.append(b['text'])
            continue
        run.append(b)
        if END.search(b['text']):
            flush()
    flush()
    before = sum(1 for b in bl if b['kind'] == 'prose')
    after = before - joined
    reflow.glued = glued
    return '\n\n'.join(out_blocks) + '\n', joined, before, after


def main():
    import w23_book as B
    bk = B.Book()
    tot = collections.Counter()
    rows = []
    for f in sorted(glob.glob(os.path.join(WT, 'editions/1979/prayers-and-'
                                               'thanksgivings/*.md'))):
        rel = os.path.relpath(f, os.path.join(WT, 'editions/1979'))
        text = I.base_text(rel)
        if '--after-groups' in sys.argv:
            # the re-flow is the LAST step: every keyed item is keyed to a
            # base paragraph, so the items go in first, then the joins
            import w23_witness as W
            text, _a, _s = W.apply(rel, text, W.GROUP_ORDER, strict=False)
        new, joined, before, after = reflow(text, bk.joined)
        tot['glued'] += len(reflow.glued)
        exact = 0
        paras = [b for b in I.blocks(new) if b['kind'] == 'prose']
        for b in paras:
            w = [x[0] for x in I.cell_spans(b['text'])]
            r = I.locate_in(bk, rel, b['line'], None, [], w, [])
            if r and not [o for o in r[3] if o[0] != 'equal']:
                exact += 1
        rows.append((rel, joined, before, after, exact))
        tot.update({'joined': joined, 'before': before, 'after': after,
                    'exact': exact})
    print('%-62s %6s %6s %6s %8s' % ('file', 'joined', 'before', 'after',
                                     'verbatim'))
    for r in rows:
        print('%-62s %6d %6d %6d %8d' % (r[0][:62], r[1], r[2], r[3], r[4]))
    print('%-62s %6d %6d %6d %8d' % ('TOTAL (%d files)' % len(rows),
                                     tot['joined'], tot['before'], tot['after'],
                                     tot['exact']))
    print('words the wrap had split, joined without a space: %d'
          % tot['glued'])
    print('dry run: nothing written')


if __name__ == '__main__':
    main()
