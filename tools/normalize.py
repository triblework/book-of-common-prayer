#!/usr/bin/env python3
"""Generate texts/normalized/ from texts/original/ by applying spelling rules.

The normalized tree is NEVER hand-edited. It is a deterministic function of the
original tree and tools/normalization_rules.yaml, so that:

  * normalization is reproducible (CI can regenerate and diff),
  * improvements to the rules are themselves reviewable as diffs, and
  * the two trees stay in lock-step.

Normalization is SPELLING ONLY (see normalization_rules.yaml). This script does
not know anything about liturgy; it only rewrites tokens according to the rules.

Determinism: same input + same rules => byte-identical output.

Usage:
    normalize.py                     # regenerate texts/normalized/ from original/
    normalize.py --check             # exit 1 if normalized/ is out of date
    normalize.py --root DIR          # repo root (default: parent of tools/)
    normalize.py --rules FILE        # rules file (default: tools/normalization_rules.yaml)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    sys.stderr.write(
        "normalize.py requires PyYAML. Install it with:\n"
        "    python3 -m pip install pyyaml\n"
    )
    raise


# A "word" for whole-word replacement: a run of letters plus a few in-word
# marks (apostrophe, thorn). Markdown punctuation is treated as a boundary.
_WORD_RE = re.compile(r"[A-Za-zþÞ']+")

_RE_FLAG_MAP = {"i": re.IGNORECASE, "m": re.MULTILINE, "s": re.DOTALL}


class Normalizer:
    def __init__(self, rules: dict):
        self.protect = {w.lower() for w in rules.get("protect", [])}
        # Lower-cased source -> replacement, for case-aware substitution.
        self.words = {
            str(k).lower(): str(v)
            for k, v in (rules.get("word_replacements") or {}).items()
        }
        self.regex_rules = []
        for r in rules.get("regex_rules") or []:
            flags = 0
            for ch in r.get("flags", ""):
                flags |= _RE_FLAG_MAP.get(ch, 0)
            self.regex_rules.append(
                (r.get("name", "?"), re.compile(r["pattern"], flags), r["replacement"])
            )

    @staticmethod
    def _match_case(source: str, target: str) -> str:
        """Cast ``target`` to the casing pattern of ``source``."""
        if source.isupper():
            return target.upper()
        if source[:1].isupper():
            return target[:1].upper() + target[1:]
        return target

    def _replace_word(self, m: re.Match) -> str:
        word = m.group(0)
        low = word.lower()
        if low in self.protect:
            return word
        target = self.words.get(low)
        if target is None:
            return word
        return self._match_case(word, target)

    def normalize_line(self, line: str) -> str:
        line = _WORD_RE.sub(self._replace_word, line)
        for _name, pattern, repl in self.regex_rules:
            line = pattern.sub(repl, line)
        return line

    def normalize_text(self, text: str) -> str:
        # splitlines(keepends=False) + rejoin keeps LF endings and the single
        # trailing newline convention that original/ already satisfies.
        lines = text.split("\n")
        return "\n".join(self.normalize_line(ln) for ln in lines)


def load_rules(rules_path: Path) -> dict:
    with rules_path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def generate(root: Path, rules_path: Path, check: bool) -> int:
    original_root = root / "texts" / "original"
    normalized_root = root / "texts" / "normalized"
    if not original_root.is_dir():
        sys.stderr.write(f"normalize.py: no such directory {original_root}\n")
        return 2

    normalizer = Normalizer(load_rules(rules_path))

    stale: list[Path] = []
    expected_files: set[Path] = set()

    for src in sorted(original_root.rglob("*.md")):
        rel = src.relative_to(original_root)
        dst = normalized_root / rel
        expected_files.add(dst)
        produced = normalizer.normalize_text(src.read_text(encoding="utf-8"))

        current = dst.read_text(encoding="utf-8") if dst.exists() else None
        if current != produced:
            stale.append(dst)
            if not check:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(produced, encoding="utf-8")

    # Detect orphaned normalized files with no original counterpart.
    if normalized_root.is_dir():
        for existing in sorted(normalized_root.rglob("*.md")):
            if existing not in expected_files:
                stale.append(existing)
                if not check:
                    existing.unlink()

    if check and stale:
        sys.stderr.write(
            "normalize.py --check: texts/normalized/ is out of date.\n"
            "Regenerate with `python3 tools/normalize.py`. Affected:\n"
            + "\n".join(f"  {p.relative_to(root)}" for p in stale)
            + "\n"
        )
        return 1
    return 0


def main(argv: list[str]) -> int:
    tools_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(tools_dir.parent))
    parser.add_argument("--rules", default=str(tools_dir / "normalization_rules.yaml"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return generate(Path(args.root), Path(args.rules), args.check)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
