#!/usr/bin/env python3
"""Wave 12 — build the four deferred sections. source -> script -> file.

Four office-like services, one file each, `##` anchors (WAVE12_SCOPING.md §7):
  occasional-offices/prayers-at-sea.md        1662, 1789, 1892
  occasional-offices/penitential-office.md    1892, 1928
  occasional-offices/family-prayer.md         1789, 1892, 1928
  occasional-offices/prayer-and-thanksgiving.md  1789, 1892

PSALMS (locked ruling): psalm bodies in the SEA forms are not transcribed here —
the Psalter is its own wave. A psalm run collapses to its printed label, which
carries the citation ("Confitemini Domino. Psalm 107"), plus a pointer rubric.
Where a run has no single psalm label (the composite hymns), NO citation is
invented: the heading stays and the omission is flagged with a VERIFY.

Psalm 51 in the PENITENTIAL OFFICE is carried IN FULL — it is the structural
core of that service, and the published `commination.md` already sets that
precedent for the same psalm on the same day (scoping doc §2a).
"""
from __future__ import annotations
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w12_spine as S

WT = HERE.parent
FAM = 'occasional-offices'

# service -> {edition: (spine name, spine edition)}
PLAN = {
 'prayers-at-sea': {'1662': ('sea-1662', None), '1789': ('sea-1789', '1789'),
                    '1892': ('sea-1789', '1892')},
 'penitential-office': {'1892': ('penitential-1892', None), '1928': ('penitential-1928', None)},
 'family-prayer': {'1789': ('family-1789', None), '1928': ('family-1928', None)},
 'prayer-and-thanksgiving': {'1789': ('thanks-1789', '1789'), '1892': ('thanks-1789', '1892')},
}

TITLES = {
 'prayers-at-sea': 'Forms of Prayer to be used at Sea',
 'penitential-office': 'A Penitential Office for Ash-Wednesday',
 'family-prayer': 'Forms of Prayer to be used in Families',
 'prayer-and-thanksgiving': 'A Form of Prayer and Thanksgiving to Almighty God',
}

PSALM_LABEL = re.compile(r'\bPsalm\s+([0-9ivxlc]+)', re.I)
# a psalm VERSE, structurally: these sources point verses with " : "
VERSE = re.compile(r'\s:\s')


def join_split_heading(blocks):
    """Rejoin a heading the source breaks across two centred blocks.

    'FORMS OF' + 'PRAYER TO BE USED IN FAMILIES.' arrive as two title blocks;
    left apart they become two anchors, one of them meaningless.
    """
    out = []
    for k, t in blocks:
        if (out and out[-1][0] == 'title' and k == 'title'
                and out[-1][1].isupper() and len(out[-1][1]) < 22
                and not out[-1][1].rstrip().endswith('.')):
            out[-1] = ('title', out[-1][1].rstrip() + ' ' + t.lstrip())
        else:
            out.append((k, t))
    return out


def render(service, edition, blocks, collapse_psalms):
    lines = [f"# {TITLES[service]}", '']
    psalm_run, last_label = [], None
    verify = []

    def flush_psalm():
        nonlocal psalm_run, last_label
        if not psalm_run:
            return
        n = len(psalm_run)
        if last_label and PSALM_LABEL.search(last_label):
            lines.append(f"> [{n} verses of {last_label.strip()} follow here; "
                         f"the psalm text is carried in the Psalter, not repeated here.]")
        else:
            lines.append(f"> [{n} psalm verses follow here.]")
            verify.append(n)
        lines.append('')
        psalm_run, last_label = [], None

    for k, t in blocks:
        # Collapse by KIND, set structurally in w12_spine (CoE: class=vlpsalm;
        # justus: a body following a psalm-naming heading). The earlier content
        # test (' : ' plus a length bound) caught 85 of 1662's 97 psalm blocks
        # and none of 1789's, so it both leaked psalm text and was inconsistent
        # between sources.
        if collapse_psalms and k == 'psalm':
            psalm_run.append(t)
            continue
        if k == 'psalm':          # not a sea form: keep the psalm in full
            k = 'body'
        flush_psalm()
        if k in ('section', 'title'):
            if t.strip().lower().rstrip('.') == TITLES[service].lower().rstrip('.'):
                continue
            lines += [f"## {t.strip()}", '']
            if PSALM_LABEL.search(t):
                last_label = t
        elif k == 'rubric':
            lines += [f"> {t.lstrip('¶').strip()}", '']
        else:
            if PSALM_LABEL.search(t) and len(t) < 60:
                last_label = t
            lines += [t.strip(), '']
    flush_psalm()
    if verify:
        lines.insert(2, "<!-- VERIFY: 'psalm-cento' — a run of psalm verses here carries no "
                        "single printed psalm label (the composite hymns), so no citation is "
                        "supplied; the text is deferred to the Psalter wave -->")
        lines.insert(3, '')
    while lines and lines[-1] == '':
        lines.pop()
    return '\n'.join(lines) + '\n'


def build(write=True):
    made = []
    for service, plan in PLAN.items():
        collapse = (service == 'prayers-at-sea')      # ruling: sea psalms -> pointer
        for edition, (name, ed) in plan.items():
            blocks, _ = S.extract(name, ed)
            blocks = join_split_heading(blocks)
            if not blocks:
                raise SystemExit(f"ABORT {service}/{edition}: no blocks")
            body = render(service, edition, blocks, collapse)
            if body.count('\n') < 5:
                raise SystemExit(f"ABORT {service}/{edition}: suspiciously short output")
            if write:
                d = WT / 'editions' / edition / FAM
                d.mkdir(parents=True, exist_ok=True)
                (d / f'{service}.md').write_text(body, encoding='utf-8')
            anchors = sum(1 for l in body.split('\n') if l.startswith('## '))
            made.append((service, edition, len(body), anchors))
    for s, e, n, a in made:
        print(f"  {e}  {s:26s} {n:6d} bytes  {a:3d} anchors")
    return made


if __name__ == '__main__':
    build(write='--dry' not in sys.argv)
