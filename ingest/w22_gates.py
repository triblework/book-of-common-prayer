#!/usr/bin/env python3
"""w22_gates.py -- the workstream-C gates (the 1892 pointing collation).

Authoring-only. Runs now with every group switched off (0 corrections applied)
and, unchanged, after the rulings switch groups on and w13_build_1892.py is
wired (Phase 2).

  1. EVIDENCE. Every keyed correction in every group -- switched on or not --
     has a record in w22_evidence.json with a scan page and a read kind of eye.
  2. KEYS. Every key, applied to the BRANCH-BASE cell, occurs there exactly
     once and no two edits in a verse overlap (a dry run of all groups, with
     SEMI_MODE 'both'), and after that dry run every verse still prints exactly
     one ' : ' -- so any ruling's combination of groups can be built.
  3. ATTESTATION. Every word form the WORDS group introduces occurs in the
     scan's own OCR (4400px Psalter record or Wave 17's 2400px record) or in
     the eye read of that place (w22_words_eye.py).
  4. CONTAINMENT. The branch-base cells (editions/1892/psalter at commit BASE,
     by full SHA -- never a live tag; R18) plus exactly the ENABLED corrections
     equal the cells in the worktree, line for line, inline flags set aside;
     nothing else moved. Every enabled key was applied exactly once.
  5. MEDIANT. Every verse of the worktree cells prints exactly one ' : ',
     except the verses in w22_witness.MEDIANT_EXEMPT (empty unless RN-2 rules
     option b).
  6. FLAGS. The worktree cells carry exactly the inline flags of
     w22_witness.VERIFY (Psalm 1:3 'water-side' among them, its key unchanged
     and its note the corrected one), each under its verse, and no other new one.

    python3 ingest/w22_gates.py              # the gates
    python3 ingest/w22_gates.py --selftest   # each gate fails on a case built to break it
"""
from __future__ import annotations
import collections, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w22_witness as X
import w22_words_eye as WE
import w17_cells

BASE = '710f635b7783f1e8188fa334ec75dca3e43a0220'
FILES = ('psalms-1-50', 'psalms-51-100', 'psalms-101-150')
findings = []


def check(label, ok, detail=''):
    print('%-7s %s %s' % ('OK' if ok else 'ANOMALY', label, detail if not ok else ''))
    if not ok:
        findings.append(label)


def base_text(f):
    return subprocess.run(['git', 'show', '%s:editions/1892/psalter/%s.md' % (BASE, f)],
                          cwd=WT, capture_output=True, text=True).stdout


def verse_lines(text):
    """Yield (index, psalm, verse, head, body) for each verse line of a cell."""
    psalm = None
    lines = text.split('\n')
    for i, line in enumerate(lines):
        m = re.match(r'^## Psalm (\d+)', line)
        if m:
            psalm = int(m.group(1))
            continue
        if psalm is None or not line.strip() or line.startswith(('#', '>', '<!--')):
            continue
        mv = re.match(r'^(\d+) ', line)
        head = mv.group(0) if mv else ''
        yield i, psalm, (int(mv.group(1)) if mv else 1), head, line[len(head):]


def strip_flags(text):
    return re.sub(r'\n<!-- VERIFY.*?-->', '', text, flags=re.S)


def rebuild(text, groups, semi_mode, log):
    lines = text.split('\n')
    for i, p, v, head, body in verse_lines(text):
        new, _ = X.apply_text(body, p, v, log, groups, semi_mode)
        lines[i] = head + new
    return '\n'.join(lines)


