#!/usr/bin/env python3
"""w13_1662.py — parse the 1662 Psalter from the Church of England (Wave 13).

Authoring-only; NOT published. PARSES ONLY; w13_render.py writes the cells, so
no psalm body is ever emitted as model tokens (HANDOFF §6).

Structural discriminators, from the page's own classes (never content):
  vlitemheading  "Psalm N."            -> a new psalm
  vllatinsub     the Latin incipit     -> also marks each Psalm-119 portion
  vlpsalm        one verse per <p>
  vlversenumber  the printed number; verse 1 carries none, as printed
"""
import html as H
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))

BASE = ("https://www.churchofengland.org/prayer-and-worship/"
        "worship-texts-and-resources/book-common-prayer")
INDEX = BASE

P = re.compile(r'<p class="(vlitemheading|vllatinsub|vlpsalm)">(.*?)</p>', re.S)
NUM = re.compile(r'<span class="vlversenumber">\s*(\d+)\s*</span>')


BOILERPLATE = "Text from The Book of Common Prayer, the rights in which"
DROPPED = []
JOINED = []


def cur_no(psalms, cur):
    for k, v in psalms.items():
        if v is cur:
            return k
    return None


def clean(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = H.unescape(s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def pages():
    import scrape
    h = scrape.fetch(INDEX)
    urls = sorted(set(re.findall(
        r'href="(/prayer-and-worship/worship-texts-and-resources/'
        r'book-common-prayer/psalter/[^"]+)"', h)))
    return ["https://www.churchofengland.org" + u for u in urls]


MULTI = []


def parse_page(url):
    """A verse paragraph can hold SEVERAL verses: the CoE packs Psalm 17's
    verses 14, 15 and 16 into one <p class="vlpsalm">, separated by <br>, each
    with its own number span. Treating a paragraph as a verse merged them
    silently -- the verse-run gate stayed green, and only the mediant count
    (three in one "verse") and the cross-edition verse count exposed it. So a
    paragraph is split at every <br> that precedes a verse-number span."""
    import scrape
    h = scrape.fetch(url)
    i = h.find('<div id="bcp">')
    j = h.find("</article>", i)
    out = []
    for cls, body in P.findall(h[i:j]):
        if cls == "vlpsalm":
            parts = re.split(r'<br\s*/?>\s*(?=<span class="vlversenumber">)', body)
            if len(parts) > 1:
                MULTI.append((url.rsplit("/", 1)[-1], len(parts)))
            for part in parts:
                out.append((cls, part))
        else:
            out.append((cls, body))
    return out


def parse():
    """-> {psalm_no: {"incipit": str, "verses": [(num, text, sub_incipit)]}}"""
    # Pages must be taken in PSALM-AND-VERSE order, not URL order. Sorting by
    # URL put Psalm 119's five pages in the order 1-32, 105-144, 145-176,
    # 33-72, 73-104, and because a portion's opening verse is unnumbered (its
    # number is inferred as previous+1) that silently renumbered verses 105-176.
    # The URL encodes the range exactly: psalm-119-33-72 -> (119, 33).
    def key(url):
        nums = [int(x) for x in re.findall(r"\d+", url.rsplit("/", 1)[-1])]
        if "psalm-119-" in url:
            return (119, nums[1])
        return (nums[0], 0)
    items = [parse_page(u) for u in sorted(pages(), key=key)]

    psalms = {}
    cur = None
    pending_sub = None
    for page in items:
        for cls, body in page:
            if cls == "vlitemheading":
                m = re.match(r"Psalm\s+(\d+)", clean(body))
                if not m:
                    continue
                n = int(m.group(1))
                if n in psalms:
                    cur = psalms[n]        # a psalm continued across pages
                else:
                    cur = psalms[n] = {"incipit": None, "verses": []}
                pending_sub = None
            elif cls == "vllatinsub":
                txt = clean(body)
                if cur is None:
                    continue
                if cur["incipit"] is None and not cur["verses"]:
                    cur["incipit"] = txt
                else:
                    pending_sub = txt       # a Psalm-119 portion
            elif cls == "vlpsalm":
                if cur is None:
                    continue
                text = clean(NUM.sub("", body))
                # (a) an empty trailing paragraph carries nothing
                if not text:
                    continue
                # (b) the site's own copyright notice is tagged as a verse at
                #     the foot of one page; it is boilerplate, not psalm text
                if text.startswith(BOILERPLATE):
                    DROPPED.append((cur_no(psalms, cur), text[:40]))
                    continue
                m = NUM.search(body)
                num = int(m.group(1)) if m else None
                # (c) some pages print the number in the text, not the span
                if num is None:
                    mt = re.match(r"^(\d{1,3})\s+(.*)$", text)
                    if mt and cur["verses"] and int(mt.group(1)) == cur["verses"][-1][0] + 1:
                        num, text = int(mt.group(1)), mt.group(2)
                if num is None:
                    # (d) An unnumbered paragraph is EITHER the opening verse
                    # of a psalm or Psalm-119 portion, OR the continuation of a
                    # verse the page split across two <p>. The page's own
                    # drop-capital (vlcaps) marks an opening; it is the
                    # structural discriminator, not the wording.
                    opens = 'class="vlcaps"' in body
                    if not cur["verses"]:
                        num = 1
                    elif opens:
                        num = cur["verses"][-1][0] + 1
                    else:
                        pn, pt, ps = cur["verses"][-1]
                        cur["verses"][-1] = (pn, pt + " " + text, ps)
                        JOINED.append((cur_no(psalms, cur), pn))
                        continue
                cur["verses"].append((num, text, pending_sub))
                pending_sub = None
    return psalms


def gate(psalms, edition="1662"):
    bad = []
    if sorted(psalms) != list(range(1, 151)):
        bad.append("%s: psalms %d, missing %s" % (
            edition, len(psalms),
            [n for n in range(1, 151) if n not in psalms][:10]))
    for n, p in sorted(psalms.items()):
        nums = [v[0] for v in p["verses"]]
        if nums != list(range(1, len(nums) + 1)):
            bad.append("%s Psalm %d: verse run %s" % (edition, n, nums[:12]))
    return bad


if __name__ == "__main__":
    ps = parse()
    bad = gate(ps)
    print("1662: %d psalms, %d verses, %d incipits, %d Ps-119 portions"
          % (len(ps), sum(len(p["verses"]) for p in ps.values()),
             sum(1 for p in ps.values() if p["incipit"]),
             sum(1 for v in ps.get(119, {"verses": []})["verses"] if v[2])))
    print("paragraphs holding several verses (split): %d %s" % (len(MULTI), MULTI))
    print("joined split verses: %d  %s" % (len(JOINED), JOINED))
    print("dropped boilerplate: %d  %s" % (len(DROPPED), DROPPED))
    print("GATE:", "clean" if not bad else "%d problems" % len(bad))
    for b in bad[:12]:
        print("  -", b)
