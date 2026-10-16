"""w22_eye_2.py -- the PHASE-2 eye reads (R21: every mediant read by eye; the
unmatched words read by eye).

Q1 pass: every Q1 verse (w22_firstpass.tsv) not already read by eye in Phase 1
(prototype pivot strips, w22_eye.txt) or Phase 1b (the control,
w22_eye_1b.CONTROL), in the fixed order q1_rest() gives, cut as pivot crops
(w22_crops.py q1rest, strips q1_NN, 40 per strip). For each strip the eye read
every crop; Q1[k] lists ONLY the crops where the book does not print ':' right
after the labelled pivot word (verse -> what it prints there, '?' = not
legible at strip scale, re-read in Q1_FIX). Every other verse of the strip was
read as ':' at the cell's word.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))

Q1 = {}          # strip index -> {verse: mark}
Q1_FIX = {}      # verse -> (mark, how it was settled)


def q1_rest():
    import w22_eye_1b as E
    q1 = [l.split('\t')[0] for l in open(os.path.join(HERE, 'w22_firstpass.tsv'))
          if not l.startswith('#') and l.split('\t')[2] == 'Q1']
    seen = set(E.CONTROL)
    for l in open(os.path.join(HERE, 'w22_eye.txt')):
        if l.startswith('#') or not l.strip():
            continue
        f = l.split('\t')
        if f[2].startswith('pivot:') and len(f) > 3 and not f[2].startswith('pivot:', 1):
            if '/' not in f[2] and f[3] in (':', ';', ',', '.', '-', '?') and 'queue' not in l:
                seen.add(f[0])
    return [r for r in q1 if r not in seen]

# ---- the Q1 pass, strip by strip (an empty dict = every crop ':' at the cell's word)
Q1.update({0: {}, 1: {}, 2: {}, 3: {}})
Q1.update({4: {}, 5: {}, 6: {}, 7: {}, 8: {}, 9: {}})
Q1.update({10: {}, 11: {}, 12: {}, 13: {}, 14: {}, 15: {}})
Q1.update({16: {}, 17: {}, 18: {}, 19: {}})
Q1.update({20: {}, 21: {}, 22: {}})
Q1.update({23: {}, 24: {}, 25: {}})
Q1.update({26: {}, 27: {}, 28: {}})
CASE_NOTES = {'83:18': "book prints 'JEHOVAH' in capitals (the cell prints it so at 33:12); the cell prints 'Jehovah' here"}
Q1.update({29: {}, 30: {}})
CASE_NOTES['89:37'] = "book prints 'thine anointed :' lower-case (whole-verse crop chk_89_37); the cell prints 'Anointed'"
Q1.update({31: {}})
CASE_NOTES['89:50'] = "book prints 'thine anointed :' lower-case (strip q1_31); the cell prints 'Anointed'"
Q1.update({32: {}, 33: {}})
Q1.update({34: {}, 35: {}})
Q1.update({36: {}})
CASE_NOTES['105:15'] = "book prints 'mine anointed :' lower-case (strip q1_36); the cell prints 'Anointed'"
Q1.update({37: {}, 38: {}})
Q1.update({39: {}, 40: {}})
Q1.update({41: {}})
Q1.update({42: {}, 43: {}})
Q1.update({44: {}, 45: {}})
Q1.update({46: {}, 47: {}})
CASE_NOTES['136:15'] = "book prints 'the Red Sea' (capital S, strip q1_47); the cell prints 'Red sea' -- check the other 4 places"
Q1.update({48: {}})
CASE_NOTES['140:8'] = "book prints 'O LORD :' in small capitals (strip q1_48); the cell prints 'O Lord'"
Q1.update({49: {}})
Q1.update({50: {}, 51: {}})

# ---- the unmatched-word pass (w22_unmatched.py, strips um_NN, runs U001..U585)
# For each strip: 'differs' = runs where the book prints other words than the
# cell's (id -> (cell words, book words)); 'recheck' = runs the crop did not
# show, re-read off a re-crop (UM_FIX). Every other run of the strip: the book
# prints the cell's words (OCR had damaged, split or dropped them).
UM = {}
UM_FIX = {}
UM[0] = {'differs': {}, 'recheck': ['U026']}
UM[1] = {'differs': {'U038': ('whom God abhorreth', 'whom GOD abhorreth (small capitals)')}, 'recheck': []}
UM[2] = {'differs': {'U056': ('set God alway', 'set GOD alway (small capitals)')}, 'recheck': ['U055']}
UM[3] = {'differs': {'U072': ('Save, LORD, and', 'Save, LORD; and'),
                     'U077': ('MY GOD, my God,', 'MY God, my God, (only the first word in capitals)'),
                     'U083': ('shoot our their lips', 'shoot out their lips'),
                     'U087': ("the LORD'S, and", "the LORD's, and (small-capital LORD, lower-case s)")},
         'recheck': []}
UM[4] = {'differs': {'U094': ('BE THOU my', 'BE thou my (only the first word in capitals)'),
                     'U095': ('my judge, O LORD', 'my Judge, O LORD'),
                     'U108': ('O LORD, for thou', 'O LORD; for thou')},
         'recheck': []}
UM[5] = {'differs': {}, 'recheck': []}
UM[6] = {'differs': {}, 'recheck': []}
UM[7] = {'differs': {'U180': ('GOD is our hope', 'God is our hope (drop capital G, then lower case)')}, 'recheck': []}
UM[8] = {'differs': {}, 'recheck': []}
UM[9] = {'differs': {}, 'recheck': []}
UM[10] = {'differs': {}, 'recheck': []}
UM[11] = {'differs': {'U250': ('GOD be merciful', 'God be merciful (drop capital G, then lower case)'),
                      'U265': ('stretch our her hands', 'stretch out her hands'),
                      'U277': ('IN THEE ,O LORD', 'IN thee, O LORD (only the first word in capitals; comma closed up)')},
          'recheck': []}
UM[12] = {'differs': {'U279': ('but rid me and', 'but rid me, and'),
                      'U283': ('the Lord God : and', 'the Lord GOD : and (small capitals)'),
                      'U301': ('full mixed, and', 'full mixt, and'),
                      'U304': ('IN JEWRY is', 'IN Jewry is (only the first word in capitals)')},
          'recheck': []}
UM[13] = {'differs': {}, 'recheck': []}
UM[14] = {'differs': {'U327': ('would not obey me.', 'would not obey me;'),
                      'U329': ('GOD standeth', 'God standeth (drop capital G, then lower case)')},
          'recheck': []}
UM[15] = {'differs': {}, 'recheck': []}
UM[16] = {'differs': {}, 'recheck': []}
UM[17] = {'differs': {'U411': ('whom they had offered', 'whom they of-|fered (no "had"; full-size crop look/p487_10637)')},
          'recheck': []}
UM[18] = {'differs': {'U428': ('my good will.', 'my goodwill. (one word)')}, 'recheck': []}
UM[19] = {'differs': {}, 'recheck': []}
UM[20] = {'differs': {'U480': ('MY SOUL hath longed', 'MY soul hath longed (only the first word in capitals)')}, 'recheck': []}
UM[21] = {'differs': {}, 'recheck': []}
UM[22] = {'differs': {}, 'recheck': []}
UM[23] = {'differs': {}, 'recheck': []}
UM[24] = {'differs': {'U555': ('O LORD,thou hast', 'O LORD, thou hast (a space after the comma)')}, 'recheck': []}
UM[25] = {'differs': {}, 'recheck': []}
UM_FIX.update({
    'U026': ('same', "7:18 'LORD most High.' -- whole-verse crop um_fix_00: the words stand; "
                     "the book capitalizes 'Most' (a CASE item)"),
    'U055': ('same', "16:1 'PRESERVE me, O God' -- whole-verse crop um_fix_00"),
})
# Spaced stops (' ,' ' .') the cells carry from the carrier: the book sets them
# closed up (whole-verse crops um_fix_00). 141:9's ' ,' is a PUNCT item (book ';').
SPACED_STOPS = ['9:8', '124:6', '12:4', '28:10', '31:10', '45:5', '118:26', '137:8', '55:16', '71:1']

# ---- LETTER CASE (by-catch of both passes; machine candidates w22_case.py,
# strips cs_00..03, cs2_00..01, cs3, cs4_00, case_whole_00, um_*, q1_*).
# (verse, cell word, which whole-word occurrence ('all' or n), the book's form,
#  kind, strip). kind: 'lord'    small capitals LORD/GOD against Lord/God, JEHOVAH
#                      'opening' a verse-1 (or Ps 119 portion) opening: the book
#                                capitalizes only the first word
#                      'caps'    any other initial capital
CASE = [
    ('2:4', 'LORD', 1, 'Lord', 'lord', 'cs2_00'),
    ('10:3', 'God', 1, 'GOD', 'lord', 'um_01'),
    ('16:9', 'God', 1, 'GOD', 'lord', 'um_02'),
    ('71:14', 'God', 1, 'GOD', 'lord', 'um_12'),
    ('83:18', 'Jehovah', 1, 'JEHOVAH', 'lord', 'q1_28, cs_01'),
] + [(r, 'Lord', 'all', 'LORD', 'lord', 'cs2_00, cs2_01') for r in (
    '139:3', '139:21', '140:1', '140:4', '140:6', '140:7', '140:8', '140:12', '141:3',
    '141:9', '142:1', '142:6', '143:1', '143:7', '143:9', '143:11')] + [
    ('11:1', 'THE', 1, 'the', 'opening', 'cs_00'),
    ('22:1', 'GOD', 1, 'God', 'opening', 'um_03'),
    ('26:1', 'THOU', 1, 'thou', 'opening', 'um_04, case_whole_00'),
    ('31:1', 'THEE', 1, 'thee', 'opening', 'cs_00'),
    ('36:1', 'HEART', 1, 'heart', 'opening', 'cs_00'),
    ('44:1', 'HAVE', 1, 'have', 'opening', 'cs_00, um_07'),
    ('45:1', 'HEART', 1, 'heart', 'opening', 'cs_00, um_07'),
    ('46:1', 'GOD', 1, 'God', 'opening', 'um_07'),
    ('56:1', 'MERCIFUL', 1, 'merciful', 'opening', 'case_whole_00, um_08'),
    ('57:1', 'MERCIFUL', 1, 'merciful', 'opening', 'case_whole_00, um_09'),
    ('62:1', 'SOUL', 1, 'soul', 'opening', 'cs_01, um_10'),
    ('67:1', 'GOD', 1, 'God', 'opening', 'um_11'),
    ('71:1', 'THEE', 1, 'thee', 'opening', 'um_11, case_whole_00'),
    ('76:1', 'JEWRY', 1, 'Jewry', 'opening', 'um_12, case_whole_00'),
    ('82:1', 'GOD', 1, 'God', 'opening', 'um_14'),
    ('89:1', 'SONG', 1, 'song', 'opening', 'cs_01, um_15'),
    ('92:1', 'IS', 1, 'is', 'opening', 'cs_02, um_15'),
    ('101:1', 'SONG', 1, 'song', 'opening', 'cs_02, um_16'),
    ('119:25', 'SOUL', 1, 'soul', 'opening', 'cs_02, um_20'),
    ('119:81', 'SOUL', 1, 'soul', 'opening', 'um_20'),
    ('124:1', 'THE', 1, 'the', 'opening', 'cs_02, um_22'),
    ('137:1', 'THE', 1, 'the', 'opening', 'cs_03, um_24'),
] + [(r, 'most', 1, 'Most', 'caps', s) for r, s in (
    ('7:18', 'um_fix_00, look/p362_0718'), ('9:2', 'cs_00'), ('21:7', 'cs_00'), ('45:4', 'cs_00'),
    ('46:4', 'cs_00'), ('50:1', 'cs_00'), ('50:14', 'cs2_00'), ('57:2', 'cs_01'), ('73:11', 'cs_01'),
    ('77:10', 'cs_01'), ('78:18', 'cs_01'), ('78:57', 'cs_01'), ('82:6', 'cs_01'), ('83:18', 'cs_01'),
    ('87:5', 'cs_01'), ('91:1', 'cs_02'), ('92:1', 'cs_02'), ('107:11', 'cs_02'))] + [
    ('50:1', 'mighty', 1, 'Mighty', 'caps', 'cs_00'),
    ('57:2', 'high', 1, 'High', 'caps', 'cs_01'),
    ('78:35', 'high', 1, 'High', 'caps', 'cs_01'),
    ('78:57', 'high', 1, 'High', 'caps', 'cs_01'),
    ('13:6', 'Highest', 1, 'highest', 'caps', 'cs_00, cs2_00'),
] + [(r, 'Anointed', 1, 'anointed', 'caps', s) for r, s in (
    ('18:51', 'cs4_00'), ('20:6', 'cs2_00'), ('28:9', 'cs_00'), ('84:9', 'cs_01'), ('89:37', 'cs_02, chk_89_37'),
    ('89:50', 'cs2_00, q1_31'), ('105:15', 'cs2_00, q1_36'), ('132:10', 'cs_03'), ('132:18', 'cs_03'))] + [
    (r, 'Red sea', 1, 'Red Sea', 'caps', 'cs_02, cs_03, q1_47') for r in ('106:7', '106:9', '106:22', '136:13', '136:15')] + [
    ('22:3', 'worship', 1, 'Worship', 'caps', 'cs_00'),
    ('24:8', 'it', 1, 'It', 'caps', 'cs_00'),
    ('24:10', 'even', 1, 'Even', 'caps', 'cs_00'),
    ('26:1', 'judge', 1, 'Judge', 'caps', 'um_04, case_whole_00'),
    ('36:7', 'How', 1, 'how', 'caps', 'cs_00, case_whole_00'),
    ('68:5', 'father', 1, 'Father', 'caps', 'cs_01'),
    ('74:15', 'Leviathan', 1, 'leviathan', 'caps', 'cs_01'),
    ('104:35', 'praise', 1, 'Praise', 'caps', 'cs_02, case_whole_00'),
    ('106:46', 'and', 2, 'And', 'caps', 'cs_02, case_whole_00'),
    ('110:4', 'priest', 1, 'Priest', 'caps', 'cs_02'),
    ('132:5', 'mighty', 1, 'Mighty', 'caps', 'cs_03'),
    ('139:19', 'depart', 1, 'Depart', 'caps', 'cs_03'),
]
# Read and found the SAME as the cell (machine candidates the eye rejected):
CASE_SAME = ['10:9 For', '38:15 For', '51:3 For', '73:26 For', '89:18 For', '103:16 For',
             '107:16 For', '107:25 For', '109:30 For', '130:4 For', '90:6 In', '129:8 The',
             '76:1 IN', '2:2 Anointed', '56:2 most', '73:8 most', '89:9 most', '92:7 most',
             '13:6 most', '37:24 LORD', '68:18 LORD', '104:35 LORD', '110:2 LORD', '118:19 LORD',
             '135:5 Lord', '136:3 Lord', '136:27 Lord', '145:15 Lord', '138:1 Lord', '147:5 Lord']
# Covered by PUNCT (a capital after a new full stop): 18:1 The, 68:35 Blessed, 104:35 Praise (2nd).
# NOT keyed -- an encoding question for a ruling: the book sets the possessive of small-capital
# LORD as LORD's (lower-case s); the cells print LORD'S in 11 verses (11:4, 22:28, 24:1, 27:16,
# 56:10, 113:3, 115:16, 116:16, 118:23, 137:4, 147:11).
