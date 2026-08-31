#!/usr/bin/env python3
"""w10_coe.py — build the 1662 propers from the Church of England pages.

Authoring-only; NOT published. File -> file: text flows page -> script -> file
and is never emitted as model output.

The CoE pages are semantically classed, which makes the Decision-B reading depth
exact rather than approximate:

    h2.vlServiceHeading   the occasion title
    h3.vlitemheading      the section (The Collect / The Epistle / The Gospel)
    p.vlnormal            spoken text  -> the collect
    p.vlrubric            a rubric     -> '> ' line
    p.vlbiblereference    the citation -> what we keep
    p.vlreading           the reading body -> NEVER read

Every 1662 file carries the Crown-copyright acknowledgment (NOTICE.md, spec 8).
"""
import html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, "tools")
import scrape                      # noqa: E402
from w10_cite import canonical     # noqa: E402

BASE = ("https://www.churchofengland.org/prayer-and-worship/worship-texts-and-"
        "resources/book-common-prayer/collects-epistles-and-gospels")

ACK = ("<!-- BCP 1662 — reproduced with the Crown-copyright acknowledgment "
       "required in the UK; see NOTICE.md -->")

# CoE slug -> our occasion slug, for sub-wave 10a.
SLUGS = [
    ("-1", "advent-1"), ("-2", "advent-2"), ("-3", "advent-3"), ("-4", "advent-4"),
    ("-6", "christmas-day"), ("-7", "christmas-1"), ("-8", "circumcision"),
    ("-9", "epiphany"),
    ("-10", "epiphany-1"), ("-11", "epiphany-2"), ("-12", "epiphany-3"),
    ("-13", "epiphany-4"), ("-14", "epiphany-5"), ("-15", "epiphany-6"),
    # ---- sub-wave 10b ---- ("/ash" is a path suffix, not a numbered slug)
    ("-16", "septuagesima"), ("-17", "sexagesima"), ("-18", "quinquagesima"),
    ("/ash", "ash-wednesday"),
    ("-20", "lent-1"), ("-21", "lent-2"), ("-22", "lent-3"), ("-23", "lent-4"),
    ("-24", "lent-5"), ("-25", "palm-sunday"),
    ("-26", "monday-before-easter"), ("-27", "tuesday-before-easter"),
    ("-28", "wednesday-before-easter"), ("-29", "thursday-before-easter"),
    ("-30", "good-friday"), ("-31", "easter-even"),
    # ---- sub-wave 10c (derived from coe_slug_map.tsv, not hand-typed;
    # note the site numbers Trinity 1 BEFORE Trinity Sunday) ----
    ("-32", "easter-day"),
    ("-33", "easter-monday"),
    ("-34", "easter-tuesday"),
    ("-35", "easter-1"),
    ("-36", "easter-2"),
    ("-37", "easter-3"),
    ("-38", "easter-4"),
    ("-39", "easter-5"),
    ("-40", "ascension-day"),
    ("-41", "ascension-1"),
    ("-42", "whitsunday"),
    ("-43", "whit-monday"),
    ("-44", "whit-tuesday"),
    ("-45", "trinity-1"),
    ("-46", "trinity-sunday"),
    ("-47", "trinity-2"),
    ("-48", "trinity-3"),
    ("-49", "trinity-4"),
    ("-50", "trinity-5"),
    ("-51", "trinity-6"),
    ("-52", "trinity-7"),
    ("-53", "trinity-8"),
    ("-54", "trinity-9"),
    ("-55", "trinity-10"),
    ("-56", "trinity-11"),
    ("-57", "trinity-12"),
    ("-58", "trinity-13"),
    ("-59", "trinity-14"),
    ("-60", "trinity-15"),
    ("-61", "trinity-16"),
    ("-62", "trinity-17"),
    ("-63", "trinity-18"),
    ("-64", "trinity-19"),
    ("-65", "trinity-20"),
    ("-66", "trinity-21"),
    ("-67", "trinity-22"),
    ("-68", "trinity-23"),
    ("-69", "trinity-24"),
    ("-70", "trinity-25"),
]

