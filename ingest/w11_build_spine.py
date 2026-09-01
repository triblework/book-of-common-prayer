#!/usr/bin/env python3
"""Wave 11 — build cells for 1552 / 1559 / 1604 / 1637 from the Wave-9 spines.

source -> script -> file; prayer text is never emitted as model output.

Units are declared by EXPLICIT spine line number, not matched by content: these
spines interleave the book's text with the justus apparatus, and a content
matcher would have to tell a genuine line from the apparatus quoting it. The
line numbers were read off the spines directly (see WAVE11_SCOPING.md §1).

1604 is DERIVED, licensed by the 1559 page's own apparatus notes:
  * 'Replaced by a prayer for the King in 1604'      -> sovereign prayer changes
  * '[prayer added 1604]' (royal-family column)      -> royal-family prayer added
  * 'The following Thanksgivings were added in 1604' -> the thanksgivings added
Nothing is derived that an apparatus note does not license.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WT = HERE.parent
SPINES = HERE / 'spines-w9'
FAMILY = 'prayers-and-thanksgivings'

# (slug, title | None, title_line | None, body_first, body_last)
UNITS = {
 '1552': [
  ('for-rain',                       227, 229, 229),
  ('for-fair-weather',               231, 233, 233),
  ('in-time-of-dearth-and-famine',   235, 237, 237),
  ('in-time-of-dearth-and-famine-2', 239, 241, 241),
  ('in-time-of-war-and-tumults',     243, 245, 245),
  ('in-time-of-plague',              247, 249, 249),
 ],
 '1559': [
  ('for-the-sovereign',              229, 231, 231),
  ('for-the-clergy-and-people',     None, 239, 239),
  ('for-rain',                       249, 251, 251),
  ('for-fair-weather',               253, 255, 255),
  ('in-time-of-dearth-and-famine',   257, 259, 259),
  ('in-time-of-war-and-tumults',     261, 263, 263),
  ('in-time-of-plague',              265, 267, 267),
 ],
 '1637': [
  ('for-the-sovereign',              227, 229, 229),
  ('for-the-royal-family',           231, 233, 233),
  ('for-the-clergy-and-people',      235, 237, 237),
  ('in-the-ember-weeks',             239, 241, 241),
  ('for-rain',                       251, 253, 253),
  ('for-fair-weather',               255, 257, 257),
  ('in-time-of-dearth-and-famine',   259, 261, 261),
  ('in-time-of-war-and-tumults',     263, 265, 265),
  ('in-time-of-plague',              267, 269, 269),
  ('prayer-after-the-former',       None, 271, 271),
  ('thanksgiving-for-rain',          273, 275, 275),
  ('thanksgiving-for-fair-weather',  277, 279, 279),
  ('thanksgiving-for-plenty',        281, 283, 283),
  ('thanksgiving-for-peace-and-deliverance',  285, 287, 287),
  ('thanksgiving-for-deliverance-from-plague', 289, 291, 291),
  ('thanksgiving-for-deliverance-from-plague-2', 293, 295, 295),
 ],
}

# 1604 = 1559, plus these blocks from the 1559 page that its apparatus dates to
# 1604. Same spine file; the apparatus is what licenses moving them to 1604.
UNITS_1604_ADDED = [
  ('for-the-royal-family',           235, 237, 237),
  ('prayer-after-the-former',       None, 269, 287),
  ('thanksgiving-for-rain',          295, 297, 297),
  ('thanksgiving-for-fair-weather',  299, 301, 301),
  ('thanksgiving-for-plenty',        303, 305, 305),
  ('thanksgiving-for-peace-and-deliverance',  307, 309, 309),
  ('thanksgiving-for-deliverance-from-plague', 311, 313, 313),
  ('thanksgiving-for-deliverance-from-plague-2', 315, 317, 317),
]

# Conventional names for prayers the book prints untitled (WAVE11_GUIDE.md).
# Cells that carry an extra recorded-gap VERIFY (see the module docstring and
# WAVE11_SCOPING.md). The 1559 page's apparatus attests only that the sovereign
# prayer was "Replaced by a prayer for the King in 1604", and its variations
# table gives only the royal STYLE ("Sovereign Lord King James"). It does not
# attest the pronoun forms or period spellings the 1604 book actually printed,
# and inventing eight her->his / she->he changes would manufacture a reading no
# allow-listed source supports. So 1604 carries the attested 1559 wording and
# RECORDS THE GAP, rather than reconstructing a text no source attests.
GAP_VERIFY = {
  ('1604', 'for-the-sovereign'):
    ("'Quene Elizabeth' — the 1559 page's apparatus says this prayer was "
     "replaced by a prayer for the King in 1604 and gives the style "
     "'Sovereign Lord King James', but attests neither the pronouns nor the "
     "spellings the 1604 book printed. The 1559 wording is retained and the "
     "gap recorded; resolve from a 1604 facsimile."),
}

UNTITLED = {
  'for-the-clergy-and-people': 'A Prayer for the Clergy and People',
  'prayer-after-the-former':   'A Prayer that may be said after any of the former',
}

APPARATUS = re.compile(r'^\s*(\*|This prayer added|The following Thanksgivings|\[)')


def lines(year: str):
    return (SPINES / f'{year}_litany.md').read_text(encoding='utf-8').split('\n')


def render(slug, title_line, body_lines, untitled, gap=None):
    if untitled:
        head = f"# [{UNTITLED[slug]}]"
    else:
        head = '# ' + title_line.lstrip('> ').strip()
    out = [head, '']
    if untitled:
        out.append(f"<!-- VERIFY: 'untitled' — the source prints this prayer "
                   f"with no title; the bracketed heading is editorial -->")
        out.append('')
    if gap:
        out.append(f"<!-- VERIFY: {gap} -->")
        out.append('')
    for b in body_lines:
        out.append(b.strip())
        out.append('')
    while out and out[-1] == '':
        out.pop()
    return '\n'.join(out) + '\n'


def build(year: str, units, srcyear=None, write=True):
    L = lines(srcyear or year)
    d = WT / 'editions' / year / FAMILY
    if write:
        d.mkdir(parents=True, exist_ok=True)
    made = []
    for slug, tl, b0, b1 in units:
        title = L[tl - 1] if tl else None
        body = [L[i - 1] for i in range(b0, b1 + 1)
                if L[i - 1].strip() and not APPARATUS.match(L[i - 1])]
        if not body:
            raise SystemExit(f"ABORT {year}/{slug}: no body at lines {b0}..{b1}")
        if tl and not L[tl - 1].strip():
            raise SystemExit(f"ABORT {year}/{slug}: title line {tl} is blank")
        if write:
            (d / f'{slug}.md').write_text(
                render(slug, title, body, tl is None,
                       GAP_VERIFY.get((year, slug))), encoding='utf-8')
        made.append(slug)
    return made


if __name__ == '__main__':
    write = '--dry' not in sys.argv
    for y in ('1552', '1559', '1637'):
        m = build(y, UNITS[y], write=write)
        print(f"{y}: {len(m)} units -> {', '.join(m[:4])}…")
    m = build('1604', UNITS['1559'] + UNITS_1604_ADDED, srcyear='1559', write=write)
    print(f"1604: {len(m)} units (1559 base + {len(UNITS_1604_ADDED)} apparatus-dated 1604 additions)")
