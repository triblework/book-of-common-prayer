#!/usr/bin/env python3
"""w13_1892.py — parse the 1892 Psalter from its own PDF (Wave 13).

Authoring-only; NOT published. PARSES ONLY; w13_render.py writes the cells.

Input is the whitespace-repaired text from w13_1892_repair.py (letters from the
PDF's plain extraction, never altered). Structure, from the page itself:

  PSALM N. <Latin incipit>     a psalm. The text layer also prints "Psalm N."
                               and once "PSALm 57 ." -- matched case-insensitively
                               with an optional space before the period.
  THE FIRST DAY. / Morning Prayer. / Evening Prayer.      course headings, skipped
  BLESSED is the man ...       verse 1: unnumbered, opening in capitals
  2. But his delight ...       numbered verses, "N."
  Retribue servo tuo.          a Psalm-119 portion: a Latin line on its own,
                               followed by a verse opening in capitals
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PSALM = re.compile(r"^psalm\s+(\d+)\s*\.\s*(.*)$", re.I)
VERSE = re.compile(r"^(\d{1,3})\.\s+(.*)$")
SKIP = re.compile(r"(?i)^(the psalter|p\s*sal\s*m\s*s of david|psalms of david|"
                  r"the [a-z-]+ day\.?|morning prayer\.?|evening prayer\.?)$")
OPENS = re.compile(r"^[A-Z]{2,}\b|^[AO] [A-Z]{2,}\b|^I [A-Z]{2,}\b")

CAPS_SPLITS = []
DROPPED = []


def cur_no(psalms, cur):
    return next((k for k, v in psalms.items() if v is cur), None)


def repaired_text():
    import w13_1892_repair as R
    return R.full_text(), R             # page 0 (the redistribution notice) is dropped


def tidy(text, vocab, R):
    """Two typographic repairs, each counted, neither touching a letter.
    (1) A drop-capital run fused to the next word: "BE MERCIFULunto" ->
        "MERCIFUL unto", only when both parts are words.
    (2) The mediant colon written without its following space (":and")."""
    def caps(m):
        a, b = m.group(1), m.group(2)
        if R._is_word(a, vocab) and R._is_word(b, vocab):
            CAPS_SPLITS.append(a + "|" + b)
            return a + " " + b
        return m.group(0)
    text = re.sub(r"\b([A-Z]{2,})([a-z]{2,})\b", caps, text)
    return re.sub(r"[ \t]*:[ \t]*(?=\S)", " : ", text)


ONLINE_SPLITS = []


def split_embedded(cur, no):
    """Split the LAST verse wherever it carries the next verse's printed number
    ("...commandments.88. O quicken"), and do it AS LINES ARRIVE, so the verse
    count is right when a Psalm-119 portion incipit follows. Done only after
    parsing, the split came too late: the parser still believed it was in verse
    87 when the Lamed incipit arrived, so the 8k portion rule could not fire.
    Returns the (possibly new) last verse."""
    while cur["verses"]:
        num, text, sub = cur["verses"][-1]
        m = re.search(r"(?:^|[\s.;:,!?])%d\.\s*(?=[A-Z])" % (num + 1), text)
        if not m or m.start() == 0:
            break
        cut = m.start() + (0 if text[m.start()].isdigit() else 1)
        cur["verses"][-1] = [num, text[:cut].strip(), sub]
        cur["verses"].append([num + 1, text[m.end():].strip(), None])
        ONLINE_SPLITS.append((no, num + 1))
    return cur["verses"][-1] if cur["verses"] else None


def parse():
    text, R = repaired_text()
    vocab = R.vocabulary()
    text = tidy(text, vocab, R)
    lines = [l.strip() for l in text.split("\n")]
    psalms, cur, verse, pending = {}, None, None, None
    for i, line in enumerate(lines):
        if not line or SKIP.match(line):
            continue
        m = PSALM.match(line)
        if m:
            n = int(m.group(1))
            cur = psalms[n] = {"incipit": m.group(2).strip() or None, "verses": []}
            verse, pending = None, None
            continue
        if cur is None:
            continue
        m = VERSE.match(line)
        if m and (not cur["verses"] or int(m.group(1)) > cur["verses"][-1][0]):
            verse = [int(m.group(1)), m.group(2), pending]
            cur["verses"].append(verse)
            pending = None
            verse = split_embedded(cur, cur_no(psalms, cur))
            continue
        # PSALM 119 is an acrostic: twenty-two portions of EIGHT verses, so every
        # portion opens at verse 8k+1 -- a structural fact, true in every
        # edition. Once verse 8k is complete, the next un-numbered short line is
        # the portion's Latin incipit and the line after it is verse 8k+1. (The
        # first version keyed on the opening word being in capitals and missed
        # verse 97, which this text layer prints "Lord," not "LORD,".)
        if cur is psalms.get(119) and cur["verses"] and pending is None:
            last = cur["verses"][-1][0]
            # verse 8k must be COMPLETE -- carrying its mediant and ending in
            # . ! or ? -- or a short continuation line ("commandment is
            # exceeding broad.") is mistaken for the next portion's incipit.
            done = (" : " in verse[1] if verse else False) and \
                re.search(r"[.!?][\"')\]]*$", verse[1].strip()) if verse else False
            if (last % 8 == 0 and verse is not None and verse[0] == last
                    and done and len(line) < 40 and not VERSE.match(line)):
                pending = line
                verse = None
                continue
        # After a portion incipit the next line IS the portion's opening verse,
        # whatever its case; the first version required capitals and so fell
        # through to a branch that discarded the line.
        if not cur["verses"] or (verse is None and (OPENS.match(line) or pending)):
            num = 1 if not cur["verses"] else cur["verses"][-1][0] + 1
            verse = [num, line, pending]
            cur["verses"].append(verse)
            pending = None
            verse = split_embedded(cur, cur_no(psalms, cur))
            continue
        if verse is not None:
            verse[1] += " " + line
            verse = split_embedded(cur, cur_no(psalms, cur))
        else:
            # NEVER discard silently: a line the parser cannot place is recorded
            # and the build refuses to proceed while any exist.
            DROPPED.append((cur_no(psalms, cur), line[:60]))
    for n, p in psalms.items():
        p["verses"] = repair_gaps(n, [(v[0], re.sub(r"\s+", " ", v[1]).strip(), v[2])
                                      for v in p["verses"]])
    split_fused(psalms, vocab, R)
    join_runs(psalms, vocab, R)
    return psalms


RUN_JOINS = []


def join_runs(psalms, vocab, R):
    """Last whitespace pass, on verse text only (never the Latin incipits).

    (a) A hyphen surviving MID-LINE from a reflowed line break ("inheri-tance")
        is removed when the joined form is a word and the halves are not both
        words.
    (b) A run of consecutive NON-WORD fragments ("und ersta nding",
        "noo nday", "li ked") is joined when the result is a known word, OR
        matches a word in the same verse of 1662 ignoring hyphens ("noon-day"),
        OR every fragment has the kerning signature (five letters or fewer).
    Only whitespace and line-break hyphens change; the letters are the PDF's.
    Every join is recorded."""
    import w13_1662
    ref = w13_1662.parse()
    for n, p in psalms.items():
        for i, (num, text, sub) in enumerate(p["verses"]):
            rv = [x for x in ref.get(n, {"verses": []})["verses"] if x[0] == num]
            rkeys = {R._key(w) for w in re.findall(r"[A-Za-z'-]+", rv[0][1])} if rv else set()

            def hy(m):
                a, b = m.group(1), m.group(2)
                if R._is_word(a + b, vocab) and not (R._is_word(a, vocab) and R._is_word(b, vocab)):
                    RUN_JOINS.append((n, num, a + "-" + b))
                    return a + b
                return m.group(0)
            t = re.sub(r"\b([A-Za-z]+)-([A-Za-z]+)\b", hy, text)

            toks = re.split(r"( +)", t)
            out, run = [], []

            def flush():
                if len(run) > 1:
                    joined = "".join(run)
                    core = R._key(joined)
                    if (R._is_word(joined, vocab) or core in rkeys
                            or all(len(R._key(x)) <= 5 for x in run)):
                        RUN_JOINS.append((n, num, " ".join(run)))
                        out.append(joined)
                        return
                    out.append(" ".join(run))
                elif run:
                    out.append(run[0])
            for tok in toks:
                if tok.strip() == "":
                    continue
                bare = re.fullmatch(r"[A-Za-z]+", tok)
                if bare and not R._standalone_word(tok, vocab):
                    run.append(tok)
                    continue
                # a fragment may carry trailing punctuation ("nding,")
                mm = re.fullmatch(r"([A-Za-z]+)([^A-Za-z]+)", tok)
                if mm and run and not R._standalone_word(mm.group(1), vocab):
                    run.append(tok)
                    flush()
                    run = []
                    continue
                flush()
                run = []
                out.append(tok)
            flush()
            new = " ".join(out)
            if new != text:
                p["verses"][i] = (num, new, sub)


FUSED = []


def split_fused(psalms, vocab, R):
    """A word boundary that NEITHER extraction carries -- typically a drop-
    capital run fused to what follows ("ICRIED", "THELORD", "LORDGod"). Ruling B
    allows 1662 to decide WHITESPACE (never a letter), and this is its narrowest
    use: a space is inserted only if the token splits into two known words AND
    the SAME VERSE in 1662 prints those two words adjacent. Every insertion is
    recorded; anything else is left exactly as printed."""
    import w13_1662
    ref = w13_1662.parse()
    for n, p in psalms.items():
        for i, (num, text, sub) in enumerate(p["verses"]):
            rv = [x for x in ref.get(n, {"verses": []})["verses"] if x[0] == num]
            if not rv:
                continue
            rwords = [w.lower() for w in re.findall(r"[A-Za-z]+", rv[0][1])]
            pairs = set(zip(rwords, rwords[1:]))

            def one(m):
                tok = m.group(0)
                if R._is_word(tok, vocab):
                    return tok
                for k in range(1, len(tok)):
                    a, b = tok[:k], tok[k:]
                    if (a.lower(), b.lower()) in pairs:
                        FUSED.append((n, num, tok, a + " " + b))
                        return a + " " + b
                return tok
            new = re.sub(r"[A-Za-z]+", one, text)
            if new != text:
                p["verses"][i] = (num, new, sub)


GAP_REPAIRS, GAP_UNREPAIRED = [], []


def repair_gaps(no, verses):
    """As for 1928: a missing verse N+1 is looked for INSIDE verse N -- the
    printed number "N+1." standing alone before a capital letter. Split there;
    otherwise report. Nothing is inferred."""
    out = []
    for num, text, sub in verses:
        while out and num > out[-1][0] + 1:
            want = out[-1][0] + 1
            pn, pt, ps = out[-1]
            m = re.search(r"(?:^|[\s.;:,!?])%d\.\s*(?=[A-Z])" % want, pt)
            if not m or m.start() == 0:
                GAP_UNREPAIRED.append((no, want))
                break
            cut = m.start() + (0 if pt[m.start()].isdigit() else 1)
            out[-1] = (pn, pt[:cut].strip(), ps)
            out.append((want, pt[m.end():].strip(), None))
            GAP_REPAIRS.append((no, want))
        out.append((num, text, sub))
    return out


if __name__ == "__main__":
    import w13_1662
    import w13_1928
    ps = parse()
    bad = w13_1662.gate(ps, "1892")
    print("1892: %d psalms, %d verses, %d incipits, %d sub-headings; caps splits %s"
          % (len(ps), sum(len(p["verses"]) for p in ps.values()),
             sum(1 for p in ps.values() if p["incipit"]),
             sum(1 for p in ps.values() for v in p["verses"] if v[2]), CAPS_SPLITS[:10]))
    print("online splits (number found inside the previous verse): %d %s" % (len(ONLINE_SPLITS), ONLINE_SPLITS))
    print("post-parse gap repairs: %s | NOT repairable: %s" % (GAP_REPAIRS, GAP_UNREPAIRED))
    print("lines the parser could not place: %d %s" % (len(DROPPED), DROPPED[:8]))
    print("fused boundaries split on 1662's word pairs (same verse): %s" % FUSED)
    print("fragment runs joined: %s" % RUN_JOINS)
    print("GATE:", "clean" if not bad else "%d problems: %s" % (len(bad), bad[:6]))
    a, c = w13_1662.parse(), w13_1928.parse()
    d = [(n, len(a[n]["verses"]), len(ps[n]["verses"]) if n in ps else None,
          len(c[n]["verses"])) for n in range(1, 151)
         if n not in ps or len(ps[n]["verses"]) not in (len(a[n]["verses"]), len(c[n]["verses"]))]
    print("psalms where 1892 matches NEITHER 1662 nor 1928 in verse count: %s" % d)
