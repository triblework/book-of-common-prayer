"""wxa_hand.py -- the passages the mechanical keying refused, hand-keyed by
script with their own anchors (R22: "what the mechanical keying refuses is
hand-keyed by script with its own anchor, or flagged").

Each entry names, in the cell's BASE paragraph (file, base line), the
stretch to replace -- from the start of `cell_from` to the end of the first
`cell_to` that ends at or after it (`cell_to` None: `cell_from` itself, the
whole block when `cell_from` is None) -- and the BOOK text that replaces it,
as a list of segments cut from the page(s) by the script:

    (prefix, book_from, book_to)   the book's text from the start of
                                   book_from to the end of the first book_to
                                   ending at or after it (None: book_from
                                   alone), searched in order, each after the
                                   last; set as one block with `prefix`
                                   ('' text, '> ' rubric, '## '/'### '
                                   heading)
    ('label', book_from, book_to)  a speaker's line: the book's first word is
                                   the speaker (italic in the PDF), set as the
                                   cell's own label form `**Name.**`
    ('label2', book_from, book_to) as 'label', the speaker's name two words
                                   ('New Bishop')
    ('or', book_from, book_to)     as '' but the book's ', or ' is set as the
                                   line's own ', *or* '
    ('lines', book_from, book_to)  one block keeping the book's line breaks
Blocks are joined with a blank line. Only anchors (a few words each) are
written here; every restored word is the book's, cut by the script. A word
the cell already has (the same letters) keeps the CELL's letter-case: no
case is taken from this witness (R11).

Two passages are NOT restored: each would carry a half-verse across the
mediant, and pointing may not be taken from this witness (R11/R22). They
are flagged instead (FLAGGED below).
"""

