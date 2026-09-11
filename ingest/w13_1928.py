#!/usr/bin/env python3
"""w13_1928.py — parse the 1928 Psalter from justus (Wave 13).

Authoring-only; NOT published. PARSES ONLY; w13_render.py writes the cells.

Source: justus 1928/Psalms{1,2,3}.htm. Each page is two-column, the Wave-10
pattern: <td width="400"> carries the 1928 TEXT, <td width="200"> carries an
apparatus of earlier readings. Per ruling B (revised) THE APPARATUS IS NOT
APPLIED -- this is the 1928 text only -- and the <sup>N</sup> reference marks
the text column uses to point into it are removed as apparatus, not text.

Traps met, all structural:
  * Headings are centred with EITHER <p align="center"> OR a bare
    <div align="center"> (the brief's trap #1: a <p>-only matcher missed 26
    psalm headings).
  * Cell attributes come in varying order (width="400" rowspan="2" ...).
  * A drop capital arrives as its own span ("W" + "HY"), so tags are removed
    WITHOUT inserting a space.
  * An unnumbered line is either a verse OPENING (a psalm's verse 1 or a
    Psalm-119 portion's first verse, both set with a drop capital) or a
    CONTINUATION of the verse before; the drop capital is the discriminator.
"""
import html as H
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))

J = "http://justus.anglican.org/resources/bcp/1928/"
TEXT_CELL = re.compile(r'<td\b[^>]*\bwidth="?400"?[^>]*>(.*?)</td>', re.S | re.I)
CENTRED = re.compile(r'<(p|div)\b[^>]*\balign="?center"?[^>]*>(.*?)</\1>',
                     re.S | re.I)
SUP = re.compile(r"<sup>.*?</sup>", re.S | re.I)
ROMAN = re.compile(r"^([IVXL]+)\.\s*(.*)$")
PSALM = re.compile(r"^Psalm\s+(\d+)\.\s*(.*)$")
SKIP_HEAD = re.compile(r"(?i)^(the .* day|morning prayer|evening prayer|book\s+[ivx]+)")

STRIPPED_SUPS = []


