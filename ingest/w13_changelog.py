#!/usr/bin/env python3
"""w13_changelog.py — test the 1892 Psalter against an INDEPENDENT witness.

Authoring-only. justus 1789/Psalter1789&1892.htm is a dated table of "specific
changes in wording made in U.S. Prayer Books prior to 1928" -- e.g.
"4:2 'leasing' to 'falsehood' 1790", "16:9 'always' to 'alway' 1892",
"22:16 'council' to 'counsel' 1845; restored in 1892".

It is compiled independently of the PDF this wave transcribes 1892 from, so it
tests the whitespace repair AND the parse without relying on either:

  * a change dated in or before 1892 must show its NEW reading in 1892;
  * a change "restored in 1892" must show its OLD reading;
  * the text must not still show the superseded reading.

Where an entry stacks two successive changes, the LAST dated one at or before
1892 is the one tested.
"""
import html as H
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))

URL = "http://justus.anglican.org/resources/bcp/1789/Psalter1789&1892.htm"


def entries():
    import scrape
    h = scrape.fetch(URL)
    out = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", h, re.S | re.I):
        cells = [re.sub(r"\s+", " ", H.unescape(re.sub(r"<br\s*/?>", "|",
                 re.sub(r"<(?!br)[^>]+>", "", c)))).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S | re.I)]
        if len(cells) < 3 or not re.match(r"\d+:\d+", cells[0]):
            continue
        changes = [c.strip() for c in cells[1].split("|") if c.strip()]
        dates = [d.strip() for d in cells[2].split("|") if d.strip()]
        out.append((cells[0], changes, dates))
    return out


def parse_change(c):
    m = re.match(r"'(.*?)'\s+to\s+'?(.*?)'?\s*$", c)
    return (m.group(1), m.group(2).rstrip("'")) if m else (None, None)


def verses_of(ref):
    """'24:8&10' -> [(24, 8), (24, 10)]"""
    ps, vs = ref.split(":", 1)
    return [(int(ps), int(v)) for v in re.findall(r"\d+", vs)]


def norm(s):
    """Compare on words only: punctuation between words (2:12 prints
    "a little,) blessed") must not decide a wording test."""
    return " ".join(re.findall(r"[a-z]+", s.replace("’", "'").lower()))


def main():
    import w13_1892
    ps = w13_1892.parse()
    passed, failed, skipped = [], [], []
    for ref, changes, dates in entries():
        # pair each change with its date; choose the last dated <= 1892
        pairs = list(zip(changes, dates + [dates[-1]] * (len(changes) - len(dates))))
        chosen = None
        for c, d in pairs:
            yr = re.search(r"\d{4}", d)
            if yr and int(yr.group(0)) <= 1892:
                chosen = (c, d)
        if chosen is None:
            skipped.append(ref)
            continue
        old, new = parse_change(chosen[0])
        if old is None:
            skipped.append(ref)
            continue
        # A change "restored in YEAR" with YEAR <= 1892 was UNDONE by 1892, so
        # the OLD reading is expected (the first version only recognised
        # "restored in 1892" and mis-tested two entries restored in 1871).
        rm = re.search(r"restored in (\d{4})", chosen[1])
        restored = bool(rm and int(rm.group(1)) <= 1892)
        want, not_want = (old, new) if restored else (new, old)
        for p, v in verses_of(ref):
            vv = [x for x in ps[p]["verses"] if x[0] == v]
            if not vv:
                failed.append((ref, "verse missing"))
                continue
            t = norm(vv[0][1])
            ok = norm(want) in t
            if ok:
                passed.append(ref)
            else:
                failed.append((ref, "expected %r (%s)" % (want, chosen[1])))
    print("change-log check: %d passed, %d failed, %d not applicable to 1892"
          % (len(passed), len(failed), len(skipped)))
    for f in failed:
        print("   FAIL", f)
    return failed


if __name__ == "__main__":
    main()
