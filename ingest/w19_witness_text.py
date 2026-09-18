"""w19_witness_text.py — extract the 1979 witness's text, page by page.

THE WITNESS. *The Book of Common Prayer* (1979), the Episcopal Church's own
PDF, published by Church Publishing Incorporated and served by Wikimedia
Commons as `File:Book of common prayer (TEC, 1979).pdf` (1001 pages,
4,911,934 bytes, sha256 d4552eb3...; producer "Acrobat PDFWriter 3.0f1r8 for
Power Macintosh"). The US Book of Common Prayer has never been under
copyright, which the publisher states and the Commons file page records.

This is NOT a page scan and NOT a volunteer keying: it is the publisher's own
typesetting, with a clean text layer. It is therefore an independent witness of
a different CLASS from justus's 1993 ASCII e-text, which is the carrier for
every 1979 cell in this repo -- so R6 ("two keyings are not two witnesses") is
satisfied, and where the two disagree the publisher's file is the book.

The extraction is deterministic (pypdf, no OCR), so the text record is NOT
committed: run this script against the cached PDF to rebuild it.

    python3 ingest/w19_witness_text.py            # writes the cache
    python3 ingest/w19_witness_text.py "a phrase" # find it
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = glob.glob('/Users/wtrible/Developer/bcp/scrape-cache/'
                '*Book_of_common_prayer__TEC__1979_*.pdf')[0]
CACHE = os.path.join(HERE, 'w19_pages.json')      # gitignored, rebuildable
SHA = 'd4552eb39fcc26c7f2bb83ccd8e15fae4801521ac0e76df12b60bbd1525a0a57'


def pages():
    """-> {pdf page number (1-based): text}"""
    if os.path.exists(CACHE):
        return {int(k): v for k, v in json.load(open(CACHE)).items()}
    import pypdf
    r = pypdf.PdfReader(SRC)
    out = {}
    for i, p in enumerate(r.pages, 1):
        try:
            out[i] = p.extract_text() or ''
        except Exception as e:                     # a page that will not parse
            out[i] = ''
            print('page %d: %s' % (i, e), file=sys.stderr)
    json.dump(out, open(CACHE, 'w'))
    return out


def flat(t):
    """Fold for searching: curly quotes to straight, runs of space to one."""
    t = (t.replace('’', "'").replace('‘', "'")
          .replace('“', '"').replace('”', '"')
          .replace('—', '--').replace('–', '-'))
    return re.sub(r'\s+', ' ', t)


def find(needle, pgs=None, ctx=140):
    """-> [(page, context)] for every page whose text contains `needle`."""
    pgs = pgs or pages()
    n = flat(needle).lower()
    hits = []
    for k in sorted(pgs):
        t = flat(pgs[k])
        i = t.lower().find(n)
        if i >= 0:
            hits.append((k, t[max(0, i - ctx):i + len(n) + ctx]))
    return hits


if __name__ == '__main__':
    pgs = pages()
    print('%d pages, %d with text, %d characters'
          % (len(pgs), sum(1 for v in pgs.values() if v.strip()),
             sum(len(v) for v in pgs.values())))
    for a in sys.argv[1:]:
        print('== %r' % a)
        for k, c in find(a, pgs):
            print('  p%-4d ...%s...' % (k, c))
