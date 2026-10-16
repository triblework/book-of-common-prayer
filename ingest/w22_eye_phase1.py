"""w22_eye_phase1.py -- writes ingest/w22_eye.txt from the PHASE-1 eye reads
(prototype strips and samples), keyed here as short words and marks only.
    python3 ingest/w22_eye_phase1.py <worktree>
"""
import json, os, sys
WT = sys.argv[1]
sys.path.insert(0, os.path.join(WT, 'ingest'))
import w22_crops as C
recs, by = C.load()
L = []
def add(ref, where, eye, cell, strip, note=''):
    ps, v = map(int, ref.split(':'))
    r = by[(ps, v)]
    pg = (r.get('pivot') or {}).get('page') or r.get('page')
    L.append('%s\tp%s\t%s\t%s\t%s\t%s%s' % (ref, pg, where, eye, cell, strip, ('\t' + note) if note else ''))
# 1. pivot strips viewed in full: every crop read ':' at the pivot
for strip, refs in (('ps001_001-006', ['1:%d' % i for i in range(1, 7)]),
                    ('ps023_001-006', ['23:%d' % i for i in range(1, 7)]),
                    ('ps078_002-026', ['78:%d' % i for i in range(2, 27)]),
                    ('ps119_001-040', ['119:%d' % i for i in range(1, 41)]),
                    ('ps119_082-121', ['119:%d' % i for i in range(82, 122)])):
    for ref in refs:
        add(ref, 'pivot:' + by[tuple(map(int, ref.split(':')))]['pivot']['word'], ':', ':', strip)
# 2. the pivots the OCR read with no colon (strip pivot_nocolon_00; whole-verse
#    crops whole_cands_00 where the pivot crop missed)
P = [('3:1', ':', ''), ('4:1', ':', 'whole crop; pivot broken righteous-|ness'),
     ('10:1', ':', 'OCR read ;'), ('22:5', ':', 'OCR read ;'), ('33:1', ':', ''),
     ('39:14', ',', 'book: thee, and a so-|journer : as -- colon after sojourner'),
     ('55:7', ':', 'OCR read ;'), ('58:1', ':', ''), ('65:1', ':', ''),
     ('66:12', ':', 'whole crop; pivot broken burnt-offer-|ings across p430/431'),
     ('68:1', ':', ''),
     ('100:2', ';', 'book: God; it is he ... ourselves : we are -- colon after ourselves'),
     ('107:1', ';', 'book: gracious ; and his -- no colon anywhere in the verse (3x zoom)'),
     ('109:1', ':', ''), ('115:7', ':', ''), ('119:41', ':', 'line end'),
     ('119:159', ':', 'whole crop; pivot broken command-|ments'),
     ('133:1', ':', 'line end'),
     ('139:7', ';', 'book: there ; if I -- no colon anywhere in the verse (3x zoom)')]
for ref, eye, note in P:
    add(ref, 'pivot:' + by[tuple(map(int, ref.split(':')))]['pivot']['word'], eye, ':',
        'pivot_nocolon_00/whole_cands_00', note)
# 3. the pivots the alignment could not place (whole-verse crops)
U = [('1:7', ':', ''), ('12:1', ':', ''), ('19:1', ':', ''), ('24:1', ':', 'line end'),
     ('63:4', ':', ''), ('78:1', ':', ''), ('85:1', ':', 'line end'),
     ('87:1', '?', 'crop lost the drop-capital row; UNREAD'), ('91:2', ':', 'book prints stronghold (cell: strong hold)'),
     ('119:81', ':', ''), ('130:1', ':', 'line end'),
     ('132:1', ':', 'and a verse-final colon after trouble'), ('141:1', ':', ''),
     ('143:12', ':', '')]
for ref, eye, note in U:
    add(ref, 'pivot:' + by[tuple(map(int, ref.split(':')))]['pivot']['word'], eye, ':',
        'unaligned_whole_00', note)
