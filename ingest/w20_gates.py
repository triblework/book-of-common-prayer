#!/usr/bin/env python3
"""w20_gates.py -- what must hold after Wave 20 (the 1662 Kalendar, Proper
Lessons, Proper Psalms and the two reading rubrics, from the Annexed Book).

    python3 ingest/w20_gates.py

  1 regenerate  the three table cells are exactly what the eye reads render to
                (w20_kal.py / w20_pl.py): no hand edit sits between the read
                and the published cell.
  2 kalendar    rows, Sunday letters and holy-day blanks clean; the course
                skips are exactly the 26 re-read ones; every A=B-against-eye
                cell was re-read (w20_evidence.json).
  3 schema      R13: no roman chapter numeral and no cell-final stop in a
                lesson cell; no Psalter Day at 1662; letters are A-G.
  4 rubrics     every word of both rubrics is attested by a machine read,
                save the named line both reads dropped.
  5 cover       the Proper Lessons cover test is sensitive (injected readings
                all rejected) -- w20_pl_check.json.
  6 splitter    R17: the old and new sentence_split give the SAME output on
                every file that existed before this wave.
  7 containment outside the five new 1662 cells, editions/ differs from HEAD
                only in 1789's pre-split Proper Psalms line, which has the
                same words.
  8 flags       the five cells carry exactly the three flags named in the
                provenance, each indexed.
"""
import json, os, re, subprocess, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w20_kal, w20_pl
from w20_cite import roman

CELLS = ['tables/calendar', 'tables/proper-lessons', 'tables/proper-psalms',
         'front-matter/order-how-psalter-appointed',
         'front-matter/order-how-rest-of-scripture']
COURSE = 26
bad = []


def check(name, ok, detail=''):
    print('%-4s %s%s' % ('ok' if ok else 'FAIL', name, '' if ok else '  <- %s' % (detail,)))
    if not ok:
        bad.append(name)


def cell(svc):
    return open(os.path.join(WT, 'editions', '1662', svc + '.md'), encoding='utf-8').read()


