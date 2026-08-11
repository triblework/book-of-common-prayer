#!/usr/bin/env python3
"""Keep inline `<!-- VERIFY: ... -->` comments and the provenance index in sync.

Every uncertain reading in the text is flagged inline with an HTML comment, e.g.

    <!-- VERIFY citation: source (justus) prints 'Psalm ii'; the verse is
         Psalm 51:3, likely a 'li'->'ii' printer error; confirm against a scan -->

and must be indexed so a human can resolve it. This tool reconciles the two.

Two contexts are auto-detected:

  * AUTHORING context (authoring/provenance.yaml + editions/ present): full
    bidirectional check. Every inline VERIFY across editions/ must correspond to
    a `verify_items` entry in provenance.yaml, and vice versa. This is the
    machine-readable source of truth (spec §7.1).

  * PUBLISHED context (texts/ + SOURCES.md present, no provenance.yaml): a single
    edition's tree is only a SUBSET of the corpus, so the check is forward-only —
    every inline VERIFY in texts/ must be documented somewhere in SOURCES.md.

Matching is on a normalized signature: the first single-quoted reading in the
comment / the `source_reading` field, lowercased with punctuation flattened to
spaces. This survives the small formatting differences between an inline comment
("Psalm ii") and a table cell ("Psalm ii.").

Usage:
    verify_index.py --check [--root DIR]     # exit 1 on any desync (CI)
    verify_index.py [--root DIR]             # list what was found (no failure)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    sys.stderr.write("verify_index.py requires PyYAML (python3 -m pip install pyyaml)\n")
    raise

_VERIFY_RE = re.compile(r"<!--\s*VERIFY\b(.*?)-->", re.DOTALL | re.IGNORECASE)
_QUOTED_RE = re.compile(r"'([^']+)'")


def normalize_sig(text: str) -> str:
    """Lowercase; collapse any run of non-alphanumerics to a single space; trim."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def first_reading(comment_body: str) -> str | None:
    """The first single-quoted reading in a VERIFY comment, normalized."""
    m = _QUOTED_RE.search(comment_body)
    if m:
        return normalize_sig(m.group(1))
    # Fall back to the whole comment if it has no quoted reading.
    sig = normalize_sig(comment_body)
    return sig or None


def collect_inline(md_roots: list[Path]) -> list[tuple[Path, str, str]]:
    """Return (file, raw_comment, signature) for every inline VERIFY found."""
    found: list[tuple[Path, str, str]] = []
    seen: set[tuple[str, str]] = set()  # de-dupe original/ vs normalized/ twins
    for root in md_roots:
        if not root.is_dir():
            continue
        for md in sorted(root.rglob("*.md")):
            text = md.read_text(encoding="utf-8")
            for m in _VERIFY_RE.finditer(text):
                body = m.group(1).strip()
                sig = first_reading(body)
                if sig is None:
                    continue
                # A service exists as original/ + normalized/ twins carrying the
                # same comment; key by (service-relative path, sig) to de-dupe.
                rel = md.name
                key = (rel, sig)
                if key in seen:
                    continue
                seen.add(key)
                found.append((md, body, sig))
    return found


def provenance_signatures(prov_path: Path) -> list[tuple[str, str]]:
    """Return (label, signature) for every verify_item in provenance.yaml."""
    data = yaml.safe_load(prov_path.read_text(encoding="utf-8")) or {}
    out: list[tuple[str, str]] = []
    for rec in data.get("records") or []:
        label = f"{rec.get('edition')} {rec.get('service')}"
        for item in rec.get("verify_items") or []:
            reading = item.get("source_reading")
            if reading:
                out.append((f"{label} :: {item.get('anchor', '?')}", normalize_sig(reading)))
            elif item.get("note"):
                sig = first_reading(item["note"])
                if sig:
                    out.append((f"{label} :: {item.get('anchor', '?')}", sig))
    return out


def check_authoring(authoring: Path) -> int:
    inline = collect_inline([authoring / "editions"])
    prov = provenance_signatures(authoring / "provenance.yaml")

    inline_sigs = {sig for _f, _b, sig in inline}
    prov_sigs = {sig for _l, sig in prov}

    problems: list[str] = []
    for md, body, sig in inline:
        if sig not in prov_sigs:
            problems.append(
                f"inline VERIFY not in provenance.yaml: {md.name} :: '{sig}'\n"
                f"      {body[:120]}"
            )
    for label, sig in prov:
        if sig not in inline_sigs:
            problems.append(f"provenance verify_item has no inline VERIFY: {label} :: '{sig}'")

    if problems:
        sys.stderr.write("verify_index.py --check (authoring): OUT OF SYNC.\n"
                         + "\n".join(f"  - {p}" for p in problems) + "\n")
        return 1
    sys.stdout.write(
        f"verify_index.py --check (authoring): OK — {len(inline)} inline VERIFY "
        f"comment(s) reconciled with {len(prov)} provenance verify_item(s).\n"
    )
    return 0


def check_published(root: Path) -> int:
    inline = collect_inline([root / "texts"])
    sources = root / "SOURCES.md"
    haystack = normalize_sig(sources.read_text(encoding="utf-8")) if sources.exists() else ""

    problems: list[str] = []
    for md, body, sig in inline:
        if sig not in haystack:
            problems.append(f"inline VERIFY not documented in SOURCES.md: {md} :: '{sig}'")

    if problems:
        sys.stderr.write("verify_index.py --check (published): OUT OF SYNC.\n"
                         + "\n".join(f"  - {p}" for p in problems) + "\n")
        return 1
    sys.stdout.write(
        f"verify_index.py --check (published): OK — {len(inline)} inline VERIFY "
        "comment(s) all documented in SOURCES.md.\n"
    )
    return 0


def main(argv: list[str]) -> int:
    tools_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(tools_dir.parent),
                        help="content root (authoring root, or a published repo root)")
    parser.add_argument("--check", action="store_true", help="exit 1 on any desync")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    if (root / "provenance.yaml").is_file() and (root / "editions").is_dir():
        return check_authoring(root)
    return check_published(root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
