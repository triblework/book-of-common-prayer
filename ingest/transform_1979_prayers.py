#!/usr/bin/env python3
"""Wave 11 — build the 1979 Prayers and Thanksgivings cells from the PD e-text.

source -> script -> file (the 1979 modern text is exactly what trips the output
content filter, so it is never emitted as model output; only counts and slugs
are printed).

Structure of `bcpprayr.txt`:
    <Section Name>   subsection heads      =N.  Title=   a prayer's title
    <page NNN>       page furniture, stripped
The `=...=` form also marks emphasis (`=Amen.=`), so a title must be `=N. ...=`.

CROSSWALK (Wave-10 Decision C, restated in WAVE11_GUIDE.md): 1979 continues a
historic prayer -> SAME slug; drops one -> absent; genuinely new -> its OWN
slug. A non-descendant is NEVER forced onto a historic slug to manufacture a
diff. Contested candidates are given their own slug and the rejection recorded,
rather than mapped on a guess.
"""
from __future__ import annotations
import glob, re, sys
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
FAMILY = 'prayers-and-thanksgivings'
CACHE = glob.glob('/Users/wtrible/Developer/bcp/scrape-cache/*bcpprayr*')

# --- confirmed lineage: 1979 text continues the historic prayer -> same slug ---
CROSSWALK = {
    ('p', 2):  'for-all-conditions-of-men',
    ('p', 9):  'for-the-clergy-and-people',
    ('p', 21): 'for-courts-of-justice',
    ('p', 31): 'for-schools-colleges-universities',
    ('p', 43): 'for-rain',
    ('t', 1):  'thanksgiving-general',
}

# --- considered and NOT mapped; each keeps its own 1979 slug -------------------
# Recorded here so the decision is auditable rather than invisible.
CROSSWALK_REJECTED = {
    ('p', 20): "1979 'For Congress or a State Legislature' merges what 1928 "
               "prints as two separate prayers (for-congress, "
               "for-a-state-legislature). Mapping it onto either would claim a "
               "one-to-one descent that does not exist.",
    ('t', 9):  "1979 'For the Harvest' resembles 'For Plenty' in theme, but the "
               "texts were not confirmed to be the same prayer. Not mapped.",
    ('t', 10): "1979 'For the Gift of a Child' vs the historic 'Thanksgiving of "
               "Women after Child-birth' (the Churching of Women) — a different "
               "occasion, not a modernization of it.",
    ('t', 11): "1979 'For the Restoration of Health' vs 'For a Recovery from "
               "Sickness' — plausible but unconfirmed. Not mapped.",
}


def slugify(t: str) -> str:
    t = t.lower().replace("'", '').replace('’', '')
    t = re.sub(r'[^a-z0-9]+', '-', t)
    return re.sub(r'-+', '-', t).strip('-')


def parse():
    L = Path(CACHE[0]).read_text(encoding='utf-8', errors='replace').split('\n')
    # body begins after the table of contents, at the second <Prayers and Thanksgivings>
    starts = [i for i, x in enumerate(L) if x.strip() == '<Prayers and Thanksgivings>']
    # BOUND the section. This file continues straight on into the Catechism,
    # the Athanasian Creed, the Articles of Religion and the Easter tables;
    # without an end marker those would be swept in as "prayers".
    end = next(i for i, x in enumerate(L)
               if i > starts[-1] and x.strip() == '<Concerning the Catechism>')
    body = L[starts[-1]:end]
    # A long title wraps: '=15.  for those about to be Baptized or' /
    # 'to renew their Baptismal Covenant='. Unjoined, the marker fails to match
    # (losing the prayer entirely) AND its tail is swallowed into the previous
    # prayer's body. Join an opening '=N.' that does not close on its own line.
    joined, i = [], 0
    while i < len(body):
        cur = body[i]
        if re.match(r'\s*=\s*\d{1,3}\.', cur) and not cur.rstrip().endswith('='):
            k = i + 1
            while k < len(body) and not body[k].rstrip().endswith('='):
                cur = cur.rstrip() + ' ' + body[k].strip()
                k += 1
            if k < len(body):
                cur = cur.rstrip() + ' ' + body[k].strip()
            joined.append(cur)
            i = k + 1
            continue
        joined.append(cur)
        i += 1
    body = joined
    units, cur, sect = [], None, 'p'
    for ln in body:
        s = ln.strip()
        if re.fullmatch(r'<page \d+>', s):
            continue
        # the e-text heads this section '<Thanksgiving>' (singular); keying on
        # the plural silently left every thanksgiving in the prayers section,
        # which collided on the crosswalked slugs.
        if s in ('<Thanksgiving>', '<Thanksgivings>') or s.startswith('<General Thanksgiving'):
            sect = 't'
            continue
        m = re.fullmatch(r'<(.+)>', s)
        if m:
            continue                      # subsection head
        m = re.fullmatch(r'=\s*(\d{1,3})\.\s+(.*?)\s*=', s)
        if m:
            if cur:
                units.append(cur)
            cur = {'n': int(m.group(1)), 'sect': sect,
                   'title': m.group(2).strip(), 'body': []}
            continue
        if cur is not None and s:
            cur['body'].append(s)
    if cur:
        units.append(cur)
    return units


def main(write=True):
    units = parse()
    d = WT / 'editions' / '1979' / FAMILY
    if write:
        d.mkdir(parents=True, exist_ok=True)
    seen, mapped, own = {}, 0, 0
    for u in units:
        key = (u['sect'], u['n'])
        if key in CROSSWALK:
            slug = CROSSWALK[key]; mapped += 1
        else:
            base = ('thanksgiving-' if u['sect'] == 't' else '') + slugify(u['title'])
            slug = base
            k = 2
            while slug in seen:
                slug = f'{base}-{k}'; k += 1
            own += 1
        if slug in seen:
            raise SystemExit(f"ABORT 1979: duplicate slug {slug!r}")
        seen[slug] = u
        if not u['body']:
            raise SystemExit(f"ABORT 1979: unit {u['n']} ({u['title']!r}) has no body")
        if write:
            out = [f"# {u['title']}", '']
            for b in u['body']:
                out.append(b); out.append('')
            while out and out[-1] == '':
                out.pop()
            (d / f'{slug}.md').write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f"1979: {len(units)} units "
          f"({sum(1 for u in units if u['sect']=='p')} prayers / "
          f"{sum(1 for u in units if u['sect']=='t')} thanksgivings); "
          f"{mapped} mapped to historic slugs, {own} on their own slugs")
    return seen


if __name__ == '__main__':
    main(write='--dry' not in sys.argv)
