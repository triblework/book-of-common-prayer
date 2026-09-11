#!/usr/bin/env python3
"""w13_1892_repair.py — recover correct word spacing from the 1892 Psalter PDF.

Authoring-only; NOT published.

THE PROBLEM. justus 1892/Psalms.pdf is a WordPerfect PDF with a text layer, and
pypdf's two extraction modes fail in OPPOSITE directions (measured):

  plain   every letter in READING ORDER, but kerning inserts spurious spaces
          inside words -- 12% of tokens are single-letter fragments:
          "BLES SED is the man that hath not wal ked ... of t he ungodly"
  layout  spacing mostly right ("thecounsel" aside) and zero fragments, but it
          DISPLACES drop capitals: Psalm 2 opens "HY do the heathen", its W
          emitted elsewhere -- a letter-level corruption.

THE RULE. Letters come ONLY from plain mode. Whitespace is decided per space:

  1. a space BOTH modes agree on is KEPT (two independent extractions);
  2. a space only plain has is a CANDIDATE. Within one layout token, the
     candidates are resolved by segmenting it into the fewest pieces that are
     all known words; if the token is itself a known word, no candidate splits.
  3. a token no segmentation resolves is kept as layout printed it and
     REPORTED -- never guessed.

The known-word list is the vocabulary of the 1662 and 1928 psalters. It is used
ONLY to arbitrate whitespace the two 1892 extractions disagree about; it can
never change, add or remove a letter. Every decision it makes is counted.
"""
import difflib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = ("/Users/wtrible/Developer/bcp/scrape-cache/"
       "justus.anglican.org_resources_bcp_1892_Psalms.pdf.ad4ccb6260dc8edf.pdf")

STATS = {"kept_agreed": 0, "candidates": 0, "candidate_kept": 0,
         "candidate_joined": 0, "unresolved_tokens": 0}
UNRESOLVED = []
PAGE_AGREE = []


def vocabulary():
    sys.path.insert(0, HERE)
    import w13_1662
    import w13_1928
    import w13_1979
    v = set()
    # Latin incipits: 1662 writes the ligature (Adh\u00e6sit), 1892 writes "ae"
    # (Adhaesit), so 1979's ASCII-keyed incipits are added -- incipits ONLY;
    # 1979's modern English verse text never enters the word list.
    for p in w13_1979.parse().values():
        for t in [p.get("incipit") or ""] + [" ".join(v2[2]) for v2 in p["verses"] if v2[2]]:
            v.update(w.lower() for w in re.findall(r"[A-Za-z]+", t))
    for ps in (w13_1662.parse(), w13_1928.parse()):
        for p in ps.values():
            for _n, t, _s in p["verses"]:
                v.update(w.lower() for w in re.findall(r"[A-Za-z]+", t))
            if p.get("incipit"):
                v.update(w.lower() for w in re.findall(r"[A-Za-z]+", p["incipit"]))
    return v


def _letters_and_bounds(text):
    """-> (letters-without-whitespace, set of indices preceded by whitespace)."""
    out, bounds, ws = [], set(), False
    for ch in text:
        if ch.isspace():
            ws = True
            continue
        if ws and out:
            bounds.add(len(out))
        ws = False
        out.append(ch)
    return "".join(out), bounds


SOFT = "\u00ac"   # marks a hyphen that ended a printed line


def _key(s):
    return re.sub(r"[^A-Za-z]", "", s.replace(SOFT, "")).lower()


def soften(text):
    """Mark every line-end hyphen ("com-" / "manded") with a sentinel that is
    NOT whitespace, so it survives into the letter string of BOTH extractions
    and the segmenter can judge the word across the break."""
    return re.sub(r"-[ \t]*\n[ \t]*", SOFT, text)


def _is_word(piece, vocab):
    """A piece is a word if every part between hyphens/apostrophes is a known
    word ("loving-kindnesses", "man's"); the vocabulary stores compounds'
    parts separately, so testing the whole compound always failed."""
    if SOFT in piece:
        # joined across the line break ("com" + "manded") OR a true compound
        # broken at the line end ("loving" + "kindness")
        return (_key(piece) in vocab or
                all(_is_word(x, vocab) for x in piece.split(SOFT)))
    parts = [p for p in re.split(r"[-'\u2019]", piece) if _key(p)]
    if not parts:
        return True
    ok = []
    for i, p in enumerate(parts):
        k = _key(p)
        ok.append(k in vocab or (i > 0 and k == "s"))
    return all(ok)


