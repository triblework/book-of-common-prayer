#!/usr/bin/env python3
"""w15_fidelity.py — gate 1 for Wave 15: did anything appear that no source attests?

Authoring-only. Per AUDIT_METHOD this catches FABRICATION and is blind to loss
(w15_audit.py is the other half).

Wave 14's gate tested WORD tokens only, which is blind to numbers -- and in a
lectionary the numbers are the content. This gate tests VALUES AS STRINGS:

  * normalization, applied to source and value alike: lower case, whitespace
    removed, dashes unified, and the ordinal look-alikes I / l / 1 unified;
  * the witness corrections are first REVERSED, per line, exactly where the
    builders applied them, so what is tested is what the carrier supports.
    A corrected reading is attested by the scan instead: each one is in
    w15_witness with its book page, and is counted, not tested;
  * a table value must be an EXACT substring of the source stream, or -- where
    the source wraps it ("25, 46," / "77, 86, 90") -- a LOCAL cover: pieces of
    6+ characters, each within 200 characters of the one before. An
    unwindowed cover is worthless against a stream this size: it passes a
    fabricated "Isa. 99:1-5". A short final piece (a wrap tail, "134") must
    sit within 60 characters of the piece before. Prose: 6+, window 600;
  * the tables of lessons are tested on the parser's RAW FRAGMENTS (every run
    piece a cell is built from), each an exact substring. A cell is only its
    fragments joined and typographically normalized (w15_src.citation);
  * row labels and calendar names are tested word by word (a numbered
    Sunday's ordinal suffix, and a wrapped name, are separate runs).

Not tested, because this wave supplies them: `# ` slug titles; the field
labels ("Morning 1:", "Sunday Letter:", "Psalms:"); " / " between stacked
alternatives; the "—" of an empty cell; a calendar row's month-and-day
(position); a small-capital label's case (set from run size).

Sensitivity is checked at the end: readings the text layer prints nowhere
(fabrications, and some of the scan's own corrections) must FAIL.
"""
from __future__ import annotations
import contextlib
import html as H
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "tools"))

import w15_src as S
import w15_witness as W

E = lambda *p: os.path.join(WT, "editions", *p)
SUPPLIED_LABEL = re.compile(
    r"^(Sunday Letter|Kalendar Note|Morning [12]|Evening [12]|Eve [12]|Morning|"
    r"Evening|Also|Psalms|Lessons|First Lesson|Second Lesson):\s*")
# Readings the text layer does NOT print (fabrications, and the scan's own
# corrections): each must FAIL the mode that tests its kind of value.
# (A whole-stream test proves a string exists SOMEWHERE in the text layer,
# not that it sits in the right cell -- "Hab. 1:1-2:4" is printed for a Lent
# Monday, so it cannot test St. Thomas's evening lesson. Placement is what the
# page-by-page witness pass verified. These readings are printed nowhere.)
MUST_FAIL_EXACT = ["Isa. 99:1-5", "Luke 18:10-19", "John 13:20-37",
                   "Mark 22:1-9", "Gen. 51:1-3", "I Kgs. 23:1-99"]
MUST_FAIL_COVER = MUST_FAIL_EXACT + ["24, 130, 132", "113, 116, 119",
                                     "65, 67, 104, 144", "4, 31:1-6, 91, 134",
                                     "148, 149, 150, 151", "2, 3, 4, 5, 6"]
TABLE_PIECE, TABLE_WINDOW = 6, 200


def norm(s):
    s = s.lower().replace("–", "-").replace("—", "-").replace("’", "'")
    s = re.sub(r"[il1]", "1", s)
    return re.sub(r"\s+", "", s)


class Src(str):
    """The normalized source stream (whitespace removed). `starts` holds the
    positions in it where a printed LINE or RUN begins -- the wrap-tail test
    needs to know that a short piece starts a line exactly where it is found,
    not merely somewhere in the source."""
    starts = frozenset()


