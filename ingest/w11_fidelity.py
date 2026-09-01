#!/usr/bin/env python3
"""w11_fidelity.py — Wave-11 anti-FABRICATION gate.

Every word of every authored cell must occur in the source it was built from.
Wave 11 applies NO text transforms (bodies are copied verbatim), so the only
words a cell may legitimately add are structural:

  * the `#` heading (fidelity_check already strips headings)
  * the bracketed editorial heading for a prayer the book prints untitled
  * the `<!-- VERIFY ... -->` comments, which are editorial by definition

Anything else is reported and fails the gate.

Pairs each cell with its own edition's source text, so a word attested only in
some OTHER edition still fails — which is the point.
"""
from __future__ import annotations
import re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w11_spine as S

WT = HERE.parent
FAMILY = 'prayers-and-thanksgivings'
SPINES = HERE / 'spines-w9'
HTML_YEARS = {'1662', '1789', '1892', '1928'}
SPINE_YEARS = {'1552': '1552', '1559': '1559', '1604': '1559', '1637': '1637'}


def toks(t: str) -> Counter:
    t = re.sub(r'[^a-z0-9]+', ' ', t.lower())
    return Counter(w for w in t.split() if w)


def source_tokens(year: str) -> Counter:
    if year in HTML_YEARS:
        blocks, _ = S.extract(year)
        return toks(' '.join(t for _, t in blocks))
    if year in SPINE_YEARS:
        return toks((SPINES / f'{SPINE_YEARS[year]}_litany.md').read_text(encoding='utf-8'))
    if year == '1979':
        import glob
        p = glob.glob('/Users/wtrible/Developer/bcp/scrape-cache/*bcpprayr*')[0]
        return toks(Path(p).read_text(encoding='utf-8', errors='replace'))
    raise SystemExit(f'no source for {year}')


def cell_tokens(p: Path) -> Counter:
    md = p.read_text(encoding='utf-8')
    md = re.sub(r'<!--.*?-->', ' ', md, flags=re.S)     # VERIFY comments: editorial
    out = []
    for line in md.splitlines():
        if line.startswith('#'):                         # heading: structural
            continue
        out.append(line.lstrip('> ').strip())
    return toks(' '.join(out))


def main(years):
    total = bad = 0
    for year in years:
        d = WT / 'editions' / year / FAMILY
        if not d.is_dir():
            continue
        src = source_tokens(year)
        miss_any = []
        for f in sorted(d.glob('*.md')):
            total += 1
            missing = {w: n for w, n in cell_tokens(f).items() if w not in src}
            if missing:
                bad += 1
                miss_any.append((f.stem, missing))
        status = 'CLEAN' if not miss_any else f'{len(miss_any)} CELL(S) WITH UNATTESTED WORDS'
        print(f"  {year}: {len(list(d.glob('*.md'))):3d} cells — {status}")
        for slug, m in miss_any[:6]:
            print(f"      !! {slug}: {list(m)[:8]}")
    print(f"\nfidelity: {total} cells checked, {bad} with unattested words "
          f"— {'PASS' if bad == 0 else 'REVIEW NEEDED'}")
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:] or ['1552', '1559', '1604', '1637',
                                   '1662', '1789', '1892', '1928', '1979']))
