#!/usr/bin/env python3
"""w10_coe_index.py — fetch the CoE 1662 Collects/Epistles/Gospels pages and
report each page's occasion title, building the slug->occasion map for Wave 10.

The CoE site is slow and intermittently times out, so each page is retried; the
shared scrape cache means re-runs are free. Prints "SLUG<TAB>TITLE" lines.
"""
import sys, re, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import scrape

B = ("https://www.churchofengland.org/prayer-and-worship/worship-texts-and-"
     "resources/book-common-prayer/collects-epistles-and-gospels")
WS = re.compile(r"\s+")


def suffixes():
    yield ""
    for i in range(0, 88):
        yield f"-{i}"


def title_of(html):
    # The occasion name is the page's <h1>; fall back to <title>.
    for m in re.finditer(r"<h1[^>]*>(.*?)</h1>", html, re.S):
        t = WS.sub(" ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
        if t:
            return t
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    return WS.sub(" ", m.group(1)).strip() if m else "?"


def main():
    want = sys.argv[1:] or list(suffixes())
    for suf in want:
        url = B + suf
        html = None
        for attempt in range(4):
            try:
                html = scrape.fetch(url)
                break
            except Exception as e:
                sys.stderr.write(f"retry {suf!r} ({attempt}): {e}\n")
                time.sleep(3 * (attempt + 1))
        if html is None:
            print(f"{suf}\t!! FETCH FAILED")
            continue
        print(f"{suf}\t{title_of(html)}", flush=True)


if __name__ == "__main__":
    main()
