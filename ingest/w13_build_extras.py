#!/usr/bin/env python3
"""w13_build_extras.py — the two Wave-13 extras (ruling D).

  psalter/selections.md      1789 -- the Selections of Psalms, "to be used
                             instead of the Psalms for the Day"
  tables/proper-psalms.md    1789 and 1892 -- the Tables of Proper Psalms on
                             Certain Days. This closes a Wave-14 recorded gap:
                             Wave 14 stopped the 1789 Psalter rubric before this
                             table and did not transcribe it.

Both are citation tables, rendered as normalized long-form (spec §10).

Two typographic normalizations, both counted: psalm lists get one space after
each comma (1789 prints "19,45,85", 1892 "2, 57, 111" -- left alone, every row
would differ between the two books on spacing alone); and a trailing comma or
period is dropped from a day name, since a period before " | " is a sentence
boundary to sentence_split.py.

justus's 1928 index links 1892's and 1928's Selections to this same 1789 page
(the Wave-12 "looks shared" trap), so ONLY 1789 is authored from it.
"""
import html as H
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WT, "tools"))
import scrape

J = "http://justus.anglican.org/resources/bcp/"
EMPTY = "—"
VERIFIES = []


def cells(tr):
    return [re.sub(r"\s+", " ", H.unescape(re.sub(r"<br[^>]*>", " | ",
            re.sub(r"<(?!br)[^>]+>", "", c)))).strip()
            for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S | re.I)]


def dayname(s):
    s = re.sub(r"(?i)^table of proper psalms on certain days\.\s*\|\s*", "", s)
    # rejoin a line-broken name; drop the hyphen only where the continuation
    # starts lower-case (the ordinary dehyphenation cue) -- "Circum- | cision"
    # -> "Circumcision", but "Christ- | Mas-day" keeps its hyphen as printed.
    s = re.sub(r"-\s*\|\s*(?=[a-z])", "", s)
    s = re.sub(r"-\s*\|\s*(?=[A-Z])", "-", s)     # a line break is not a space
    s = re.sub(r"\s*\|\s*", " ", s)
    return re.sub(r"[.,]+$", "", s).strip()


def psalms(s):
    s = re.sub(r"(?i)\b(morning|evening)\b[.,]?", "", s)
    s = re.sub(r"<[^>]*>|\|", " ", s)
    nums = re.findall(r"\d+", s)
    return ", ".join(nums) if nums else EMPTY


def proper_table(url, start):
    h = scrape.fetch(url)
    # the title can be split by markup ("PROPER <br> PSALMS"), so words may be
    # separated by tags as well as whitespace
    pat = r"(?:\s|<[^>]+>)+".join(map(re.escape, start.split()))
    m0 = re.search(pat, h)
    if not m0:
        raise SystemExit("%s: title %r not found" % (url, start))
    i = m0.start()
    # The 1892 title sits INSIDE the table's first cell, so "the next table
    # after the title" skipped past the data. Use the enclosing table when the
    # title is inside one, otherwise the next.
    op, cl = h.rfind("<table", 0, i), h.rfind("</table>", 0, i)
    j = op if op > cl else h.find("<table", i)
    k = h.find("</table>", j)
    left, right = [], []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", h[j:k + 8], re.S | re.I):
        c = [x for x in cells(tr) if x.replace("|", "").strip()]
        if len(c) < 3:
            continue
        for side, trip in ((left, c[0:3]), (right, c[3:6])):
            if len(trip) == 3 and re.search(r"[A-Za-z]", trip[0]) \
                    and re.search(r"\d", trip[1] + trip[2]):
                side.append((dayname(trip[0]), psalms(trip[1]), psalms(trip[2])))
    return left + right          # left column, then right: liturgical order


def write(edition, rel, title, rows):
    p = os.path.join(WT, "editions", edition, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    body = ["# " + title, ""] + rows
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("\n".join(body).rstrip("\n") + "\n")
    print("%s %-28s rows=%d" % (edition, rel, sum(1 for r in rows if " | " in r)))


def main():
    # 1789 proper psalms
    rows = []
    for d, m, e in proper_table(J + "1789/FrontMatter_1789.htm", "Psalms on Certain Days"):
        rows.append("%s | Morning: %s | Evening: %s" % (d, m, e))
    write("1789", "tables/proper-psalms.md", "Proper Psalms on Certain Days", rows)

    # 1892 proper psalms. For an impossible psalm number, the note cites what
    # 1789 prints for the same day, as corroboration -- never as a correction.
    ref1789 = {re.sub(r"[^a-z]", "", d.lower()): (m, e) for d, m, e in
               proper_table(J + "1789/FrontMatter_1789.htm", "Psalms on Certain Days")}
    rows = []
    for d, m, e in proper_table(J + "1892/Psalms_1892.htm", "PROPER PSALMS"):
        rows.append("%s | Morning: %s | Evening: %s" % (d, m, e))
        if re.search(r"\b1(9\d|[5-9]\d\d)\b", m + " " + e) or any(
                int(x) > 150 for x in re.findall(r"\d+", m + " " + e)):
            bad = [x for x in re.findall(r"\d+", m + " " + e) if int(x) > 150]
            k = re.sub(r"[^a-z]", "", d.lower())
            also = ("; for the same day 1789 prints Morning %s, Evening %s, which "
                    "suggests a 3-for-8 misreading -- and if so, a valid-looking "
                    "number beside it may be misread too" % ref1789[k]) \
                if k in ref1789 else ""
            note = ("the 1892 table prints Psalm %s, which does not exist (the "
                    "Psalter has 150). A misprint; the intended number cannot be "
                    "known from this source, so it is carried as printed%s"
                    % (", ".join(bad), also))
            rows.append("<!-- VERIFY: '%s'; %s -->" % (", ".join(bad), note))
            VERIFIES.append({"edition": "1892", "service": "tables/proper-psalms",
                             "anchor": d, "source_reading": ", ".join(bad),
                             "note": note})
    write("1892", "tables/proper-psalms.md", "Table of Proper Psalms on Certain Days", rows)

    # 1789 Selections of Psalms
    md = scrape.html_to_markdown(scrape.fetch(J + "1789/Psalter_1789.htm"))
    lines = [l.strip() for l in md.split("\n") if l.strip()]
    rows, cur = [], None
    for l in lines:
        m = re.match(r"^Selection\s+(\w+)\s*$", l)
        if m:
            cur = ["Selection " + m.group(1)]
            rows.append(cur)
            continue
        if cur is not None and re.match(r"^Psalm\s+\d+", l):
            cur.append(re.sub(r"\s+", " ", l).rstrip("."))
    out = [" | ".join(r) for r in rows if len(r) > 1]
    write("1789", "psalter/selections.md", "Selections of Psalms", out)
    import json
    json.dump(VERIFIES, open(os.path.join(HERE, "wave13_extras_verifies.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