def main():
    # 1 regenerate
    months = w20_kal.parse(os.path.join(HERE, 'w20_kal_eye.txt'))
    check('calendar == render(eye read)', w20_kal.render(months) == cell('tables/calendar'))
    title, secs, ps = w20_pl.parse(os.path.join(HERE, 'w20_pl_eye.txt'))
    check('proper-lessons == render(eye read)',
          w20_pl.render_lessons(title, secs) == cell('tables/proper-lessons'))
    check('proper-psalms == render(eye read)',
          w20_pl.render_psalms(ps) == cell('tables/proper-psalms'))
    # 2 kalendar
    res = json.load(open(os.path.join(HERE, 'w20_kal_check.json')))
    check('kalendar rows/letters/blanks clean',
          not (res['rows'] or res['letter'] or res['blank']), res['rows'] + res['letter'])
    check('course skips are the %d re-read ones' % COURSE, len(res['course']) == COURSE,
          len(res['course']))
    ev = json.load(open(os.path.join(HERE, 'w20_evidence.json')))
    check('every contra cell re-read', len(res['machine']['contra']) == ev['contra_relooked']['count'],
          len(res['machine']['contra']))
    days = sum(1 for l in cell('tables/calendar').splitlines() if re.match(r'^[A-Z][a-z]+ \d+ \|', l))
    check('366 day rows (Feb prints a 29th)', days == 366, days)
    # 3 schema
    offend = []
    for svc in ('tables/calendar', 'tables/proper-lessons'):
        for l in cell(svc).splitlines():
            for m in re.finditer(r'(?:Morning|Evening) [12]: ([^|]*)', l):
                v = m.group(1).strip()
                if v.endswith('.') or any(roman(t) for t in re.findall(r'[A-Za-z]+', v)):
                    offend.append(v)
    check('R13: lesson cells arabic, no cell-final stop', not offend, offend[:5])
    cal = cell('tables/calendar')
    check('no Psalter Day at 1662', 'Psalter Day' not in cal)
    letters = set(re.findall(r'Sunday Letter: (\S+)', cal))
    check('Sunday letters are A-G (and — for Feb 29)', letters <= set('ABCDEFG') | {'—'}, letters)
    # 4 rubrics
    for page, svc, allowed in ((34, 'front-matter/order-how-psalter-appointed', {'viii'}),
                               (35, 'front-matter/order-how-rest-of-scripture', {'time', 'jm', 'oveable', 'otherwise'})):
        # each exception is a word both machine reads garble or drop, read by eye
        # off the page (w20_evidence.json 'rubric_eye_only')
        ours = [w.lower() for w in re.findall(r'[A-Za-z]+', cell(svc).split('\n', 1)[1])]
        seen = set()
        for tag in 'AB':
            d = json.load(open(os.path.join(HERE, 'w20_rub_%s%d.json' % (tag, page))))
            seen |= {w.lower() for l in d['lines'] for w in re.findall(r'[A-Za-z]+', l['t'].replace('-', ''))}
            seen |= {w.lower() for w in re.findall(r'[A-Za-z]+', ' '.join(
                l['t'] for l in sorted(d['lines'], key=lambda l: l['y'])).replace('- ', ''))}
        un = sorted({w for w in ours if w not in seen} - allowed)
        check('rubric p.%d: every word machine-attested (bar %s)' % (page, sorted(allowed) or 'none'),
              not un, un)
    # 5 cover
    pc = json.load(open(os.path.join(HERE, 'w20_pl_check.json')))
    check('proper-lessons cover test sensitive', pc['caught'] == pc['injected'] and pc['injected'],
          pc['caught'])
    # 6 splitter
    old_src = subprocess.run(['git', '-C', WT, 'show', 'HEAD:tools/sentence_split.py'],
                             capture_output=True, text=True, check=True).stdout
    spec = importlib.util.spec_from_loader('old_ss', loader=None)
    old = importlib.util.module_from_spec(spec); exec(old_src, old.__dict__)
    sys.path.insert(0, os.path.join(WT, 'tools'))
    import sentence_split as new
    tracked = subprocess.run(['git', '-C', WT, 'ls-files', 'editions'], capture_output=True,
                             text=True, check=True).stdout.split()
    diff = []
    for rel in tracked:
        if not rel.endswith('.md'):
            continue
        t = open(os.path.join(WT, rel), encoding='utf-8').read()
        vm = new.is_verse_file(__import__('pathlib').Path(rel))
        if old.process_text(t, verse_mode=vm) != new.process_text(t, verse_mode=vm):
            diff.append(rel)
    check('R17: old and new splitter agree on every pre-existing file', not diff, diff[:5])
    # 7 containment
    changed = subprocess.run(['git', '-C', WT, 'diff', '--name-only', 'HEAD', '--', 'editions'],
                             capture_output=True, text=True, check=True).stdout.split()
    extra = [c for c in changed if c != 'editions/1789/tables/proper-psalms.md']
    check('editions/: nothing else moved', not extra, extra)
    before = subprocess.run(['git', '-C', WT, 'show', 'HEAD:editions/1789/tables/proper-psalms.md'],
                            capture_output=True, text=True, check=True).stdout
    after = open(os.path.join(WT, 'editions/1789/tables/proper-psalms.md'), encoding='utf-8').read()
    check('1789 proper-psalms: same words, and the published split unchanged',
          before.split() == after.split() and new.process_text(after) == old.process_text(before))
    # 8 flags
    n = sum(cell(s).count('<!-- VERIFY') for s in CELLS)
    check('three flags in the five cells', n == 3, n)
    r = subprocess.run([sys.executable, os.path.join(WT, 'tools/verify_index.py'), '--root', WT,
                        '--check'], capture_output=True, text=True)
    check('verify_index --check', r.returncode == 0, r.stdout[-200:])
    print('\nw20 gates: %d anomalies' % len(bad))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
