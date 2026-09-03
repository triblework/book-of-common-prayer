#!/usr/bin/env python3
"""w14_1979.py — parse the 1979 Lectionary e-text (Wave 14).

Authoring-only; NOT published. Source: the eleventh part of the public-domain
1979 e-text, `bcplectn.txt` (pp. 887-1001), which no prior wave had fetched.
It carries BOTH 1979 lectionaries:

  * The Lectionary          pp. 888-931  three-year eucharistic (Years A/B/C)
  * Daily Office Lectionary pp. 934-1001 two-year (Years One/Two)

Structure of the e-text (verified, not assumed):

  <Section Heading>            angle brackets, column 0
  Occasion Name:               column 0, ends with ':' or ': =subtitle='
    citation; citation; ...    indented two spaces, MAY WRAP TO COLUMN 0

The wrap is the trap: a continuation line sits at column 0 like an occasion
heading. The discriminator is structural and exact — an occasion line ENDS with
':' (optionally followed by an '=subtitle='); a continuation never does.

Daily Office entries add a psalm line of their own:

  Sunday:  146, 147; 111, 112, 113        morning psalms ; evening psalms
    Isa. 1:1-9; 2 Pet. 3:1-10; ...        the readings

This module only PARSES and REPORTS. Writing cells is w14_build_1979.py, so no
liturgical body is ever emitted as model tokens (HANDOFF §6).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "tools"))

URL = "http://justus.anglican.org/resources/bcp/bcplectn.txt"

# An occasion heading: column 0, ends with ':' or ': =subtitle='.
OCCASION = re.compile(r"^(?P<name>[A-Z0-9][^:]*):\s*(?:=(?P<sub>[^=]*)=)?\s*$")
# A Daily Office day heading carries its psalms on the same line.
DAYLINE = re.compile(r"^(?P<name>[A-Z][A-Za-z0-9 .'()/-]*?):\s+(?P<ps>\S.*)$")
HEADING = re.compile(r"^<(?P<h>[^>]+)>\s*$")
PAGE = re.compile(r"^<page (\d+)>\s*$")


def _fetch():
    import scrape
    return scrape.fetch(URL)


def strip_markup(s):
    """The e-text marks italics with *...* and bold with =...=."""
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"=(.+?)=", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def load_lines(text=None):
    text = text if text is not None else _fetch()
    lines = text.split("\n")
    # Drop the FTP/README header that precedes the first real heading.
    for i, l in enumerate(lines):
        if l.strip() == "<The Lectionary>":
            return lines[i:]
    raise SystemExit("w14_1979: '<The Lectionary>' heading not found")


def split_books(lines):
    for i, l in enumerate(lines):
        if l.strip() == "<Daily Office Lectionary>":
            return lines[:i], lines[i:]
    raise SystemExit("w14_1979: Daily Office Lectionary heading not found")


# A field that does not begin with a book name is a CONTINUATION of the previous
# field: the book prints multi-part readings as "Galatians 3:23-25; 4:4-7" and
# "Acts 11:19-30; 13:1-3", so ';' alone is not a field separator. The
# discriminator is structural (does this field name a book?), not a guess about
# content.
# NOTE: a numbered book ("2 Pet. 3:1-10", "1 Corinthians 1:1-9") also begins
# with a digit, so the test must require punctuation after the number: a
# continuation is "4:4-7" / "13:1" / "(5:1-20)", never "2 Peter ...".
_CONTINUATION = re.compile(r"^(?:\(|[0-9]+\s*[:.,-])")


def split_fields(raw):
    """Split a citation string into fields, rejoining ';'-internal readings."""
    parts = [c.strip() for c in raw.split(";")]
    out = []
    for i, c in enumerate(parts):
        if not c:
            continue
        if out and _CONTINUATION.match(c) and i > 0 and out[-1] and not _CONTINUATION.match(out[-1]):
            out[-1] = out[-1] + "; " + c
        else:
            out.append(c)
    return out


def _flush(buf):
    return strip_markup(" ".join(x.strip() for x in buf if x.strip()))


def parse_eucharistic(lines):
    """-> list of dicts {section, occasion, subtitle, citations:[...], pages}"""
    out = []
    section = "Year A"          # the <Year A> heading died with page 889
    cur = None
    buf = []
    page = None
    for l in lines:
        mp = PAGE.match(l.strip())
        if mp:
            page = int(mp.group(1))
            continue
        mh = HEADING.match(l.strip())
        if mh:
            h = mh.group("h").strip().rstrip(":")
            if cur:
                cur["raw"] = _flush(buf); out.append(cur); cur, buf = None, []
            if h in ("Year B", "Year C"):
                section = h
            elif h in ("Holy Days", "The Common of Saints", "Various Occasions"):
                section = h
            elif h == "The Season after Pentecost":
                pass       # a sub-heading inside the current year
            continue
        mo = OCCASION.match(l)
        if mo and not l.startswith(" "):
            if cur:
                cur["raw"] = _flush(buf); out.append(cur)
            cur = {"section": section, "occasion": mo.group("name").strip(),
                   "subtitle": (mo.group("sub") or "").strip(), "page": page}
            buf = []
            continue
        if cur is not None:
            if not l.strip():
                if buf:
                    cur["raw"] = _flush(buf); out.append(cur); cur, buf = None, []
                continue
            buf.append(l)
    if cur:
        cur["raw"] = _flush(buf); out.append(cur)
    for e in out:
        e["citations"] = split_fields(e["raw"])
    return out


def parse_daily_office(lines):
    """-> list of dicts {year, week, day, psalms, readings, page}"""
    out = []
    year = None
    week = None
    cur = None
    buf = []
    page = None
    for l in lines:
        mp = PAGE.match(l.strip())
        if mp:
            page = int(mp.group(1)); continue
        mh = HEADING.match(l.strip())
        if mh:
            h = mh.group("h").strip()
            if cur:
                cur["raw"] = _flush(buf); out.append(cur); cur, buf = None, []
            hs = strip_markup(h).strip()
            if hs in ("Year One", "Year Two"):
                year = hs; week = None
            elif hs.startswith("/Year"):
                pass
            elif hs == "Daily Office Lectionary":
                pass
            else:
                week = hs
            continue
        md = DAYLINE.match(l)
        if md and not l.startswith(" "):
            if cur:
                cur["raw"] = _flush(buf); out.append(cur)
            cur = {"year": year, "week": week, "day": md.group("name").strip(),
                   "psalms": strip_markup(md.group("ps")), "page": page}
            buf = []
            continue
        if cur is not None:
            if not l.strip():
                if buf:
                    cur["raw"] = _flush(buf); out.append(cur); cur, buf = None, []
                continue
            buf.append(l)
    if cur:
        cur["raw"] = _flush(buf); out.append(cur)
    for e in out:
        e["readings"] = split_fields(e["raw"])
    return out


def report():
    lines = load_lines()
    eu, do = split_books(lines)
    E = parse_eucharistic(eu)
    D = parse_daily_office(do)
    from collections import Counter, OrderedDict
    print("EUCHARISTIC: %d entries" % len(E))
    c = Counter(e["section"] for e in E)
    for k in ("Year A", "Year B", "Year C", "Holy Days",
              "The Common of Saints", "Various Occasions"):
        print("   %-24s %3d" % (k, c.get(k, 0)))
    nf = Counter(len(e["citations"]) for e in E)
    print("   citations-per-entry:", dict(sorted(nf.items())))
    empty = [e for e in E if not e["citations"]]
    print("   entries with NO citation: %d %s"
          % (len(empty), [e["occasion"][:40] for e in empty][:6]))
    print("DAILY OFFICE: %d entries" % len(D))
    c2 = Counter(e["year"] for e in D)
    for k, v in c2.items():
        print("   %-24s %3d" % (k, v))
    nr = Counter(len(e["readings"]) for e in D)
    print("   readings-per-entry:", dict(sorted(nr.items())))
    print("   weeks:", len(set((e["year"], e["week"]) for e in D)))
    return E, D


if __name__ == "__main__":
    report()
