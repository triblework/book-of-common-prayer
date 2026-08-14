#!/usr/bin/env python3
"""w9_build.py — Wave 9 front-matter structurer (file -> file; no model tokens).

Reads the byte-faithful spines in ingest/spines-w9/ and writes each authored
edition cell under editions/<year>/front-matter/<piece>.md. Text flows
spine -> script -> file so the output content filter is never fed large
verbatim liturgical blocks as model output (see the subagent-write-content-filter
memory / Wave 8 method).

Each cell is defined by:
  - the spine file it draws from,
  - the '# Title' heading,
  - an ordered list of paragraph START substrings; for each, the script emits
    the FULL spine line containing that substring (first match), stripped of any
    leading '> ' that hc_clean added and of trailing bracket-only editorial notes.

This gives precise control and skips interleaved editorial/cruft lines that a
naive range would include.
"""
import os, sys, re

HERE = os.path.dirname(__file__)
SPINES = os.path.join(HERE, "spines-w9")
WT = os.path.abspath(os.path.join(HERE, ".."))


def spine_lines(name):
    with open(os.path.join(SPINES, name), encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f]


def para_for(lines, sub):
    """Return the full spine paragraph line that contains `sub` (first match)."""
    for ln in lines:
        probe = re.sub(r"^>\s*", "", ln).strip()
        if sub in probe:
            return probe
    raise SystemExit(f"  !! selector not found: {sub!r}")


def build_cell(spine, title, selectors, out_rel):
    lines = spine_lines(spine)
    paras = [para_for(lines, s) for s in selectors]
    body = "\n\n".join(paras)
    # A mis-decoded apostrophe byte in the 1637 source surfaced as U+FFFD in a
    # few "God's" tokens; restore the curly apostrophe the source uses elsewhere.
    body = body.replace("�", "’")
    out = f"# {title}\n\n{body}\n"
    dest = os.path.join(WT, "editions", out_rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"  wrote {out_rel}  ({len(paras)} paras, {len(out)} bytes)")


# ---------------------------------------------------------------------------
# CELL DEFINITIONS
# ---------------------------------------------------------------------------
CELLS = [
    # ---- concerning-the-service (the "There was never any thing" preface) ----
    dict(spine="1549_frontmatter.md", title="The Preface",
         out="1549/front-matter/concerning-the-service.md",
         sel=[
             "THERE was never any thing by the wit of man",
             "These inconveniences therfore considered",
             "And where heretofore, there hath been great diversitie",
             "And farsomuche as nothyng can",
             "Though it be appointed in the afore written preface",
         ]),
    dict(spine="1552_frontmatter.md", title="The Preface",
         out="1552/front-matter/concerning-the-service.md",
         sel=[
             "THERE was never anye thynge by the wytte of man",
             "These inconveniences therefore consydered",
             "And where heretofore there hath been greate diversitie",
             "And for asmuche as nothynge can almoste",
             "Though it be appoynted in the afore wrytten Preface",
             "And all Priestes and Deacons shalbe bounde to say dayly",
             "And the Curate that ministreth in every Parish Churche",
         ]),
    dict(spine="1662_concerning.md", title="Concerning the Service of the Church",
         out="1662/front-matter/concerning-the-service.md",
         sel=[
             "There was never any thing by the wit of man",
             "But these many years passed",
             "These inconveniences therefore considered",
             "Yet, because there is no remedy",
             "And whereas heretofore there hath been great diversity",
             "And forasmuch as nothing can be so plainly",
             "Though it be appointed, That all things",
             "And all Priests and Deacons are to say daily",
             "And the Curate that ministereth in every Parish-Church",
         ]),
    dict(spine="1637_frontmatter.md", title="The Preface",
         out="1637/front-matter/concerning-the-service.md",
         sel=[
             "THE Church of Christ hath in all ages had a prescript forme",
             "It was not the least part of our late Soveraigne King JAMES",
             "But as there is nothing, how good and warrantable",
             "Our first Reformers were of the same minde",
             "ALL Presbyters and Deacons shall be bound to say daily",
             "And the curate that ministereth in every Parish-Church",
         ]),

    # ---- of-ceremonies ----
    dict(spine="1549_ofceremonies.md",
         title="Of Ceremonies, why some be abolished and some retayned",
         out="1549/front-matter/of-ceremonies.md",
         sel=[
             "OF suche Ceremonies as be used in the Church",
             "Some are put awaye, because the great excesse",
             "Furthermore, the most weightye cause of the abolishement",
         ]),
    dict(spine="1662_ceremonies.md",
         title="Of Ceremonies, why some be abolished, and some retained",
         out="1662/front-matter/of-ceremonies.md",
         sel=[
             "Of such Ceremonies as be used in the Church",
             "And although the keeping or omitting of a Ceremony",
             "And whereas in this our time, the minds of men",
             "Some are put away, because the great excess",
             "But now as concerning those persons",
         ]),
    dict(spine="1637_frontmatter.md",
         title="Of Ceremonies, why some be abolish'd and some retain'd",
         out="1637/front-matter/of-ceremonies.md",
         sel=[
             "OF such Ceremonies as be used in the Church, and have had their Beginning",
             "Let all things be done among you (saith Saint Paul)",
             "And whereas in this our Time, the Minds of Men",
             "Some are put away, because the great Excess and Multitude",
             "But what would St. Augustine have said",
             "And besides this, Christ’s Gospel is not a Ceremonial Law",
             "Furthermore, the most weighty Cause of the Abolishment",
         ]),

    # ---- preface (the 1662 English addition) ----
    dict(spine="1662_preface.md", title="The Preface",
         out="1662/front-matter/preface.md",
         sel=[
             "It hath been the wisdom of the Church of England",
             "By what undue means, and for what mischievous purposes",
             "In which review we have endeavoured to observe",
             "Our general aim therefore in this undertaking",
             "And having thus endeavoured to discharge our duties",
         ]),
]


def main():
    for c in CELLS:
        build_cell(c["spine"], c["title"], c["sel"], c["out"])


if __name__ == "__main__":
    main()