TAG = re.compile(
    r'<(?P<tag>h2|h3|p)\b[^>]*class="(?P<cls>[^"]*)"[^>]*>(?P<body>.*?)</(?P=tag)>',
    re.S | re.I)


def text_of(fragment):
    s = re.sub(r"<[^>]+>", "", fragment)
    s = html.unescape(s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


H1 = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.S | re.I)


def title_of(doc):
    """The occasion title: h2.vlServiceHeading on some pages, a bare h1 on most."""
    m = re.search(r'<h2\b[^>]*class="[^"]*vlServiceHeading[^"]*"[^>]*>(.*?)</h2>',
                  doc, re.S | re.I)
    if m:
        return text_of(m.group(1))
    for m in H1.finditer(doc):
        candidate = text_of(m.group(1))
        if candidate and candidate.lower() not in {"site nav", "footer", "social",
                                                   "breadcrumb"}:
            return candidate
    return None


def parse(doc):
    """Return the occasion's title and its ordered sections."""
    cell = {"title": None, "collect": [], "rubrics": [],
            "epistle": None, "gospel": None}
    cell["title"] = title_of(doc)
    section = None
    for m in TAG.finditer(doc):
        cls, body = m.group("cls"), m.group("body")
        content = text_of(body)
        if not content:
            continue
        if "vlServiceHeading" in cls:
            if cell["title"] is None:
                cell["title"] = content
            continue
        if "vlitemheading" in cls:
            low = content.lower()
            if "collect" in low:
                section = "collect"
            elif "epistle" in low:
                section = "epistle"
                cell["epistle"] = {"cite": None,
                                   "for_the": low.startswith("for the")}
            elif "gospel" in low:
                section = "gospel"
                cell["gospel"] = {"cite": None, "for_the": False}
            else:
                section = None
            continue
        if "vlreading" in cls:
            continue                      # the reading body: never transcribed
        if "vlbiblereference" in cls:
            if section in ("epistle", "gospel") and cell[section]:
                cell[section]["cite"] = content
            continue
        if "vlrubric" in cls:
            cell["rubrics"].append(content)
            continue
        if "vlnormal" in cls and section == "collect":
            cell["collect"].append(content)
    return cell


def render(cell):
    parts = [ACK, "", f"# {cell['title']}", ""]
    if cell["collect"]:
        parts += ["## The Collect", ""]
        for para in cell["collect"]:
            parts += [para, ""]
    for rub in cell["rubrics"]:
        parts += ["> " + rub, ""]
    for anchor, slot in (("The Epistle", cell["epistle"]),
                         ("The Gospel", cell["gospel"])):
        if not slot or not slot.get("cite"):
            continue
        parts += [f"## {anchor}", ""]
        if slot.get("for_the"):
            parts += ["> For the Epistle.", ""]
        parts += [canonical(slot["cite"]), ""]
    text = "\n".join(parts)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def main():
    out = []
    for coe_slug, slug in SLUGS:
        doc = scrape.fetch(BASE + coe_slug)
        cell = parse(doc)
        # Monday-Thursday before Easter carry NO proper Collect in 1662 -- Palm
        # Sunday's serves all week -- so a cell with only readings is valid.
        has_reading = any(cell[k] and cell[k].get("cite") for k in ("epistle", "gospel"))
        if not cell["title"] or not (cell["collect"] or has_reading):
            print(f"  !! {slug}: title={cell['title']!r} collect={len(cell['collect'])}")
            continue
        dest = os.path.abspath(os.path.join(
            HERE, "..", "editions", "1662", "collects-epistles-gospels", f"{slug}.md"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(render(cell))
        ep = cell["epistle"] and cell["epistle"]["cite"]
        go = cell["gospel"] and cell["gospel"]["cite"]
        out.append(f"  {slug:14s} {cell['title'][:40]:42s} {ep} / {go}")
    print("\n".join(out))
    print(f"1662: {len(out)} cells")


if __name__ == "__main__":
    main()
