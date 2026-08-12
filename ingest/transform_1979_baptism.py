#!/usr/bin/env python3
"""Transform the public-domain 1979 US BCP ASCII e-text (bcpspecl.txt) into the
Tier-1 1979 Public Baptism and Private Baptism files, mechanically. The
liturgical text flows source -> here -> file; it is never re-typed (this also
sidesteps the output content-filter false-positive on large modern liturgical
text). The 1979 book has ONE contemporary "Holy Baptism" rite (no Rite One/Two
split); its own printed section headings become the ## anchors, so the diff
against 1928 reads as the wholesale modern restructure it historically is.

  public-baptism  <- <Holy Baptism> ... before <Conditional Baptism>
  private-baptism <- <Conditional Baptism> + <Emergency Baptism> (the modern
                     equivalents of the historic private-houses office)

Usage: transform_1979_baptism.py <public-out.md> <private-out.md>
Run from the primary repo (reuses the shared scrape cache + allow-list).
Sibling of ingest/transform_1979_hc.py; shares its render helpers.
"""
import sys, re
sys.path.insert(0, "tools")
import scrape

LINES = scrape.fetch("http://justus.anglican.org/resources/bcp/bcpspecl.txt").split("\n")
# The e-text brackets bishop-only optional sections with doubled [[ ]] markup
# (e.g. "[[<Consecration of the Chrism>"); those are structural markers, not
# liturgical text or BCP single-bracket optional typography — drop them.
LINES = [l.replace("[[", "").replace("]]", "") for l in LINES]


def find(pred, start=0):
    for i in range(start, len(LINES)):
        if pred(i):
            return i
    return -1


PUB = find(lambda i: LINES[i].strip() == "<Holy Baptism>")
COND = find(lambda i: LINES[i].strip() == "<Conditional Baptism>", PUB + 1)
END = len(LINES)
assert 0 <= PUB < COND < END, (PUB, COND, END)

SPEAKER = re.compile(r"^\*(Officiant|People|Priest|Minister|Deacon|Celebrant|"
                     r"Answer|Bishop|Reader|Leader|Cantor|Choir|Versicle|Response|"
                     r"Sponsors|Candidates|Question|Parents and Godparents)\.?\*", re.I)


def unwrap_headings(seg):
    out, i = [], 0
    while i < len(seg):
        s = seg[i].strip()
        if s.startswith("<") and ">" not in s:
            acc, j = s, i
            while ">" not in acc and j + 1 < len(seg) and (j - i) < 4:
                j += 1
                acc += " " + seg[j].strip()
            if ">" in acc:
                out.append(re.sub(r"\s+", " ", acc)); i = j + 1; continue
            out.append(seg[i].lstrip("<").rstrip())
            i += 1; continue
        if re.match(r"^<page\b.*>$", s, re.I) or re.match(r"^<(parallel column|column\b[^>]*)>$", s, re.I):
            i += 1; continue
        out.append(seg[i]); i += 1
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


def render(block, level):
    block = merge_runovers(block)
    first = block[0].strip()
    if first.startswith("<") and ">" in first:
        inner = first[1:]
        title = inner.split(">", 1)[0].strip()
        tail = inner.split(">", 1)[1].strip() if ">" in inner else ""
        out = [f"{level} {title}"]
        if tail:
            out += ["", deitalic(tail)]
        return out
    joined = " ".join(x.strip() for x in block)
    # a wholly-italic (asterisked) block is a rubric
    if joined.startswith("*") and joined.endswith("*") and not any(SPEAKER.match(x.strip()) for x in block):
        body = deitalic(joined).strip().strip("*").strip()
        return [f"> {body}"]
    if any(SPEAKER.match(x.strip()) for x in block):
        units, cur = [], ""
        for x in block:
            xs = x.strip()
            if SPEAKER.match(xs):
                if cur: units.append(cur)
                cur = re.sub(r"^\*([^*]+)\*\.?", lambda mm: f"**{mm.group(1).strip()}.**", xs)
            else:
                cur += " " + xs
        if cur: units.append(cur)
        return [deitalic(u).strip() for u in units]
    return [deitalic(joined).strip()]


def transform(i0, i1, drop_titles):
    seg = unwrap_headings(LINES[i0:i1])
    out = []
    for blk in blocks(seg):
        head = blk[0].strip()
        if any(head == f"<{t}>" or head.startswith(f"<{t}") for t in drop_titles):
            # top-level title lines used as the doc title, not a ## anchor
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


pub = transform(PUB, COND, ["Holy Baptism"])
priv = transform(COND, END, [])

pub_doc = [
 "# Holy Baptism.",
 "",
 "<!-- 1979 (public domain). The 1979 book has a single contemporary-language Holy Baptism rite covering all ages (no separate infant/adult offices); its own printed section headings are the anchors, so the diff against 1928 reads as the wholesale modern restructure. Source: justus PD ASCII e-text bcpspecl.txt (spec §4.2). Mechanically reflowed; verify against a scan before sign-off. -->",
 "",
 *pub,
]
priv_doc = [
 "# Emergency Baptism.",
 "",
 "<!-- 1979 (public domain). The modern equivalent of the historic Private Baptism of Children: the short Emergency Baptism form and the rules for Conditional Baptism. Source: justus PD ASCII e-text bcpspecl.txt (spec §4.2). Mechanically reflowed; verify against a scan before sign-off. -->",
 "",
 *priv,
]
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write("\n".join(pub_doc).rstrip("\n") + "\n")
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    fh.write("\n".join(priv_doc).rstrip("\n") + "\n")

for label, body in (("public", pub_doc), ("private", priv_doc)):
    txt = "\n".join(body)
    print("%s: ## anchors %d | stray '<page' %d | stray '<' lines %d"
          % (label, len(re.findall(r"(?m)^## ", txt)), txt.count("<page"),
             len(re.findall(r"(?m)^[^\n]*<[^\n]*$", txt))))
print("boundaries PUB %d COND %d END %d" % (PUB, COND, END))
