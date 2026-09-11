#!/usr/bin/env python3
"""w13_render.py — write the three psalter cells for one edition (Wave 13).

Authoring-only; NOT published. Takes the {psalm: {...}} structure a per-edition
parser produces and writes psalter/psalms-{1-50,51-100,101-150}.md. The psalm
text never passes through model tokens (HANDOFF §6).

Two normalizations, both typographic and both ruled:

  * THE MEDIANT becomes " : " (ruling C). 1928 and 1979 print "*", 1892 and the
    CoE print ":", and 1789 printed none.
  * THE VERSE NUMBER is written "N " (never "N."): a digit + period + space +
    capital is a sentence boundary to sentence_split.py, which would split the
    number off its verse.

A GATE counts mediants: a verse should carry exactly one. Zero or two usually
means a verse was split or merged, so every exception is reported.
"""
import os
import re

WT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = [("psalms-1-50", 1, 50), ("psalms-51-100", 51, 100),
         ("psalms-101-150", 101, 150)]


def mediant(text, mark):
    """Normalize one verse's pointing to ' : '."""
    t = text
    if mark == "*":
        t = re.sub(r"\s*\*\s*", " : ", t)
    elif " : " not in t:
        # A colon printed without its leading space ("was known: the word").
        t = re.sub(r"\s*:\s+", " : ", t, count=1)
    return re.sub(r"\s+", " ", t).strip()


def render(edition, psalms, mark, title="The Psalter", number_first=False):
    """Write the three cells. `number_first`: the book prints verse 1's number
    (1979 does; the Coverdale books leave it unnumbered)."""
    anomalies = []
    out_dir = os.path.join(WT, "editions", edition, "psalter")
    os.makedirs(out_dir, exist_ok=True)
    for name, lo, hi in FILES:
        lines = ["# " + title, ""]
        for n in range(lo, hi + 1):
            p = psalms.get(n)
            if p is None:
                continue
            lines += ["## Psalm %d" % n, ""]
            if p.get("incipit"):
                lines += ["> " + p["incipit"], ""]
            for num, text, sub in p["verses"]:
                if sub:
                    lines += ["> " + sub, ""]
                t = mediant(text, mark)
                k = t.count(" : ")
                if k != 1:
                    anomalies.append((n, num, k))
                if num == 1 and not number_first:
                    lines.append(t)
                else:
                    lines.append("%d %s" % (num, t))
                lines.append("")
        text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).rstrip("\n")) + "\n"
        with open(os.path.join(out_dir, name + ".md"), "w", encoding="utf-8") as fh:
            fh.write(text)
    return anomalies
