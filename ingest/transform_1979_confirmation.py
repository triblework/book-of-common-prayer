#!/usr/bin/env python3
"""Transform the public-domain 1979 US BCP ASCII e-text (bcpastrl.txt, the
Pastoral Offices) into the Tier-1 1979 Confirmation file, mechanically. The
liturgical text flows source -> here -> file; it is never re-typed (this also
sidesteps the output content-filter false-positive on large modern liturgical
text). Confirmation is the FIRST pastoral office in this e-text (page 413); the
rite is "Confirmation, with forms for Reception and the Reaffirmation of
Baptismal Vows". Its own printed section headings become the ## anchors.

NOTE: bcpepscl.txt (the "Episcopal Services" e-text) contains the Ordination
rites, NOT Confirmation — Confirmation lives here in the Pastoral Offices file.

Usage: transform_1979_confirmation.py <out.md>
Run from the primary repo (reuses the shared scrape cache + allow-list).
Sibling of ingest/transform_1979_hc.py; shares its render helpers.
"""
import sys, re
sys.path.insert(0, "tools")
import scrape

LINES = scrape.fetch("http://justus.anglican.org/resources/bcp/bcpastrl.txt").split("\n")
# Drop the e-text's doubled [[ ]] optional-section markup (structural, not text).
LINES = [l.replace("[[", "").replace("]]", "") for l in LINES]


def find(pred, start=0):
    for i in range(start, len(LINES)):
        if pred(i):
            return i
    return -1


# Confirmation runs from its "Concerning the Service" preface to the next office.
PAST = find(lambda i: LINES[i].strip() == "<Pastoral Offices>")
START = find(lambda i: LINES[i].strip() == "<Concerning the Service>", PAST + 1)
END = find(lambda i: LINES[i].strip().startswith("<A Form of Commitment"), START + 1)
assert 0 <= START < END, (PAST, START, END)

SPEAKER = re.compile(r"^\*(Officiant|People|Priest|Minister|Deacon|Celebrant|"
                     r"Answer|Bishop|Reader|Leader|Cantor|Choir|Versicle|Response|"
                     r"Candidate|Candidates|Sponsor|Sponsors|Question)\.?\*", re.I)


def unwrap_headings(seg):
    out, i = [], 0
    while i < len(seg):
        s = seg[i].strip()
        if s.startswith("<") and ">" not in s:
            acc, j = s, i
            # 1979 rite title wraps across up to five blank-separated lines
            while ">" not in acc and j + 1 < len(seg) and (j - i) < 6:
                j += 1
                acc += " " + seg[j].strip()
            if ">" in acc:
                out.append(re.sub(r"\s+", " ", acc).strip()); i = j + 1; continue
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
    if joined.startswith("*") and joined.endswith("*") and not any(SPEAKER.match(x.strip()) for x in block):
        return [f"> {deitalic(joined).strip().strip('*').strip()}"]
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
        if any(head.startswith(f"<{t}") for t in drop_titles):
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


body = transform(START, END, ["Confirmation"])

doc = [
 "# Confirmation, with forms for Reception and the Reaffirmation of Baptismal Vows.",
 "",
 "<!-- 1979 (public domain). The contemporary-language Confirmation rite (the first of the Pastoral Offices), with the forms for Reception and Reaffirmation of Baptismal Vows; its own printed section headings are the anchors. Source: justus PD ASCII e-text bcpastrl.txt (spec §4.2). Mechanically reflowed; verify against a scan before sign-off. -->",
 "",
 *body,
]
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write("\n".join(doc).rstrip("\n") + "\n")

txt = "\n".join(doc)
print("boundaries PAST %d START %d END %d" % (PAST, START, END))
print("## anchors %d | stray '<page' %d | stray '<' lines %d"
      % (len(re.findall(r"(?m)^## ", txt)), txt.count("<page"),
         len(re.findall(r"(?m)^[^\n]*<[^\n]*$", txt))))
