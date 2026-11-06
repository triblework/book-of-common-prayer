"""w25_fontruns.py -- what typeface Church Publishing's 1979 file sets each
possessive of small-capital LORD in. Wave 25; authoring-only; EVIDENCE ONLY.

R11 forbids taking letter case from this file's text layer: it renders the
book's small-capital LORD as "Lord". Its addendum (2026-10-16) records that
the file names each run's font (Sabon-RomanSC for small capitals), so case is
recoverable from the runs -- and queues that reopening as a pass of its own.
This script gathers the evidence for the question; it changes no cell.

For each of the 13 places where a 1979 cell prints the possessive of
small-capital LORD (12 "LORD'S", 1 "LORD's"), the page's runs are searched for
"Lord" + apostrophe + "s" with the cell's words around it, and the font of
each of those six characters is reported (the L, the o-r-d, the apostrophe,
the s). The whole file is also counted: every "Lord" + apostrophe + "s"
whose o-r-d is set in the small-capital face, by the face of its s.

Runs are extracted with pypdf (visitor_text) into ingest/.cache/w25_runs.json
(gitignored, rebuildable). Deterministic; no OCR.

    python3 ingest/w25_fontruns.py
"""
import collections, glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WB = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import w19_witness_text as WTX

CACHE = os.path.join(HERE, '.cache', 'w25_runs.json')
POSS = re.compile(r"(?<![A-Za-z])LORD['’][Ss](?![A-Za-z])")
APOS = "'’"


def runs():
    if os.path.exists(CACHE):
        return json.load(open(CACHE))
    import pypdf
    r = pypdf.PdfReader(WTX.SRC)
    raw = {}
    for i, p in enumerate(r.pages, 1):
        rr = []

        def v(text, cm, tm, fd, fs):
            if text:
                rr.append([((fd or {}).get('/BaseFont') or '?').lstrip('/'), text])
        try:
            p.extract_text(visitor_text=v)
        except Exception:
            rr = []
        raw[str(i)] = rr
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(raw, open(CACHE, 'w'))
    return raw


def chars(page_runs):
    """-> (text, fonts): the page's characters in run order, one font each."""
    t, f = [], []
    for font, txt in page_runs:
        for c in txt:
            t.append(c)
            f.append(font)
    return ''.join(t), f


def short(font):
    return font.split('+')[-1]


def cell_places():
    out = []
    for path in sorted(glob.glob(os.path.join(WB, 'editions/1979/**/*.md'), recursive=True)):
        ps = None
        for n, line in enumerate(open(path, encoding='utf-8'), 1):
            m = re.match(r'^## Psalm (\d+)', line)
            if m:
                ps = int(m.group(1))
            for h in POSS.finditer(line):
                v = re.match(r'^(\d+) ', line)
                where = ('Ps %d:%s' % (ps, v.group(1))) if ('psalter' in path and v and ps) else \
                    os.path.relpath(path, WB).split('/', 2)[2] + ':%d' % n
                before = re.sub(r'[^A-Za-z ]', ' ', line[:h.start()]).split()[-3:]
                after = re.sub(r'[^A-Za-z ]', ' ', line[h.end():]).split()[:3]
                out.append((where, h.group(0), before, after, os.path.relpath(path, WB), n))
    return out


def letters(s):
    return re.sub(r'[^a-z]', '', s.lower())


def main():
    R = runs()
    pages = {int(k): chars(v) for k, v in R.items()}
    # every Lord + apostrophe + s in the file whose o-r-d is small-capital
    whole = collections.Counter()
    hits = collections.defaultdict(list)
    for k, (t, f) in pages.items():
        for m in re.finditer(r"Lord[%s]s(?![a-z])" % APOS, t):
            i = m.start()
            if not all('RomanSC' in f[j] for j in range(i + 1, i + 4)):
                continue
            key = (short(f[i]), short(f[i + 4]), short(f[i + 5]))
            whole[key] += 1
            ctx = letters(t[max(0, i - 40):i]) + '|' + letters(t[i + 6:i + 46])
            hits[k].append((i, key, ctx))
    print('the whole file: "Lord" + apostrophe + "s" with o-r-d in the small-capital face, by face')
    print('  (L, apostrophe, s):')
    for key, n in whole.most_common():
        print('   %4d  %s' % (n, ' / '.join(key)))
    print()
    print('the 13 cell places:')
    rec = []
    for where, form, before, after, path, n in cell_places():
        want_b, want_a = letters(' '.join(before)), letters(' '.join(after))
        found = []
        for k, lst in hits.items():
            for i, key, ctx in lst:
                b, a = ctx.split('|')
                if b.endswith(want_b[-12:]) and a.startswith(want_a[:12]):
                    found.append((k, key))
        rec.append({'place': where, 'cell': form, 'file': path, 'line': n,
                    'found': [[k, list(key)] for k, key in found]})
        print('  %-38s %-7s %s' % (where, form, '; '.join('p%d %s' % (k, ' / '.join(key))
                                                         for k, key in found) or 'NOT FOUND'))
    json.dump(rec, open(os.path.join(HERE, '.cache', 'w25_fontruns_places.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