def clean(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = H.unescape(s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def tokens(page_html):
    """-> [("H", heading_text) | ("L", line_text, opens_with_dropcap)]"""
    # A CELL BOUNDARY IS A LINE BOUNDARY. The text column runs through many
    # <tr> rows, and joining the cells with a bare newline fused the last line
    # of one cell to the first line of the next -- burying Psalm 10's verses
    # 15-20 inside verse 14. The verse-run gate stayed green throughout, because
    # the swallowed numbers never broke the 1..N run; only a cross-edition
    # verse count exposed it.
    body = "<br>".join(TEXT_CELL.findall(page_html))
    STRIPPED_SUPS.append(len(SUP.findall(body)))
    body = SUP.sub("", body)
    out = []
    pos = 0
    for m in CENTRED.finditer(body):
        out += _lines(body[pos:m.start()])
        out += _centred(m.group(2))
        pos = m.end()
    out += _lines(body[pos:])
    return out


def _centred(raw):
    """A centred block is NOT one heading. It may hold a day heading AND a
    psalm heading in separate paragraphs (Psalm 18: "Evening Prayer." then
    "Psalm 18. Diligam te" -- classified as one day heading, it was skipped and
    Psalm 18's verses fell into Psalm 17), or, where the source closes its
    <div> late, the heading AND the psalm's text (Psalm 100). So each paragraph
    is classified on its own."""
    out = []
    for seg in re.split(r"<br\s*/?>|</p>|<p\b[^>]*>", raw, flags=re.I):
        t = clean(seg)
        if not t:
            continue
        if PSALM.match(t):
            # "Psalm N. <em>Latin</em>" -- the heading ends at the incipit;
            # anything after it in the same segment is verse text.
            k = seg.lower().find("</em>")
            if k >= 0:
                head, rest = seg[:k + 5], seg[k + 5:]
                out.append(("H", clean(head)))
                if clean(rest):
                    out.append(("L", clean(rest), "dropcap" in rest))
            else:
                out.append(("H", t))
        elif SKIP_HEAD.match(t) or ROMAN.match(t) or re.fullmatch(r"[IVXL]+\.?", t):
            out.append(("H", t))
        else:
            out.append(("L", t, "dropcap" in seg))
    return out


def _lines(chunk):
    out = []
    for seg in re.split(r"<br\s*/?>|</p>|<p\b[^>]*>", chunk, flags=re.I):
        opens = "dropcap" in seg
        t = clean(seg)
        if t:
            out.append(("L", t, opens))
    return out


def parse():
    import scrape
    psalms = {}
    cur = None
    pending = None
    for n in (1, 2, 3):
        for tok in tokens(scrape.fetch(J + "Psalms%d.htm" % n)):
            if tok[0] == "H":
                h = tok[1]
                m = PSALM.match(h)
                if m:
                    no = int(m.group(1))
                    rest = m.group(2).strip()
                    cur = psalms[no] = {"incipit": None, "verses": []}
                    pending = None
                    mr = ROMAN.match(rest)
                    if no == 119 and mr:
                        cur["incipit"] = mr.group(2).strip() or None
                    else:
                        cur["incipit"] = rest or None
                    continue
                if cur is not None and cur is psalms.get(119):
                    mr = ROMAN.match(h)
                    if mr:
                        pending = mr.group(2).strip() or None
                        continue
                if SKIP_HEAD.match(h) or re.fullmatch(r"[IVXL]+", h):
                    continue
                continue
            _t, text, opens = tok
            if cur is None:
                continue
            # A line with no letters is not a verse: Psalm 17's incipit is
            # printed "<em>Exaudi, Domine</em>." and the closing period arrived
            # as its own line, becoming an empty "verse 1" that shifted every
            # verse after it by one.
            if not re.search(r"[A-Za-z]", text):
                continue
            mv = re.match(r"^(\d{1,3})\s+(.*)$", text)
            # A numbered line is a new verse whenever it ADVANCES the count.
            # Requiring exactly previous+1 meant one missing <br> (Psalm 92
            # prints verse 2 inside verse 1) turned every later verse into a
            # "continuation" and collapsed the psalm to a single verse. A gap
            # is repaired afterwards, or reported.
            if mv and (not cur["verses"]
                       or 0 < int(mv.group(1)) - cur["verses"][-1][0] <= 3):
                cur["verses"].append((int(mv.group(1)), mv.group(2), pending))
                pending = None
            elif not cur["verses"]:
                cur["verses"].append((1, text, pending))
                pending = None
            elif opens:
                cur["verses"].append((cur["verses"][-1][0] + 1, text, pending))
                pending = None
            else:
                pn, pt, ps = cur["verses"][-1]
                cur["verses"][-1] = (pn, pt + " " + text, ps)
    for no, p in psalms.items():
        p["verses"] = repair_gaps(no, p["verses"])
    return psalms


GAP_REPAIRS = []
GAP_UNREPAIRED = []


def repair_gaps(no, verses):
    """Where verse N+1 is missing, look for it INSIDE verse N: the exact number
    N+1, standing alone and followed by a capital letter, is a verse the source
    printed without its line break. Split there. Nothing else is inferred; a
    gap that cannot be found that way is REPORTED, never filled."""
    out = []
    for num, text, sub in verses:
        while out and num > out[-1][0] + 1:
            want = out[-1][0] + 1
            pn, pt, ps = out[-1]
            m = re.search(r"(?:^|\s)%d\s+(?=[A-Z])" % want, pt)
            if not m or m.start() == 0:
                GAP_UNREPAIRED.append((no, want))
                break
            out[-1] = (pn, pt[:m.start()].strip(), ps)
            out.append((want, pt[m.end():].strip(), None))
            GAP_REPAIRS.append((no, want))
        out.append((num, text, sub))
    return out


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    import w13_1662
    ps = parse()
    bad = w13_1662.gate(ps, "1928")
    print("1928: %d psalms, %d verses, %d incipits, %d sub-headings; %d <sup> "
          "apparatus marks stripped"
          % (len(ps), sum(len(p["verses"]) for p in ps.values()),
             sum(1 for p in ps.values() if p["incipit"]),
             sum(1 for p in ps.values() for v in p["verses"] if v[2]),
             sum(STRIPPED_SUPS)))
    print("gap repairs (verse found inside the previous one): %d %s"
          % (len(GAP_REPAIRS), GAP_REPAIRS[:20]))
    print("gaps NOT repairable: %s" % GAP_UNREPAIRED)
    print("GATE:", "clean" if not bad else "%d problems" % len(bad))
    for b in bad[:12]:
        print("  -", b)
