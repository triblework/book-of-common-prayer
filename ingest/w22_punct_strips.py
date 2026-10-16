"""w22_punct_strips.py -- crops of every place the page OCR's stop and the cell's
stop disagree (away from the cell's mediant), for the eye.

Workstream C, Phase 1b. From w22_align.json, every matched cell word other than
the pivot whose cell mark differs from the OCR mark ('other'). Each crop starts
at the word and runs to the end of its printed row; the label gives only the
verse, page and word -- not the cell's mark and not the OCR's -- so the eye
reads what the book prints without being told what to expect.
Positions are numbered (P001...) in verse order; w22_punct.py keys the eye
reads by that number and writes ingest/w22_punct.tsv.

    python3 ingest/w22_punct_strips.py      # -> <render>/strips/pu_NN.png
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w22_crops as C

PER = 40


def positions():
    recs, by = C.load()
    out = []
    for r in recs:
        for o in sorted(r['other'], key=lambda o: o['off']):
            out.append((r, o))
    return out


def main():
    pos = positions()
    items = []
    for k, (r, o) in enumerate(pos, 1):
        rect = C.rect_around(o['box'], o['rowbox'], None, None, o.get('mbox'),
                             o['rowbox'][0] + o['rowbox'][2] + 60)
        rect[2] = min(rect[2], 900)
        items.append({'label': 'P%03d %d:%d\nafter: %s' % (k, r['psalm'], r['verse'], o['word']),
                      'png': C.page_png(o['page']), 'rect': rect})
    for s in range(0, len(items), PER):
        C.strip(items[s:s + PER], 'pu_%02d' % (s // PER), cols=2)
    print('%d positions, %d strips' % (len(items), (len(items) + PER - 1) // PER))


if __name__ == '__main__':
    main()
