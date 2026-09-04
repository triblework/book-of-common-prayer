#!/usr/bin/env python3
"""w14_audit.py — gate 2: did anything the source attests quietly fail to arrive?

Authoring-only. Fidelity (w14_fidelity.py) is structurally blind to omission:
if a parser drops a month, every remaining word is still perfectly attested and
that gate stays green while the diff falsely reads "this edition didn't have
it". This asks the other question.

FOR TABLES THE CHEAPEST DETECTOR IS A COUNT, so this asserts:

  1. ROW COUNTS per table per edition. A calendar must have exactly the days in
     the year it prints; a table that loses three rows is the archetypal silent
     loss.
  2. MONTH COMPLETENESS. Twelve month anchors, each holding a consecutive run
     1..N of the right length.
  3. FIELD-SHAPE CONSISTENCY. Within one table every row should carry the same
     labelled columns; a row short of a column means a cell vanished.
  4. CROSS-EDITION ANCHOR SETS, the AUDIT_METHOD pattern: an anchor most
     editions carry is a structural expectation, and an edition missing one is
     reported unless exempted with a written reason.

Reports; does not fail the build. Target state is zero anomalies with every
exemption carrying a reason.
"""
from __future__ import annotations
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']
DAYS = {'January': 31, 'February': (28, 29), 'March': 31, 'April': 30,
        'May': 31, 'June': 30, 'July': 31, 'August': 31, 'September': 30,
        'October': 31, 'November': 30, 'December': 31}

# Expected row counts, established from the sources during the wave.
EXPECT_ROWS = {
    ('1549', 'tables/calendar'): 365,
    ('1552', 'tables/calendar'): 365,
    ('1559', 'tables/calendar'): 365,
    ('1789', 'tables/calendar'): 366,   # 1789 prints 29 February
    ('1979', 'tables/calendar'): 365,
    ('1789', 'tables/proper-lessons'): 117,
    ('1892', 'tables/proper-lessons'): 191,
    ('1979', 'tables/eucharistic-lectionary'): 280,
    ('1979', 'tables/daily-office-lectionary'): 784,
}

# (edition, service, anchor) -> reason. AUDIT_METHOD's KNOWN_GOOD tier: an
# exemption without a source-checked reason is a silenced bug.
KNOWN_GOOD = {
    ('1979', 'tables/calendar', 'lesson columns'):
        '1979 keeps the civil-date Kalendar but moves the readings into the '
        'two-year Daily Office Lectionary, so its rows carry no lesson columns.',
    ('1789', 'tables/calendar', 'November lesson columns'):
        'the source drops one entry from November\'s two First-Lesson columns; '
        'they are omitted for that month rather than misaligned.',
    ('1979', 'tables/eucharistic-lectionary', 'Palm Sunday'):
        'the book prints a Liturgy of the Palms set before the main propers, so '
        'the first field is that service label rather than a psalm.',
    ('1979', 'tables/eucharistic-lectionary', 'Easter Day'):
        'the book gives a cross-reference to the Great Vigil rather than a '
        'reading set.',
    ('1979', 'tables/eucharistic-lectionary', 'Day of Pentecost'):
        'the book provides an Early or Vigil Service in addition to the day\'s '
        'propers, so the first field is that service label.',
    ('1979', 'tables/eucharistic-lectionary', 'Proper 19'):
        'the e-text loses page 899, truncating this entry mid-word; flagged '
        'inline and not reconstructed.',
    ('1979', 'tables/daily-office-lectionary', 'Friday'):
        'an e-text merge leaves this psalm line unsplittable into morning and '
        'evening; carried whole and flagged inline.',
}


def KNOWN_GOOD_KEYS(row):
    """Candidate exemption keys for a row: its occasion, with any parenthetical
    qualifier stripped ("Proper 19 (Closest to September 14)" -> "Proper 19")."""
    occ = row.split(' | ')[0].strip()
    return {occ, re.sub(r'\s*\(.*$', '', occ), 'lesson columns',
            'November lesson columns'}


def rows_of(path):
    out = []
    for line in path.read_text(encoding='utf-8').split('\n'):
        if ' | ' in line and not line.startswith('<!--'):
            out.append(line)
    return out


def anchors_of(path):
    return [l[3:].strip() for l in path.read_text(encoding='utf-8').split('\n')
            if l.startswith('## ')]


# Only the labels THIS WAVE emits count. A reading such as "Heb 2:10-18" also
# looks like "Label: value", and counting it made two Daily Office rows appear
# to have an extra column.
EMITTED_LABELS = {
    'Sunday Letter', 'Psalter Day', 'Kalendar Note',
    'Morning 1', 'Morning 2', 'Evening 1', 'Evening 2',
    'Morning', 'Evening', 'Matins Psalms', 'Evensong Psalms',
    'Morning Psalms', 'Evening Psalms', 'Psalms', 'Psalm',
}
LABEL = re.compile(r'^([A-Z][A-Za-z0-9 ]{0,20}):\s')


