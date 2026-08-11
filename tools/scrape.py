#!/usr/bin/env python3
"""Fetch + clean + convert source HTML into a first-pass Markdown transcription.

This tool is ASSISTIVE, not authoritative. Clean transcription of 16th–20th
century liturgy needs human judgment, so the intended workflow is:

    1. scrape.py fetches a source page (cached, rate-limited, allow-listed),
    2. it strips site chrome and converts the liturgical HTML to rough Markdown
       following the format conventions in the brief §3,
    3. a human verifies the result against a page scan, marks anything doubtful
       with an ``<!-- VERIFY: ... -->`` comment, and only then commits it,
    4. sentence_split.py + normalize.py finish the mechanical formatting.

Guardrails (brief §1 and §7):
    * Only allow-listed source domains may be fetched. Anything else is refused.
    * Responses are cached under scrape-cache/ (gitignored) so re-runs are free
      and polite.
    * Requests are rate-limited (>= MIN_INTERVAL seconds apart).
    * robots.txt is consulted and honored for each host.

Usage:
    scrape.py URL [--out FILE] [--title "The Order for Morning Prayer"]
    scrape.py URL --raw            # print cleaned text without markdown massaging
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

# Only these hosts may be fetched (brief §1, §7). Add-only, reviewed via diff.
# A host is added ONLY after confirming the licensing of what we take from it.
ALLOWED_HOSTS = {
    "justus.anglican.org",       # Charles Wohlers / Society of Archbishop Justus
    "commons.wikimedia.org",     # public-domain page scans for cross-checking
    "upload.wikimedia.org",
    "www.loc.gov",               # Library of Congress
    "loc.gov",
    # Church of England — the authoritative publisher of the 1662 text, whose
    # UK rights are Crown copyright administered by CUP. We reproduce the 1662
    # text with the required `BCP 1662` acknowledgment (see NOTICE.md). Used
    # only because justus serves 1662 as a ligature-heavy PDF that cannot be
    # extracted faithfully without OCR.
    "www.churchofengland.org",
}

USER_AGENT = "bcp-diff-repo/1.0 (+https://github.com; liturgical text archival; contact via repo)"
MIN_INTERVAL = 1.0  # seconds between network requests (politeness)
CACHE_DIR = Path(__file__).resolve().parent.parent / "scrape-cache"

_LAST_REQUEST = [0.0]
_ROBOTS_CACHE: dict[str, "_Robots"] = {}


class _Robots:
    """Minimal, correct robots.txt matcher.

    Python's stdlib ``urllib.robotparser`` mis-handles the ``*``/``$`` wildcard
    extensions and the grouping in some real-world files (e.g. it returns a
    blanket deny for pages that are actually allowed). This implements the
    modern de-facto rules used by Google/Bing: group by User-agent, then for a
    given path the matching Allow/Disallow rule with the LONGEST pattern wins;
    ties go to Allow; an empty ``Disallow:`` means "allow all"; if no rule
    matches, the path is allowed.
    """

    def __init__(self, text: str, user_agent: str):
        self.rules: list[tuple[bool, re.Pattern]] = []  # (is_allow, compiled)
        ua_token = user_agent.split("/", 1)[0].lower()

        groups: list[tuple[set[str], list[tuple[bool, str]]]] = []
        cur_agents: set[str] = set()
        cur_rules: list[tuple[bool, str]] = []
        expecting_agent = True

        def flush():
            if cur_agents:
                groups.append((set(cur_agents), list(cur_rules)))

        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            field, _, value = line.partition(":")
            field = field.strip().lower()
            value = value.strip()
            if field == "user-agent":
                if not expecting_agent:
                    flush()
                    cur_agents = set()
                    cur_rules = []
                    expecting_agent = True
                cur_agents.add(value.lower())
            elif field in ("allow", "disallow"):
                expecting_agent = False
                cur_rules.append((field == "allow", value))
        flush()

        chosen: list[tuple[bool, str]] = []
        for agents, rules in groups:
            if ua_token in agents or user_agent.lower() in agents:
                chosen = rules
                break
        else:
            for agents, rules in groups:
                if "*" in agents:
                    chosen = rules
                    break

        for is_allow, pattern in chosen:
            if pattern == "" and not is_allow:
                continue  # empty Disallow: => no restriction
            self.rules.append((is_allow, self._compile(pattern)))

    @staticmethod
    def _compile(pattern: str) -> re.Pattern:
        out = ["^"]
        for ch in pattern:
            if ch == "*":
                out.append(".*")
            elif ch == "$":
                out.append("$")
            else:
                out.append(re.escape(ch))
        return re.compile("".join(out))

    def can_fetch(self, url: str) -> bool:
        path = urllib.parse.urlparse(url).path or "/"
        best_len = -1
        best_allow = True
        for is_allow, rx in self.rules:
            m = rx.match(path)
            if m:
                length = m.end()
                if length > best_len or (length == best_len and is_allow):
                    best_len = length
                    best_allow = is_allow
        return best_allow


def _check_host(url: str) -> str:
    host = urllib.parse.urlparse(url).hostname or ""
    if host.lower() not in ALLOWED_HOSTS:
        raise SystemExit(
            f"REFUSED: {host!r} is not in the allow-list.\n"
            f"Allowed hosts: {sorted(ALLOWED_HOSTS)}\n"
            "Add a host to ALLOWED_HOSTS only after confirming its licensing (brief §1)."
        )
    return host


def _robots_ok(url: str) -> bool:
    parts = urllib.parse.urlparse(url)
    base = f"{parts.scheme}://{parts.netloc}"
    if base not in _ROBOTS_CACHE:
        robots_url = urllib.parse.urljoin(base, "/robots.txt")
        try:
            req = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as resp:
                text = resp.read().decode("utf-8", errors="replace")
            _ROBOTS_CACHE[base] = _Robots(text, USER_AGENT)
        except Exception:
            # If robots.txt is unreachable, err on the side of allowing the
            # single, rate-limited, allow-listed fetch.
            _ROBOTS_CACHE[base] = None  # type: ignore[assignment]
    robots = _ROBOTS_CACHE[base]
    if robots is None:
        return True
    return robots.can_fetch(url)


def _cache_path(url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", url.split("://", 1)[-1])[:80]
    return CACHE_DIR / f"{safe}.{digest}.html"


def fetch(url: str, force: bool = False) -> str:
    _check_host(url)
    cache = _cache_path(url)
    if cache.exists() and not force:
        return cache.read_text(encoding="utf-8", errors="replace")

    if not _robots_ok(url):
        raise SystemExit(f"REFUSED by robots.txt: {url}")

    # Rate limit.
    wait = MIN_INTERVAL - (time.monotonic() - _LAST_REQUEST[0])
    if wait > 0:
        time.sleep(wait)

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
    _LAST_REQUEST[0] = time.monotonic()

    text = raw.decode(charset, errors="replace")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------------------
# HTML -> rough Markdown
# ---------------------------------------------------------------------------
_BLOCK_TAGS = {"p", "div", "br", "tr", "li", "blockquote", "h1", "h2", "h3", "h4"}
_DROP_TAGS = {"script", "style", "head", "nav", "footer", "header"}


class _Extractor(HTMLParser):
    """Collect visible text as a list of (kind, emphasis, text) paragraph runs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paras: list[dict] = []
        self._buf: list[str] = []
        self._drop_depth = 0
        self._emph_depth = 0
        self._strong_depth = 0
        self._cur_kind = "p"
        self._all_emph = True  # whether the current paragraph is entirely italic
        self._any_text = False

    def _flush(self) -> None:
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        if text:
            self.paras.append(
                {"kind": self._cur_kind, "emph": self._all_emph and self._any_text, "text": text}
            )
        self._buf = []
        self._cur_kind = "p"
        self._all_emph = True
        self._any_text = False

    def handle_starttag(self, tag, attrs):
        if tag in _DROP_TAGS:
            self._drop_depth += 1
            return
        if self._drop_depth:
            return
        if tag in ("h1", "h2", "h3", "h4"):
            self._flush()
            self._cur_kind = tag
        elif tag in ("p", "div", "blockquote", "tr", "li"):
            self._flush()
        elif tag == "br":
            self._flush()
        elif tag in ("i", "em"):
            self._emph_depth += 1
        elif tag in ("b", "strong"):
            self._strong_depth += 1

    def handle_endtag(self, tag):
        if tag in _DROP_TAGS:
            self._drop_depth = max(0, self._drop_depth - 1)
            return
        if self._drop_depth:
            return
        if tag in ("h1", "h2", "h3", "h4", "p", "div", "blockquote", "tr", "li"):
            self._flush()
        elif tag in ("i", "em"):
            self._emph_depth = max(0, self._emph_depth - 1)
        elif tag in ("b", "strong"):
            self._strong_depth = max(0, self._strong_depth - 1)

    def handle_data(self, data):
        if self._drop_depth:
            return
        if data.strip():
            self._any_text = True
            if self._emph_depth == 0:
                self._all_emph = False
        self._buf.append(data)

    def close(self):
        super().close()
        self._flush()


