#!/usr/bin/env python3
"""w9_american.py — Wave 9 American front-matter (1789 Ratification + Preface)
and 1979 'Concerning the Service of the Church'. File -> file, no model tokens.

1789: from justus 1789/FrontMatter_1789.htm (HTML). Paragraphs on that page are
separated by runs of &nbsp; entities; we strip tags, split on &nbsp; runs, decode
numeric entities, and slice the Ratification body and the Preface body by their
textual boundaries.

1979: from the justus PD ASCII e-text bcpoffce.txt. The front matter sits at the
head of the file; we slice the '<Concerning the Service of the Church>' section
(a distinct modern text) and reflow its fixed-width paragraphs.
"""
import os, sys, re, html as _html

HERE = os.path.dirname(__file__)
WT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(WT, "tools"))
sys.path.insert(0, "tools")
import scrape  # noqa: E402


def clean(p):
    # justus renders a stray space before some commas; drop that noise. (Only
    # commas: space before colon/semicolon is authentic period French spacing
    # and is preserved.)
    p = re.sub(r"\s+,", ",", p)
    return p


def write_cell(out_rel, title, paras):
    paras = [clean(p) for p in paras]
    body = "\n\n".join(paras)
    out = f"# {title}\n\n{body}\n"
    dest = os.path.join(WT, "editions", out_rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"  wrote {out_rel}  ({len(paras)} paras, {len(out)} bytes)")


# ---------------------------------------------------------------------------
# 1789 — Ratification + Preface
# ---------------------------------------------------------------------------
def build_1789():
    raw = scrape.fetch(
        "http://justus.anglican.org/resources/bcp/1789/FrontMatter_1789.htm")
    # strip tags but keep &nbsp; entities (used as paragraph separators)
    t = re.sub(r"<[^>]+>", " ", raw)
    # paragraph separator = a run of 2+ &nbsp; (optionally space-interleaved)
    t = re.sub(r"(?:&nbsp;\s*){2,}", "", t)   # 0x01 = para break marker
    t = t.replace("&nbsp;", " ")
    t = _html.unescape(t)                            # decode &#146; etc.
    # normalise intra-paragraph whitespace, keep the para markers
    parts = [re.sub(r"\s+", " ", p).strip() for p in t.split("")]
    parts = [p for p in parts if p]

    # --- Ratification body (merged into the TOC part on this page; slice it
    #     from the full decoded text). It is a single paragraph. ---
    full = re.sub(r"\s+", " ", " ".join(parts))
    full = full.replace("T HIS Convention", "THIS Convention")
    m = re.search(r"(THIS Convention having.*?seven hundred and ninety\.)", full)
    if not m:
        raise SystemExit("  !! 1789 Ratification body not found")
    rat = m.group(1).strip()
    write_cell("1789/front-matter/ratification.md",
               "The Ratification of the Book of Common Prayer", [rat])

    # --- Preface: from "It is a most invaluable part" through
    #     "...our blessed Lord and Saviour." (before the Psalter table) ---
    start = end = None
    for i, p in enumerate(parts):
        if start is None and "most invaluable part" in p:
            start = i
        if start is not None and "our blessed Lord and Saviour" in p:
            end = i
            break
    if start is None or end is None:
        raise SystemExit(f"  !! 1789 Preface bounds not found ({start},{end})")
    pref = parts[start:end + 1]
    # strip the "PREFACE." heading label and normalise the split "I T is"
    pref[0] = re.sub(r"^\s*PREFACE\.\s*", "", pref[0])
    pref[0] = re.sub(r"^I T is", "It is", pref[0])
    # trim any trailing Psalter-table text that shares the last paragraph
    pref[-1] = re.sub(r"\s*THE ORDER.*$", "", pref[-1]).strip()
    write_cell("1789/front-matter/preface.md", "The Preface", pref)


# ---------------------------------------------------------------------------
# 1979 — Concerning the Service of the Church (distinct modern text)
# ---------------------------------------------------------------------------
def build_1979():
    t = scrape.fetch("http://justus.anglican.org/resources/bcp/bcpoffce.txt")
    # The front-matter section heading spans two lines:
    #   <Concerning the Service\nof the Church>
    # and runs (pages 13-14) up to <page 15> (the Calendar).
    m = re.search(
        r"<Concerning the Service\s+of the Church>(.*?)<page 15>", t, re.S)
    if not m:
        raise SystemExit("  !! 1979 Concerning section not found")
    block = m.group(1)
    # collapse <page N> markers WITH their surrounding blank lines to a single
    # newline, so a sentence split across a page break rejoins (not a new para)
    block = re.sub(r"\n\s*<[Pp]age\s+\d+>\s*\n", "\n", block)
    block = re.sub(r"<[^>\n]*>", "", block)   # any stray heading fragments
    block = block.replace("=", "")            # e-text italic/bold markers
    # paragraphs are separated by blank lines; reflow fixed-width wraps
    paras = []
    for chunk in re.split(r"\n\s*\n", block):
        para = re.sub(r"\s+", " ", chunk).strip()
        if para:
            paras.append(para)
    if not paras:
        raise SystemExit("  !! 1979 Concerning: no paragraphs")
    write_cell("1979/front-matter/concerning-the-service.md",
               "Concerning the Service of the Church", paras)


def main():
    build_1789()
    build_1979()


if __name__ == "__main__":
    main()