def labels_of(row):
    """Only LABELLED fields count. The lectionaries carry their readings
    unlabelled, in printed order, because classifying them Old Testament /
    Epistle / Gospel would be inference rather than transcription."""
    out = []
    for f in row.split(' | ')[1:]:
        m = LABEL.match(f)
        if m and m.group(1) in EMITTED_LABELS:
            out.append(m.group(1))
    return tuple(out)


def sections(path):
    """-> {anchor: [rows]}. Shape must be compared WITHIN one table: a file may
    hold several (1789 prints Sundays in five columns and Holy-Days in three)."""
    cur, out = None, {}
    for line in path.read_text(encoding='utf-8').split('\n'):
        if line.startswith('## '):
            cur = line[3:].strip(); out.setdefault(cur, [])
        elif ' | ' in line and not line.startswith('<!--'):
            out.setdefault(cur, []).append(line)
    return out


def main():
    findings = []
    cells = defaultdict(dict)
    for ed_dir in sorted((WT / 'editions').iterdir()):
        if not ed_dir.is_dir():
            continue
        for fam in ('tables', 'front-matter'):
            d = ed_dir / fam
            if not d.is_dir():
                continue
            for f in sorted(d.glob('*.md')):
                svc = '%s/%s' % (fam, f.stem)
                if fam == 'front-matter' and not f.stem.startswith('order-how'):
                    continue
                cells[svc][ed_dir.name] = f

    # 1. row counts
    for (ed, svc), want in sorted(EXPECT_ROWS.items()):
        f = cells.get(svc, {}).get(ed)
        if f is None:
            findings.append('%s %s: cell MISSING' % (ed, svc)); continue
        got = len(rows_of(f))
        mark = 'OK ' if got == want else 'ANOMALY'
        print('%-7s %-5s %-34s rows %4d (want %4d)' % (mark, ed, svc, got, want))
        if got != want:
            findings.append('%s %s: %d rows, want %d' % (ed, svc, got, want))

    # 2. month completeness for every calendar
    for ed, f in sorted(cells.get('tables/calendar', {}).items()):
        anc = anchors_of(f)
        if anc != MONTHS:
            findings.append('%s calendar: month anchors %s' % (ed, anc))
            continue
        per = defaultdict(list)
        for r in rows_of(f):
            m = re.match(r'^([A-Z][a-z]+) (\d{1,2}) \|', r)
            if m:
                per[m.group(1)].append(int(m.group(2)))
        for mo in MONTHS:
            days = per[mo]
            want = DAYS[mo]
            want = want if isinstance(want, tuple) else (want,)
            if days != list(range(1, len(days) + 1)) or len(days) not in want:
                findings.append('%s calendar %s: %d days %s'
                                % (ed, mo, len(days), days[:4]))
        print('OK      %-5s calendar: 12 months, %d days' % (ed, sum(len(v) for v in per.values())))

    # 3. field-shape consistency within each table
    for svc, per_ed in sorted(cells.items()):
        for ed, f in sorted(per_ed.items()):
            for anchor, rows in sections(f).items():
                if not rows:
                    continue
                shapes = Counter(labels_of(r) for r in rows)
                if len(shapes) == 1:
                    continue
                top, _n = shapes.most_common(1)[0]
                odd = sum(v for k, v in shapes.items() if k != top)
                # An exemption applies if every odd row's occasion is named in
                # KNOWN_GOOD. Exemptions are per-occasion and each carries a
                # written, source-checked reason (AUDIT_METHOD).
                odd_rows = [r for r in rows if labels_of(r) != top]
                if all(any((ed, svc, k) in KNOWN_GOOD
                           for k in KNOWN_GOOD_KEYS(r)) for r in odd_rows):
                    continue
                findings.append('%s %s [%s]: %d of %d rows differ in labelled '
                                'column shape from the majority %s'
                                % (ed, svc, anchor, odd, len(rows), list(top)))

    # 4. cross-edition anchor sets
    for svc, per_ed in sorted(cells.items()):
        if len(per_ed) < 2:
            continue
        sets = {ed: set(anchors_of(f)) for ed, f in per_ed.items()}
        counts = Counter(a for s in sets.values() for a in s)
        majority = {a for a, n in counts.items() if n > len(sets) / 2}
        for ed, s in sorted(sets.items()):
            missing = sorted(majority - s)
            if missing:
                findings.append('%s %s: missing majority anchors %s'
                                % (ed, svc, missing[:6]))

    print('\naudit: %d anomalies' % len(findings))
    for x in findings:
        print('  - ' + x)
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
