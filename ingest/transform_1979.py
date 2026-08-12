#!/usr/bin/env python3
"""Transform the public-domain 1979 US BCP ASCII e-text (bcpoffce.txt) into the
Tier-1 Morning Prayer office file, mechanically. The liturgical text flows
source -> here -> file; it is never re-typed. Rite I is the office body; Rite II
is a clearly separated `## Rite Two` section (spec §4.2).
"""
import sys, re
sys.path.insert(0, "tools")
import scrape

LINES = scrape.fetch("http://justus.anglican.org/resources/bcp/bcpoffce.txt").split("\n")

def find(pred, start=0):
    for i in range(start, len(LINES)):
        if pred(i):
            return i
    return -1

def two_line(i, a, b):
    return LINES[i].strip() == a and i+1 < len(LINES) and LINES[i+1].strip() == b

# Section boundaries (verified against the e-text heading layout):
R1_MP = find(lambda i: two_line(i, "<Daily Morning Prayer:", "Rite One>"))
R1_END = find(lambda i: two_line(i, "<Daily Evening Prayer:", "Rite One>"), R1_MP+2)
R2_MP = find(lambda i: two_line(i, "<Daily Morning Prayer:", "Rite Two>"))
# Rite Two MP ends at the next office-level heading (An Order of Service for Noonday).
R2_END = find(lambda i: LINES[i].strip().startswith("<An Order")
                     or LINES[i].strip() == "<Daily Evening Prayer:", R2_MP+2)
assert 0 <= R1_MP < R1_END and 0 <= R2_MP < R2_END, (R1_MP, R1_END, R2_MP, R2_END)

SPEAKER = re.compile(r"^\*(Officiant|People|Priest|Minister|Deacon|Celebrant|"
                     r"Answer|Bishop|Reader|Leader|Cantor|Choir|Versicle|Response)\.?\*", re.I)

def unwrap_headings(seg):
    """Join a heading that wraps across two lines ('<Daily Morning Prayer:' / 'Rite One>')
    and drop <page N> furniture."""
    out, i = [], 0
    while i < len(seg):
        s = seg[i].strip()
        if s.startswith("<") and ">" not in s:            # an unclosed heading opener
            acc, j = s, i
            while ">" not in acc and j+1 < len(seg):
                j += 1
                acc += " " + seg[j].strip()
            out.append(acc); i = j+1; continue
        if re.match(r"^<page\b.*>$", s, re.I) or re.match(r"^<(parallel column|column\b[^>]*)>$", s, re.I):
            i += 1; continue                              # page / two-column layout furniture
        out.append(seg[i]); i += 1
    return out

def blocks(seg):
    """Blank-line-delimited blocks; a complete <...> heading is its own block."""
    cur = []
    for ln in seg:
        s = ln.strip()
        if s == "":
            if cur: yield cur; cur = []
            continue
        if s.startswith("<") and ">" in s:               # complete heading (maybe + =cite=)
            if cur: yield cur; cur = []
            yield [ln]; continue
        cur.append(ln)
    if cur: yield cur

def merge_runovers(block):
    out = []
    for ln in block:
        st = ln.strip()
        if st.startswith("/") and out:
            out[-1] = out[-1].rstrip() + " " + st[1:].strip()
        else:
            out.append(ln)
    return out

def deitalic(s):
    return re.sub(r"=([^=]+)=", r"\1", s)

def norm_mediant(s):
    # the 1979 canticle/psalm mediant is an asterisk; render it as the ' : ' used
    # by the other editions (pointing/typography, not text).
    return re.sub(r"[;,]?\s*\*\s+", " : ", s)

def render(block, level):
    block = merge_runovers(block)
    first = block[0].strip()

    if first.startswith("<") and ">" in first:
        inner = first[1:]
        cite = None
        m = re.search(r"=([^=]+)=", inner)
        if m:
            cite = m.group(1).strip()
            inner = inner[:m.start()]
        title = inner.split(">", 1)[0].strip()
        tail = inner.split(">", 1)[1].strip() if ">" in inner else ""
        out = [f"{level} {title}"]
        if cite:
            out += ["", f"> {cite}"]
        if tail:                                   # rare: text glued onto heading line
            out += ["", norm_mediant(deitalic(tail))]
        return out

    joined = " ".join(x.strip() for x in block)

    # whole-block italic label (e.g. seasonal '=Advent=') or whole-block rubric
    if re.fullmatch(r"=[^=]+=", joined) or (joined.startswith("*") and joined.endswith("*") and not SPEAKER.match(joined)):
        return [f"> {deitalic(joined).strip().strip('*').strip()}"]

    if any(SPEAKER.match(x.strip()) for x in block):
        units, cur = [], ""
        for x in block:
            xs = x.strip()
            if SPEAKER.match(xs):
                if cur: units.append(cur)
                cur = re.sub(r"^\*([^*]+)\*", lambda mm: f"**{mm.group(1).strip()}**", xs)
            else:
                cur += " " + xs
        if cur: units.append(cur)
        return [norm_mediant(deitalic(u)).strip() for u in units]

    return [norm_mediant(deitalic(joined)).strip()]

def transform(i0, i1, level):
    seg = unwrap_headings(LINES[i0:i1])
    out = []
    for blk in blocks(seg):
        if blk[0].strip().startswith("<Daily Morning Prayer"):
            continue
        out += render(blk, level)
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

rite1 = transform(R1_MP, R1_END, "##")
rite2 = transform(R2_MP, R2_END, "###")

doc = [
 "# The Order for Daily Morning Prayer.",
 "",
 "<!-- 1979 (public domain). Rite I is the office body (its diff against 1928 is the meaningful one); Rite II follows as a separate section. Source: justus PD ASCII e-text bcpoffce.txt (spec §4.2). Mechanically reflowed from the e-text; verify against a scan before sign-off. -->",
 "",
 *rite1,
 "",
 "## Rite Two",
 "",
 "> The contemporary-language rite. Its opening — 'Lord, open our lips. / And our mouth shall proclaim your praise.' — is the tradition's most dramatic modernization.",
 "",
 *rite2,
]
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write("\n".join(doc).rstrip("\n") + "\n")

txt = "\n".join(doc)
print("boundaries R1: %d-%d  R2: %d-%d" % (R1_MP, R1_END, R2_MP, R2_END))
print("rite1 lines %d | rite2 lines %d" % (len(rite1), len(rite2)))
print("## anchors %d | ### anchors %d" % (len(re.findall(r"(?m)^## ", txt)), len(re.findall(r"(?m)^### ", txt))))
# sanity: no leftover page furniture or stray heading gluing
print("stray '<page' occurrences:", txt.count("<page"))
print("heading lines gluing text ('>' inside a ## line):", len(re.findall(r"(?m)^##+ [^\n]*>[^\n]", txt)))
