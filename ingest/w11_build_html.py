#!/usr/bin/env python3
"""Wave 11 — build per-prayer cells for the four HTML editions (1662/1789/1892/1928).

source -> script -> file. Prayer text is never emitted as model output.
Aborts on an unmapped title, an empty unit, or a duplicate slug.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w11_spine as S
import w11_map as M

WT = HERE.parent
FAMILY = 'prayers-and-thanksgivings'

SECT_OF = {
    'prayers': 'p', 'thanksgivings': 't', 'collects': 'c',
}


def units(year: str):
    blocks, dropped = S.extract(year)
    sect = 'p'
    cur = None
    out = []
    ember_n = 0
    for kind, text in blocks:
        n = M.norm(text)
        if kind in ('section', 'title') and n in SECT_OF:
            sect = SECT_OF[n]
            continue
        if kind in ('section', 'title') and n in M.SECTION_HEADS:
            continue
        if kind == 'title' and n in M.RUBRIC_AS_TITLE:
            if cur:                      # belongs to the prayer it follows
                cur['rubrics'].append(text)
            continue
        if kind == 'title':
            if n in M.SECOND_FORM:
                if not cur:
                    raise SystemExit(f"{year}: '{text}' with no preceding prayer")
                slug = cur['slug'] + '-2'
                out.append(cur); cur = {'slug': slug, 'title': text,
                                        'rubrics': [], 'body': [], 'sect': sect}
                continue
            if n.startswith(M.EMBER[:40]):
                ember_n += 1
                slug = 'in-the-ember-weeks' + ('' if ember_n == 1 else '-2')
            else:
                key = (sect, n)
                if key not in M.MAP:
                    raise SystemExit(
                        f"ABORT {year}: unmapped title in section {sect!r}:\n"
                        f"  raw : {text!r}\n  norm: {n!r}\n"
                        f"Add it to w11_map.MAP -- never drop it.")
                slug = M.MAP[key]
            if cur:
                out.append(cur)
            cur = {'slug': slug, 'title': text, 'rubrics': [], 'body': [], 'sect': sect}
            continue
        if kind == 'rubric':
            (cur['rubrics'] if cur else []).append(text)
            continue
        if kind == 'body':
            if sect == 'c':
                # the 1928 Collects are printed untitled: one unit per body,
                # slugged by order, all sharing the block's rubric
                idx = sum(1 for u in out if u['sect'] == 'c') + (1 if cur and cur['sect'] == 'c' else 0)
                if idx >= len(M.COLLECTS_1928):
                    raise SystemExit(f"ABORT {year}: more Collects than slugs ({idx+1})")
                if cur:
                    out.append(cur)
                cur = {'slug': M.COLLECTS_1928[idx], 'title': f'A Collect.',
                       'rubrics': list(shared_rubric), 'body': [text], 'sect': 'c'}
                out.append(cur); cur = None
                continue
            if cur:
                cur['body'].append(text)
            continue
    if cur:
        out.append(cur)
    return out, dropped


shared_rubric: list[str] = []


def render(u) -> str:
    lines = [f"# {u['title'].strip()}", '']
    for r in u['rubrics']:
        r = r.lstrip('¶').strip().lstrip('*').strip()
        lines.append(f"> {r}")
    if u['rubrics']:
        lines.append('')
    for b in u['body']:
        lines.append(b.strip())
        lines.append('')
    while lines and lines[-1] == '':
        lines.pop()
    return '\n'.join(lines) + '\n'


def build(year: str, write: bool = True):
    global shared_rubric
    shared_rubric = []
    # capture the 1928 Collects' shared rubric before unit grouping
    blocks, _ = S.extract(year)
    for i, (k, t) in enumerate(blocks):
        if k == 'title' and M.norm(t) == 'collects':
            for k2, t2 in blocks[i + 1:]:
                if k2 == 'rubric':
                    shared_rubric = [t2]
                break
            break
    us, dropped = units(year)
    seen = {}
    for u in us:
        if not u['body']:
            raise SystemExit(f"ABORT {year}: unit {u['slug']!r} has no body")
        if u['slug'] in seen:
            raise SystemExit(f"ABORT {year}: duplicate slug {u['slug']!r} "
                             f"({seen[u['slug']]!r} vs {u['title']!r})")
        seen[u['slug']] = u['title']
    if write:
        d = WT / 'editions' / year / FAMILY
        d.mkdir(parents=True, exist_ok=True)
        for u in us:
            (d / f"{u['slug']}.md").write_text(render(u), encoding='utf-8')
    return us, dropped


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry' in sys.argv
    for y in args or ['1662', '1789', '1892', '1928']:
        us, dropped = build(y, write=not dry)
        print(f"{y}: {len(us)} units written ({dropped} blocks excluded)")
        for u in us:
            print(f"    {u['slug']:46s} <- {u['title'][:44]}")