HAND = [
    # --- collects: two "Or this" collects spliced into one --------------
    dict(file='collects-epistles-gospels/christmas-day.md', line=27, page=213,
         cell_from='to whom with you and the sa', cell_to='after Christmas Day.*',
         segs=[('', 'to whom with you and the same Spirit',
                'now and for ever. Amen.'),
               ('> ', 'The Collect immediately preceding',
                'First Sunday after Christmas Day.')]),
    dict(file='collects-epistles-gospels/easter-day.md', line=23, page=222,
         cell_from='may worship only-begotten Son', cell_to=None,
         segs=[('', 'may worship you in sincerity', 'now and for ever. Amen.'),
               ('> ', 'or this', None),
               ('', 'Almighty God, who through your only-begotten',
                'only-begotten Son')]),
    # --- the Holy Eucharist --------------------------------------------
    dict(file='holy-communion/holy-communion.md', line=129, page=329,
         cell_from='in all thy works, departed', cell_to=None,
         segs=[('', 'in all thy works, that, rejoicing',
                'stewards of thy bounty.'),
               ('', 'And we most humbly beseech thee, of thy goodness',
                'or any other adversity.'),
               ('> ', 'Additional petitions and thanksgivings',
                'may be included here.'),
               ('', 'And we also bless thy holy Name for all thy servants',
                'servants departed')]),
    dict(file='holy-communion/holy-communion.md', line=243, page=336,
         cell_from='manifold sins, to off all honor', cell_to=None,
         segs=[('', 'manifold sins, to offer unto thee any sacrifice',
                'Holy Ghost, all honor')]),
    dict(file='holy-communion/holy-communion.md', line=311, page=339,
         cell_from='to whom with Son Jesus Christ our Lord;', cell_to=None,
         segs=[('', 'to whom, with thee and the Holy Ghost',
                'world without end. Amen.'),
               ('> ', 'The Bishop when present', 'gives the blessing'),
               ('', 'The peace of God, which passeth',
                'Son Jesus Christ our Lord;')]),
    dict(file='holy-communion/holy-communion.md', line=471, page=346,
         cell_from='who put their iced for us', cell_to=None,
         segs=[('', 'who put their trust in him.', None),
               ('> ', 'Easter', None),
               ('', 'But chiefly are we bound', 'who was sacrificed for us')]),
    dict(file='holy-communion/holy-communion.md', line=551, page=355,
         cell_from=None, cell_to=None,
         segs=[('### ', 'The Word of God', None),
               ('> ', 'A hymn, psalm, or anthem may be sung.', None),
               ('> ', 'The people standing, the Celebrant says', None),
               ('', 'Blessed be God: Father, Son, and Holy Spirit.', None),
               ('label', 'People And blessed be his kingdom', 'Amen.'),
               ('> ', 'In place of the above, from Easter Day',
                'the Day of Pentecost')]),
    dict(file='holy-communion/holy-communion.md', line=654, page=359,
         cell_from=None, cell_to=None,
         segs=[('', 'Those who suffer and those in any trouble', None),
               ('', 'The departed (with commemoration', 'when appropriate)'),
               ('> ', 'See the forms beginning on page 383.', None)]),
    dict(file='holy-communion/holy-communion.md', line=1002, page=375,
         cell_from='all the saints whe have', cell_to=None,
         segs=[('', 'all the saints who have', None)]),
    dict(file='holy-communion/holy-communion.md', line=1136, page=349,
         cell_from='Through Jesus Cepared for us', cell_to=None,
         segs=[('', 'Through Jesus Christ our Lord; who rose victorious',
                'there is prepared for us')]),
    dict(file='holy-communion/holy-communion.md', line=1230, page=386,
         cell_from=None, cell_to=None,
         segs=[('', 'I ask your prayers for all who seek God',
                'knowledge of him.'),
               ('', 'Pray that they may find and be found by him.', None),
               ('> ', 'Silence', None),
               ('', 'I ask your prayers for the departed', '].'),
               ('', 'Pray for those who have died.', None),
               ('> ', 'Silence', None),
               ('> ', 'Members of the congregation may ask', 'those present')]),
    dict(file='holy-communion/holy-communion.md', line=1420, page=394,
         cell_from=None, cell_to=None,
         segs=[('### ', 'The Collect at the Prayers', None),
               ('> ', 'For the concluding Collect', 'the Celebrant selects'),
               ('', '(a) a Collect appropriate', 'being celebrated;'),
               ('', '(b) a Collect expressive', 'local congregation;'),
               ('', '(c) a Collect for the mission of the Church;', None)]),
    # --- the Burial of the Dead ------------------------------------------
    dict(file='occasional-offices/burial.md', line=300, page=480,
         cell_from="The Apostle's creed may be said, all standing", cell_to=None,
         segs=[('', 'The Apostles\u2019 Creed may be said', 'all standing.')]),
    dict(file='occasional-offices/burial.md', line=380, page=484,
         cell_from=None, cell_to=None,
         segs=[('', 'The Song of Zechariah, Benedictus', None),
               ('', 'The Song of Simeon, Nunc dimittis', None),
               ('', 'Christ our Passover, Pascha nostrum', None),
               ('## ', 'The Committal', None),
               ('> ', 'The following anthem is sung or said', None),
               ('', 'In the midst of life we are in death;',
                'art justly displeased?')]),
    dict(file='occasional-offices/burial.md', line=454, page=489,
         cell_from='who with the who', cell_to=None,
         segs=[('', 'who with the Father and the Holy Spirit',
                'now and for ever. Amen.'),
               ('', 'Almighty God, Father of mercies', 'with all those who')]),
    dict(file='occasional-offices/burial.md', line=750, page=503,
         cell_from='from the ng in his sight', cell_to=None,
         segs=[('', 'from the dead our Lord Jesus Christ',
                'well-pleasing in his sight')]),
    # --- the occasional offices --------------------------------------------
    dict(file='occasional-offices/churching.md', line=125, page=444,
         cell_from='Grant, mostChrist our Lord', cell_to=None,
         segs=[('', 'Grant, most merciful Father', 'through Jesus Christ our Lord')]),
    dict(file='occasional-offices/confirmation.md', line=45, page=413,
         cell_from=None, cell_to=None,
         segs=[('label', 'Bishop One Lord, one Faith, one Baptism;', None),
               ('label', 'People One God and Father of all.', None),
               ('label', 'Bishop The Lord be with you.', None),
               ('label', 'People And also with you.', None),
               ('label', 'Bishop Let us pray.', None),
               ('> ', 'The Collect of the Day', None),
               ('label', 'People Amen.', None),
               ('> ', 'At the principal service on a Sunday',
                'may be substituted.')]),
    dict(file='occasional-offices/confirmation.md', line=185, page=418,
         cell_from='brought us to yourselt your Son', cell_to=None,
         segs=[('', 'brought us to yourself, and that',
                'through Jesus Christ your Son')]),
    dict(file='occasional-offices/matrimony.md', line=219, page=433,
         cell_from='prescribed fo service.', cell_to=None,
         segs=[('', 'prescribed for celebrations of the Holy Eucharist',
                'in the Marriage service.')]),
    dict(file='occasional-offices/public-baptism.md', line=19, page=298,
         cell_from=None, cell_to=None,
         segs=[('> ', 'It is fitting that parents be included',
                'members of his Church.'),
               ('> ', 'Additional Directions are on page 312.', None),
               ('> ', 'A hymn, psalm, or anthem may be sung.', None),
               ('> ', 'The people standing, the Celebrant says', None)]),
    dict(file='occasional-offices/public-baptism.md', line=167, page=303,
         cell_from=None, cell_to=None,
         segs=[('label', 'Presenters I present these persons for Confirmation.',
                None),
               ('> ', 'or', None),
               ('', 'I present these persons to be received', 'Communion.'),
               ('> ', 'or', None),
               ('', 'I present these persons who desire',
                'baptismal vows.')]),
    dict(file='occasional-offices/public-baptism.md', line=345, page=309,
         cell_from='*The Bishodaily increase', cell_to=None,
         segs=[('> ', 'The Bishop lays hands upon each one and says', None),
               ('', 'Strengthen, O Lord, your servant N.', 'of his life. Amen.'),
               ('> ', 'or this', None),
               ('', 'Defend, O Lord, your servant N.', 'daily increase')]),
    dict(file='occasional-offices/visitation-sick.md', line=123, page=458,
         cell_from='O Father of mercierve him', cell_to=None,
         segs=[('', 'O Father of mercies and God of all comfort', 'preserve him')]),
    dict(file='occasional-offices/visitation-sick.md', line=123, page=458,
         cell_from='grant that he may dwell with thee', cell_to=None,
         segs=[('', 'grant that finally he may dwell with thee', None)]),
    # --- the Ordinal -----------------------------------------------------
    dict(file='ordinal/consecration-bishops.md', line=103, page=516,
         cell_from=None, cell_to=None,
         segs=[('> ', 'or the Reader may say', None),
               ('', 'Here ends the Reading (Epistle).', None),
               ('> ', 'Silence may follow.', None),
               ('> ', 'A Psalm, canticle, or hymn follows each Reading.', None),
               ('> ', 'Then, all standing, a Deacon or a Priest',
                'first saying')]),
    dict(file='ordinal/ordering-deacons.md', line=11, page=537,
         cell_from=None, cell_to='forgives all our sins',
         segs=[('label', 'People And blessed be his kingdom', 'Amen.'),
               ('> ', 'In place of the above, from Easter Day',
                'the Day of Pentecost'),
               ('label', 'Bishop Alleluia. Christ is risen.', None),
               ('label', 'People The Lord is risen indeed. Alleluia.', None),
               ('> ', 'In Lent and on other penitential occasions', None),
               ('label', 'Bishop Bless the Lord who forgives all our sins',
                None)]),
    dict(file='ordinal/ordering-deacons.md', line=87, page=540,
         cell_from='1 Tiks be to God.', cell_to=None,
         segs=[('or', '1 Timothy 3:8-13, or Acts 6:2-7', None),
               ('> ', 'The Reader first says', None),
               ('', 'A Reading (Lesson) from', '.'),
               ('> ', 'A citation giving chapter', 'may be added.'),
               ('> ', 'After each Reading, the Reader may say', None),
               ('', 'The Word of the Lord.', None),
               ('label', 'People Thanks be to God.', None)]),
    dict(file='ordinal/preface.md', line=9, page=510,
         cell_from='but is a nt custom,', cell_to=None,
         segs=[('', 'but is a gift from God', 'priest, and deacon.'),
               ('## ', 'Concerning the Ordination of a Bishop', None),
               ('', 'In accordance with ancient custom,', None)]),
]

