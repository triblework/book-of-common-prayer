#!/usr/bin/env python3
"""w10_editions.py — wire the Wave-10 (10a) propers into editions.yaml.

Authoring-only. Edits the flow-style present:/absent: lists in place, per
edition id, inserting before the closing ']'. Idempotent.

Presence follows the sources (WAVE10_GUIDE.md 5):
  1549/1552/1559/1604  13 occasions (only five Sundays after the Epiphany)
  1662                 +epiphany-6 (a clean insert at v1604->v1662)
  1637                 13, from 1604; the Scottish line never gains epiphany-6
  1764                 all absent (Communion-only "Wee Bookie"); 1929 inherits
  1789/1892/1928       +christmas-2 (an American addition) = 15
  1979                 +epiphany-7, epiphany-8, epiphany-last = 18
"""
import os, re

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH = os.path.join(WT, "editions.yaml")
F = "collects-epistles-gospels/"

BASE13 = [F + s for s in (
    "advent-1", "advent-2", "advent-3", "advent-4", "christmas-day",
    "christmas-1", "circumcision", "epiphany", "epiphany-1", "epiphany-2",
    "epiphany-3", "epiphany-4", "epiphany-5")]
EP6 = [F + "epiphany-6"]
XMAS2 = [F + "christmas-2"]
NEW1979 = [F + s for s in ("epiphany-7", "epiphany-8", "epiphany-last")]

# ---- sub-wave 10b ----
GESIMA = [F + s for s in ("septuagesima", "sexagesima", "quinquagesima")]
LENT = [F + s for s in ("ash-wednesday", "lent-1", "lent-2", "lent-3", "lent-4",
                        "lent-5")]
HOLYWEEK = [F + s for s in (
    "palm-sunday", "monday-before-easter", "tuesday-before-easter",
    "wednesday-before-easter", "thursday-before-easter", "good-friday",
    "easter-even")]
W10B = GESIMA + LENT + HOLYWEEK

AMERICAN = BASE13 + EP6 + XMAS2

ADD = {
    "1549": (BASE13 + W10B, []),
    "1552": (BASE13 + W10B, []),
    "1559": (BASE13 + W10B, []),
    "1604": (BASE13 + W10B, []),
    "1662": (BASE13 + EP6 + W10B, []),
    "1637": (BASE13 + W10B, []),
    "1764": ([], BASE13 + W10B),
    "1929": ([], []),
    "1789": (AMERICAN + W10B, []),
    "1892": (AMERICAN + W10B, []),
    "1928": (AMERICAN + W10B, []),
    # 1979 abolishes the pre-Lent "Gesima" Sundays -> a genuine drop.
    "1979": (AMERICAN + NEW1979 + LENT + HOLYWEEK, GESIMA),
}


def add_to_list(line, services):
    m = re.match(r"^(\s*(?:present|absent):\s*\[)(.*)(\]\s*)$", line)
    assert m, f"not a flow list line: {line!r}"
    head, body, tail = m.group(1), m.group(2), m.group(3)
    existing = [s.strip() for s in body.split(",") if s.strip()]
    for s in services:
        if s not in existing:
            existing.append(s)
    return head + ", ".join(existing) + tail


def main():
    with open(PATH, encoding="utf-8") as fh:
        lines = fh.readlines()
    cur = None
    for i, ln in enumerate(lines):
        m = re.match(r"^\s*- id:\s*(\S+)", ln)
        if m:
            cur = m.group(1)
            continue
        if cur in ADD:
            pres, absent = ADD[cur]
            if re.match(r"^\s*present:\s*\[", ln) and pres:
                lines[i] = add_to_list(ln.rstrip("\n"), pres) + "\n"
            elif re.match(r"^\s*absent:\s*\[", ln) and absent:
                lines[i] = add_to_list(ln.rstrip("\n"), absent) + "\n"
    with open(PATH, "w", encoding="utf-8") as fh:
        fh.writelines(lines)
    print("editions.yaml wired")


if __name__ == "__main__":
    main()