# 4. verse-final marks the OCR flagged (strip final_sample_00)
F = [('2:2', 'Anointed', ':', '.'), ('2:5', 'displeasure', ':', '.'), ('17:4', 'destroyer', '.', '.'),
     ('18:5', 'God', ':', '.'), ('18:18', 'upholder', '.', '.'), ('22:20', 'dog', '.', '.'),
     ('23:1', 'nothing', '.', '.'), ('25:4', 'long', '.', '.'), ('27:14', 'wrong', '.', '.'),
     ('29:8', 'honour', '.', '.'), ('30:6', 'strong', '.', '.'), ('30:12', 'gladness', ':', '.'),
     ('35:28', 'long', '.', '.'), ('37:13', 'coming', '.', '.'), ('38:1', 'displeasure', ':', '.'),
     ('38:12', 'long', '.', '.'), ('41:7', 'evil', ':', '.'), ('43:3', 'dwelling', '.', '.'),
     ('47:6', 'King', '.', '.'), ('47:7', 'understanding', '.', '.'), ('48:7', 'ever', '.', '.'),
     ('49:3', 'understanding', '.', '.'), ('49:14', 'dwelling', '.', '.'),
     ('50:18', 'adulterers', '.', '.'), ('56:13', 'living', '.', '.'),
     ('9:13', 'death', ';', '.'), ('13:3', 'death', ';', '.'), ('17:11', 'ground', ';', '.'),
     ('26:6', 'altar', ';', '.'), ('26:9', 'blood-thirsty', ';', '.'),
     ('8:6', 'feet', ':', ';'), ('18:47', 'salvation', ':', ';'), ('20:1', 'thee', ':', ';'),
     ('20:2', 'Sion', ':', ';'), ('20:3', 'burnt-sacrifice', ':', ';')]
for ref, w, eye, cell in F:
    add(ref, 'end:' + w, eye, cell, 'final_sample_00')
# 5. internal marks the OCR flagged (strip internal_sample)
I = [('26:1', 'my', '-', '-', "OCR moved the pivot's colon onto the next word"),
     ('39:14', 'sojourner', ':', ',', 'the book mediant (see pivot)'),
     ('91:2', 'strong', ':', ':', 'book one word stronghold; same mediant'),
     ('100:2', 'ourselves', ':', ';', 'the book mediant (see pivot)'),
     ('117:2', 'ever', '.', '.', 'the SECOND ever (the alignment mapped the first): consistent'),
     ('4:4', 'chamber', ',', ','), ('10:9', 'secretly', ';', ','), ('13:1', 'LORD', ';', ','),
     ('14:5', 'sepulchre', ';', ','), ('16:2', 'God', ';', ','), ('18:1', 'trust', ';', ','),
     ('18:6', 'him', ';', ','), ('18:15', 'chiding', ',', ','), ('18:47', 'liveth', ';', ','),
     ('21:4', 'thee', ';', ','), ('22:11', 'me', ';', ','), ('22:14', 'water', ',', ','),
     ('22:23', 'Jacob', ';', ','), ('22:24', 'him', ';', ','), ('24:7', 'gates', ';', ','),
     ('24:9', 'gates', ';', ','), ('25:10', 'sin', ';', ','), ('30:11', 'Hear', ',', ','),
     ('31:1', 'confusion', ';', ','), ('31:15', 'side', ';', ','), ('32:8', 'in', ';', ','),
     ('39:4', 'me', ';', ','), ('39:13', 'prayer', ',', ','), ('40:21', 'tarrying', ',', ','),
     ('41:6', 'himself', ';', ','), ('43:2', 'strength', ';', ','), ('49:14', 'sheep', ';', ','),
     ('54:2', 'prayer', ',', ','), ('56:6', 'together', ',', ','), ('57:1', 'me', ';', ',')]