def make_src(text):
    t = text.lower().replace("–", "-").replace("—", "-").replace("’", "'")
    t = re.sub(r"[il1]", "1", t)
    flat, starts = [], set()
    at_start = True
    for ch in t:
        if ch == "\n":
            at_start = True
            continue
        if ch.isspace():
            continue
        if at_start:
            starts.add(len(flat))
            at_start = False
        flat.append(ch)
    out = Src("".join(flat))
    out.starts = frozenset(starts)
    return out


def stream(which):
    raw = S.source_text(which)
    # each run on its own line too, so a tail set as its own run begins one
    runs = "\n".join(t for i in range(len(S.reader(which).pages))
                     for _y, _x, t, _s in S.runs(which, i + 1))
    return make_src(raw + "\n" + runs)


def html_stream(url):
    import scrape
    t = scrape.fetch(url)
    return make_src(H.unescape(re.sub(r"<[^>]+>", "\n", t)))


def covered(value, src, min_piece=None, window=400):
    """Exact substring, or (with `min_piece`) a LOCAL cover -- see above."""
    v = norm(value)
    if not v or v in src:
        return True
    if not min_piece:
        return False

    def extend(i, near):
        out = []
        for end in range(len(v), i, -1):
            piece = v[i:end]
            lo = 0 if near is None else max(0, near - window)
            hi = len(src) if near is None else near + window + len(piece)
            pos = src.find(piece, lo, hi)
            found = 0
            while pos >= 0 and found < (8 if end == len(v) else 1):
                out.append((end, pos))
                found += 1
                pos = src.find(piece, pos + 1, hi)
            if len(out) >= 12:
                break
        return out

    def search(i, near, depth):
        if i == len(v):
            return True
        if depth > 4:
            return False
        for end, pos in extend(i, near if near is None else near):
            short = end - i < min_piece
            # A short piece only as the LAST, and only in the two shapes a
            # genuine wrap takes: it BEGINS a printed line (or run) -- "134"
            # under Selection III -- or it completes a line-break hyphen,
            # "Matri-" / "mony". A "132" found mid-line above, or a ",134" in
            # the next column, is neither.
            if short:
                if end < len(v) or near is None:
                    continue
                # THIS occurrence must begin a line or run, within 90
                # characters after the previous piece; or the previous piece
                # must end at a line-break hyphen
                begins = pos in src.starts and 0 <= pos - near <= 90
                hyphen = src[near:near + 1] == "-"
                if not (begins or hyphen):
                    continue
            if search(end, pos + (end - i), depth + 1):   # near = piece END
                return True
        return False

    return search(0, None, 0)


def words_in(text, src):
    return all(norm(w) in src for w in re.findall(r"[A-Za-z]{2,}", text))


def cell_values(text, pairs=()):
    """-> [(kind, value, corrected)] for a cell's text."""
    out = []
    for line in text.split("\n"):
        if not line.strip() or line.startswith("# ") or line.startswith("<!--"):
            continue
        orig = line
        for tl, scan in pairs:
            if scan and scan in line:
                line = line.replace(scan, tl or "", 1)
        hit = line != orig
        if line.startswith("#"):
            out.append(("line", line.lstrip("#").strip(), hit))
        elif line.startswith("> "):
            out.append(("line", line[2:], hit))
        elif " | " in line:
            fields = line.split(" | ")
            out.append(("label", fields[0], hit))
            for f in fields[1:]:
                f = SUPPLIED_LABEL.sub("", f)
                for part in f.split(" / "):
                    if part not in ("—", ""):
                        out.append(("value", part, hit))
        else:
            out.append(("line", line, hit))
    return out


