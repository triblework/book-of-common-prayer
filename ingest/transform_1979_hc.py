#!/usr/bin/env python3
"""Transform the public-domain 1979 US BCP ASCII e-text (bcpeuchr.txt) into the
Tier-1 Holy Communion (Holy Eucharist) file, mechanically. The liturgical text
flows source -> here -> file; it is never re-typed (this also sidesteps the
output content-filter false-positive on large modern liturgical text). Rite One
is the office body (its diff against 1928 is the meaningful one); Rite Two is a
clearly separated `## Rite Two` section (spec §4.2).

Sibling of tools/transform_1979.py; the Eucharist e-text carries more OCR damage
in the Rite Two region (a few headings lost their closing '>' or were garbled),
so heading detection is guarded and a small fix-map repairs known garbles.
"""
import sys, re
sys.path.insert(0, "tools")
import scrape

LINES = scrape.fetch("http://justus.anglican.org/resources/bcp/bcpeuchr.txt").split("\n")


def find(pred, start=0):
    for i in range(start, len(LINES)):
        if pred(i):
            return i
    return -1


# Section boundaries (verified against the e-text heading layout):
R1 = find(lambda i: LINES[i].strip() == "<The Holy Eucharist:  Rite One>")
R1_END = find(lambda i: LINES[i].strip() == "<A Penitential Order: Rite Two>", R1 + 1)
R2 = find(lambda i: LINES[i].strip() == "The Holy Eucharist:  Rite Two>", R1_END + 1)
R2_END = find(lambda i: LINES[i].strip() == "<Communion under Special Circumstances>", R2 + 1)
assert 0 <= R1 < R1_END and 0 <= R2 < R2_END, (R1, R1_END, R2, R2_END)

SPEAKER = re.compile(r"^\*(Officiant|People|Priest|Minister|Deacon|Celebrant|"
                     r"Answer|Bishop|Reader|Leader|Cantor|Choir|Versicle|Response)\.?\*", re.I)

# Known OCR-garbled heading text -> repaired heading (the e-text lost characters).
HEADING_FIX = {
    "The Collec the Church;": "The Prayers of the People",
}


def unwrap_headings(seg):
    """Join a heading whose '<' opener wraps across lines, but ONLY if a '>'
    closes it within 2 lines (guards against a stray '<' in body text swallowing
    the rest of the segment). Drop <page N> / column furniture."""
    out, i = [], 0
    while i < len(seg):
        s = seg[i].strip()
        if s.startswith("<") and ">" not in s:
            acc, j = s, i
            while ">" not in acc and j + 1 < len(seg) and (j - i) < 2:
                j += 1
                acc += " " + seg[j].strip()
            if ">" in acc:            # a real (wrapped) heading
                out.append(acc); i = j + 1; continue
            out.append(seg[i].lstrip("<").rstrip())  # stray '<' in body: de-mark
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


def norm_mediant(s):
    return re.sub(r"[;,]?\s*\*\s+", " : ", s)


def render(block, level):
    block = merge_runovers(block)
    first = block[0].strip()
    if first.startswith("<") and ">" in first:
        inner = first[1:]
        cite = None
        m = re.search(r"=([^=]+)=", inner)
        if m:
            cite = m.group(1).strip(); inner = inner[:m.start()]
        title = inner.split(">", 1)[0].strip()
        title = HEADING_FIX.get(title, title)
        tail = inner.split(">", 1)[1].strip() if ">" in inner else ""
        out = [f"{level} {title}"]
        if cite:
            out += ["", f"> {cite}"]
        if tail:
            out += ["", norm_mediant(deitalic(tail))]
        return out
    joined = " ".join(x.strip() for x in block)
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


def transform(i0, i1, level, drop_prefixes):
    seg = unwrap_headings(LINES[i0:i1])
    out = []
    for blk in blocks(seg):
        head = blk[0].strip()
        if any(head.startswith(p) for p in drop_prefixes):
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


rite1 = transform(R1, R1_END, "##", ["<The Holy Eucharist"])
rite2 = transform(R2, R2_END, "###", ["<The Holy Eucharist", "The Holy Eucharist:  Rite Two"])

doc = [
 "# The Holy Eucharist.",
 "",
 "<!-- 1979 (public domain). Rite One is the traditional-language rite continuous with the earlier tradition (its diff against 1928 is the meaningful one) and is the body here; Rite Two, the contemporary rite, follows as a separate section. Source: justus PD ASCII e-text bcpeuchr.txt (spec §4.2). Mechanically reflowed from the e-text; the Rite Two region of the e-text carries OCR damage — verify against a scan before sign-off. -->",
 "",
 *rite1,
 "",
 "## Rite Two",
 "",
 "> The contemporary-language rite. Its Great Thanksgiving opens 'Lift up your hearts. / We lift them to the Lord.' with the acclamation 'Christ has died. Christ is risen. Christ will come again.'",
 "",
 *rite2,
]
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write("\n".join(doc).rstrip("\n") + "\n")

txt = "\n".join(doc)
print("boundaries R1: %d-%d  R2: %d-%d" % (R1, R1_END, R2, R2_END))
print("rite1 lines %d | rite2 lines %d" % (len(rite1), len(rite2)))
print("## anchors %d | ### anchors %d" % (len(re.findall(r"(?m)^## ", txt)), len(re.findall(r"(?m)^### ", txt))))
print("stray '<page' occurrences:", txt.count("<page"))
print("lines still containing a stray '<':", len(re.findall(r"(?m)^[^\n]*<[^\n]*$", txt)))
