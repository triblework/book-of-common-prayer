#!/usr/bin/env python3
"""w15_src.py — the Wave-15 sources: two text-layer PDFs and one scan (1928).

Authoring-only; NOT published.

  CAL   1928/Calendar&Tables_1928.pdf  the Calendar, the Tables and Rules for
                                       the feasts and fasts, and the Easter
                                       arithmetic (6 landscape sheets).
  LEC   1928/Lectionary_1928.pdf       Concerning the Service of the Church,
                                       the psalm tables, the Selections, the
                                       three tables of lessons (9 sheets).
  SCAN  1928/BCP1929.pdf               "The original 1928 printing as PDF
                                       graphics" -- the WITNESS. Two book pages
                                       per scan page; its own OCR layer is
                                       unusable, so it is read as page images.

The two text layers are Charles Wohlers's keyed transcription ("has not been
proofread and undoubtedly will contain errors", says the justus index). They
are the machine-readable CARRIER; every emitted row is checked against the scan
of the original printing, and where the two disagree the scan wins and the
correction is logged in w15_witness.py. See ingest/WAVE15_GUIDE.md.

Why the scan and not the text layer decides: the justus index gives the
Calendar at page xlvi, but in the original printing it is page xxix -- the
transcription was paginated from a LATER printing. Its content was checked
table by table against the original and matches (Tables of Precedence
included), apart from keying errors.

Every sheet carries TWO book pages. `runs()` returns text runs with their page
coordinates, which is the structural discriminator this wave uses: a column is
an x-range and a row is a y-value, never a guess from reading order.
"""
from __future__ import annotations
import glob
import os
import re
import subprocess

CACHE = "/Users/wtrible/Developer/bcp/scrape-cache/"
J = "http://justus.anglican.org/resources/bcp/"
URL = {
    "CAL": J + "1928/Calendar&Tables_1928.pdf",
    "LEC": J + "1928/Lectionary_1928.pdf",
    "SCAN": J + "1928/BCP1929.pdf",
}
_GLOB = {
    "CAL": "justus.anglican.org_resources_bcp_1928_Calendar_Tables_1928.pdf.*.pdf",
    "LEC": "justus.anglican.org_resources_bcp_1928_Lectionary_1928.pdf.*.pdf",
    "SCAN": "justus.anglican.org_resources_bcp_1928_BCP1929.pdf.*.pdf",
}
_READERS = {}


def path(which):
    hits = glob.glob(CACHE + _GLOB[which])
    if len(hits) != 1:
        raise SystemExit("%s: expected one cached PDF, found %d -- fetch it "
                         "raw into scrape-cache first (see WAVE15_GUIDE §4)"
                         % (which, len(hits)))
    return hits[0]


def reader(which):
    import pypdf
    if which not in _READERS:
        _READERS[which] = pypdf.PdfReader(path(which))
    return _READERS[which]


def runs(which, page):
    """-> [(y, x, text, size)] for sheet `page` (1-based), top to bottom."""
    out = []

    def visit(text, cm, tm, _fd, size):
        if text.strip():
            x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
            y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
            out.append((round(y, 1), round(x, 1), text, size))

    reader(which).pages[page - 1].extract_text(visitor_text=visit)
    return sorted(out, key=lambda r: (-r[0], r[1]))


def plain(which, page):
    return reader(which).pages[page - 1].extract_text() or ""


def layout(which, page):
    return reader(which).pages[page - 1].extract_text(
        extraction_mode="layout") or ""


def source_text(which):
    """Every extraction of the whole PDF joined -- the fidelity gate's corpus."""
    r = reader(which)
    parts = []
    for i in range(len(r.pages)):
        parts.append(plain(which, i + 1))
        parts.append(layout(which, i + 1))
        parts.append(" ".join(t for _y, _x, t, _s in runs(which, i + 1)))
    return "\n".join(parts)


# --------------------------------------------------------------------------
# The scan: page images for the witness pass
# --------------------------------------------------------------------------
SCRATCH = os.environ.get("W15_SCRATCH", "/tmp/w15scan")


