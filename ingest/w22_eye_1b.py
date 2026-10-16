"""w22_eye_1b.py -- the PHASE-1b eye reads, keyed as they were made.

Workstream C. Every entry is what the EYE saw on a whole-verse crop of the 4400px
scan (strips built by w22_crops.py, listed in <render>/strips/*_index.txt):

  MEDIANT[ref] = 'P|w1M w2M ...'
      P   the mark the book prints right after the cell's pivot word
          (':' ';' ',' '.' '-' none, '?' unread)
      wM  every OTHER colon-class mark (':' or ';') the eye saw anywhere in the
          verse, as the word before it + the mark ('Anointed:', 'trouble;');
          a word that occurs twice in the verse may carry '#2'
  The cell's own marks are NOT shown on the strips (only the pivot word, so the
  eye knows where the cell's mediant falls); w22_eye_build.py compares.
"""
MEDIANT = {}
CONTROL = {}
PUNCT = {}

# strip mq_00
MEDIANT.update({
    '1:7': ':|', '2:2': ':|Anointed:', '2:5': ':|displeasure:', '3:1': ':|',
    '4:1': ':|trouble;', '4:4': ':|', '7:4': ':|enemy;', '8:6': ':|feet:',
    '9:13': ':|LORD; death;',
})
# strip mq_01
MEDIANT.update({
    '10:1': ':|', '10:9': ':|secretly;', '12:1': ':|', '13:1': ':|LORD;',
    '13:3': ':|death;', '14:5': ':|sepulchre;', '16:2': ':|God;', '17:4': ':|',
    '17:11': ':|ground;',
})
# strip mq_02
MEDIANT.update({
    '18:1': ':|trust;', '18:5': ':|God:', '18:6': ':|him;', '18:15': ':|',
    '18:18': ':|', '18:47': ':|liveth; salvation:', '19:1': ':|',
})
NOTES = {'18:1': "book: 'my strength. The LORD' (a period and a capital where the cell has ' ; the')"}
# strip mq_03
MEDIANT.update({
    '20:1': ':|thee#2:', '20:2': ':|Sion:', '20:3': ':|burnt-sacrifice:', '21:4': ':|thee;',
    '22:5': ':|', '22:11': ':|me;', '22:14': ':|', '22:20': ':|', '22:23': ':|Jacob;',
    '22:24': ':|him;',
})
# strip mq_04
MEDIANT.update({
    '23:1': ':|', '24:1': ':|', '24:7': ':|gates;', '24:9': ':|gates;', '25:4': ':|salvation;',
    '25:10': ':|sin;', '26:1': ':|',
})
# strip mq_05
MEDIANT.update({
    '26:6': ':|altar;', '26:9': ':|blood-thirsty;', '27:14': ':|', '29:8': ':|', '30:6': ':|',
    '30:11': ':|', '30:12': ':|gladness:', '31:1': ':|confusion;', '31:15': ':|side;',
})
RECROP = {'31:1': 'first crop ended at righteous-; re-cropped (recrop_31_1): the verse ends ness. -- no further mark'}
# strip mq_06
MEDIANT.update({
    '32:8': ':|in;', '33:1': ':|', '35:28': ':|', '37:13': ':|', '38:1': ':|displeasure:',
    '38:12': ':|', '39:4': ':|me; tongue:', '39:13': ':|tears;', '39:14': ',|sojourner:',
})
# strip mq_07
MEDIANT.update({
    '40:9': ':|come;', '40:21': ':|', '41:6': ':|himself;', '41:7': ':|evil:', '43:2': ':|strength;',
    '43:3': ':|', '44:1': ':|old:', '47:6': ':|', '47:7': ':|', '48:7': ':|',
})
# strip mq_08
MEDIANT.update({
    '49:3': ':|', '49:14': ':|sheep;', '50:18': ':|', '52:7': ':|scorn:', '54:2': ':|',
    '55:2': ':|vexed;', '55:7': ':|', '55:12': ':|it#2;', '55:13': ':|him;', '56:6': ':|',
    '56:13': ':|',
})
# strip mq_09
MEDIANT.update({
    '57:1': ':|me;', '57:4': ':|lions;', '58:1': ':|', '59:14': ':|', '62:7': ':|might;',
    '62:9': ':|weights;', '62:10': ':|robbery;', '63:2': ':|thee;', '63:4': ':|',
})
# strip mq_10
MEDIANT.update({
    '64:5': ':|snares;', '65:1': ':|', '65:11': ':|furrows;', '65:14': ':|', '66:1': ':|Name;',
    '67:6': ':|', '68:1': ':|', '68:28': ':|',
})
# strip mq_11
MEDIANT.update({
    '68:33': ':|voice;', '69:23': ':|', '70:6': ':|', '71:1': ':|trust; righteousness;',
    '71:9': ':|me; him;', '71:19': ':|side:', '73:4': ':|', '73:13': ':|',
})
# strip mq_12
MEDIANT.update({
    '74:10': ':|tokens;', '76:5': ':|', '78:1': ':|', '78:30': ':|filled;', '78:60': ':|Israel;',
    '78:71': ':|sheep-folds:', '83:5': ':|thee:', '85:1': ':|', '86:17': ':|good;', '87:1': ':|',
})
# strip mq_13
MEDIANT.update({
    '88:1': ':|calling;', '89:3': ':|servant:', '89:19': ':|', '89:49': ':|people;', '90:17': ':|us#2;',
    '91:2': ':|', '92:13': ':|well-liking;', '93:3': ':|', '93:5': ':|', '94:10': ':|knowledge;',
})
NOTES['91:2'] = "book prints 'stronghold' as one word (cell: 'strong hold')"
# strip mq_14
MEDIANT.update({
    '95:8': ':|wilderness;', '95:10': ':|ways:', '98:6': ':|', '98:7': ':|', '99:1': ':|',
    '99:5': ':|footstool;', '100:1': ':|', '100:2': ';|ourselves:', '101:1': ':|',
})
NOTES['99:1'] = "book prints 'impa-|tient' (impatient) where the cell has 'unpatient' -- a WORD difference"
# strip mq_15
MEDIANT.update({
    '103:2': ':|benefits:', '104:23': ':|', '105:5': ':|mouth;', '105:11': ':|inheritance:',
    '106:46': ':|', '107:1': ';|', '108:5': ':|earth;', '108:8': ':|head;',
    '108:9': ':|lawgiver; shoe;', '109:1': ':|',
})
# strip mq_16
MEDIANT.update({
    '109:14': ':|earth;', '109:16': ':|', '109:25': ':|mercy;', '109:29': ':|multitude;',
    '110:2': ':|', '110:3': ':|', '115:7': ':|not;', '116:8': ':|', '116:9': ':|', '117:2': ':|',
})
# strip mq_17
MEDIANT.update({
    '119:34': ':|', '119:41': ':|', '119:73': ':|', '119:81': ':|', '119:125': ':|servant;',
    '119:159': ':|', '120:6': ':|peace;', '126:7': ':|', '128:6': ':|long;', '129:1': ':|say;',
})
# strip mq_18
MEDIANT.update({
    '130:1': ':|', '132:1': ':|trouble:', '132:2': ':|Jacob:', '132:11': ':|it:', '132:17': ':|',
    '133:1': ':|', '133:2': ':|', '135:10': ':|kings:', '136:7': ':|ever:', '136:18': ':|ever:',
    '136:20': ':|ever;',
})
# strip mq_19
MEDIANT.update({
    '137:3': ':|', '137:5': ':|', '139:1': ':|up-rising;', '139:7': ';|', '139:11': ':|',
    '140:1': ':|man#2;', '141:1': ':|', '141:7': ':|words;', '141:9': ':|trust;',
})
NOTES['139:11'] = "the stop after 'with thee' (p525 last row) is damaged type; read at 3x as a comma, not a semicolon, but not certain"
# strip mq_20
MEDIANT.update({
    '143:10': ':|thee;', '143:12': ':|soul;', '144:1': ':|fight:', '144:11': ':|iniquity:',
    '144:12': ':|temple;', '144:13': ':|streets;', '145:8': ':|', '146:4': ':|God#2:',
    '146:9': ':|strangers;',
})
# strip mq_21
MEDIANT.update({
    '147:7': ':|God:', '149:2': ':|', '149:8': ':|iron;',
})

