"""w22_words_eye.py -- EYE reads of the word candidates (w22_words.py --strips,
strips wd_00..wd_02; each crop is the candidate's whole printed row, labelled
with the verse, page and the CELL's word).

READ[n] = (verse, page, cell form, what the book prints, verdict)
  verdict 'differs'  the book prints another form than the cell
          'same'     the book prints the cell's form (the OCR misread it)
Forms are single words or a short phrase (never a passage).
"""
READ = {
    1: ('18:15', 373, 'springs of water', 'springs of waters', 'differs'),
    2: ('18:19', 373, 'even', 'even', 'same'),
    3: ('22:18', 380, 'and casts lots', 'and cast lots', 'differs'),
    4: ('23:4', 381, 'Yea, thou I walk', 'Yea, though I walk', 'differs'),
    5: ('23:4', 381, 'for thou art', 'for thou art', 'same'),
    6: ('32:3', 390, 'For while I held', 'For whilst I held', 'differs'),
    7: ('38:16', 401, 'my foot slipped,', 'my foot slipt,', 'differs'),
    8: ('38:17', 401, 'ever', 'ever', 'same'),
    9: ('41:1', 404, 'and', 'and', 'same'),
    10: ('48:10', 412, 'the daughters of Judah', 'the daughter of Judah', 'differs'),
    11: ('50:20', 415, 'Thou satest, and', 'Thou sattest and', 'differs'),
    12: ('52:3', 417, 'a sharp rasor', 'a sharp razor', 'differs'),
    13: ('52:4', 417, 'more then goodness', 'more than goodness', 'differs'),
    14: ('71:2', 438, 'strong hold', 'stronghold', 'differs'),
    15: ('71:20', 439, 'instrument of musick', 'instrument of music', 'differs'),
    16: ('74:9', 443, 'make havock of', 'make havoc of', 'differs'),
    17: ('76:4', 445, 'art', 'art', 'same'),
    18: ('78:21', 449, 'the waters gushed', 'the water gushed', 'differs'),
    19: ('79:14', 453, 'ever', 'ever', 'same'),
    20: ('86:9', 460, 'thou hadst made', 'thou hast made', 'differs'),
    21: ('89:39', 464, 'strong holds', 'strongholds', 'differs'),
    22: ('91:2', 467, 'strong hold', 'stronghold', 'differs'),
    23: ('99:1', 474, 'never so unpatient', 'never so impatient', 'differs'),
    24: ('104:1', 479, 'art', 'art', 'same'),
    25: ('104:1', 479, 'art', 'art', 'same'),
    26: ('104:11', 480, 'wild', 'wild', 'same'),
    27: ('105:23', 483, 'land', 'land', 'same'),
    28: ('106:10', 485, "the adversaries' hand", "the adversary's hand", 'differs'),
    29: ('107:28', 489, 'So when thy cry', 'So when they cry', 'differs'),
    30: ('107:40', 490, 'evil intreated', 'evil entreated', 'differs'),
    31: ('109:18', 492, 'as the cloke', 'as the cloak', 'differs'),
    32: ('109:28', 493, 'with a cloke', 'with a cloak', 'differs'),
    33: ('112:8', 495, 'heart is established', 'heart is stablished', 'differs'),
    34: ('119:105', 508, 'THY', 'THY', 'same'),
    35: ('124:2', 515, 'when thy were', 'when they were', 'differs'),
    36: ('125:2', 515, 'even', 'even', 'same'),
    37: ('136:9', 522, 'ever', 'ever', 'same'),
    38: ('136:12', 522, 'hand, and stretched out arm', 'hand and stretched-out arm', 'differs'),
    39: ('139:15', 526, 'being unperfect', 'being imperfect', 'differs'),
    40: ('141:1', 527, 'thee', 'thee', 'same'),
    41: ('141:1', 527, 'thee', 'thee', 'same'),
    42: ('144:9', 530, 'ten- stringed', 'ten-stringed', 'differs'),
}