def scan_png(page):
    """Scan page (1-based) -> PNG path (the page image is JPEG 2000; macOS
    `sips` converts it, so no imaging library is needed)."""
    os.makedirs(SCRATCH, exist_ok=True)
    png = os.path.join(SCRATCH, "s%03d.png" % page)
    if os.path.exists(png):
        return png
    pg = reader("SCAN").pages[page - 1]
    xo = pg["/Resources"]["/XObject"]
    imgs = [v.get_object() for v in xo.values()
            if v.get_object().get("/Subtype") == "/Image"]
    if len(imgs) != 1:
        raise SystemExit("scan page %d: %d images" % (page, len(imgs)))
    jp2 = png[:-4] + ".jp2"
    with open(jp2, "wb") as fh:
        fh.write(imgs[0]._data)
    subprocess.run(["sips", "-s", "format", "png", jp2, "--out", png],
                   check=True, capture_output=True)
    return png


def scan_crop(page, top, left, height, width, scale=2, tag=""):
    """Crop a region of a scan page (pixels) and enlarge it for reading."""
    src = scan_png(page)
    out = os.path.join(SCRATCH, "c%03d_%d_%d_%d_%d%s.png"
                       % (page, top, left, height, width, tag))
    subprocess.run(["sips", "-c", str(height), str(width), "--cropOffset",
                    str(top), str(left), src, "--out", out],
                   check=True, capture_output=True)
    if scale != 1:
        subprocess.run(["sips", "-z", str(height * scale), str(width * scale),
                        out, "--out", out], check=True, capture_output=True)
    return out


def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


# Small capitals are typography: the page sets "First Sunday in Advent" with
# large capitals F, S, A and the rest in small capitals, and the text layer
# keys it all upper-case. Row LABELS are rendered back to that capitalization;
# headings and prose keep the text layer's letters.
_LOWER = {"and", "of", "the", "in", "after", "before", "next", "or", "for",
          "a", "an", "to", "on", "by", "at", "all"}   # "Saint Michael and all
                                                        # Angels" (scan p. viii)


def smallcaps_title(s):
    words = s.split(" ")
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        core = re.sub(r"[^a-z]", "", lw)
        if i > 0 and core in _LOWER:
            out.append(lw)
        else:
            # "TWENTY-FIRST" -> "Twenty-first"; "SAINTS’" -> "Saints’"
            out.append(lw[:1].upper() + lw[1:])
    return " ".join(out)


def psalm_list(s):
    """Typographic normalization of a printed psalm list, counted by callers:
    one space after each comma or semicolon ("1,15,146" -> "1, 15, 146"),
    en dash to hyphen inside a verse range, space after a colon removed
    ("89: 1-30" -> "89:1-30"). Digits are never changed."""
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\s*([,;])\s*", r"\1 ", s)
    s = re.sub(r"(\d)\s*:\s*(\d)", r"\1:\2", s)
    s = re.sub(r"(\d)\s*-\s*(\d)", r"\1-\2", s)
    return norm_ws(s).rstrip(".,; ")


# --------------------------------------------------------------------------
# De-kerning. The Corel PDF engine turns kerning offsets into spaces, so the
# text layer reads "Ash W ednesd ay", "Rogati on Sun day", "Evang elist". The
# repair below ONLY REMOVES SPACES -- it never changes, adds or drops a letter
# -- and it merges fragments only when
#   (a) the joined form is an attested word, and
#   (b) some fragment is not a word by itself, OR the 1928/1892 corpus uses
#       the joined form and never the spaced pair ("Sunday" vs "Sun day").
# The corpus is the clean justus HTML transcriptions of the 1928 and 1892
# books plus the authored 1789/1892/1928 cells; the dictionary is the system
# word list. Every row this feeds is then checked against the scan, so a
# wrong merge is caught there -- this only reduces the number of corrections.
# --------------------------------------------------------------------------
_VOCAB = {}


