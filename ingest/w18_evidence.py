"""w18_evidence.py — build ingest/w18_evidence.json from the witness pages.

For every item in w18_witness.ITEMS, read the line twice: the page OCR
(w18_scan_ocr.json, the first read) and a fresh OCR of that line cropped out of
a 4400px render (the second read). The crop path is kept so the reading can be
checked by eye, and EYE[] records the items whose crop was in fact read by eye
in the wave -- every one that turns on a blank, and every psalter correction.

    python3 ingest/w18_evidence.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w18_read
import w18_render as R
import w18_witness as W

OUT = os.path.join(HERE, 'w18_evidence.json')

# Items whose crop was read by eye as well as by machine, and what was seen.
EYE = {
    'ps-2-12': 'the colon after "way" is clear at 4400px',
    'ps-68-1': 'read on the crop: "scattered : let them also that hate him"',
    'ps-89-50': 'read on the crop: verse 50 runs on into "praised be the Lord '
                'for evermore. Amen, and Amen." and "The xc. Psalm." follows',
    'king-mp': 'read on the page: "our most gracious soveraign Lord King Charles"',
    'royal-mp': 'read on the page: "A Prayer for" with nothing after it, and '
                'two blank lines between "to bless" and "Indue them"',
    'royal-ep': 'read on the page: the same unfinished title and the same blank',
    'royal-litany': 'read on the page: the petition breaks off after "preserve" '
                    'and the response follows a blank line',
    'royal-ordinal': 'read on the page: the petition breaks off after "preserve"',
    'sea-navy': 'read on the crop: "also vsed in his Majesties Navy every day"',
}


def main():
    rec = []
    for it in W.ITEMS:
        if it.get('box'):
            # Vision merges these lines into one garbled block, so the line
            # matcher has nothing to match; crop the printed block instead.
            top, left, h, w = it['box']
            crop = R.crop(R.page_png(it['page'], 4400), top, left, h, w, scale=2)
            got = {'first': '(page OCR merged this block)',
                   'second': w18_read.ocr(crop), 'crop': crop}
        else:
            got = w18_read.read_line(it['page'], it['needle'],
                                     span=it.get('span', 1), before=1)
        rec.append({
            'id': it['id'], 'kind': it['kind'], 'page': it['page'],
            'expect': it['expect'],
            'first': got['first'], 'second': got['second'],
            'crop': os.path.relpath(got['crop'], os.path.dirname(HERE)),
            'eye': EYE.get(it['id'], ''),
            'says': it['says'],
        })
        print('%-18s p%-4d %s' % (it['id'], it['page'], got['second'][:80]))
    json.dump(rec, open(OUT, 'w'), indent=1)
    print('%d items -> %s' % (len(rec), os.path.basename(OUT)))


if __name__ == '__main__':
    main()
