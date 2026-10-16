"""w22_punct_eye.py -- the EYE reads of the punctuation positions (w22_punct_strips).

One string per strip pu_NN, one symbol per position in order (P001...):
  ':' ';' ',' '.' '!'  the mark the book prints right after the word
  'Q'                  a question mark
  '-'                  no mark
  '?'                  not legible at strip scale -- re-read at 3x, see FIX
  'W'                  a word-division difference (the book prints one word)
  'X'                  the crop does not show the cell's word (misplaced by the
                       alignment) -- re-read off a whole-verse crop, see FIX
"""
STRIPS = {}
FIX = {}       # position number -> (mark, note) read off a whole-verse crop

STRIPS[0] = '::-.-,.-,,-;,.-:-;-Q,,;Q,X.,-;;;;--.-,,,'
STRIPS[1] = ';-.,;:;-,---,.-;:-:::--;X--;,.;--;,,.-;;'
STRIPS[2] = '..;,-;;,-.,-,.,,.,:;X,-;-;--,,-,,--,!!-!'
FIX[101] = ('.', "line-end 'righteous-|ness.'; read off recrop_31_1")
STRIPS[3] = '!,.-.,,,:-.,--;:,;:,.--,;,,,,!!,,,-;,:-.'
STRIPS[4] = ';.:,-,.,....-;..--,:-.,.;,-;-;,.;;.-Q,,-'
STRIPS[5] = ',.-;;;?;,;,;.;;.,,-,-,;.X..!!,.,;W,-.;!!'
STRIPS[6] = ':,..--,;Q,.,,-,;,,;:,-.,.,:,,X..;,,,;,:,'
STRIPS[7] = '.,W;-;W-;,..;.,;:,.,.,;.:.!,,:,,.,,,,,.;'
STRIPS[8] = ';,:-,-,,,,,,.,,,-;;;;.;,,-;-;,..!,...,,.'
STRIPS[9] = '.,.,,,,!;.---.-.-,!;,,;;X:::.!.,:,,:,-:,'
STRIPS[10] = ',,,.-,,,,;?,;,X,;;,,;::;,;,,.,:;:-,,.;X'
FIX[411] = (',', "damaged type after 'with thee' (p525 last row); at 3x a comma, not a semicolon -- uncertain")
# the misplaced positions, re-read off whole-verse crops (strip pu_fix)
FIX[26] = (',', "12:1 'HELP me, LORD' -- the alignment had mapped the incipit's 'me'")
FIX[65] = (';', "22:1 'look upon me;' -- the alignment had mapped the second 'me'")
FIX[207] = (',', "63:1 'O God, thou art' -- display type; a comma at 3x")
FIX[225] = (',', "69:1 'SAVE me, O God' -- the alignment had mapped the incipit's 'me'")
FIX[270] = ('-', "85:1 'thou art become' -- no mark")
FIX[385] = (',', "132:1 'LORD, remember David'")
FIX[415] = (',', "141:1 'upon thee, haste thee'")
FIX[439] = ('.', "150:6: the cell carries the colophon 'THE END OF THE PSALTER' inside the verse, without its stop; the book sets it as a separate line ending in a period")
# notes on what else the crop shows at a position (the mark itself is in STRIPS)
NOTE = {
    43: "book: 'strength. The LORD' -- a full stop AND a capital T (cell: ' ; the')",
    224: "book: 'people. Blessed be God' -- a full stop AND a capital B (cell: '; blessed')",
    319: "book: 'soul. Praise the' -- a full stop AND a capital P (cell: ', praise')",
    199: "cell prints a full stop inside the vocative 'thou. O LORD' -- a carrier slip",
    14: "the cell's verse ends with no stop at all -- a carrier slip",
    195: "the cell's verse ends with no stop at all -- a carrier slip",
    177: "book: 'Thou sattest and spakest' -- no comma AND the spelling sattest (cell: 'satest,')",
}