def main():
    keys = list(X.all_keys())
    print('keyed corrections: %d (%s)' % (len(keys), dict(collections.Counter(e[0] for _, _, e in keys))))
    print('groups enabled: %s; SEMI_MODE %s' % ({k: v for k, v in X.GROUPS.items() if v} or 'none',
                                                X.SEMI_MODE))

    # 1. evidence
    missing, noeye = [], []
    for p, v, (grp, tag, key, new) in keys:
        rec = X.EVIDENCE.get(tag)
        if rec is None:
            missing.append(tag)
        elif not rec.get('page') or not rec.get('eye'):
            noeye.append(tag)
    check('every keyed correction has evidence (%d keys)' % len(keys), not missing, missing[:8])
    check('every evidence record has a scan page and an eye read', not noeye, noeye[:8])

    # 2. keys: dry run of ALL groups over the branch-base cells
    on = {k: True for k in X.GROUPS}
    dry_log, bad_med = [], []
    for f in FILES:
        try:
            txt = rebuild(base_text(f), on, 'both', dry_log)
        except SystemExit as e:
            check('dry run %s: every key exactly once, no overlaps' % f, False, str(e))
            continue
        for i, p, v, head, body in verse_lines(txt):
            if body.count(' : ') != 1:
                bad_med.append('%d:%d' % (p, v))
    check('dry run of all groups applies every key exactly once (%d edits)' % len(dry_log),
          len(dry_log) == len(keys), '%d of %d' % (len(dry_log), len(keys)))
    check('after the dry run every verse prints exactly one mediant', not bad_med, bad_med[:8])

    # 3. attestation of introduced word forms (apostrophe styles compared alike)
    ap = lambda s: s.replace('\u2019', "'")
    scan = []
    for name in ('w22_scan_ocr.json', 'w17_scan_ocr.json'):
        d = json.load(open(os.path.join(HERE, name), encoding='utf-8'))
        for lines in d.values():
            txt = '\n'.join(l[0] if isinstance(l, list) else l for l in lines)
            scan.append(re.sub(r'-\s*\n\s*', '', txt))
    scan_words = {w.lower() for w in re.findall(r"[A-Za-z'-]+", ap('\n'.join(scan)))}
    eye_words = {w.lower() for r in WE.READ.values() if r[4] == 'differs'
                 for w in re.findall(r"[A-Za-z'-]+", ap(r[3]))}
    intro = set()
    for p, v, key, new in X.WORDS:
        intro |= {w.lower() for w in re.findall(r"[A-Za-z'-]+", ap(new))} - \
                 {w.lower() for w in re.findall(r"[A-Za-z'-]+", ap(key))}
    # (CASE and PUNCT change no letter; FURNITURE only deletes)
    un = sorted(w for w in intro if w not in scan_words | eye_words)
    in_ocr = sorted(w for w in intro if w in scan_words)
    check('every introduced word form is in the scan OCR or the eye read (%d forms; %d in OCR)'
          % (len(intro), len(in_ocr)), not un, un)

    # 4. containment, and 5. mediant, over the worktree cells
    log = []
    for f in FILES:
        base = base_text(f)
        if not base:
            check('containment %s: branch-base cell available' % f, False)
            continue
        want = strip_flags(rebuild(strip_flags(base), None, None, log))
        have = strip_flags(open(os.path.join(WT, 'editions/1892/psalter/%s.md' % f),
                                encoding='utf-8').read())
        ok = want == have
        detail = ''
        if not ok:
            a, b = want.split('\n'), have.split('\n')
            diff = [(i, x[:60], y[:60]) for i, (x, y) in enumerate(zip(a, b)) if x != y]
            detail = '%d lines differ, first %s' % (len(diff), diff[:2])
        check('containment %s: base + enabled corrections == worktree cell' % f, ok, detail)
    applied = len(log)
    per = collections.Counter(g for g, *_ in log)
    print('corrections applied (enabled groups): %d %s' % (applied, dict(per)))
    expect = collections.Counter()
    for p, v, (grp, tag, key, new) in keys:
        if X.GROUPS.get(grp) and not (grp == 'POINTING_SEMI' and X.SEMI_MODE == 'keep'):
            expect[grp] += 1
    check('every enabled key applied exactly once (%d)' % sum(expect.values()),
          per == expect, 'applied %s, expected %s' % (dict(per), dict(expect)))
    cells = w17_cells.cells('1892')
    bad = ['%d:%d' % (p, v) for p in cells for v, t in cells[p].items()
           if t.count(' : ') != (0 if (p, v) in X.MEDIANT_EXEMPT else 1)]
    check('every verse prints exactly one mediant (%d verses, %d exempt)'
          % (sum(len(x) for x in cells.values()), len(X.MEDIANT_EXEMPT)), not bad, bad[:8])

    # 6. the inline flags
    found = {}
    for f in FILES:
        lines = open(os.path.join(WT, 'editions/1892/psalter/%s.md' % f), encoding='utf-8').read().split('\n')
        psalm = verse = None
        for line in lines:
            m = re.match(r'^## Psalm (\d+)', line)
            if m:
                psalm, verse = int(m.group(1)), None
                continue
            mv = re.match(r'^(\d+) ', line)
            if psalm and line and not line.startswith(('#', '>', '<!--')):
                verse = int(mv.group(1)) if mv else 1
            mf = re.match(r"^<!-- VERIFY: '(.*?)'; (.*) -->$", line)
            if mf:
                found[(psalm, verse)] = (mf.group(1), mf.group(2))
    want = {k: v for k, v in X.VERIFY.items()}
    check('the cells carry exactly the flags of w22_witness.VERIFY (%d)' % len(want),
          found == want, 'found %s' % sorted(found))
    t = open(os.path.join(WT, 'editions/1892/psalter/psalms-1-50.md'), encoding='utf-8').read()
    check("Psalm 1:3 'water-side' VERIFY present, key unchanged, note corrected",
          "<!-- VERIFY: 'water-side';" in t and 'water-side :' in t and 'waterside' in t
          and 'breaks the word at the same line end' in t)

    print('\nw22 gates: %d anomalies; %d corrections applied' % (len(findings), applied))
    return 1 if findings else 0