# ---- CONTROL SAMPLE (w22_control.py, seed 20261016) ----
# strip ctl_00
CONTROL.update({
    '2:3': ':|', '2:10': ':|', '7:9': ':|', '9:17': ':|', '10:7': ':|', '10:10': ':|',
    '11:1': ':|', '17:3': ':|season;', '17:6': ':|', '18:29': ':|',
})
# strip ctl_01
CONTROL.update({k: ':|' for k in ('18:46', '18:50', '21:7', '21:11', '21:13', '22:4', '22:6',
                                  '22:9', '22:16', '22:18', '22:21')})
# strip ctl_02
CONTROL.update({k: ':|' for k in ('26:11', '29:1', '31:12', '31:22', '33:5', '34:6', '34:8', '35:4')})
CONTROL['28:1'] = ':|me;'
# strip ctl_03
CONTROL.update({k: ':|' for k in ('35:11', '36:5', '37:14', '37:20', '37:34', '38:4', '39:7',
                                  '40:8', '40:12')})
RECROP['37:20'] = 'first crop ended before the last row; re-cropped (recrop_37_20): ends away. -- no further mark'
# strip ctl_04
CONTROL.update({k: ':|' for k in ('44:4', '44:11', '46:7', '48:3', '50:22', '51:9', '54:1')})
CONTROL.update({'40:15': ':|me;', '49:8': ':|ever;', '50:16': ':|mouth;'})
# strip ctl_05
CONTROL.update({k: ':|' for k in ('54:4', '54:7', '57:8', '58:5', '59:10', '61:4', '65:2',
                                  '68:10', '69:7')})
