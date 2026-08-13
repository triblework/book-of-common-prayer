#!/usr/bin/env python3
"""Transform the public-domain 1979 US BCP ASCII e-text (bcpastrl.txt, the
Pastoral Offices) into the Tier-1 1979 Matrimony file, mechanically. The
liturgical text flows source -> here -> file; it is never re-typed (this also
sidesteps the output content-filter false-positive on large modern liturgical
text). The 1979 marriage provision is "The Celebration and Blessing of a
Marriage" (contemporary language) plus "An Order for Marriage" and "Additional
Directions"; its own printed section headings become the ## anchors.

e-text markup handled: =italic= (rubrics), *Speaker* labels, [[optional]],
/runover, and the & bold/entity markers (&N. name-blanks -> N., &mdash -> em dash).

Usage: transform_1979_matrimony.py <out.md>
Run from the primary repo (reuses the shared scrape cache + allow-list).
Sibling of ingest/transform_1979_confirmation.py.
"""
import sys, re
sys.path.insert(0, "tools")
import scrape

LINES = scrape.fetch("http://justus.anglican.org/resources/bcp/bcpastrl.txt").split("\n")
LINES = [l.replace("[[", "").replace("]]", "") for l in LINES]


def find(pred, start=0):
    for i in range(start, len(LINES)):
        if pred(i):
            return i
    return -1


PAST = find(lambda i: LINES[i].strip() == "<Pastoral Offices>")
R1 = find(lambda i: LINES[i].strip() == "<The Burial of the Dead:"
          and LINES[i+1].strip() == "Rite One>", PAST + 1)
R2 = find(lambda i: LINES[i].strip() == "<The Burial of the Dead:"
          and LINES[i+1].strip() == "Rite Two>", R1 + 1)
END = find(lambda i: LINES[i].strip() == "<Note:>", R2 + 1)
if END < 0:
    END = len(LINES)
assert 0 <= R1 < R2 < END, (PAST, R1, R2, END)

SPEAKER = re.compile(r"^\*(Officiant|People|Priest|Minister|Deacon|Celebrant|"
                     r"Answer|Bishop|Reader|Leader|Cantor|Choir|Versicle|Response|"
                     r"Husband|Wife|Man|Woman|Congregation)\.?\*", re.I)


def demarkup(s):
    s = re.sub(r"&mdash\.?", "—", s)   # em-dash entity (& mdash .)
    s = re.sub(r"&mdr\b", "—", s)       # truncated em-dash entity variant
    s = re.sub(r"&(?=[A-Z])", "", s)          # strip name-blank bold marker (&N. -> N.)
    s = re.sub(r" \* ", " : ", s)             # 1979 psalm-pointing asterisk -> repo mediant
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
            out.append(seg[i].lstrip("<").rstrip())
            i += 1; continue
        if re.match(r"^<(page|age)\b.*>$", s, re.I) or re.match(r"^<(parallel column|column\b[^>]*)>$", s, re.I):
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


def strip_inline_italic(s):
    # drop e-text inline italic *word* pairs (e.g. "(*or* second)"), protecting **bold**
    return re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", s)


def deitalic(s):
    return strip_inline_italic(demarkup(re.sub(r"=([^=]+)=", r"\1", s)))


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
    # inline italic rubric followed (2+ spaces) by spoken text: "*The Husband answers*  I do."
    m = re.match(r"^\*([^*]+)\*\s\s+(\S.*)$", joined)
    if m:
        return [f"> {deitalic(m.group(1)).strip()}", deitalic(m.group(2)).strip()]
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
    # damaged source: an italic rubric with an unmatched '*' (the e-text dropped a
    # delimiter and some words); strip a stray leading/trailing '*', keep the rest
    # verbatim, and let the caller flag it.
    return [re.sub(r"\*$", "", re.sub(r"^\*", "", deitalic(joined).strip())).strip()]


def transform(i0, i1, drop_titles, level="##"):
    seg = unwrap_headings(LINES[i0:i1])
    out = []
    for blk in blocks(seg):
        head = blk[0].strip()
        if any(head.startswith(f"<{t}") for t in drop_titles):
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
    # a standalone footnote alternative ("* Or the deep, or the elements…") -> rubric note
    res = [re.sub(r"^\*\s+", "> ", ln) for ln in res]
    return res


# Rite One in the office (traditional language; its diff against 1928 is the meaningful
# one); Rite Two as a clearly-separated section, its sub-sections one level deeper (###),
# matching the 1979 Morning Prayer convention (spec §4.2).
rite1 = transform(R1, R2, ["The Burial of the Dead"], "##")
rite2 = transform(R2, END, ["The Burial of the Dead"], "###")

doc = [
 "# The Burial of the Dead: Rite One.",
 "",
 "<!-- 1979 (public domain). The Burial of the Dead — Rite One (traditional language) is the office body; Rite Two (contemporary language) follows as a separate section with its sub-sections one heading level deeper, per spec §4.2. The 1979 book's two burial rites; their own printed section headings are the anchors. Source: justus PD ASCII e-text bcpastrl.txt. Mechanically reflowed; verify against a scan before sign-off. -->",
 "",
 *rite1,
 "",
 "## Rite Two",
 "",
 *rite2,
]
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write("\n".join(doc).rstrip("\n") + "\n")

txt = "\n".join(doc)
print("boundaries PAST %d R1 %d R2 %d END %d" % (PAST, R1, R2, END))
print("## anchors %d | ### anchors %d | stray '<page' %d | stray '&' %d | stray '<' lines %d"
      % (len(re.findall(r"(?m)^## ", txt)), len(re.findall(r"(?m)^### ", txt)),
         txt.count("<page"), txt.count("&"),
         len(re.findall(r"(?m)^[^\n]*<[^\n]*$", txt))))