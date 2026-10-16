"""w21_witness.py -- the 1928 Psalter read against two page scans: the keyed
corrections they warrant (Workstream B). Applied by w13_build.py (Phase 2,
after the maintainer's rulings R19/R20 of 2026-10-16):

  R19  BCP1929 (the original printing) is THE witness. The 1952 facsimile is a
       second witness within limits: it corroborates where both agree and
       settles the four compounds 1929 breaks at a line end (1:3, 80:10,
       104:17, 139:1). Printing disagreements are recorded, never imported:
       inline VERIFY at 32:3 and 55:14 only; the other eight go to provenance.
  R20  "The End of the Psalter." is book furniture: deleted from 150:6.
  The recommended policy (17 corrections) is approved; the five compounds
  broken at a line end in BOTH printings keep the carrier's form, flagged.

THE SCANS (both justus "PDF graphics"; see the Phase 1 report):
  1929  1928/BCP1929.pdf -- the "Cambridge Edition" (Old Corner Book Store,
        Boston), certified 1929 by the Custodian (Robinson) against "a
        certified copy of the Standard Book": the original 1928 printing.
  1952  1928Standard/1952std.pdf -- the 1952 facsimile of Updike's Standard
        Book, certified Sept. 1952 (Suter) as conforming to the Standard Book
        "as amended by subsequent actions of General Conventions".
Two different typesettings, so a compound broken at a line end in one is
often whole in the other.

THE CARRIER is justus 1928/Psalms1-3.htm (w13_1928.parse()), which keeps the
book's '*' mediant; w13_render turns it into the corpus's ' : '. Every
correction below is stated in CARRIER form, keyed to the reading it replaces
(a short fragment that must occur EXACTLY ONCE in that verse, else the build
stops), and applied to the parsed carrier before rendering.

`attest` says what each scan prints at that place (w21_eye.txt,
w21_evidence.json): 'mid' the form whole in one printed line, 'brk' broken at
a line end (that page cannot decide a hyphen), 'read' a word or a mark read
twice by machine and by eye. A correction is applied only when the POLICY
admits its attestation (see apply()): which scan is THE witness, and whether
the other may settle what the first cannot (Rulings 1 and 2, pending).

DISAGREE lists where the two PRINTINGS differ and the carrier already reads
as 1952 does. They are not corrections under the recommended policy; they
become corrections only if the ruling makes BCP1929 win a disagreement, and
otherwise belong in provenance/VERIFY as recorded variants.
"""
import re

