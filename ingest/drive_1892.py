#!/usr/bin/env python3
"""Derive the 1892 U.S. Ordinal deltas from the 1789 files, file->file. justus:
"This text in the 1892 Book is essentially identical … any differences are
indicated." Only Priests and Bishops change; Deacons + Preface inherit 1789.

  Priests: the Communion rubric adds "the Nicene Creed shall be said, and".
  Bishops: (a) the presentation rubric adds the Nicene Creed + Sermon; (b) the
           Litany cross-reference "&c." -> "etc."; (c) the printed Veni Creator
           hymn is replaced by a cross-reference to the Ordering of Priests.
"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)


def read(p):
    return open(os.path.join(WT, p)).read()


def write(p, s):
    os.makedirs(os.path.dirname(os.path.join(WT, p)), exist_ok=True)
    open(os.path.join(WT, p), "w").write(s)


# ---- Priests: add the Nicene Creed to the Communion rubric ----
pr = read("editions/1789/ordinal/ordering-priests.md")
old = "> When this is done, the Bishop shall go on in the Service of the Communion"
new = "> When this is done, the Nicene Creed shall be said, and the Bishop shall go on in the Service of the Communion"
assert old in pr, "1789 priests communion rubric not found"
write("editions/1892/ordinal/ordering-priests.md", pr.replace(old, new, 1))

# ---- Bishops ----
bi = read("editions/1789/ordinal/consecration-bishops.md")
# (a) presentation rubric
pres_old = "> After the Gospel and the Sermon are ended, the Elected Bishop"
pres_new_prefix = "> Then shall follow the Nicene Creed, and after that the Sermon; which being ended, the Elected Bishop"
lines = bi.split("\n")
for i, ln in enumerate(lines):
    if ln.startswith(pres_old):
        lines[i] = ln.replace(
            "> After the Gospel and the Sermon are ended, the Elected Bishop",
            pres_new_prefix, 1)
        break
bi = "\n".join(lines)
# (b) &c. -> etc. in the Litany cross-reference rubric
bi = bi.replace("That it may please thee to illuminate all Bishops, &c.",
                "That it may please thee to illuminate all Bishops, etc.")
# (c) replace the printed hymn (Veni Creator section body) with the 1892 cross-ref,
#     keeping the anchor and the intro rubric.
lines = bi.split("\n")
a = next(i for i, l in enumerate(lines) if l.strip() == "## Veni, Creator Spiritus")
b = next(i for i in range(a + 1, len(lines)) if lines[i].startswith("## "))
intro = next(l for l in lines[a:b] if l.startswith("> Then shall the Bishop elect put on"))
crossref = ("> Or else the longer paraphrase of the same Hymn, as in the Ordering of Priests.\n"
            "<!-- VERIFY: 'Or else the longer paraphrase of the same Hymn, as in the Ordering of Priests.'; "
            "the justus 1789 apparatus notes only that in 1892 the printed hymn is replaced by this cross-reference; "
            "confirm the exact 1892 rubric wording against a 1892 page scan -->")
new_section = ["## Veni, Creator Spiritus", "", intro, "", crossref, ""]
lines = lines[:a] + new_section + lines[b:]
bi = "\n".join(lines)
write("editions/1892/ordinal/consecration-bishops.md", bi)

print("wrote 1892 priests + bishops")