def _corpus():
    if "words" in _VOCAB:
        return _VOCAB
    import html as H
    texts = []
    for f in glob.glob(CACHE + "justus.anglican.org_resources_bcp_19[2]8_*.html") \
            + glob.glob(CACHE + "justus.anglican.org_resources_bcp_1892_*.html"):
        if ".pdf." in f:
            continue
        t = open(f, encoding="utf-8", errors="replace").read()
        texts.append(H.unescape(re.sub(r"<[^>]+>", " ", t)))
    wt = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for ed in ("1789", "1892", "1928"):
        for f in glob.glob(os.path.join(wt, "editions", ed, "**", "*.md"),
                           recursive=True):
            if "/tables/" in f:
                continue              # never learn from this wave's own output
            texts.append(open(f, encoding="utf-8").read())
    words = re.findall(r"[A-Za-z]+", "\n".join(texts))
    low = [w.lower() for w in words]
    from collections import Counter
    _VOCAB["words"] = Counter(low)
    _VOCAB["pairs"] = Counter(zip(low, low[1:]))
    try:
        with open("/usr/share/dict/words", encoding="utf-8") as fh:
            _VOCAB["dict"] = {w.strip().lower() for w in fh}
    except OSError:
        _VOCAB["dict"] = set()
    return _VOCAB


def _core(tok):
    return re.sub(r"[^A-Za-z]", "", tok).lower()


def _is_word(w, V):
    return bool(w) and (V["words"][w] > 0 or w in V["dict"]) and (
        len(w) > 1 or w in ("a", "i", "o"))


def _word_cost(w, V):
    """-log P(w) under the corpus unigram model; a dictionary-only word gets a
    small pseudo-count; anything else is a fragment and costs a lot."""
    import math
    if not w:
        return 0.0
    if len(w) == 1 and w not in ("a", "i", "o"):
        return 25.0
    n = V.setdefault("N", sum(V["words"].values()))
    c = V["words"][w] + (0.2 if w in V["dict"] else 0.0)
    return -math.log(c / n) if c > 0 else 25.0


def _group_cost(parts, V):
    """Cost of emitting `parts` joined as one token (None = not allowed)."""
    joined = _core("".join(parts))
    if len(parts) == 1:
        return _word_cost(joined, V)
    # no merging across punctuation inside the run ("Day; and", "Paul All")
    if any(re.search(r"[^A-Za-z’'-]$", p) for p in parts[:-1]):
        return None
    if any(re.match(r"[^A-Za-z]", p) for p in parts[1:]):
        return None
    cost = _word_cost(joined, V)
    if cost >= 25.0:
        return None
    cores = [_core(p) for p in parts]
    # two (or more) real words the corpus prints SPACED stay apart ("Holy
    # Day", "every day", "a way"). Relative, because the corpus has its own
    # stray splits ("a nd" 9 times against "and" 20,000): the spaced pair
    # must occur at least 1/50 as often as the joined word to veto.
    # Two REAL words merge only when the joined word is common (>= 50) and
    # at least 100 times more frequent than the spaced pair: "Sun day" ->
    # "Sunday" (891 : 1), never "a way" -> "away".
    joined_n = V["words"][joined]
    if all(V["words"][c] > 0 and len(c) > 1 or c in ("a", "i", "o")
           for c in cores):
        pair_n = max(V["pairs"][(a, b)] for a, b in zip(cores, cores[1:]))
        if joined_n < 50 or pair_n * 100 > joined_n:
            return None
        # ...and only in the shape kerning produces: a capitalized first part
        # continued in lower case ("Sun day"), or an all-caps run ("SUN DAY").
        # "a way", "in to" and "Holy Day" are not that shape.
        letters = [re.sub(r"[^A-Za-z]", "", p) for p in parts]
        caps_run = all(l.isupper() for l in letters)
        cap_then_lower = letters[0][:1].isupper() and all(
            l.islower() for l in letters[1:])
        if not (caps_run or cap_then_lower):
            return None
    return cost


def dekern(s):
    """Minimum-cost regrouping of space-separated fragments (see above)."""
    V = _corpus()
    toks = [t for t in s.split(" ") if t]
    n = len(toks)
    best = [0.0] + [None] * n
    back = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - 5), j):
            if best[i] is None:
                continue
            c = _group_cost(toks[i:j], V)
            if c is None:
                continue
            if best[j] is None or best[i] + c < best[j] - 1e-9:
                best[j], back[j] = best[i] + c, i
    out, j = [], n
    while j > 0:
        i = back[j]
        out.append("".join(toks[i:j]))
        j = i
    s = " ".join(reversed(out))
    s = re.sub(r"\s+([,.;:)])", r"\1", s)
    return re.sub(r"\(\s+", "(", s)
