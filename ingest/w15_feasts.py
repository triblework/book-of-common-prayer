#!/usr/bin/env python3
"""w15_feasts.py — 1928 Tables and Rules for the Feasts and Fasts (Wave 15).

Authoring-only; NOT published. source -> script -> file (HANDOFF §6).
Writes editions/1928/tables/feasts-and-fasts.md from Calendar&Tables_1928.pdf
sheet 3 (book pp. xxxi-xxxii of the original printing, scan page 17 -- the
text layer's two book pages are the scan's pp. xxxi and xxxii).

Scope follows the 1892 precedent (w14_build_feasts.py): the Tables and Rules
up to, not including, "Tables for finding Holy Days" -- the Easter and
golden-number arithmetic is excluded apparatus (Wave 14 ruling B).

Conventions, matched to the 1892 cell so `git diff v1892 v1928` aligns: the
printed headings are plain lines as printed (no `##`, which 1892 does not
have), and every list entry is its own line. A two-column list is emitted
LEFT COLUMN FIRST, then the right, which is the printed reading order.

STRUCTURE. Layout-mode text, split at the gutter into the two book pages, then
cut into blocks by their printed headings. In a list line the columns are
separated by a gap of 6+ spaces (kerning never exceeds 4); a line holding fewer
pieces than the block has columns is placed by position, and a piece that
begins lower-case, or follows an entry ending "-" or in a function word, is a
wrapped continuation of the entry above it in the same column.
"""
from __future__ import annotations
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import w15_src as S
import w15_witness as W

OUT = os.path.join(WT, "editions", "1928", "tables", "feasts-and-fasts.md")
TITLE = "Tables and Rules for the Feasts and Fasts"   # the slug title (1892's)
GUTTER = 132            # layout-mode character column between the pages

# (start regex, kind[, columns]) in printed order, per book page. A block runs
# until the next block's start.
LEFT = [
    (r"^Tables and Rules for the", "heading"),
    (r"^Together with the Days", "heading"),
    (r"^RULES TO KNOW", "heading"),
    (r"^E?ASTER DAY", "para"),
    (r"^But NOTE", "para"),
    (r"^Advent Sunday is", "lines"),
    (r"^A TABLE OF FEASTS", "heading"),
    (r"^TO BE OBS", "heading"),
    (r"^All Sundays in the Year", "cols", 2),
]
RIGHT = [
    (r"^A TABLE OF FASTS", "heading"),
    (r"^Ash W ?ednesday", "cols", 2),
    (r"^OTHER DAYS OF FASTING", "heading"),
    (r"^I\. The Forty", "ordinals"),
    (r"^DAYS OF SOLEMN", "heading"),
    (r"^The three Rogation", "para"),
    (r"^TABLES OF PRECEDENCE", "heading"),
    (r"^The Holy Days following", "para"),
    (r"^The Sundays in Adven", "cols", 2),
    (r"^If any\s+other Holy Day", "para"),
    (r"^The following Holy Days", "para"),
    (r"^St\. Step ?hen", "cols", 2),
    (r"^On the ?se Holy Days", "para"),
    (r"^A TABLE$", "heading"),
    (r"^OF THOSE DAYS", "heading"),
    (r"^The Ember Days", "cols", 3),
]
FUNCTION_END = re.compile(r"(?:\b(?:of|a|an|the|and|or|to|in)|-)$")


def halves():
    lines = S.layout("CAL", 3).split("\n")
    left = [l[:GUTTER].rstrip() for l in lines]
    right = [l[GUTTER:].rstrip() for l in lines]
    return left, right


def drop_caps():
    """Drop capitals are single-letter runs in a large size. Layout mode
    displaces them to the start of the paragraph's SECOND line ("Ethe Full
    Moon"); they belong before the first word ("EASTER DAY")."""
    return [t.strip() for _y, _x, t, size in S.runs("CAL", 3)
            if size > 15 and len(t.strip()) == 1]


