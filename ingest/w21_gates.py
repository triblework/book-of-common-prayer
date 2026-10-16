#!/usr/bin/env python3
"""w21_gates.py -- the Workstream B gates (the 1928 Psalter against the 1929
printing and the 1952 Standard Book facsimile).

Runs in either state of the cells and says which:
  UNAPPLIED  editions/1928/psalter == the cells at the branch base (full SHA
             below): 0 corrections applied (Phase 1b; w13_build not wired);
  APPLIED    the cells == branch-base cells + exactly the selected corrections
             - the closed flags + the opened flags (w21_witness.NEW_VERIFIES)
             (Phase 2, after w13_build applies w21_witness).
Anything else is an anomaly. Every other gate is checked on the SIMULATED
result (base + corrections) and, when applied, on the cells themselves.

  1. EVIDENCE      every selected correction has an eye reading in
                   w21_evidence.json for each scan its attestation cites, and
                   the eye reading agrees with the attestation (mid / brk).
  2. ATTESTATION   every word form a correction introduces occurs in an
                   attesting scan's page OCR or in an eye reading; every form it
                   replaces occurs NOWHERE in either scan's page OCR (clear
                   tokens, pp. 345-525). Sensitivity: forms the scans print
                   nowhere must fail the same test.
  3. CONTAINMENT   base + corrections == cells (see above), nothing else moves.
  4. POINTING      every one of the 2,508 verses carries exactly one ' : ', and
                   no '~' remains.
  5. FLAGS         the three Wave-13 'no mediant' flags are closed; each opened
                   flag stands on the line after its verse and its quoted key
                   occurs in that verse line.
  6. DISAGREEMENTS under the policy, no 1929-only reading is imported.

    python3 ingest/w21_gates.py [--policy recommended|bcp1929-only|both-must-agree]
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w21_witness as W
import w21_psalter as P
from w13_render import mediant, _verify

BASE = '710f635b7783f1e8188fa334ec75dca3e43a0220'     # branch base, by full SHA
FILES = ('psalms-1-50', 'psalms-51-100', 'psalms-101-150')
findings = []


def check(label, ok, detail=''):
    print('%-8s %s %s' % ('OK' if ok else 'ANOMALY', label, detail))
    if not ok:
        findings.append(label)


def base_text(f):
    r = subprocess.run(['git', 'show', '%s:editions/1928/psalter/%s.md' % (BASE, f)],
                       cwd=WT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def verse_lines(text):
    """-> [(line index, psalm, verse, head, body)] for the verse lines."""
    out, ps = [], None
    lines = text.split('\n')
    for i, line in enumerate(lines):
        m = re.match(r'^## Psalm (\d+)', line)
        if m:
            ps, first = int(m.group(1)), True
            continue
        if ps is None or not line.strip() or line.startswith(('>', '<!--', '#')):
            continue
        mv = re.match(r'^(\d+) (.*)$', line)
        if mv:
            out.append((i, ps, int(mv.group(1)), mv.group(1) + ' ', mv.group(2)))
        else:
            out.append((i, ps, 1, '', line))
    return lines, out


def simulate(text, items):
    """Branch-base cell -> expected cell: corrections applied in CELL form to
    their verse line (exactly once), the closed flags' VERIFY lines dropped,
    the opened flags inserted on the line after their verse."""
    lines, vl = verse_lines(text)
    applied, drop, add = [], set(), {}
    newv = {(n, v): (key, note) for n, v, key, note in W.NEW_VERIFIES}
    for i, ps, v, head, body in vl:
        if (ps, v) in newv:
            add[i] = _verify(*newv[(ps, v)])
        for c in items:
            if (c['ps'], c['v']) != (ps, v):
                continue
            was, now = mediant(c['was'], '*'), mediant(c['now'], '*')
            if body.count(was) != 1:
                raise SystemExit('w21_gates: %s: %r not exactly once in the base '
                                 'cell' % (c['key'], was))
            body = body.replace(was, now)
            applied.append(c['key'])
        lines[i] = head + body
        if (ps, v) in W.CLOSES and i + 1 < len(lines) and \
                lines[i + 1].startswith('<!-- VERIFY') and "'no mediant'" in lines[i + 1]:
            drop.add(i + 1)
    out = []
    for k, l in enumerate(lines):
        if k in drop:
            continue
        out.append(l)
        if k in add:
            out.append(add[k])
    return '\n'.join(out), applied, len(drop)


def ocr_forms():
    clear, lb = {}, {}
    for w in ('1929', '1952'):
        toks, _h = P.witness_tokens(w)
        clear[w] = {t['f'] for t in toks if 'f' in t and not t.get('lb')}
        lb[w] = {x for t in toks if t.get('lb') for x in (t['f'], t['lb_alt'])}
    return clear, lb


def main(policy='recommended'):
    items = W.selected(policy)
    ev = json.load(open(os.path.join(HERE, 'w21_evidence.json')))
    print('policy %s: %d corrections selected (%s)' % (
        policy, len(items), ', '.join(sorted({c['kind'] for c in items}))))

    # 3. containment (first: it says which state the cells are in)
    state, sim_all, n_applied = None, {}, 0
    for f in FILES:
        base = base_text(f)
        if base is None:
            check('containment %s: branch-base cell readable at %s' % (f, BASE[:12]), False)
            continue
        cur = open(os.path.join(WT, 'editions/1928/psalter/%s.md' % f), encoding='utf-8').read()
        sim, applied, dropped = simulate(base, items)
        sim_all[f] = sim
        if cur == base:
            st = 'unapplied'
        elif cur == sim:
            st, n_applied = 'applied', n_applied + len(applied)
        else:
            st = 'MOVED'
        state = st if state in (None, st) else 'mixed'
        check('containment %s: cells %s (simulated: %d corrections, %d flags dropped)'
              % (f, st, len(applied), dropped), st in ('unapplied', 'applied'))
    check('containment: one state for all three files (%s); corrections applied to '
          'the cells: %d' % (state, n_applied), state in ('unapplied', 'applied'))

    # 1. evidence
    for c in items:
        e = ev.get(c['key'])
        if not e:
            check('evidence %s' % c['key'], False, 'no record')
            continue
        bad = []
        for w, a in c['attest'].items():
            s = e['scans'].get(w)
            if a in ('mid', 'read') and not s:
                bad.append('%s: no eye reading' % w)
            elif s and a == 'mid' and ' / ' in s['eye']:
                bad.append('%s: eye shows a break' % w)
            elif s and a == 'brk' and ' / ' not in s['eye']:
                bad.append('%s: eye shows no break' % w)
        check('evidence %-24s %s' % (c['key'], {w: e['scans'][w]['book'] for w in e['scans']}),
              not bad, bad)

    # 2. attestation, with its sensitivity
    clear, lb = ocr_forms()
    eye_words = {x for e in ev.values() for s in e['scans'].values()
                 for x in re.findall(r"[a-z]+(?:-[a-z]+)*", s['eye'].lower())}
    for form in sorted(W.introduced(policy)):
        hit = [w for w in clear if form in clear[w]]
        check('attested: %-16s in the page OCR of %s' % (form, hit or '-'),
              bool(hit) or form in eye_words)
    for form in sorted(W.replaced(policy)):
        f = P.form(form)
        hit = [w for w in clear if f in clear[w]]
        check('gone:     %-16s printed nowhere in either scan' % form, not hit, hit)
    for fake in ('cheek-bones', 'by-words', 'hoar-frosty', 'seven-folds', 'us-wards'):
        hit = [w for w in clear if fake in clear[w]]
        check('sensitivity: %-14s (printed nowhere) fails the test' % fake, not hit, hit)
    check('discrimination: the 1929 misprint "thanskgiving" is in 1929 only',
          'thanskgiving' in clear['1929'] and 'thanskgiving' not in clear['1952'])

    # 4. pointing and 5. flags, on the simulated cells (and on the cells if applied)
    def pointing(texts):
        n = bad = tilde = 0
        for t in texts.values():
            _l, vl = verse_lines(t)
            for _i, ps, v, _h, body in vl:
                n += 1
                bad += body.count(' : ') != 1
                tilde += '~' in body
        return n, bad, tilde
    n, bad, tilde = pointing(sim_all)
    check('pointing (simulated): %d verses, %d without exactly one mediant, %d with ~'
          % (n, bad, tilde), n == 2508 and bad == 0 and tilde == 0)
    cur_texts = {f: open(os.path.join(WT, 'editions/1928/psalter/%s.md' % f), encoding='utf-8').read()
                 for f in FILES}
    n2, bad2, tilde2 = pointing(cur_texts)
    print('INFO     pointing (cells as they stand): %d verses, %d without exactly one '
          'mediant, %d with ~' % (n2, bad2, tilde2))
    if state == 'applied':
        check('pointing (cells)', bad2 == 0 and tilde2 == 0)
    open_sim = sum(t.count("'no mediant'") for t in sim_all.values())
    open_cur = sum(t.count("'no mediant'") for t in cur_texts.values())
    check('flags: the three no-mediant flags closed in the simulated cells (%d left; %d '
          'open in the cells as they stand)' % (open_sim, open_cur), open_sim == 0)
    if state == 'applied':
        check('flags: no no-mediant flag left in the cells', open_cur == 0)
        for n, v, key, _note in W.NEW_VERIFIES:
            found = False
            for f, t in cur_texts.items():
                lines, vl = verse_lines(t)
                for i, ps, vv, head, body in vl:
                    if (ps, vv) == (n, v):
                        nxt = lines[i + 1] if i + 1 < len(lines) else ''
                        found = (nxt.startswith("<!-- VERIFY: '%s';" % key)
                                 and body.count(key) == 1)
            check('flag opened at %d:%-3d %-20r after its verse, key in the verse line'
                  % (n, v, key), found)

    # 6. disagreements
    P_ = W.POLICIES[policy]
    if not P_.get('primary_wins_disagreements'):
        for d in W.DISAGREE:
            keep = mediant(d['was'], '*')
            ok = any(keep in t for t in sim_all.values())
            check('disagreement %-22s the cell keeps the Standard Book reading' % d['key'], ok)

    print('\nw21 gates: %d anomalies (cells %s; %d corrections applied)'
          % (len(findings), state, n_applied))
    return 1 if findings else 0


if __name__ == '__main__':
    pol = 'recommended'
    if '--policy' in sys.argv:
        pol = sys.argv[sys.argv.index('--policy') + 1]
    sys.exit(main(pol))