def html_to_markdown(html: str) -> str:
    ex = _Extractor()
    ex.feed(html)
    ex.close()

    out: list[str] = []
    for i, para in enumerate(ex.paras):
        kind, text = para["kind"], para["text"]
        if kind == "h1":
            out.append(f"# {text}")
        elif kind == "h2":
            out.append(f"## {text}")
        elif kind in ("h3", "h4"):
            out.append(f"### {text}")
        elif para["emph"]:
            # Whole-paragraph italic => rubric heuristic (spoken-word instruction).
            out.append(f"> {text}")
        else:
            out.append(text)
        out.append("")  # paragraph break; sentence_split collapses runs
    return "\n".join(out).strip() + "\n"


# ---------------------------------------------------------------------------
# plain-text -> rough Markdown  (--text ingest mode, brief §4.2 / spec §5.6)
#
# Some public-domain sources are fixed-width ASCII e-texts, not HTML — notably
# the 1979 US BCP e-text on justus (bcpoffce.txt et al.), whose header states it
# is in the PUBLIC DOMAIN and permits derivative works. Its line breaks are
# significant, so we must NOT reflow. This mode strips the license header and
# page furniture, lightly converts the e-text's own markup to rough Markdown,
# and leaves the result for sentence_split.py + human verification. It is
# ASSISTIVE, like html_to_markdown; a human formats the anchors and verifies
# against a scan before anything is committed.
#
# e-text conventions handled (justus/Project-Gutenberg-style BCP e-text):
#   <heading>            a section heading (may wrap onto a second line)
#   *rubric*             italic rubric / stage direction
#   *Officiant* text     a speaker label
#   =text=               italic text: scripture citations and sung responses
#   /word                a poetic run-over (continuation of the line above)
#   <page NN>            page-number furniture (dropped)
# ---------------------------------------------------------------------------
_SPEAKER_RE = re.compile(
    r"^\s*\*(Officiant|People|Priest|Minister|Deacon|Celebrant|Answer|Bishop|"
    r"Reader|Leader|Cantor|Choir|Versicle|Response)\.?\*",
    re.IGNORECASE,
)