def repair_page(plain, layout, vocab):
    sp, bp = _letters_and_bounds(plain)
    sl, bl = _letters_and_bounds(layout)
    # map layout letter indices onto plain letter indices through equal blocks
    lmap = {}
    for a, b, size in difflib.SequenceMatcher(None, sp, sl,
                                              autojunk=False).get_matching_blocks():
        for k in range(size):
            lmap[b + k] = a + k
    agreed = {lmap[b] for b in bl if b in lmap} & bp
    PAGE_AGREE.append((len(agreed), len(bp), len(lmap), len(sp), len(sl)))
    candidates = bp - agreed
    STATS["kept_agreed"] += len(agreed)
    STATS["candidates"] += len(candidates)

    # Segment the plain letters at AGREED boundaries (and at line structure,
    # which plain mode carries as newlines -- kept as newlines).
    keep = set(agreed)
    cuts = sorted(agreed | {0, len(sp)})
    for lo, hi in zip(cuts, cuts[1:]):
        inner = sorted(c for c in candidates if lo < c < hi)
        if not inner:
            continue
        token = sp[lo:hi]
        if _is_word(token, vocab):
            STATS["candidate_joined"] += len(inner)
            continue
        # Word-break by dynamic programming over the candidate points: the
        # fewest pieces that are all known words. (An exhaustive subset search
        # was exponential in the number of candidates and never finished.)
        pts = [lo] + inner + [hi]
        INF = 10 ** 9
        cost = {lo: 0}
        back = {}
        for j in pts[1:]:
            best_c, best_i = INF, None
            for i in pts:
                if i >= j or i not in cost:
                    continue
                if _is_word(sp[i:j], vocab) and cost[i] + 1 < best_c:
                    best_c, best_i = cost[i] + 1, i
            if best_i is not None:
                cost[j], back[j] = best_c, best_i
        best = None
        if hi in cost:
            chosen, j = [], hi
            while j != lo:
                j = back[j]
                if j != lo:
                    chosen.append(j)
            best = tuple(sorted(chosen))
        if best is None:
            # SAFE FALLBACK: keep plain mode's spacing. Plain mode carries every
            # real boundary (plus spurious ones), so keeping it can only leave a
            # visible, reportable fragment; JOINING -- the first version's
            # fallback -- deleted real boundaries and collapsed whole pages
            # into one unspaced run. Never destroy evidence to hide a failure.
            STATS["unresolved_tokens"] += 1
            UNRESOLVED.append(token)
            keep.update(inner)
            STATS["candidate_kept"] += len(inner)
            continue
        keep.update(best)
        STATS["candidate_kept"] += len(best)
        STATS["candidate_joined"] += len(inner) - len(best)

    # Rebuild: plain's letters, whitespace only where kept. Newlines in plain
    # mode are preserved as line breaks at kept boundaries.
    nl = set()
    out_i = 0
    for ch in plain:
        if ch == "\n":
            nl.add(out_i)
        elif not ch.isspace():
            out_i += 1
    res = []
    for i, ch in enumerate(sp):
        if i in keep:
            res.append("\n" if i in nl else " ")
        res.append(ch)
    return "".join(res)


def reading_order(layout):
    """Re-order a layout-mode page into READING order.

    The 1892 Psalter is printed in TWO COLUMNS. Layout mode reads straight
    across each physical row, so every line holds the left column's line AND
    the right column's line; plain mode reads the left column top to bottom and
    then the right. Aligned as-is, the two modes agreed on only ~55% of letters,
    and the unaligned half left whole pages without an agreed word boundary.

    The column boundary is STRUCTURAL: justification gaps inside a column are 2-3
    spaces, while the right column always starts at a fixed offset (measured:
    84-91 on every page). The page's gutter is the smallest offset at which a
    right-column segment begins; each line is split there.
    """
    lines = layout.split("\n")
    starts = []
    for l in lines:
        for m in re.finditer(r"(?<=\S)( {6,})(?=\S)", l):
            if m.end() >= 70:
                starts.append(m.end())
    if not starts:
        return layout
    gutter = min(starts)
    left, right = [], []
    for l in lines:
        a, b = l[:gutter].rstrip(), l[gutter:].strip()
        if a.strip():
            left.append(a)
        if b:
            right.append(b)
    return "\n".join(left + right)


FIXES = {"line_hyphen_joined": 0, "line_hyphen_kept": 0, "dropcap_joined": 0}
LINE_HYPHEN_UNRESOLVED = []