def selftest():
    """Sensitivity: each gate must FAIL on a case built to break it."""
    ok = True
    # containment: enable a group without rebuilding the cells
    was = X.GROUPS['CASE_CAPS']
    X.GROUPS['CASE_CAPS'] = not was
    base = base_text('psalms-1-50')
    want = strip_flags(rebuild(strip_flags(base), None, None, []))
    have = strip_flags(open(os.path.join(WT, 'editions/1892/psalter/psalms-1-50.md'),
                            encoding='utf-8').read())
    ok &= want != have
    print('selftest containment detects a group the cells were not built with: %s' % (want != have))
    X.GROUPS['CASE_CAPS'] = was
    # stale key: a key that does not occur must stop the build
    X.WORDS.append((1, 1, 'NO SUCH WORDS', 'x'))
    try:
        rebuild(base, {'WORDS': True}, None, [])
        hit = False
    except SystemExit:
        hit = True
    X.WORDS.pop()
    ok &= hit
    print('selftest a stale key stops the build: %s' % hit)
    # duplicate key: a key occurring twice must stop the build
    X.WORDS.append((1, 1, 'the', 'thee'))
    try:
        rebuild(base, {'WORDS': True}, None, [])
        hit = False
    except SystemExit:
        hit = True
    X.WORDS.pop()
    ok &= hit
    print('selftest a key occurring twice stops the build: %s' % hit)
    # mediant: SEMI_MODE 'semi' with no exemption leaves verses without a mediant
    txt = rebuild(base_text('psalms-101-150'), {'POINTING_SEMI': True}, 'semi', [])
    bad = [1 for i, p, v, h, b in verse_lines(txt) if b.count(' : ') != 1]
    ok &= len(bad) == 2
    print("selftest SEMI_MODE 'semi' without exemptions leaves %d verses unpointed (want 2)" % len(bad))
    print('selftest: %s' % ('all gates sensitive' if ok else 'A GATE IS BLIND'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(selftest() if '--selftest' in sys.argv else main())