for t in I:
    ref, w, eye, cell = t[:4]
    add(ref, 'after:' + w, eye, cell, 'internal_sample', t[4] if len(t) > 4 else '')
# 6. commas the OCR and the cell disagree on (strip comma_sample, a random 20 + 20)
K1 = [('86:17', 'me'), ('87:6', 'it'), ('64:5', 'themselves'), ('146:1', 'live'), ('10:2', 'ungodly'),
      ('139:18', 'up'), ('35:4', 'confounded'), ('50:23', 'right'), ('104:28', 'them'), ('6:4', 'me'),
      ('79:11', 'heathen'), ('78:50', 'displeasure'), ('71:2', 'strong'), ('68:33', 'all'),
      ('135:11', 'Og'), ('30:4', 'him'), ('35:28', 'praise'), ('28:1', 'LORD'), ('127:4', 'children'),
      ('78:55', 'mountain')]
for ref, w in K1:
    add(ref, 'after:' + w, ',', '-', 'comma_sample', 'book one word stronghold' if w == 'strong' else '')
K2 = [('77:4', 'feeble', '-'), ('44:6', 'under', '-'), ('35:23', 'God', '-'), ('119:170', 'me', '-'),
      ('49:10', 'die', '-'), ('23:3', 'righteousness', '-'), ('2:12', 'yea', '-'), ('18:32', 'God', '-'),
      ('22:24', 'despised', '-'), ('27:7', 'sing', '-'), ('106:23', 'said', '-'), ('89:12', 'world', ','),
      ('55:13', 'adversary', '-'), ('38:8', 'feeble', '-'), ('36:3', 'unrighteous', '-'),
      ('17:12', 'whelp', '-'), ('18:12', 'hailstones', '-'), ('105:25', 'turned', '-'),
      ('40:9', 'Burnt-offerings', '-'), ('4:3', 'LORD', '-')]
for ref, w, eye in K2:
    add(ref, 'after:' + w, eye, ',', 'comma_sample',
        'book: turned so, that' if ref == '105:25' else ('line end' if ref == '2:12' else ''))
hdr = ('# w22_eye.txt -- pointing and stops read BY EYE off 4400px crops of the 1892\n'
       '# Standard Book scan (strips in the workstream render dir, built by w22_crops.py).\n'
       '# PHASE 1 (prototype and sampling only; no cell has been changed).\n'
       '# columns: verse, scan page, where (pivot:W = the word the cell mediant follows;\n'
       '# end:W = the verse\'s last word; after:W = another word), what the eye saw\n'
       "# (':' ';' ',' '.' or '-' for no mark; '?' unread), the cell's mark there, strip, note.\n")
open(os.path.join(WT, 'ingest', 'w22_eye.txt'), 'w').write(hdr + '\n'.join(L) + '\n')
print(len(L), 'eye reads')

# ---------------------------------------------------------------- Phase 1b
# Whole-verse eye reads of the flagged/other queues (Q2+Q3, 197 verses) and of
# the seeded control sample of Q1 (150 verses), from w22_eye_1b.py.
import w22_eye_1b as E1B
import w22_eye_cmp as KC
import w17_cells as W17
_cells = W17.cells('1892')
_q = {l.split('\t')[0]: l.split('\t')[2] for l in open(os.path.join(WT, 'ingest', 'w22_firstpass.tsv'))
      if not l.startswith('#')}
out = ['', '# ---- PHASE 1b: whole-verse eye reads (strips mq_NN = Q2+Q3; ctl_NN = control) ----',
       '# columns: verse, scan page, queue, pivot word, mark the eye saw at the pivot,',
       "# every other ':'/';' the eye saw in the verse (word+mark), disagreements with the",
       '# cell (w22_eye_cmp), note.']