def post_pass(text, vocab):
    """Two typographic repairs on the rebuilt page, each counted.

    LINE-END HYPHENATION. A word broken across a line ("com-" / "fort") is
    rejoined without its hyphen ONLY when the joined form is a known word. A
    true compound broken at a line end ("loving-" / "kindness") keeps its hyphen.
    Otherwise the break is left as printed and reported. Removing a line-break
    hyphen is typography, like the terminal-period rule, not a change of reading.

    DROP CAPITALS. A lone capital letter separated from a capitalised fragment
    ("W HY") is joined when the result is a word and the fragment alone is not.
    "O LORD" and "I WILL" are untouched: in each the fragment is itself a word.
    """
    def hyph(m):
        a, b = m.group(1), m.group(2)
        if _is_word(a + b, vocab) and _key(a + b):
            FIXES["line_hyphen_joined"] += 1
            return a + b
        if _is_word(a, vocab) and _is_word(b, vocab):
            FIXES["line_hyphen_kept"] += 1
            return a + "-" + b
        LINE_HYPHEN_UNRESOLVED.append(a + "-" + b)
        return a + "-\n" + b
    # (line-end hyphens are sentinels by this point -- see soften/resolve_soft)

    def cap(m):
        a, b = m.group(1), m.group(2)
        if _is_word(a + b, vocab) and not _is_word(b, vocab):
            FIXES["dropcap_joined"] += 1
            return a + b
        return m.group(0)
    return re.sub(r"(?<![A-Za-z])([A-Z])\s+([A-Z]{1,}(?:[a-z]*)?)(?![A-Za-z])", cap, text)


INTERNAL = {"hyphen": {}, "joined": {}}
HYPHEN_BY_USAGE = []


def learn_usage(pages):
    """Count how 1892 ITSELF writes each compound in the middle of a line --
    "loving-kindness" or "lovingkindness". A line-break hyphen is then decided
    by the document's own usage BEFORE the reference vocabulary is consulted.
    Consulting the vocabulary first pulled 1892 toward 1928: it joined
    "loving-" / "kindness" into "lovingkindness", a form that is in the word
    list only because 1928 prints it, while 1892 prints "loving-kindness"."""
    body = SOFT.join(pages)
    for m in re.finditer(r"(?<![A-Za-z%s])([A-Za-z]+)-([A-Za-z]+)(?![A-Za-z])" % SOFT, body):
        k = (m.group(1).lower() + m.group(2).lower())
        INTERNAL["hyphen"][k] = INTERNAL["hyphen"].get(k, 0) + 1
    for w in re.findall(r"[A-Za-z]+", re.sub(SOFT + r"[A-Za-z]*|[A-Za-z]*" + SOFT, " ", body)):
        k = w.lower()
        INTERNAL["joined"][k] = INTERNAL["joined"].get(k, 0) + 1


def usage(a, b):
    """-> '-' if 1892 writes a-b mid-line, '' if it writes ab, None if never."""
    k = (a + b).lower()
    h, j = INTERNAL["hyphen"].get(k, 0), INTERNAL["joined"].get(k, 0)
    if h > j:
        return "-"
    if j > h:
        return ""
    return None


def resolve_soft(text, vocab):
    """Settle each marked line-end hyphen: drop it when the joined word is known
    ("com" + "manded" -> "commanded"), keep it as a hyphen when both halves are
    words ("loving" + "kindness"), otherwise leave "-" and report."""
    def one(m):
        a, b = m.group(1), m.group(2)
        u = usage(a, b)
        if u is not None:
            HYPHEN_BY_USAGE.append(a + u + b)
            FIXES["line_hyphen_joined" if u == "" else "line_hyphen_kept"] += 1
            return a + u + b
        if _key(a + b) in vocab:
            FIXES["line_hyphen_joined"] += 1
            return a + b
        if _is_word(a, vocab) and _is_word(b, vocab):
            FIXES["line_hyphen_kept"] += 1
            return a + "-" + b
        LINE_HYPHEN_UNRESOLVED.append(a + "-" + b)
        return a + "-" + b
    return re.sub(r"([A-Za-z]*)%s([A-Za-z]*)" % SOFT, one, text)


FRAG_JOINS = []


def _standalone_word(tok, vocab):
    """Is this token a word ON ITS OWN? Lower-case 'i' is not (the pronoun is
    always 'I'); otherwise defer to the vocabulary."""
    # A single letter other than "a", "I" or "O" is never a word on its own.
    # (The vocabulary does contain a bare "s" -- the tail of "man's" split at
    # the apostrophe -- so without this, "ha s" was not recognised as a
    # fragment pair.)
    if len(tok) == 1 and tok not in ("a", "A", "I", "O"):
        return False
    return _is_word(tok, vocab) and bool(_key(tok))


