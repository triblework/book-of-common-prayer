#!/usr/bin/env python3
"""Enforce "one unit per line" (semantic line breaks) on liturgical Markdown.

Git diffs by line, so a reflowed paragraph shows up as one giant changed block.
To keep edition-to-edition diffs readable we put each sentence, versicle,
response, or rubric on its own line. This tool enforces that convention and,
just as importantly, is *idempotent*: running it on already-split text is a
no-op. That property is what CI checks.

What it does, line by line:
  * strips trailing whitespace
  * splits a text/blockquote line into one sentence per line, preserving any
    leading Markdown marker (``> `` for rubrics, ``**Priest.** `` style speaker
    labels stay attached to the clause they introduce)
  * leaves heading lines (``#`` ...) untouched
  * collapses 3+ consecutive blank lines to a single blank line
  * guarantees exactly one trailing newline at EOF

Sentence boundaries are detected conservatively: a boundary is a ``.``, ``?`` or
``!`` (optionally followed by a closing quote/paren) that is followed by
whitespace and then a capital letter or another sentence. A short abbreviation
allow-list prevents splitting after things like "St." or "Mr.".

Usage:
    sentence_split.py PATH [PATH ...]        # rewrite files in place
    sentence_split.py --check PATH [...]     # exit 1 if any file would change
    sentence_split.py --stdin                # read stdin, write stdout
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Abbreviations after which a period does NOT end a sentence.
_ABBREVIATIONS = {
    "mr", "mrs", "ms", "st", "dr", "rev", "hon", "esq",
    "i.e", "e.g", "cf", "viz", "chap", "ver", "vs",
    "no", "vol", "cap", "etc", "al",
    # Abbreviated books of the Bible, so marginal scripture citations like
    # "Dan. ix." or "Psa. cxliii." stay on one line instead of fragmenting.
    "gen", "exod", "lev", "num", "deut", "josh", "judg", "ruth", "sam",
    "kin", "kings", "chron", "ezra", "neh", "esth", "job", "ps", "psa",
    "psalm", "prov", "eccles", "cant", "isa", "isai", "jer", "jerem", "lam",
    "ezek", "ezech", "dan", "hos", "joel", "amos", "obad", "jon", "jonah",
    "jere", "psal", "matt", "math", "matth",
    "mic", "nah", "hab", "zeph", "hag", "zech", "mal",
    # Wave 14: abbreviations printed in the Kalendar's annotation column
    # (saints' days, astronomical notes and law-term notes) and in archaic
    # lesson citations. Additive: an entry here can only PREVENT a split, so it
    # cannot fragment text that is correct today.
    "andr", "annun", "annuncia", "apo", "apos", "barna", "barnab", "bart",
    "bartho", "beg", "beh", "con", "convers", "edw", "evan", "incap", "inv",
    "ja", "jo", "januarii", "laur", "laurence", "libr", "luc", "mar", "marg",
    "na", "nat", "port", "pur", "puri", "rich", "sainct", "scorp", "sol",
    "tho", "tr", "v", "visit", "w", "s",
    "acte", "gene", "genes", "hiere", "hierem", "esaie", "sapie", "eccls",
    "judic", "josue", "hester", "mala", "dani", "naum", "agge", "zach",
    "toby", "judi", "hebre", "ephe", "ephes", "collos", "coloss", "roma",
    "math", "mathe", "jhon", "levi", "leviti", "nume", "deu", "deute",
    "reg", "esd", "thren", "ezech", "osee", "abdi", "michae", "abac",
    "sopho", "corin", "gala", "thessa", "timo", "tite", "phile", "jame",
    "pete", "apoca", "philip", "machab", "sap", "tobi", "exo",
    "joh", "less", "sy", "ju", "sim", "jud", "m", "a", "anti",
    "di", "luk", "hagg", "jude", "abd", "soph", "mich",
    "magd", "aeq", "sar", "prid", "kl", "id", "no", "circumci",
    "epiphani", "pau", "purif", "trans", "trin", "dedic",
    "mark", "luke", "john", "acts", "rom", "cor", "gal", "eph", "phil",
    "col", "thess", "tim", "tit", "philem", "heb", "jas", "pet", "rev",
}

# A sentence terminator: . ? or !, optionally followed by closing quotes/parens.
_TERMINATOR = re.compile(r"""([.?!]+['")\]]*)(\s+)(?=\S)""")


def _leading_marker(line: str) -> tuple[str, str]:
    """Split a line into (marker, rest).

    The marker is a leading blockquote prefix (one or more ``> ``) that we must
    re-attach to every sentence produced from the line. Speaker labels such as
    ``**Priest.**`` are treated as part of the body (they cling to the following
    clause), so they are not returned here.
    """
    m = re.match(r"^((?:>\s?)+)", line)
    if m:
        return m.group(1), line[m.end():]
    return "", line


def _looks_like_abbrev(chunk: str) -> bool:
    """True if ``chunk`` ends with an allow-listed abbreviation + period."""
    tail = re.search(r"([A-Za-z.]+)\.$", chunk.strip())
    if not tail:
        return False
    word = tail.group(1).lower().rstrip(".")
    return word in _ABBREVIATIONS


def split_sentences(body: str) -> list[str]:
    """Split a single logical line of prose into one sentence per element."""
    body = body.strip()
    if not body:
        return []

    pieces: list[str] = []
    start = 0
    for m in _TERMINATOR.finditer(body):
        candidate = body[start:m.end(1)]
        # Don't split inside an allow-listed abbreviation.
        if _looks_like_abbrev(candidate):
            continue
        # Don't split when the next token starts with a digit: a real sentence
        # almost never begins with a number, but numeric scripture references
        # ("Ezek. 18. 31. 32.", "Joel 2. 13") do — keep them intact.
        if m.end() < len(body) and body[m.end()].isdigit():
            continue
        pieces.append(candidate.strip())
        start = m.end()
    tail = body[start:].strip()
    if tail:
        pieces.append(tail)
    return pieces or [body]


def process_text(text: str) -> str:
    out_lines: list[str] = []
    blank_run = 0
    for raw in text.splitlines():
        line = raw.rstrip()
        if line == "":
            blank_run += 1
            if blank_run <= 1:
                out_lines.append("")
            continue
        blank_run = 0

        # Headings pass through verbatim (still trailing-stripped above).
        if line.lstrip().startswith("#"):
            out_lines.append(line)
            continue

        # HTML comments (editorial VERIFY/SCOPE notes) are metadata: keep the
        # whole comment on one line rather than splitting it into sentences.
        if line.lstrip().startswith("<!--"):
            out_lines.append(line)
            continue

        marker, body = _leading_marker(line)
        for sentence in split_sentences(body):
            out_lines.append(f"{marker}{sentence}".rstrip())

    # Drop trailing blank lines, then guarantee exactly one trailing newline.
    while out_lines and out_lines[-1] == "":
        out_lines.pop()
    return "\n".join(out_lines) + "\n" if out_lines else ""


def _iter_files(paths: list[str]):
    for p in paths:
        path = Path(p)
        if path.is_dir():
            yield from sorted(path.rglob("*.md"))
        else:
            yield path


def main(argv: list[str]) -> int:
    args = list(argv)
    check = False
    if "--check" in args:
        check = True
        args.remove("--check")

    if "--stdin" in args:
        sys.stdout.write(process_text(sys.stdin.read()))
        return 0

    if not args:
        sys.stderr.write(__doc__ or "")
        return 2

    changed: list[Path] = []
    for path in _iter_files(args):
        original = path.read_text(encoding="utf-8")
        result = process_text(original)
        if result != original:
            changed.append(path)
            if not check:
                path.write_text(result, encoding="utf-8")

    if check and changed:
        sys.stderr.write(
            "sentence_split: the following files are not normalized:\n"
            + "\n".join(f"  {p}" for p in changed)
            + "\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
