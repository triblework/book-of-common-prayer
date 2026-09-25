"""w20_fetch.py -- fetch a BINARY file from an allow-listed host (Wave 20).

tools/scrape.py fetches text; the witness's page renderings are images. This
reuses its guardrails unchanged -- the host allow-list, robots.txt, the
rate limit, the user agent -- and caches under scrape-cache/ with the same
naming scheme, keeping the file's own extension.

    python3 ingest/w20_fetch.py URL        -> prints the cached path
"""
import hashlib, os, re, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
import scrape as S


def cache_path(url):
    digest = hashlib.sha256(url.encode('utf-8')).hexdigest()[:16]
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', url.split('://', 1)[-1])[:80]
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or '.bin'
    return S.CACHE_DIR / f'{safe}.{digest}{ext}'


def fetch(url):
    S._check_host(url)
    out = cache_path(url)
    if out.exists():
        return out
    if not S._robots_ok(url):
        raise SystemExit(f'REFUSED by robots.txt: {url}')
    wait = S.MIN_INTERVAL - (time.monotonic() - S._LAST_REQUEST[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={'User-Agent': S.USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    S._LAST_REQUEST[0] = time.monotonic()
    S.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return out


if __name__ == '__main__':
    for u in sys.argv[1:]:
        print(fetch(u))