def blocks(lines, spec):
    """-> [(kind, cols, [raw lines])] cut at each spec's start regex."""
    idx = []
    k = 0
    for i, l in enumerate(lines):
        if k < len(spec) and re.search(spec[k][0], l.strip()):
            idx.append((i, spec[k]))
            k += 1
    if k != len(spec):
        raise SystemExit("feasts: block %r not found" % (spec[k][0],))
    out = []
    for n, (i, sp) in enumerate(idx):
        j = idx[n + 1][0] if n + 1 < len(idx) else len(lines)
        body = [l for l in lines[i:j] if l.strip()]
        out.append((sp[1], sp[2] if len(sp) > 2 else 1, body))
    return out


def clean(s):
    return S.dekern(S.norm_ws(s))


def join_wrapped(parts):
    """Rejoin a wrapped line: a trailing hyphen is a line-break hyphen when the
    continuation starts lower-case ("fore-" + "going", "Matri-" + "mony")."""
    out = ""
    for p in parts:
        if out.endswith("-") and p[:1].islower():
            out = out[:-1] + p
        else:
            out = (out + " " + p).strip()
    return out


def columns(body, ncols):
    """Split a list block into ncols columns of entries."""
    first = next(l for l in body if len(re.split(r"\s{6,}", l.strip())) == ncols)
    starts = [m.start() for m in re.finditer(r"(?:^|\s{6,})(\S)", first)]
    starts = [first.index(p) for p in re.split(r"\s{6,}", first.strip())]
    cols = [[] for _ in range(ncols)]
    for l in body:
        lead = len(l) - len(l.lstrip())
        pos = lead
        for piece in re.split(r"(\s{6,})", l.strip()):
            if not piece.strip():
                pos += len(piece)
                continue
            c = min(range(ncols), key=lambda k: abs(starts[k] - pos))
            text = clean(piece)
            if cols[c] and (text[:1].islower()
                            or FUNCTION_END.search(cols[c][-1])):
                # de-kern AFTER rejoining: "M atri-" + "m ony" -> "Matrimony"
                cols[c][-1] = clean(join_wrapped([cols[c][-1], text]))
            else:
                cols[c].append(text)
            pos += len(piece)
    return [e for col in cols for e in col]


def render(kind, ncols, body, caps):
    if kind == "heading":
        return [join_wrapped([clean(l) for l in body])]
    if kind == "para":
        text = join_wrapped([clean(l) for l in body])
        return [text]
    if kind == "lines":
        return [clean(l) for l in body]
    if kind == "ordinals":
        # each printed ordinal (I. II. III.) opens an entry; wraps continue it
        out = []
        for l in body:
            c = clean(l)
            if re.match(r"^[IVX]+\b", c) or not out:
                out.append(c)
            else:
                out[-1] = join_wrapped([out[-1], c])
        return out
    if kind == "cols":
        return columns(body, ncols)
    raise SystemExit(kind)


def build():
    left, right = halves()
    caps = drop_caps()
    out = []
    for spec, lines in ((LEFT, left), (RIGHT, right)):
        for kind, ncols, body in blocks(lines, spec):
            if kind == "para" and caps and re.match(r"^\s*ASTER", body[0]):
                # the drop capital "E" belongs before "ASTER DAY"; layout mode
                # glued it to the start of the next line
                cap = caps.pop(0)
                body = [re.sub(r"^\s*", cap, body[0], count=1)] + [
                    re.sub(r"^" + cap, "", body[1], count=1)] + body[2:]
            out.extend(render(kind, ncols, body, caps))
    return out


def apply_witness(lines):
    log = []
    for c in W.FEASTS:
        hits = [i for i, l in enumerate(lines) if c["text_layer"] in l]
        if len(hits) != 1:
            raise SystemExit("witness (feasts): %r found %d times"
                             % (c["text_layer"], len(hits)))
        i = hits[0]
        lines[i] = lines[i].replace(c["text_layer"], c["scan"], 1)
        log.append(c)
    return log


def main():
    lines = build()
    log = apply_witness(lines)
    body = ["# " + TITLE, ""]
    for l in lines:
        body += [l, ""]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(body).rstrip("\n")) + "\n"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("1928  feasts-and-fasts lines=%d words=%d witness corrections=%d"
          % (len(lines), len(text.split()), len(log)))


if __name__ == "__main__":
    main()
