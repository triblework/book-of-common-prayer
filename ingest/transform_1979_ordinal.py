#!/usr/bin/env python3
"""Transform the public-domain 1979 US BCP ASCII e-text (bcpepscl.txt, the
Episcopal Services) into the four Tier-1 1979 Ordinal files, mechanically. The
liturgical text flows source -> here -> file; it is never re-typed (this also
sidesteps the output content-filter false-positive on large modern text).

The 1979 Ordination rites live in bcpepscl.txt:
  <Preface to the Ordination Rites>  -> ordinal/preface.md
  <The Ordination of a Bishop>       -> ordinal/consecration-bishops.md
  <The Ordination of a Priest>       -> ordinal/ordering-priests.md
  <The Ordination of a Deacon>       -> ordinal/ordering-deacons.md  (+ the Litany
                                        for Ordinations appended)
Each rite's own printed section headings (<The Presentation>, <The Examination>,
<The Consecration of the Bishop>, ...) become the ## anchors. Sibling of
ingest/transform_1979_confirmation.py; shares its render helpers.

Usage: transform_1979_ordinal.py <out-dir>   (writes the four files under it)
Run from the primary repo (reuses the shared scrape cache + allow-list).
"""
import sys, os, re
sys.path.insert(0, "tools")
import scrape

LINES = scrape.fetch("http://justus.anglican.org/resources/bcp/bcpepscl.txt").split("\n")
LINES = [l.replace("[[", "").replace("]]", "") for l in LINES]


def find(pred, start=0):
    for i in range(start, len(LINES)):
        if pred(i):
            return i
    return -1


SPEAKER = re.compile(r"^\*(Officiant|People|Priest|Minister|Deacon|Celebrant|"
                     r"Answer|Bishop|Bishops|Presiding Bishop|Ordinand|Consecrator|"
                     r"Consecrators|Reader|Leader|Cantor|Choir|Versicle|Response)\.?\*", re.I)


def clean_entities(s):
    s = s.replace("&mdash.", "—").replace("&mdash", "—")
    s = s.replace("&N.&N.", "N.N.").replace("&N.", "N.")
    return s


def unwrap_headings(seg):
    out, i = [], 0
    while i < len(seg):
        s = seg[i].strip()
        if s.startswith("<") and ">" not in s:
            acc, j = s, i
            while ">" not in acc and j + 1 < len(seg) and (j - i) < 6:
                j += 1
                acc += " " + seg[j].strip()
            if ">" in acc:
                out.append(re.sub(r"\s+", " ", acc).strip()); i = j + 1; continue
            out.append(seg[i].lstrip("<").rstrip()); i += 1; continue
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


def deitalic(s):
    return clean_entities(re.sub(r"=([^=]+)=", r"\1", s))


def render(block, level, prose_rubrics=False):
    first = block[0].strip()
    if first.startswith("<") and ">" in first:
        inner = first[1:]
        title = inner.split(">", 1)[0].strip()
        tail = inner.split(">", 1)[1].strip()
        out = [f"{level} {title}"]
        if tail:
            out += ["", deitalic(tail)]
        return out
    joined = " ".join(x.strip() for x in block)
    if joined.startswith("*") and joined.endswith("*") and not any(SPEAKER.match(x.strip()) for x in block):
        body = deitalic(joined).strip().strip("*").strip()
        return [body if prose_rubrics else f"> {body}"]
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


def transform(i0, i1, drop_titles, prose_rubrics=False):
    seg = unwrap_headings(LINES[i0:i1])
    out = []
    for blk in blocks(seg):
        head = blk[0].strip()
        if any(head.startswith(f"<{t}") for t in drop_titles):
            continue
        out += render(blk, "##", prose_rubrics=prose_rubrics)
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


H = {
    "preface": find(lambda i: LINES[i].strip() == "<Preface to the Ordination Rites>"),
    "bishop": find(lambda i: LINES[i].strip() == "<The Ordination of a Bishop>"),
    "priest": find(lambda i: LINES[i].strip() == "<The Ordination of a Priest>"),
    "deacon": find(lambda i: LINES[i].strip() == "<The Ordination of a Deacon>"),
    "litany": find(lambda i: LINES[i].strip() == "<The Litany for Ordinations>"),
    "end": find(lambda i: LINES[i].strip().startswith("<Letter of Institution")),
}
assert all(v >= 0 for v in H.values()), H

NOTE = ("<!-- 1979 (public domain). Contemporary-language rite; the rite's own printed "
        "section headings are the anchors. Source: justus PD ASCII e-text bcpepscl.txt "
        "(Episcopal Services; spec §4.2). Mechanically reflowed; the e-text carries some "
        "OCR artifacts — verify against a page scan before sign-off. -->")

outdir = sys.argv[1]
os.makedirs(outdir, exist_ok=True)


def write(name, title, body):
    doc = [f"# {title}", "", NOTE, "", *body]
    with open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
        fh.write("\n".join(doc).rstrip("\n") + "\n")


write("preface.md", "The Preface to the Ordination Rites",
      transform(H["preface"], H["bishop"], ["Preface to the Ordination Rites"], prose_rubrics=True))
write("consecration-bishops.md", "The Ordination of a Bishop",
      transform(H["bishop"], H["priest"], ["The Ordination of a Bishop"]))
write("ordering-priests.md", "The Ordination of a Priest",
      transform(H["priest"], H["deacon"], ["The Ordination of a Priest"]))
deacon_body = transform(H["deacon"], H["litany"], ["The Ordination of a Deacon"])
litany_body = transform(H["litany"], H["end"], [])
write("ordering-deacons.md", "The Ordination of a Deacon", deacon_body + [""] + litany_body)

print("boundaries:", {k: v for k, v in H.items()})
for f in ["preface.md", "consecration-bishops.md", "ordering-priests.md", "ordering-deacons.md"]:
    t = open(os.path.join(outdir, f)).read()
    print("%-26s anchors=%2d  stray'<'=%d" % (
        f, len(re.findall(r"(?m)^## ", t)), len(re.findall(r"(?m)^[^\n]*<[a-zA-Z/][^\n]*$", t))))
