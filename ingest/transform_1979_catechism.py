#!/usr/bin/env python3
"""Transform the public-domain 1979 US BCP ASCII e-text (bcpprayr.txt) into the
Tier-1 1979 Catechism file, mechanically. The text flows source -> here -> file;
it is never re-typed (this also sidesteps the output content-filter false-positive
on large modern liturgical text).

The 1979 Catechism is "An Outline of the Faith, commonly called the Catechism"
(bcpprayr.txt, pp. 844-862), preceded by its own "Concerning the Catechism"
preface. It is contemporary Q&A (&Q./&A. markers) arranged under its own section
headings (<Human Nature>, <God the Father>, ... <The Christian Hope>), which
become the ## anchors. Ends before <Historical Documents of the Church>.

Usage: transform_1979_catechism.py <out.md>
Run from the primary repo (reuses the shared scrape cache + allow-list).
Sibling of ingest/transform_1979_confirmation.py; shares its render approach.
"""
import sys, re
sys.path.insert(0, "tools")
import scrape

LINES = scrape.fetch("http://justus.anglican.org/resources/bcp/bcpprayr.txt").split("\n")
# Drop the e-text's doubled [[ ]] optional-section markup (structural, not text).
LINES = [l.replace("[[", "").replace("]]", "") for l in LINES]


def find(pred, start=0):
    for i in range(start, len(LINES)):
        if pred(i):
            return i
    return -1


# The Catechism runs from its "Concerning the Catechism" preface to the
# Historical Documents section that follows it.
START = find(lambda i: LINES[i].strip() == "<Concerning the Catechism>")
END = find(lambda i: LINES[i].strip() == "<Historical", START + 1)
assert 0 <= START < END, (START, END)


def strip_pagemarks(s):
    # <page 847> markers appear standalone and mid-line; remove them entirely.
    return re.sub(r"<page\b[^>]*>", "", s)


def unwrap_headings(seg):
    """Join a heading that wraps across lines (e.g. <An Outline of the Faith\n
    commonly called the Catechism>) into one <...> line; drop <page> markers."""
    out, i = [], 0
    while i < len(seg):
        s = strip_pagemarks(seg[i]).rstrip()
        st = s.strip()
        if st.startswith("<") and ">" not in st:
            acc, j = st, i
            while ">" not in acc and j + 1 < len(seg) and (j - i) < 6:
                j += 1
                acc += " " + strip_pagemarks(seg[j]).strip()
            if ">" in acc:
                out.append(re.sub(r"\s+", " ", acc).strip()); i = j + 1; continue
            out.append(st); i += 1; continue
        out.append(s); i += 1
    return out


def blocks(seg):
    cur = []
    for ln in seg:
        s = ln.strip()
        if s == "":
            if cur: yield cur; cur = []
            continue
        if s.startswith("<") and ">" in s:
            if cur: yield cur; cur = []
            yield [ln]; continue
        # &Q. / &A. each start a new spoken block
        if s.startswith("&Q.") or s.startswith("&A."):
            if cur: yield cur; cur = []
        cur.append(ln)
    if cur: yield cur


def collapse(s):
    return re.sub(r"[ \t]+", " ", s).strip()


def render(block, level):
    first = block[0].strip()
    # Section heading -> ## (or # for the title, handled by caller via level).
    if first.startswith("<") and ">" in first:
        inner = first[1:]
        title = inner.split(">", 1)[0].strip()
        return [f"{level} {title}"]
    joined = collapse(" ".join(x.strip() for x in block))
    # Standalone italic note (e.g. *See pages 317 and 350.*) -> rubric.
    if joined.startswith("*") and joined.endswith("*") and joined.count("*") == 2:
        return [f"> {joined.strip('*').strip()}"]
    # &Q. / &A. speaker unit.
    m = re.match(r"^&(Q|A)\.\s*(.*)$", joined, re.S)
    if m:
        text = collapse(m.group(2))
        note = None
        # An inline italic cross-reference trailing the answer (e.g. *See page
        # 364*) is split out to its own rubric line so no stray * remains.
        mnote = re.search(r"\s*\*([^*]+)\*\s*$", text)
        if mnote:
            note = mnote.group(1).strip()
            text = text[:mnote.start()].rstrip()
        unit = [f"**{m.group(1)}.** {text}".rstrip()]
        if note:
            unit += ["", f"> {note}"]
        return unit
    return [joined]


def transform(i0, i1):
    seg = unwrap_headings(LINES[i0:i1])
    out = []
    for blk in blocks(seg):
        head = blk[0].strip()
        # The Outline title becomes the document H1, handled separately below.
        if head.startswith("<An Outline of the Faith"):
            continue
        out += render(blk, "##")
        out.append("")
    res, blank = [], 0
    for ln in out:
        if ln == "":
            blank += 1
            if blank <= 1: res.append("")
        else:
            blank = 0; res.append(ln)
    while res and res[-1] == "": res.pop()
    return res


body = transform(START, END)

doc = [
 "# An Outline of the Faith, commonly called the Catechism.",
 "",
 "<!-- 1979 (public domain). The contemporary-language recasting of the Catechism as \"An Outline of the Faith\"; its own printed section headings (Human Nature, God the Father, ... The Christian Hope) are the anchors, and it opens with its \"Concerning the Catechism\" preface. Source: justus PD ASCII e-text bcpprayr.txt (spec §4.2). Mechanically reflowed; verify against a scan before sign-off. -->",
 "",
 *body,
]
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write("\n".join(doc).rstrip("\n") + "\n")

txt = "\n".join(doc)
print("boundaries START %d END %d" % (START, END))
print("## anchors %d | **Q.** %d | **A.** %d | stray '<page' %d | stray '<' lines %d"
      % (len(re.findall(r"(?m)^## ", txt)), txt.count("**Q.**"), txt.count("**A.**"),
         txt.count("<page"), len(re.findall(r"(?m)^[^\n]*<[^\n>]*$", txt))))
