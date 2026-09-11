#!/usr/bin/env python3
"""Wave 13 — SOURCES.md rows and scope, NOTICE.md, README.md.

The SOURCES scope paragraph is published prose no gate validates; after this
wave it must stop listing the Psalter as outstanding, and must say in plain
words that the Psalter's first appearance at v1662 is an artefact.
"""
from __future__ import annotations
import re
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
RR = WT / 'repo-root'
VERIFY_RE = re.compile(r"<!--\s*VERIFY:\s*'([^']*)'(.*?)-->", re.S)
LABEL = {'1662': '1662', '1789': '1789 (American)', '1892': '1892 (American)',
         '1928': '1928 (American)', '1979': '1979 (American)'}


def rows():
    out = []
    for ed in ('1662', '1789', '1892', '1928', '1979'):
        for rel in ('psalter/psalms-1-50.md', 'psalter/psalms-51-100.md',
                    'psalter/psalms-101-150.md', 'psalter/selections.md',
                    'tables/proper-psalms.md'):
            f = WT / 'editions' / ed / rel
            if not f.exists():
                continue
            cur = None
            for line in f.read_text(encoding='utf-8').split('\n'):
                m = re.match(r'^## (.+)$', line)
                if m:
                    cur = m.group(1)
                for v in VERIFY_RE.finditer(line):
                    note = re.sub(r'\s+', ' ', v.group(2)).strip().lstrip(';').strip()
                    where = cur or ('Proper Psalms' if 'proper' in rel else 'Psalter')
                    out.append('| %s %s | `%s` | %s |' % (LABEL[ed], where, v.group(1), note))
    return out


OLD_SCOPE = '''**Not yet transcribed**, tracked as a later wave: the **Psalter**. Several tables
are also carried for some editions but not others;'''
NEW_SCOPE = '''The **Psalter** is transcribed under `psalter/`, one verse per line in three
files of fifty psalms, for 1662, 1892, 1928 and 1979, each from its own source.
**It first appears in the history at `v1662`, and that is an artefact of
sourcing, not of history**: the Coverdale psalter was in the book from 1549, but
no allow-listed source gives the 1549-1604 text, so nothing earlier can hold the
file. The 1789 book's own Psalter is likewise unsourced, and 1789 inherits
1662's. Neither is a claim about those books.

Several tables are also carried for some editions but not others;'''

GAP_ROWS = '''| 1549–1604 | the Psalter | No allow-listed source; the Psalter enters the history at 1662 (see above). |
| 1789 | the Psalter | justus's 1789 index points its Psalter link at the shared 1928 page, and the 1790 folio's text layer is unusable OCR. Deriving it backwards from 1892 or 1928 was rejected: an apparatus is only as complete as its editor, so silence is not evidence of no change. |
| 1892, 1928 | Selections of Psalms | justus links them to the 1789 page (a page that only looks shared); each inherits the 1789 list. |
| 1928 | Table of Proper Psalms | PDF-only; inherits 1892's. |
'''

NOTICE = '''- **2026-09-11** — Wave 13: the **Psalter**, under a new `psalter/` family:
  one verse per line, printed verse numbering kept (including the Coverdale
  books' unnumbered verse 1), in three files of fifty, for **1662, 1892, 1928 and
  1979 — each from its own source, with no edition derived from another**. The
  1928 page's sidebar of earlier readings is deliberately not applied, and 1892
  is taken from its own PDF. **The Psalter first appears at `v1662`, and that is
  an artefact**: the Coverdale psalter was in the book from 1549, but no
  allow-listed source reaches earlier, so the history cannot hold it there.
  1789's own Psalter is likewise unsourced and 1789 inherits 1662's. **The
  mediant is normalized to ` : `** in every edition (pointing is typography):
  1928 and 1979 print an asterisk, 1892 a musical colon, 1662 a colon, and 1789
  printed no breath-mark at all. Flagship diffs: `git diff v1892 v1928 --
  texts/normalized/psalter/psalms-1-50.md` shows 1928 remove the Romans-3
  interpolation from Psalm 14 and re-translate the opening of Psalm 45;
  `git diff v1928 v1979` replaces Coverdale with the 1979 translation. Also added:
  the 1789 **Selections of Psalms** and the **Tables of Proper Psalms on Certain
  Days** (1789, 1892), the latter closing a gap Wave 14 recorded. The 1892 text
  was tested against an independent witness, justus's dated table of pre-1928
  U.S. psalter changes, and agrees with 51 of its 55 applicable entries,
  including 32 of the 35 it dates to 1892 itself; the four disagreements are
  flagged inline.
- **2026-09-11** — `tools/sentence_split.py` gains a **verse mode** for files under
  `psalter/`. The Psalter's unit is the verse, and sentence splitting would have
  broken 25 Coverdale verses and 180 of 1979's across two lines, one of them
  without its number. Verse files still get whitespace and blank-line
  normalization. Every file outside `psalter/` behaves exactly as before.
'''


def main():
    p = RR / 'SOURCES.md'
    s = p.read_text(encoding='utf-8')
    r = rows()
    anchor = '## Uncertain passages (`<!-- VERIFY -->`)'
    i = s.index(anchor)
    j = s.index('\n\n', s.index('|----------------|', i))
    s = s[:j] + '\n' + '\n'.join(r) + s[j:]
    if OLD_SCOPE not in s:
        raise SystemExit('SOURCES scope paragraph not found -- re-read it by hand')
    s = s.replace(OLD_SCOPE, NEW_SCOPE)
    s = s.replace("- **`tables/`** —", "- **`psalter/`** — the Psalter, one verse per line (1662, 1892, 1928, 1979),\n  with the 1789 Selections of Psalms\n- **`tables/`** —")
    k = s.index('### Recorded gaps in the tables')
    k2 = s.index('|---|---|---|', k)
    k3 = s.index('\n', k2) + 1
    s = s[:k3] + GAP_ROWS + s[k3:]
    s = s.replace('nine service families', 'ten service families')
    p.write_text(s, encoding='utf-8')
    print('SOURCES.md: +%d uncertain rows, scope rewritten, gap rows added' % len(r))

    p = RR / 'NOTICE.md'
    p.write_text(p.read_text(encoding='utf-8').rstrip('\n') + '\n' + NOTICE, encoding='utf-8')
    print('NOTICE.md: rebuild-log entries appended')

    p = RR / 'README.md'
    s = p.read_text(encoding='utf-8')
    s = s.replace('**Coming soon**: the Psalter.',
                  'The **Psalter** is transcribed under `psalter/`, one verse per line, for 1662,\n1892, 1928 and 1979, each from its own source.')
    s = s.replace('# The Kalendar loses its lesson columns between 1789 and 1979',
                  '# The 1928 Psalter removes the Romans-3 interpolation from Psalm 14 (verses 5-7\n'
                  '# of the Coverdale text) and re-translates the opening of Psalm 45:\n'
                  'git diff v1892 v1928 -- texts/normalized/psalter/psalms-1-50.md\n\n'
                  '# The Kalendar loses its lesson columns between 1789 and 1979')
    p.write_text(s, encoding='utf-8')
    print('README.md: status and flagship diff')


if __name__ == '__main__':
    main()
