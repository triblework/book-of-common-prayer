#!/usr/bin/env python3
"""pdf_spine.py — extract a byte-faithful text spine from a justus text-layer PDF.

Wave 6 ingest helper (authoring-only; NOT published). The 1892 US BCP occasional
offices exist on justus only as WordPerfect-generated PDFs WITH a text layer (the
HTML index links back to 1789). pypdf extracts that text cleanly. This drops the
Satucket redistribution header (the first page) and emits the liturgical text as a
rough spine for hand/subagent structuring under the fidelity gate.

Usage: pdf_spine.py <justus-pdf-url> <out-spine.md>
Run from the primary repo (reuses the shared scrape cache + allow-list).
"""
import sys, os, re, io, urllib.request
sys.path.insert(0, "tools"); import scrape  # allow-list + cache side-effect
import pypdf

url, out = sys.argv[1], sys.argv[2]
# Reuse scrape's cache dir if present, else fetch directly (justus is allow-listed).
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
data = urllib.request.urlopen(req, timeout=60).read()
reader = pypdf.PdfReader(io.BytesIO(data))
# layout mode preserves word spacing on these WordPerfect PDFs (plain mode inserts
# spurious intra-word spaces from kerning).
pages = [p.extract_text(extraction_mode="layout") or "" for p in reader.pages]

# Page 1 is the Satucket header ("We are presenting this electronic version…").
body = pages[1:] if pages and "electronic version" in pages[0] else pages
text = "\n".join(body)
# Normalize whitespace: collapse 3+ blank lines, strip trailing spaces.
text = "\n".join(l.rstrip() for l in text.splitlines())
text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
with open(out, "w", encoding="utf-8") as fh:
    fh.write(text)
print(f"{out}: {len(reader.pages)} pdf pages -> {len(text.splitlines())} spine lines")