# Short paragraphs the mechanical keying refused as look-alike risks, keyed
# here in their own place.
HAND += [
    dict(file='daily-office/evening-prayer.md', line=161, page=67,
         cell_from='And also with you.', cell_to=None,
         segs=[('', 'And with thy spirit.', None)]),
    dict(file='daily-office/morning-prayer.md', line=480, page=54,
         cell_from='And also with you.', cell_to=None,
         segs=[('', 'And with thy spirit.', None)]),
    dict(file='holy-communion/holy-communion.md', line=87, page=326,
         cell_from=None, cell_to=None,
         segs=[('label', 'People Glory be to thee, O Lord.', None)]),
    dict(file='the-litany/litany.md', line=134, page=153,
         cell_from=None, cell_to=None,
         segs=[('lines', 'Kyrie eleison.', 'Christe eleison. Kyrie eleison.')]),
    dict(file='occasional-offices/burial.md', line=723, page=502,
         cell_from='People and Celebrant', cell_to=None,
         segs=[('', 'Celebrant and People', None)]),
    dict(file='occasional-offices/public-baptism.md', line=405, page=312,
         cell_from=None, cell_to=None,
         segs=[('> ', 'If the movement to the font is', 'may be sung.'),
               ('> ', 'Where practicable, the font is to be filled',
                'before the Thanksgiving over the Water.')]),
]