CONTROL.update({'58:4': ':|ears;', '62:11': ':|God#2;', '68:32': ':|Lord;'})
# strip ctl_06
CONTROL.update({k: ':|' for k in ('69:11', '71:4', '72:1', '73:1', '73:18', '74:15', '76:1',
                                  '77:15', '78:62', '81:5')})
# strip ctl_07
CONTROL.update({k: ':|' for k in ('83:2', '83:17', '85:5', '86:4', '86:8', '87:7', '89:10',
                                  '89:13', '89:45', '90:6')})
CONTROL.update({'89:31': ':|judgments;', '92:7': ':|ever;'})
# strip ctl_08
CONTROL.update({k: ':|' for k in ('94:5', '94:13', '94:21', '95:3', '97:12', '98:9', '103:7',
                                  '103:12', '105:4', '105:40', '105:41')})
CONTROL.update({'102:9': ':|weeping;', '102:20': ':|death;'})
# strip ctl_09
CONTROL.update({k: ':|' for k in ('106:3', '106:31', '106:39', '107:8', '107:16', '107:18',
                                  '108:11', '109:8', '109:23')})
CONTROL.update({'106:34': ':|them;', '106:36': ':|devils;', '107:10': ':|iron;'})
# strip ctl_10
CONTROL.update({k: ':|' for k in ('114:6', '116:5', '116:7', '116:16', '118:1', '118:5',
                                  '118:15', '119:3', '119:64')})
CONTROL.update({'112:10': ':|away;', '113:6': ':|mire;'})
# strip ctl_11
CONTROL.update({k: ':|' for k in ('119:70', '119:95', '119:101', '119:104', '119:107',
                                  '119:119', '119:139', '119:165', '126:1', '130:3', '132:9')})
CONTROL['132:3'] = ':|bed;'
# strip ctl_12
CONTROL.update({k: ':|' for k in ('136:4', '137:6', '137:9', '138:7', '139:6', '140:2',
                                  '142:2', '144:5', '144:6')})
CONTROL.update({'135:1': ':|LORD#3;', '136:19': ':|ever;'})
# strip ctl_13
CONTROL.update({k: ':|' for k in ('145:6', '145:14', '146:8', '147:13', '148:12', '150:3')})
CONTROL.update({'146:5': ':|ever;', '148:8': ':|word;'})
NOTES['37:20'] = "book: 'perish, and the' -- a comma where the cell prints ';' (control sample)"