for name, book in (('queue', E1B.MEDIANT), ('control', E1B.CONTROL)):
    for ref in sorted(book, key=lambda r: tuple(map(int, r.split(':')))):
        ps, v = map(int, ref.split(':'))
        r = by[(ps, v)]
        pg = (r.get('pivot') or {}).get('page') or r.get('page')
        piv, rest = book[ref].split('|', 1)
        d = KC.compare(ref, book[ref], _cells)
        dd = ' '.join('%s:%s:%s>%s' % (x[0], x[1], x[2], x[3]) for x in d) or 'agrees'
        note = '; '.join(x for x in (E1B.NOTES.get(ref, ''), E1B.RECROP.get(ref, '')) if x)
        out.append('%s\tp%s\t%s/%s\tpivot:%s\t%s\t%s\t%s%s' % (
            ref, pg, name, _q.get(ref, '?'), (r.get('pivot') or {}).get('word', '?'), piv,
            rest.strip() or '-', dd, ('\t' + note) if note else ''))
with open(os.path.join(WT, 'ingest', 'w22_eye.txt'), 'a') as fh:
    fh.write('\n'.join(out) + '\n')
print(len(E1B.MEDIANT) + len(E1B.CONTROL), 'phase-1b whole-verse reads appended')

# ---------------------------------------------------------------- Phase 2
# (R21) the full eye pass over the rest of Q1 (strips q1_NN, 40 pivot crops
# each), the eye pass over the words the alignment left unmatched (um_NN), and
# the letter-case reads (cs*, um_*, q1_*) -- from w22_eye_2.py.
import w22_eye_2 as E2
idx = json.load(open(os.path.join(C.STRIPS, 'q1_index.json')))
out = ['', '# ---- PHASE 2a: the rest of the machine-clean queue (Q1), every pivot read by eye ----',
       '# columns: verse, scan page, pivot word, the mark the eye saw right after it, strip.']
for k, refs in enumerate(idx):
    marks = E2.Q1[k]
    for ref in refs:
        r = by[tuple(map(int, ref.split(':')))]
        p = r['pivot']
        mk = marks.get(ref, ':')
        out.append('%s\tp%s\tpivot:%s\t%s\tq1_%02d%s' % (
            ref, p['page'], p['word'], mk, k,
            ('\t' + E2.CASE_NOTES[ref]) if ref in E2.CASE_NOTES else ''))
um = [l.rstrip('\n').split('\t') for l in open(os.path.join(WT, 'ingest', 'w22_unmatched.tsv'))
      if not l.startswith('#')]
uidx = json.load(open(os.path.join(C.STRIPS, 'um_index.json')))
where = {uid: k for k, ids in enumerate(uidx) for uid in ids}
out += ['', '# ---- PHASE 2b: the cell words the alignment left unmatched, read by eye ----',
        '# columns: run id, verse, scan page, the cell words, what the eye saw (same = the book',
        '# prints the cell words; otherwise the book form), strip.']
for uid, ref, page, cw in um:
    k = where[uid]
    d = E2.UM[k]['differs'].get(uid)
    fix = E2.UM_FIX.get(uid)
    eye = ('book: ' + d[1]) if d else ('same' + ((' -- ' + fix[1]) if fix else ''))
    out.append('%s\t%s\tp%s\t%s\t%s\tum_%02d' % (uid, ref, page, cw, eye, k))
out += ['', '# ---- PHASE 2c: letter case, read by eye (NOT RULED; group off) ----',
        '# columns: verse, cell word, occurrence, the book form, kind, strip.']
for ref, w, occ, book, kind, strip in E2.CASE:
    out.append('%s\t%s\t%s\t%s\t%s\t%s' % (ref, w, occ, book, kind, strip))
for s in E2.CASE_SAME:
    out.append('%s\t%s\t-\tsame\t-\tcs*' % tuple(s.split(' ', 1)))
with open(os.path.join(WT, 'ingest', 'w22_eye.txt'), 'a') as fh:
    fh.write('\n'.join(out) + '\n')
print(len(out), 'phase-2 lines appended')
