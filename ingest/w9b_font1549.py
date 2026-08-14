#!/usr/bin/env python3
"""w9b_font1549.py — append the 1549 'Blessing of the Font' appendix to the 1549
Private Baptism file (file -> file; no model tokens). Present ONLY at 1549 (the
1552 book dropped this separate monthly font-blessing), so it produces a clean
deletion diff v1549 -> v1552 on private-baptism.md. Deferred from Wave 5.

Source: the font-blessing block at the end of the byte-faithful 1549 baptism
spine (ingest/spines-w9/1549_baptism.md), which hc_clean already de-drop-capped.
"""
import os, re

HERE = os.path.dirname(__file__)
WT = os.path.abspath(os.path.join(HERE, ".."))
SPINE = os.path.join(HERE, "spines-w9", "1549_baptism.md")
DEST = os.path.join(WT, "editions", "1549", "occasional-offices", "private-baptism.md")

ANCHOR = "## The Blessing of the Font"


def spine_para(lines, sub):
    for ln in lines:
        probe = re.sub(r"^>\s*", "", ln).strip()
        if sub in probe:
            return probe
    raise SystemExit(f"  !! not found in spine: {sub!r}")


def main():
    lines = [ln.rstrip("\n") for ln in open(SPINE, encoding="utf-8")]
    rubric = spine_para(lines, "The water in the fonte shalbe chaunged")
    prayers = [
        spine_para(lines, "O MOSTE mercifull god our savioure"),
        spine_para(lines, "O MERCIFULL God"),
        spine_para(lines, "GRAUNT that all carnal affeccions"),
        spine_para(lines, "GRAUNT to all them which at this fountayne"),
        spine_para(lines, "WHOSOEVER shal confesse the"),
        spine_para(lines, "GRAUNT that al sinne and vice"),
        spine_para(lines, "GRAUNTE that whosoever here shall begynne"),
        spine_para(lines, "GRAUNT that all they which for thy sake"),
        spine_para(lines, "GRAUNT that whosoever is here dedicated"),
    ]
    versicle = spine_para(lines, "The Lorde be with you")
    answer = spine_para(lines, "And with thy spirite")
    answer = re.sub(r"^Answere\.\s*", "", answer)
    final = spine_para(lines, "ALMIGHTYE everliving God")

    body = [ANCHOR, "", "> " + rubric, ""]
    body += "\n\n".join(prayers).split("\n")
    body += ["", versicle, f"**Answer.** {answer}", "", final]
    section = "\n".join(body) + "\n"

    cur = open(DEST, encoding="utf-8").read()
    if ANCHOR in cur:
        print("  (skip) Blessing of the Font already present")
        return
    cur = cur.rstrip("\n") + "\n\n" + section
    open(DEST, "w", encoding="utf-8").write(cur)
    print(f"  appended Blessing of the Font ({len(prayers)} prayers) to 1549 private-baptism.md")


if __name__ == "__main__":
    main()