#  key            (psalm, verse)   carrier fragment      becomes               attest
CORRECTIONS = [
    # the three flagged mediants: both printings point them
    dict(key='18:28:mediant', ps=18, v=28, kind='pointing',
         was='in adversity, and shalt', now='in adversity, * and shalt',
         attest={'1929': 'read', '1952': 'read'}),
    dict(key='109:21:mediant', ps=109, v=21, kind='pointing',
         was='poor, ~ and', now='poor, * and',
         attest={'1929': 'read', '1952': 'read'}),
    dict(key='119:1:mediant', ps=119, v=1, kind='pointing',
         was='in the way, and walk', now='in the way, * and walk',
         attest={'1929': 'read', '1952': 'read'}),
    # readings and spacing (keying slips in the carrier)
    dict(key='29:4:LORDd', ps=29, v=4, kind='reading',
         was='the LORDd is', now='the LORD is',
         attest={'1929': 'read', '1952': 'read'}),
    dict(key='12:1:me,LORD,', ps=12, v=1, kind='spacing',
         was='me,LORD,', now='me, LORD,',
         attest={'1929': 'read', '1952': 'read'}),
    dict(key='20:9:Save,LORD;', ps=20, v=9, kind='spacing',
         was='Save,LORD;', now='Save, LORD;',
         attest={'1929': 'read', '1952': 'read'}),
    # compounds the carrier closes and the book hyphenates, whole in a line
    dict(key='3:7:cheekbone', ps=3, v=7, kind='hyphen',
         was='the cheekbone;', now='the cheek-bone;',
         attest={'1929': 'mid', '1952': 'mid'}),
    dict(key='40:6:usward', ps=40, v=6, kind='hyphen',
         was='to usward;', now='to us-ward;',
         attest={'1929': 'mid', '1952': 'mid'}),
    dict(key='44:15:byword', ps=44, v=15, kind='hyphen',
         was='a byword among', now='a by-word among',
         attest={'1929': 'mid', '1952': 'mid'}),
    dict(key='65:8:outgoings', ps=65, v=8, kind='hyphen',
         was='the outgoings of', now='the out-goings of',
         attest={'1929': 'mid', '1952': 'mid'}),
    dict(key='28:2:mercyseat', ps=28, v=2, kind='hyphen',
         was='the mercyseat of', now='the mercy-seat of',
         attest={'1929': 'mid', '1952': 'brk'}),
    dict(key='42:10:daytime', ps=42, v=10, kind='hyphen',
         was='the daytime;', now='the day-time;',
         attest={'1929': 'mid', '1952': 'brk'}),
    dict(key='79:13:sevenfold', ps=79, v=13, kind='hyphen',
         was='them, O Lord, sevenfold', now='them, O Lord, seven-fold',
         attest={'1929': 'mid', '1952': 'brk'}),
    dict(key='119:149:lovingkindness', ps=119, v=149, kind='hyphen',
         was='thy lovingkindness;', now='thy loving-kindness;',
         attest={'1929': 'mid', '1952': 'brk'}),
    dict(key='147:16:hoarfrost', ps=147, v=16, kind='hyphen',
         was='the hoarfrost like', now='the hoar-frost like',
         attest={'1929': 'mid', '1952': 'brk'}),
    dict(key='139:1:uprising', ps=139, v=1, kind='hyphen',
         was='mine uprising;', now='mine up-rising;',
         attest={'1929': 'brk', '1952': 'mid'}),
    # structure: the book's colophon fused into the last verse by the parser
    dict(key='150:6:colophon', ps=150, v=6, kind='structure',
         was='the LORD. The End of the Psalter.', now='the LORD.',
         attest={'1929': 'read', '1952': 'read'}, needs='ruling-colophon'),
]

# Where the two printings differ; the carrier reads as 1952 (the Standard Book
# facsimile) in every case. `was` is the carrier's reading, `p1929` what the
# 1929 printing prints there.
DISAGREE = [
    dict(key='32:3:whilst', ps=32, v=3, kind='reading',
         was='For whilst I', p1929='For while I'),
    dict(key='37:38:bring', ps=37, v=38, kind='reading',
         was='shall bring a man', p1929='shall being a man'),          # misprint
    dict(key='55:14:own', ps=55, v=14, kind='reading',
         was='mine own familiar', p1929='mine old familiar'),
    dict(key='69:31:thanksgiving', ps=69, v=31, kind='reading',
         was='with thanksgiving.', p1929='with thanskgiving.'),        # misprint
    dict(key='116:15:thanksgiving', ps=116, v=15, kind='reading',
         was='of thanksgiving,', p1929='of thanskgiving,'),            # misprint
    dict(key='37:20:perish,', ps=37, v=20, kind='punctuation',
         was='shall perish, and', p1929='shall perish and'),
    dict(key='119:25:MY', ps=119, v=25, kind='reading',
         was='MY soul cleaveth', p1929='M soul cleaveth'),             # misprint
    dict(key='18:10:mediant', ps=18, v=10, kind='pointing',
         was='came down, * and', p1929='came down, and'),
    dict(key='73:20:mediant', ps=73, v=20, kind='pointing',
         was='awaketh; * so', p1929='awaketh; so'),
    dict(key='123:2:mediant', ps=123, v=2, kind='pointing',
         was='mistress, * even', p1929='mistress, even'),
]

# Compounds broken at a line end in BOTH printings: neither page decides the
# hyphen. The carrier's form stands; Phase 2 would flag each (Wave 17's 1:3).
UNDECIDABLE = ['35:13:sack-cloth', '50:9:he-goats', '78:27:southwest-wind',
               '81:17:wheat-flour', '103:8:long-suffering']

