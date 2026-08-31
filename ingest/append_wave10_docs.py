#!/usr/bin/env python3
"""Append the Wave-10 (10a) provenance block to provenance.yaml and the
'Uncertain passages' rows to SOURCES.md. Idempotent: re-running replaces the
Wave-10 block rather than duplicating it.

Usage: append_wave10_docs.py <authoring-root>
"""
import os, sys

WT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
BEGIN = "  # --- Wave 10 (10a): collects-epistles-gospels ---"
END = "  # --- end Wave 10 (10a) ---"
S_BEGIN = "<!-- wave10-10a rows: begin -->"
S_END = "<!-- wave10-10a rows: end -->"


def splice(text, begin, end, payload):
    block = f"{begin}\n{payload.rstrip()}\n{end}\n"
    if begin in text and end in text:
        head = text[:text.index(begin)]
        tail = text[text.index(end) + len(end):].lstrip("\n")
        return head + block + tail
    return text.rstrip("\n") + "\n" + block


def main():
    prov_path = os.path.join(WT, "provenance.yaml")
    block = open(os.path.join(WT, "ingest", "wave10_provenance_block.yaml"),
                 encoding="utf-8").read()
    prov = open(prov_path, encoding="utf-8").read()
    open(prov_path, "w", encoding="utf-8").write(splice(prov, BEGIN, END, block))

    rows = open(os.path.join(WT, "ingest", "wave10_sources_rows.md"),
                encoding="utf-8").read()
    src_path = os.path.join(WT, "repo-root", "SOURCES.md")
    src = open(src_path, encoding="utf-8").read()
    if S_BEGIN in src and S_END in src:
        src = splice(src, S_BEGIN, S_END, rows)
    else:
        marker = "| 1552 Morning Prayer |"
        idx = src.index(marker)
        end_of_table = src.index("\n\n", idx)
        src = (src[:end_of_table] + "\n" + S_BEGIN + "\n" + rows.rstrip()
               + "\n" + S_END + src[end_of_table:])
    open(src_path, "w", encoding="utf-8").write(src)
    print("provenance.yaml + SOURCES.md updated")


if __name__ == "__main__":
    main()