# Not restored (pointing, R11/R22): flagged, with the book's page.
# --- found in Phase 2 (the edge, size and furniture guards, wxa_items):
# items the mechanical keying made that cut a paragraph short, or that
# aligned a paragraph to the wrong text, are refused there and the passage
# is keyed here from the book.
HAND += [
    # Evening Prayer, Rite Two: the 1993 keying set Morning Prayer's
    # invitation to confession and four of its collects in Evening
    # Prayer's slots (each is word for word the Morning Prayer text, pp.
    # 79, 98-99); the book prints Evening Prayer's own (pp. 116, 123)
    dict(file='daily-office/evening-prayer.md', line=319, page=116,
         cell_from=None, cell_to=None,
         segs=[('', 'Dear friends in Christ, here', 'infinite goodness and mercy.')]),
    dict(file='daily-office/evening-prayer.md', line=517, page=123,
         cell_from=None, cell_to=None,
         segs=[('', 'Lord God, whose Son our Savior',
                'reigns for ever and ever. Amen.')]),
    dict(file='daily-office/evening-prayer.md', line=521, page=123,
         cell_from=None, cell_to=None,
         segs=[('', 'Lord Jesus Christ, by your death',
                "tender mercies' sake. Amen.")]),
    dict(file='daily-office/evening-prayer.md', line=525, page=123,
         cell_from=None, cell_to=None,
         segs=[('', 'O God, the source of eternal light',
                'through Jesus Christ our Lord. Amen.')]),
    dict(file='daily-office/evening-prayer.md', line=529, page=123,
         cell_from=None, cell_to=None,
         segs=[('', 'Most holy God, the source of all',
                'Christ Jesus our Savior. Amen.')]),
    # traditional collects keyed with a contemporary ending
    dict(file='collects-epistles-gospels/good-friday.md', line=7, page=169,
         cell_from='Holy Spirit, one God,', cell_to='Amen.',
         segs=[('', 'Holy Ghost ever, one God,', 'world without end. Amen.')]),
    dict(file='collects-epistles-gospels/st-peter.md', line=7, page=190,
         cell_from='the Holy Spirit, one God,', cell_to='Amen.',
         segs=[('', 'the same Spirit, one God,', 'for ever and ever. Amen.')]),
    # a swallowed stretch whose stub the word pass had read as a word
    dict(file='occasional-offices/burial.md', line=440, page=487,
         cell_from='Almightons;', cell_to=None,
         segs=[('', 'Almighty and everlasting God, we yield',
                'their several generations;')]),
    dict(file='occasional-offices/burial.md', line=519, page=493,
         cell_from='death, an one God,', cell_to=None,
         segs=[('', 'death, and brought life and immortality',
                'and reigns, one God,')]),
    dict(file='occasional-offices/burial.md', line=667, page=499,
         cell_from='body, says', cell_to=None,
         segs=[('', 'Alleluia, alleluia, alleluia.', None),
               ('', 'Give rest, O Christ, to your servant(s)',
                'but life everlasting.'),
               ('> ', 'The Celebrant, facing the body, says', None)]),
    dict(file='ordinal/consecration-bishops.md', line=241, page=523,
         cell_from='m this time forth for evermore.', cell_to=None,
         segs=[('', 'who lives and reigns with you and',
                'now and for ever. Amen.'),
               ('> ', 'The new Bishop blesses the people,', 'first saying'),
               ('', 'Our help is in the Name of the Lord;', None),
               ('label', 'People The maker of heaven and earth.', None),
               ('label2', 'New Bishop Blessed be the Name of the Lord;', None),
               ('label', 'People From this time forth for evermore.', None)]),
    dict(file='ordinal/ordering-priests.md', line=51, page=527,
         cell_from=None, cell_to=None,
         segs=[('> ', 'The Ordinand then signs the above Declaration',
                'in the sight of all present.'),
               ('> ', 'All stand. The Bishop says to the people', None),
               ('', 'Dear friends in Christ, you know the importance',
                'and make it known.')]),
    dict(file='ordinal/ordering-deacons.md', line=241, page=549,
         cell_from='Tho the end,', cell_to=None,
         segs=[('', 'That he may faithfully fulfill the duties',
                'Lord, hear our prayer.'),
               ('', 'That by the indwelling of the Holy Spirit',
                'to persevere to the end,')]),
    dict(file='holy-communion/holy-communion.md', line=185, page=333,
         cell_from=None, cell_to=None,
         segs=[('> ', 'The Celebrant may begin the Offertory',
                'other sentence of Scripture.'),
               ('> ', 'During the Offertory, a hymn,', 'may be sung.'),
               ('> ', 'Representatives of the congregation bring',
                'placed on the Altar.')]),
    dict(file='holy-communion/holy-communion.md', line=884, page=369,
         cell_from='pd of', cell_to=None,
         segs=[('> ', 'The Celebrant continues', None),
               ('', 'And we offer our sacrifice of praise', 'O Lord of')]),
    dict(file='occasional-offices/visitation-sick.md', line=65, page=455,
         cell_from='Christ, stren', cell_to=None,
         segs=[('', 'Christ, strengthen you in all goodness,',
                'in eternal life. Amen.'),
               ('> ', 'A deacon or lay person using the preceding',
                'for "your."')]),
]