def join_fragments(text, vocab):
    """Some spurious spaces are present in BOTH extractions ("punish m e",
    "t he", "puttet h", "G od"), so rule 1 kept them. Join two adjacent tokens
    only when the joined form is a known word AND at least one side is not a
    word by itself -- which leaves genuine pairs ("O LORD", "a man", "to day")
    alone. Every join is recorded for review."""
    # Token-by-token, not re.sub: a substitution CONSUMES its right-hand token,
    # so in "punish m e" it tested "punish|m", ate the "m", and never tested
    # "m|e". Here each token is compared with the (possibly already merged)
    # token before it.
    parts = re.split(r"([ \n]+)", text)
    out = []
    for piece in parts:
        if not out or piece == "" or re.fullmatch(r"[ \n]+", piece):
            out.append(piece)
            continue
        if len(out) >= 2 and re.fullmatch(r"[ \n]+", out[-1]):
            a, b = out[-2], piece
            wa = re.fullmatch(r"[A-Za-z'\u2019]+", a)
            wb = re.fullmatch(r"[A-Za-z'\u2019]+[^A-Za-z]*", b)
            if wa and wb:
                core_b = re.match(r"[A-Za-z'\u2019]+", b).group(0)
                if (_is_word(a + core_b, vocab) and _key(a + core_b)
                        and not (_standalone_word(a, vocab)
                                 and _standalone_word(core_b, vocab))):
                    FRAG_JOINS.append(a + "|" + core_b)
                    out.pop()
                    out[-1] = a + b
                    continue
        out.append(piece)
    return "".join(out)


def repaired_pages():
    import pypdf
    vocab = vocabulary()
    r = pypdf.PdfReader(PDF)
    learn_usage([soften(pg.extract_text() or "") for pg in r.pages[1:]])
    pages = []
    for pg in r.pages:
        plain = soften(pg.extract_text() or "")
        layout = soften(reading_order(pg.extract_text(extraction_mode="layout") or ""))
        pages.append(resolve_soft(repair_page(plain, layout, vocab), vocab))
    return pages


PAGE_HYPHENS = []


def full_text(pages=None):
    """Join the pages FIRST, then run the passes that look across a boundary.

    Run page by page, they never saw a word broken over a PAGE break
    ("congrega" | "tion", "und ersta" | "nding") or a hyphen ending a page's
    last line ("inheri-" | "tance"). Page 0 is the redistribution notice and is
    dropped."""
    pages = pages if pages is not None else repaired_pages()
    vocab = vocabulary()
    text = "\n".join(pages[1:])

    def page_hyphen(m):
        a, b = m.group(1), m.group(2)
        u = usage(a, b)
        if u is not None:
            HYPHEN_BY_USAGE.append(a + u + b)
            PAGE_HYPHENS.append(a + u + b)
            return a + u + b
        if _key(a + b) in vocab:
            PAGE_HYPHENS.append(a + b)
            return a + b
        if _is_word(a, vocab) and _is_word(b, vocab):
            PAGE_HYPHENS.append(a + "-" + b)
            return a + "-" + b
        return m.group(0)
    text = re.sub(r"([A-Za-z]+)-\n([a-z]+)", page_hyphen, text)
    return join_fragments(post_pass(text, vocab), vocab)


if __name__ == "__main__":
    pages = repaired_pages()
    txt = "\n".join(pages[1:])
    words = re.findall(r"[A-Za-z]+", txt)
    frag = sum(1 for w in words if len(w) == 1 and w.lower() not in ("a", "i", "o"))
    print(STATS)
    print("after repair: %d words, %d single-letter fragments (%.2f%%)"
          % (len(words), frag, 100.0 * frag / max(1, len(words))))
    print(FIXES, "line-hyphen unresolved:", LINE_HYPHEN_UNRESOLVED[:12])
    print("fragment joins: %d; sample %s" % (len(FRAG_JOINS), FRAG_JOINS[:40]))
    body_unres = [u for u in UNRESOLVED if "redistribute" not in u]
    print("unresolved tokens outside the PDF header (%d): %s" % (len(body_unres), body_unres[:30]))
    low = [(i, a, b, m, ls, ll) for i, (a, b, m, ls, ll) in enumerate(PAGE_AGREE) if b and a / b < 0.5]
    print("pages where under half the plain spaces are agreed: %d" % len(low))
    for i, a, b, m, ls, ll in low[:8]:
        print("   page %2d: agreed %d/%d spaces; mapped %d of %d letters (layout %d)" % (i, a, b, m, ls, ll))
    i = txt.find("BLESSED")
    print("\nsample:", re.sub(r"\s+", " ", txt[i:i + 300]))
