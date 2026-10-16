"""w22_evidence.py -- write ingest/w22_evidence.json, one record per finding.

Workstream C, Phase 1b. Wave 17's shape (key -> {page, eye|auto, read, ...}),
with the read kind stated: every item here is 'eye' -- read off a 4400px crop
of the scan (the strip is named), never from OCR. Keys are the tags
w22_witness.edits_for() gives each keyed correction, plus the open flag:

  '<p>:<v>:mediant'           POINTING_MOVE / POINTING_SEMI
  '<p>:<v>:word:<key>'        WORDS
  '<p>:<v>:punct:<id>'        PUNCT (id = the w22_punct.tsv row)
  '<p>:<v>:spacing:<key>'     SPACING
  '1:3:water-side'            the open flag (not a correction)

Short fragments only (the eye's read of a few words), never a passage.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w22_words_eye as WE

OUT = os.path.join(HERE, 'w22_evidence.json')

MEDIANT = {
    '39:14:mediant': {'page': 402, 'eye': "thee, and a so-|journer : as all",
                      'strip': 'mq_06 (and pivot_nocolon_00)', 'group': 'POINTING_MOVE',
                      'note': "the book's colon follows 'sojourner'; 'thee' carries a comma"},
    '100:2:mediant': {'page': 475, 'eye': "is God; it is he ... we ourselves : we are",
                      'strip': 'mq_14 (and pivot_nocolon_00)', 'group': 'POINTING_MOVE',
                      'note': "the book's colon follows 'ourselves'; 'God' carries a semicolon"},
    '107:1:mediant': {'page': 487, 'eye': "he is gracious ; and his mercy",
                      'strip': 'mq_15; 3x zoom look/p487_10701x3', 'group': 'POINTING_SEMI',
                      'note': 'a semicolon at the pivot; no colon anywhere in the verse'},
    '139:7:mediant': {'page': 525, 'eye': "thou art there ; if I go",
                      'strip': 'mq_19; 3x zoom look/p525_13907x3', 'group': 'POINTING_SEMI',
                      'note': 'a semicolon at the pivot; no colon anywhere in the verse'},
}


def _pages():
    import w22_crops as C
    recs, by = C.load()
    return {'%d:%d' % k: (r.get('pivot') or {}).get('page') or r.get('page') for k, r in by.items()}


def main():
    import w22_witness as K
    ev = dict(MEDIANT)
    # WORDS: from the eye reads of the candidate rows (wd_NN strips)
    by = {}
    for n, (ref, page, cellf, book, verdict) in WE.READ.items():
        if verdict == 'differs':
            by.setdefault(ref, []).append((n, page, cellf, book))
    import w22_eye_2 as E2
    um_words = {}            # Phase 2: WORDS found by the unmatched-word pass
    for k, strip in E2.UM.items():
        for uid, (cellw, bookw) in strip['differs'].items():
            um_words[uid] = (k, cellw, bookw)
    UM_WORDS = {(22, 7): 'U083', (68, 31): 'U265', (75, 9): 'U301', (106, 37): 'U411',
                (109, 4): 'U428'}
    pages = _pages()
    for p, v, key, new in K.WORDS:
        ref = '%d:%d' % (p, v)
        if (p, v) in UM_WORDS and key not in [r[2] for r in by.get(ref, [])]:
            uid = UM_WORDS[(p, v)]
            k, cellw, bookw = um_words[uid]
            ev['%s:word:%s' % (ref, key)] = {'page': pages[ref], 'eye': bookw,
                                              'strip': 'um_%02d' % k, 'read': uid,
                                              'group': 'WORDS',
                                              'found_by': 'eye pass over the cell words the '
                                                          'alignment left unmatched (Phase 2)'}
            continue
        hit = next((r for r in by.get(ref, []) if key.split()[-1].rstrip(',') in r[2]
                    or key in r[2]), None)
        if hit is None:
            hit = by[ref][0]
        n, page, cellf, book = hit
        ev['%s:word:%s' % (ref, key)] = {'page': page, 'eye': book, 'strip': 'wd_%02d' % ((n - 1) // 20),
                                          'read': 'W%02d' % n, 'group': 'WORDS',
                                          'found_by': 'two page OCRs (4400px, 2400px) agree on a real word'}
    # PUNCT: one record per keyed correction, from the TSV row
    rows = {}
    for line in open(os.path.join(HERE, 'w22_punct.tsv'), encoding='utf-8'):
        if not line.startswith('#'):
            f = line.rstrip('\n').split('\t')
            rows[f[0]] = f
    extra = {e[4]: e for e in K.PUNCT_EXTRA}
    for p, v, old, new, pid in K.PUNCT:
        if pid in extra:
            k = next(k for k, st in E2.UM.items() if pid in st['differs'])
            ev['%d:%d:punct:%s' % (p, v, pid)] = {
                'page': pages['%d:%d' % (p, v)], 'eye': E2.UM[k]['differs'][pid][1],
                'cell': old, 'strip': 'um_%02d' % k, 'source': 'unmatched-word pass (Phase 2)',
                'group': 'PUNCT', 'class': 'found by eye on a whole-row crop'}
            continue
        f = rows[pid]
        strip = ('pu_%02d' % ((int(pid) - 1) // 40)) if pid.isdigit() else 'mq (whole verse)'
        ev['%d:%d:punct:%s' % (p, v, pid)] = {
            'page': int(f[2]) if f[2] else None, 'eye': f[5], 'cell': f[4], 'ocr': f[6],
            'class': f[8], 'strip': strip, 'source': f[9], 'group': 'PUNCT',
            'note': f[11] or None}
    semis = {(27, 1), (27, 16), (77, 2), (77, 18), (107, 10), (143, 12)}
    for p, v, key, new in K.SPACING:
        if (p, v) in semis:
            ev['%d:%d:spacing:%s' % (p, v, key)] = {
                'page': pages['%d:%d' % (p, v)], 'eye': ';', 'strip': 'spacing',
                'group': 'SPACING',
                'note': "the book sets a thin space before ';' and ':' throughout (the "
                        "compositor's); the corpus closes it (R16, R21) -- a convention, not a reading"}
        else:
            ev['%d:%d:spacing:%s' % (p, v, key)] = {
                'page': pages['%d:%d' % (p, v)], 'eye': new,
                'strip': 'um_24' if (p, v) == (139, 1) else 'um_fix_00',
                'group': 'SPACING',
                'note': "the book sets this stop closed up (no space before ',' or '.')"
                        if (p, v) != (139, 1) else "the book sets a space after the comma"}
    for p, v, key, new in K.FURNITURE:
        ev['%d:%d:furniture' % (p, v)] = {
            'page': 536, 'eye': 'THE END OF THE PSALTER. -- set as a line of its own after 150:6',
            'strip': 'pu_10 (P439)', 'group': 'FURNITURE',
            'note': 'R20: the closing line is book furniture; deleted'}
    for k in json.load(open(os.path.join(HERE, 'w22_case_keys.json'), encoding='utf-8')):
        ref = '%d:%d' % (k['psalm'], k['verse'])
        ev['%s:case:%s' % (ref, k['id'])] = {
            'page': pages[ref], 'eye': k['book'], 'cell': k['cell'], 'kind': k['kind'],
            'strip': k['strip'], 'group': k['group'],
            'note': 'letter case -- NOT RULED (group off)'}
    for (p, v), (key, note) in K.VERIFY.items():
        if (p, v) == (1, 3):
            continue
        ev['%d:%d:verify:%s' % (p, v, key)] = {
            'page': 525 if (p, v) == (139, 11) else pages['%d:%d' % (p, v)], 'eye': {(107, 1): 'gracious ; and',
                                                     (139, 7): 'there ; if',
                                                     (139, 11): 'with thee, (damaged)'}[(p, v)],
            'status': 'open', 'group': 'VERIFY',
            'strip': {(107, 1): 'mq_15, look/p487_10701x3', (139, 7): 'mq_19, look/p525_13907x3',
                      (139, 11): 'mq_19, look/p525_13911x3'}[(p, v)]}
    ev['1:3:water-side'] = {
        'page': 357, 'eye': 'water- / side (a line break)', 'strip': 'C1 page look',
        'status': 'open', 'group': 'VERIFY',
        'searched': '4400px Psalter OCR and 2400px OCR of all 596 scan pages: no other '
                    'occurrence of water-side / waterside / water side',
        'note': 'R21: stays flagged; note corrected (the keyed Standard text breaks the word '
                'at the same line end; it does not print "waterside")',
        'context': 'every other water- compound the book sets mid-line is hyphenated '
                   '(water-flood x2, water-floods, water-brooks, water-pipes, water-springs x2, '
                   'water-pots x2 at p102) -- analogy, not attestation; the carrier 1892/Psalms.pdf '
                   'prints water-side; justus\'s keyed Standard text breaks it water-/side at the '
                   'same place; the dated change table has no entry for 1:3; 1662 cell water-side, '
                   '1928 cell water-side'}
    json.dump(ev, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False, sort_keys=True)
    print('%d evidence records -> %s' % (len(ev), OUT))


if __name__ == '__main__':
    main()
