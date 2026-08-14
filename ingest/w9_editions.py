#!/usr/bin/env python3
"""w9_editions.py — wire the Wave-9 front-matter services into editions.yaml.

Edits the flow-style present:/absent: lists in place (per edition id), inserting
the new services just before the closing ']'. Idempotent.
"""
import os, re

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH = os.path.join(WT, "editions.yaml")

CS = "front-matter/concerning-the-service"
OC = "front-matter/of-ceremonies"
PR = "front-matter/preface"
RA = "front-matter/ratification"

# per edition id: services to add to present:, services to add to absent:
ADD = {
    "1549": (["front-matter/concerning-the-service", OC], []),
    "1552": ([CS, OC], []),
    "1559": ([CS, OC], []),
    "1604": ([CS, OC], []),
    "1662": ([PR, CS, OC], []),
    "1637": ([CS, OC], []),
    "1764": ([], [CS, OC]),
    "1789": ([PR, RA], [CS, OC]),
    "1892": ([PR, RA], []),
    "1928": ([PR, RA], []),
    "1979": ([PR, RA, CS], []),
}


def add_to_list(line, services):
    """Insert services before the closing ']' of a flow list, skipping dups."""
    m = re.match(r"^(\s*(?:present|absent):\s*\[)(.*)(\]\s*)$", line)
    assert m, f"not a flow list line: {line!r}"
    head, body, tail = m.group(1), m.group(2), m.group(3)
    existing = [s.strip() for s in body.split(",") if s.strip()]
    for s in services:
        if s not in existing:
            existing.append(s)
    return head + ", ".join(existing) + tail


def main():
    with open(PATH, encoding="utf-8") as f:
        lines = f.readlines()
    cur = None
    for i, ln in enumerate(lines):
        m = re.match(r"^\s*- id:\s*(\S+)", ln)
        if m:
            cur = m.group(1)
            continue
        if cur in ADD:
            pres_add, abs_add = ADD[cur]
            if re.match(r"^\s*present:\s*\[", ln) and pres_add:
                lines[i] = add_to_list(ln.rstrip("\n"), pres_add) + "\n"
            elif re.match(r"^\s*absent:\s*\[", ln) and abs_add:
                lines[i] = add_to_list(ln.rstrip("\n"), abs_add) + "\n"
    with open(PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("editions.yaml updated")


if __name__ == "__main__":
    main()
