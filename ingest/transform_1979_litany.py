#!/usr/bin/env python3
"""Transform the public-domain 1979 US BCP ASCII e-text (bcpoffce.txt) into the
Tier-1 'The Great Litany' file, mechanically (source -> file, never re-typed).

The Great Litany occupies bcpoffce.txt lines 6438..6688 (the section heading
'<The Great Litany>' through the concluding Grace, before '<The Supplication>').
In this e-text: '=text=' marks an italic spoken RESPONSE (rendered here as a plain
spoken line), '*text*' marks a rubric, '&V.'/'&R.' mark versicle/response, a line
beginning '/' is a run-over of the previous line, '<page N>' is page furniture.
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

START = find(lambda i: LINES[i].strip() == "<The Great Litany>")
END = find(lambda i: LINES[i].strip() == "<The Supplication>", START + 1)
assert 0 <= START < END, (START, END)
seg = LINES[START:END]

def deitalic(s):
    return s.replace("=", "")

# join run-overs ('/...') and drop page furniture
clean = []
for ln in seg:
    s = ln.rstrip()
    if re.match(r"^\s*<page\b", s):
        continue
    st = s.strip()
    if st.startswith("/") and clean:
        clean[-1] = clean[-1].rstrip() + " " + st[1:].strip()
    else:
        clean.append(s)

# group into blank-line-separated blocks
blocks, cur = [], []
for ln in clean:
    if ln.strip() == "":
        if cur:
            blocks.append(cur); cur = []
    else:
        cur.append(ln)
if cur:
    blocks.append(cur)

out = ["# The Great Litany", ""]
prayers_started = False
for blk in blocks:
    joined = " ".join(x.strip() for x in blk)
    first = blk[0].strip()

    if first == "<The Great Litany>":
        continue
    # concluding collect bidding marks the start of ## The Prayers
    if not prayers_started and re.search(r"The Officiant concludes with the following", joined):
        out += ["", "## The Prayers", ""]
        prayers_started = True
    # whole-block rubric  *...*
    if joined.startswith("*") and joined.endswith("*"):
        out.append("> " + deitalic(joined).strip("*").strip())
        out.append("")
        continue
    # versicle / response markers
    if first.startswith("&V.") or first.startswith("&R."):
        for x in blk:
            xs = x.strip()
            lab = "V." if xs.startswith("&V.") else "R."
            out.append(f"**{lab}** " + deitalic(xs[3:]).strip())
        out.append("")
        continue
    # a block may be [petition lines...] + [=response=]; split them
    petition, responses = [], []
    for x in blk:
        xs = x.strip()
        if xs.startswith("=") and xs.endswith("="):
            responses.append(deitalic(xs).strip())
        else:
            petition.append(deitalic(xs).strip())
    if petition:
        out.append(" ".join(petition))
    for r in responses:
        out.append(r)
    out.append("")

# insert ## The Litany after the opening rubric (first '> ' block)
final = []
lit_inserted = False
for i, ln in enumerate(out):
    final.append(ln)
    if not lit_inserted and ln.startswith("> ") and out[0].startswith("# "):
        final.append("")
        final.append("## The Litany")
        lit_inserted = True

# normalize blank runs
res, blank = [], 0
for ln in final:
    if ln == "":
        blank += 1
        if blank <= 1: res.append("")
    else:
        blank = 0; res.append(ln)
while res and res[-1] == "": res.pop()

with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write("\n".join(res).rstrip("\n") + "\n")

txt = "\n".join(res)
print("Great Litany lines %d-%d | out lines %d" % (START, END, len(res)))
print("## anchors:", re.findall(r"(?m)^## (.+)$", txt))
print("stray '<' furniture:", txt.count("<page"), "| stray '=':", txt.count("="))