def _blockish(lines: list[str]) -> str:
    out: list[str] = []
    blank = 0
    for ln in lines:
        if ln == "":
            blank += 1
            if blank <= 1:
                out.append("")
            continue
        blank = 0
        out.append(ln)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n" if out else ""


def text_to_markdown(raw: str, strip_until: str | None = None,
                     strip_after: str | None = None) -> str:
    lines = raw.split("\n")

    # Optional range trim: keep from the first line matching strip_until, and
    # cut at the first line (after that) matching strip_after. Both are regexes.
    start = 0
    if strip_until:
        rx = re.compile(strip_until)
        for i, ln in enumerate(lines):
            if rx.search(ln):
                start = i
                break
    end = len(lines)
    if strip_after:
        rx = re.compile(strip_after)
        for i in range(start + 1, len(lines)):
            if rx.search(lines[i]):
                end = i
                break
    lines = lines[start:end]

    out: list[str] = []
    pending_heading: str | None = None  # accumulate a wrapped <heading>
    for raw_ln in lines:
        s = raw_ln.replace("\t", " ").rstrip()
        stripped = s.strip()

        if not stripped:
            if pending_heading is not None:
                out.append(f"## {pending_heading.strip()}")
                pending_heading = None
            out.append("")
            continue

        # page-number furniture
        if re.match(r"^<page\b.*>$", stripped, re.IGNORECASE):
            continue

        # a heading opened on a previous line but not yet closed with '>'
        if pending_heading is not None:
            pending_heading += " " + stripped.rstrip(">")
            if stripped.endswith(">"):
                out.append(f"## {pending_heading.strip()}")
                pending_heading = None
            continue

        # <heading> possibly wrapping across lines
        if stripped.startswith("<") and not stripped.startswith("<page"):
            inner = stripped[1:]
            if inner.endswith(">"):
                out.append(f"## {inner[:-1].strip()}")
            else:
                pending_heading = inner
            continue

        # strip poetic run-over marker '/'
        s = re.sub(r"^(\s*)/", r"\1", s)
        # =italic= (citations / responses) -> plain text
        s = re.sub(r"=([^=]+)=", r"\1", s)

        # whole-line rubric  *...*  (but not a speaker label)
        m = re.match(r"^\s*\*(.+?)\*\s*$", s)
        if m and not _SPEAKER_RE.match(s):
            out.append(f"> {m.group(1).strip()}")
            continue

        # inline speaker label  *Officiant* text -> **Officiant** text
        if _SPEAKER_RE.match(s):
            s = re.sub(r"^\s*\*([^*]+)\*", lambda mm: f"**{mm.group(1).strip()}**", s)

        out.append(s.strip())

    if pending_heading is not None:
        out.append(f"## {pending_heading.strip()}")
    return _blockish(out)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--out", help="write Markdown here (default: stdout)")
    parser.add_argument("--title", help="prepend a level-1 heading")
    parser.add_argument("--raw", action="store_true", help="skip markdown massaging")
    parser.add_argument("--text", action="store_true",
                        help="treat the source as a plain-text e-text (brief §4.2), "
                             "not HTML; strip header/furniture and emit rough Markdown")
    parser.add_argument("--strip-until", help="--text: keep from the first line matching this regex")
    parser.add_argument("--strip-after", help="--text: cut at the first line matching this regex")
    parser.add_argument("--force", action="store_true", help="bypass cache")
    parser.add_argument("--sources", help="append a provenance line to this SOURCES file")
    args = parser.parse_args(argv)

    raw = fetch(args.url, force=args.force)
    if args.text:
        body = raw if args.raw else text_to_markdown(raw, args.strip_until, args.strip_after)
    else:
        body = raw if args.raw else html_to_markdown(raw)
    if args.title and not args.raw:
        body = f"# {args.title}\n\n{body}"

    if args.out:
        Path(args.out).write_text(body, encoding="utf-8")
        sys.stderr.write(f"wrote {args.out}\n")
    else:
        sys.stdout.write(body)

    retrieved = datetime.now(timezone.utc).date().isoformat()
    note = f"- {args.url} (retrieved {retrieved})"
    if args.sources:
        with open(args.sources, "a", encoding="utf-8") as fh:
            fh.write(note + "\n")
    sys.stderr.write(note + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
