#!/usr/bin/env python3
"""hc_clean.py — byte-faithful cleaner for justus Holy Communion pages.

Wave 4 ingest helper (authoring-only; NOT published). Runs scrape.html_to_markdown
on a cached justus Communion page and strips the recurring page-scan furniture
(country nav, image captions, footer) so what remains is the liturgical text,
source-faithful. It does NOT place anchors or speaker labels — that structuring
is done by hand/assembler against this spine so the WORDS always come from the
source, never from memory.

Usage:
    python3 ingest/hc_clean.py <justus-url>            # print cleaned spine
Run from the primary repo so it reuses the shared scrape cache + allow-list.
"""
import sys, os, re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
sys.path.insert(0, "tools")
import scrape  # noqa: E402

# Lines matching any of these (case-insensitive substring/regex) are page
# furniture, not liturgical text. Kept deliberately specific so real rubrics
# (which can mention "image", "table", etc.) are never dropped.
CRUFT = [
    r"^The Book of Common Prayer$",
    r"^The Book of Common Prayer - \d{4}$",
    r"United States\s+England\s+Scotland",
    r"Clicking on the image",
    r"readable image of this page",
    r"^Above (is|are) the",
    r"^(These|This|The above|Below) (two )?images? (how|show|shows|is|are|display)",
    r"^Return to the",
    r"^Web author:",
    r"Charles Wohlers",
    r"Society of Archbishop Justus",
    r"larger \(\d+K",
    r"^\s*$",  # collapse blank runs (re-added between blocks below)
]
CRUFT_RE = [re.compile(p, re.I) for p in CRUFT]


def clean(url: str) -> str:
    md = scrape.html_to_markdown(scrape.fetch(url))
    out = []
    for raw in md.splitlines():
        line = raw.rstrip()
        probe = re.sub(r"^>\s*", "", line)  # cruft can arrive already blockquoted
        if any(r.search(line) or r.search(probe) for r in CRUFT_RE):
            # keep a single blank separator where a blank line was
            if line.strip() == "" and out and out[-1] != "":
                out.append("")
            continue
        # pilcrow-prefixed paragraphs are rubrics in the justus source
        line = re.sub(r"^�\s*", "> ", line)   # replacement char sometimes
        line = re.sub(r"^¶\s*", "> ", line)    # actual pilcrow
        out.append(line)
    # collapse 3+ blank lines to 1
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.stdout.write(clean(sys.argv[1]))