FLAGGED = [
    dict(file='occasional-offices/burial.md', line=188, page=476,
         key='and lead me forth in the paths',
         note="the 1993 keying fuses two verses of Psalm 23; the witness "
              "(Church Publishing's PDF, p. 476) prints the half-verse "
              "'beside the waters of comfort' and the verse 'He shall convert "
              "my soul', but restoring them would take a mediant from the "
              "file (R11, R22), so the verse is carried as the e-text prints it"),
    dict(file='occasional-offices/burial.md', line=230, page=478,
         key='face froRD in the land of the living',
         note="the 1993 keying fuses two verses of Psalm 27 ('froRD'); the "
              "witness (Church Publishing's PDF, p. 478) prints 'from me' and "
              "the next verse, but restoring them would take a mediant and "
              "the small-capital Name from the file (R11, R22), so the verse "
              "is carried as the e-text prints it"),
    dict(file='occasional-offices/burial.md', line=136, page=474,
         key='morning watch;redemption.',
         note="the 1993 keying fuses two verses of Psalm 130 ('watch;"
              "redemption'); the witness (Church Publishing's PDF, p. 474) "
              "prints the half-verse 'I say, before the morning watch' and "
              "the verse that follows, but restoring them "
              "would take a mediant from the file (R11, R22), so the verse is "
              "carried as the e-text prints it"),
]