def check(name, text, src, pairs=(), skip_label=False, words=False):
    bad, n, hits = [], 0, 0
    for kind, value, hit in cell_values(text, pairs):
        if kind == "label" and skip_label:
            continue
        n += 1
        hits += hit
        if kind == "label" or words:
            ok = words_in(value, src)
        elif kind == "line":
            ok = covered(value, src, min_piece=6, window=600)
        else:
            ok = covered(value, src, TABLE_PIECE, TABLE_WINDOW)
        if not ok:
            bad.append(value)
    print("%-44s values=%4d  corrected=%3d  unattested=%d %s"
          % (name, n, hits, len(bad), bad[:4] if bad else ""))
    return len(bad)


def read(*p):
    return open(E(*p), encoding="utf-8").read()


def lessons(src):
    import w15_lessons as L
    with contextlib.redirect_stdout(io.StringIO()):
        cy, _notes = L.christian_year()
        fh = L.fixed_holy_days()
        so = L.special_occasions()
    frags, labels = [], []
    strip = lambda c: [p[2:] if p.startswith("/ ") else p for p in c]
    for r in cy:
        if "sub" in r:
            frags.append(r["sub"])
            continue
        labels += r["label"]
        frags += [r["directive"]] if r.get("directive") else []
        for c in r["cells"]:
            frags += strip(c)
    for r in fh:
        labels.append(r["label"])
        for pair in r["cells"]:
            for c in pair:
                frags += c
    for r in so:
        labels.append(r["label"])
        for c in r["cells"]:
            frags += strip(c)
    bad = [f for f in frags if not covered(f, src)]
    bad += [l for l in labels if not words_in(l, src)]
    print("%-44s fragments=%4d  labels=%3d  corrected=%3d  unattested=%d %s"
          % ("1928 tables/proper-lessons", len(frags), len(labels),
             len(W.LESSONS), len(bad), bad[:4] if bad else ""))
    return len(bad)


def main():
    cal, lec = stream("CAL"), stream("LEC")
    bad = 0
    # names word by word; letters are trivially present and the audit's
    # cycle gate checks them (a letter correction is not a substring edit)
    bad += check("1928 tables/calendar", read("1928", "tables", "calendar.md"),
                 cal, skip_label=True, words=True)
    bad += check("1928 tables/feasts-and-fasts",
                 read("1928", "tables", "feasts-and-fasts.md"), cal,
                 [(c["text_layer"], c["scan"]) for c in W.FEASTS])
    pairs = [(c["text_layer"], c["scan"]) for c in W.PSALMS]
    bad += check("1928 tables/proper-psalms",
                 read("1928", "tables", "proper-psalms.md"), lec, pairs)
    bad += check("1928 psalter/selections",
                 read("1928", "psalter", "selections.md"), lec, pairs)
    for slug in ("order-how-psalter-appointed", "order-how-rest-of-scripture"):
        # the rewritten Scripture passage spans two paragraphs of the cell,
        # so the reversal runs on the whole text before it is split
        text = read("1928", "front-matter", slug + ".md")
        for c in W.RUBRICS:
            text = text.replace(c["scan"], c["text_layer"])
        bad += check("1928 front-matter/" + slug, text, lec)
    bad += lessons(lec)
    import w14_build_rubrics as R
    src92 = html_stream(S.J + "1892/Front_Matter_1892.htm")
    for slug in ("order-how-psalter-appointed", "order-how-rest-of-scripture"):
        bad += check("1892 front-matter/" + slug,
                     read("1892", "front-matter", slug + ".md"), src92,
                     [(a, b) for a, b in R.SOURCE_NOISE])
    leaks = [v for v in MUST_FAIL_EXACT if covered(v, lec)]
    leaks += [v for v in MUST_FAIL_COVER
              if covered(v, lec, TABLE_PIECE, TABLE_WINDOW)]
    total = len(MUST_FAIL_EXACT) + len(MUST_FAIL_COVER)
    print("sensitivity: %d/%d readings absent from the text layer rejected%s"
          % (total - len(leaks), total,
             " -- LEAKED %s" % leaks if leaks else ""))
    print("\nw15 fidelity: %d unattested values" % (bad + len(leaks)))
    return 1 if bad or leaks else 0


if __name__ == "__main__":
    sys.exit(main())