# The three Wave-13 flags these corrections close (w13_build.V1928).
CLOSES = [(18, 28), (109, 21), (119, 1)]

# The inline flags this pass OPENS (R19), added to the parsed psalms by
# apply() so that w13_render writes them on the line after the verse, as it
# writes every psalter flag. The key (first single-quoted string) is a fragment
# of the verse as rendered; the note gives both printings' readings and pages.
# 1929 = BCP1929.pdf (scan page = (book+40)//2), 1952 = 1952std.pdf (scan
# page = (book+62)//2); L for an even book page, R for an odd one.
NEW_VERIFIES = [
    (32, 3, 'whilst',
     'the 1928 witnesses disagree: the 1929 printing (BCP1929, scan 208R, p. 377) '
     'reads "For while I held"; the 1952 facsimile of the Standard Book (scan 219R, '
     'p. 377) reads "whilst", as the carrier. A printing disagreement, recorded and '
     'not imported (R19)'),
    (55, 14, 'mine own familiar',
     'the 1928 witnesses disagree: the 1929 printing (BCP1929, scan 223R, p. 407) '
     'reads "mine old familiar friend"; the 1952 facsimile of the Standard Book '
     '(scan 234R, p. 407) reads "own", as the carrier. A printing disagreement, '
     'recorded and not imported (R19)'),
    (35, 13, 'sack-cloth',
     'both 1928 printings break this word at a line end ("sack-" / "cloth"): '
     'BCP1929 scan 211L and the 1952 facsimile scan 222L, both p. 382, so neither '
     'page says whether the hyphen belongs to the word. Carried as the carrier prints it'),
    (50, 9, 'he-goats',
     'both 1928 printings break this word at a line end ("he-" / "goats"): '
     'BCP1929 scan 221L and the 1952 facsimile scan 232L, both p. 402, so neither '
     'page says whether the hyphen belongs to the word. Carried as the carrier prints it'),
    (78, 27, 'southwest-wind',
     'both 1928 printings break this word at a line end ("southwest-" / "wind"): '
     'BCP1929 scan 238L and the 1952 facsimile scan 249L, both p. 436, so neither '
     'page says whether the hyphen belongs to the word. Carried as the carrier prints it'),
    (81, 17, 'wheat-flour',
     'both 1928 printings break this word at a line end ("wheat-" / "flour"): '
     'BCP1929 scan 241R and the 1952 facsimile scan 252R, both p. 443, so neither '
     'page says whether the hyphen belongs to the word. Carried as the carrier prints it'),
    (103, 8, 'long-suffering',
     'both 1928 printings break this word at a line end ("long-" / "suffering"): '
     'BCP1929 scan 253L and the 1952 facsimile scan 264L, both p. 466, so neither '
     'page says whether the hyphen belongs to the word. Carried as the carrier prints it'),
]

POLICY = 'recommended'          # approved by the maintainer, 2026-10-16

# Policies. RECOMMENDED = Ruling 1 (B): BCP1929 the witness; Ruling 2 (a): the
# facsimile a second witness that corroborates, and settles a compound BCP1929
# breaks at a line end; disagreements recorded, never applied.
POLICIES = {
    'recommended': dict(primary='1929', second='1952', second_settles_breaks=True,
                        primary_wins_disagreements=False, colophon=True),
    'bcp1929-only': dict(primary='1929', second=None, second_settles_breaks=False,
                         primary_wins_disagreements=False, colophon=True),
    'both-must-agree': dict(primary='1929', second='1952', both_required=True,
                            second_settles_breaks=False,
                            primary_wins_disagreements=False, colophon=True),
}


def admitted(c, policy):
    a, P = c['attest'], POLICIES[policy] if isinstance(policy, str) else policy
    if c.get('needs') == 'ruling-colophon' and not P.get('colophon'):
        return False
    prim, sec = a.get(P['primary']), a.get(P.get('second')) if P.get('second') else None
    if P.get('both_required'):
        return prim in ('mid', 'read') and sec in ('mid', 'read')
    if prim in ('mid', 'read'):
        return True
    if prim == 'brk' and sec == 'mid' and P.get('second_settles_breaks'):
        return True
    return False


def selected(policy=None):
    policy = policy or POLICY
    out = [c for c in CORRECTIONS if admitted(c, policy)]
    P = POLICIES[policy] if isinstance(policy, str) else policy
    if P.get('primary_wins_disagreements'):
        out += [dict(d, now=d['p1929'], attest={'1929': 'read'}) for d in DISAGREE]
    return out


def apply_text(text, ps, v, items, log):
    for c in items:
        if (c['ps'], c['v']) != (ps, v):
            continue
        if text.count(c['was']) != 1:
            raise SystemExit('w21_witness: stale reading at Psalm %d:%d -- the '
                             'carrier no longer reads %r exactly once'
                             % (ps, v, c['was']))
        text = text.replace(c['was'], c['now'])
        log.append((c['kind'], ps, v, c['key']))
    return text


def apply(psalms, policy=None, log=None):
    """Patch w13_1928.parse()'s structure in place; -> the correction log.
    Every selected correction must fire exactly once. Also attaches the
    NEW_VERIFIES flags (w13_render writes them after their verse); each key
    must occur in its verse as corrected, else the build stops."""
    policy = policy or POLICY
    items = selected(policy)
    out = []
    for n, p in psalms.items():
        for i, (num, text, sub) in enumerate(p['verses']):
            new = apply_text(text, n, num, items, out)
            if new != text:
                p['verses'][i] = (num, new, sub)
    fired = {k for _kind, _p, _v, k in out}
    missing = [c['key'] for c in items if c['key'] not in fired]
    if missing:
        raise SystemExit('w21_witness: corrections that did not fire: %s' % missing)
    for n, v, key, note in NEW_VERIFIES:
        verse = [t for num, t, _s in psalms[n]['verses'] if num == v]
        if len(verse) != 1 or verse[0].count(key) != 1:
            raise SystemExit('w21_witness: flag key %r not exactly once in Psalm %d:%d'
                             % (key, n, v))
        psalms[n].setdefault('verifies', []).append((v, key, note))
    if log is not None:
        log.extend(out)
    return out


def introduced(policy=None):
    policy = policy or POLICY
    """Lower-case word forms the corrections ADD (hyphenated forms whole)."""
    added = set()
    for c in selected(policy):
        f = lambda s: set(re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)*", s.lower()))
        added |= f(c['now']) - f(c['was'])
    return added


def introduced_tokens(policy=None):
    """The LETTER-RUN tokens the corrections add -- the unit w13_fidelity tests
    ([A-Za-z]+, so "cheek-bone" is "cheek" + "bone"). These are attested by
    the scans (w21_gates: attestation), not by the justus carrier, which
    prints the closed forms."""
    policy = policy or POLICY
    tok = lambda s: {w.lower() for w in re.findall(r"[A-Za-z]+", s)}
    added = set()
    for c in selected(policy):
        added |= tok(c['now']) - tok(c['was'])
    return added


def replaced(policy=None):
    policy = policy or POLICY
    """Lower-case forms the corrections REMOVE (must be nowhere in the scans)."""
    gone = set()
    for c in selected(policy):
        if c['kind'] == 'structure':
            continue                      # removes furniture, not a word form
        f = lambda s: set(re.findall(r"[A-Za-z,~]+(?:-[A-Za-z]+)*", s.lower()))
        gone |= {w for w in f(c['was']) - f(c['now'])}
    return gone


if __name__ == '__main__':
    for pol in POLICIES:
        s = selected(pol)
        print('%-16s %2d corrections: %s' % (pol, len(s), sorted({c['kind'] for c in s})))
    print('introduced (recommended):', sorted(introduced()))
    print('replaced   (recommended):', sorted(replaced()))
