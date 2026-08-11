#!/usr/bin/env python3
"""Build the reader's-viewer data artifact from the published git layer only.

Spec: BCP-VIEWER-SPEC.md §3.1. This tool is **decoupled** and **git-only**:
it reads nothing but the published repository — the ``v*`` tags, the three
content branches (main / scottish / american), both spelling trees under
``texts/``, and the published ``SOURCES.md`` / ``NOTICE.md``. It never reads the
``authoring`` branch, ``editions.yaml``, or ``provenance.yaml`` on the default
path, and it runs to completion on a plain clone that has the tags but no
``authoring`` branch. It runs independently of ``build_history.py``.

Everything is read with ``git show`` / ``git ls-tree`` / ``git for-each-ref`` —
never by checking out a working tree — so it is safe against a bare or
shallow-but-tagged clone.

Determinism: same published tags + same tool => byte-identical JSON. ``--check``
is the analog of ``normalize.py --check``.

Usage:
    python tools/build_viewer_data.py --out viewer/data
    python tools/build_viewer_data.py --check          # byte-stable rebuild gate
    python tools/build_viewer_data.py --authoring .    # optional enrichment (off by default)

Dependencies: Python stdlib only. PyYAML is imported lazily, and only for the
optional ``--authoring`` enrichment path; the default git-only path needs nothing
beyond the standard library.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Line id -> branch name. Order matters: a tag is assigned to the EARLIEST line
# (english, then scottish, then american) whose branch tip has it as an ancestor
# (spec §3.1). This is git-ancestry line assignment, never tag-name guessing.
LINES = [("english", "main"), ("scottish", "scottish"), ("american", "american")]
LINE_LABEL = {"english": "English", "scottish": "Scottish", "american": "American"}

TREES = ("normalized", "original")
TEXTS = "texts"  # texts/<tree>/<service>.md

DEFAULT_REPO_NAME = "triblework/book-of-common-prayer"

# Cosmetic-only prettification of DISCOVERED slugs (labels + display order).
# This is NOT a hard-coded service list: discovery is always observed from git
# (git ls-tree), and any slug not named here falls back to Title Case / a
# trailing bucket. It only controls how the reader menu reads. (Spec §8.)
GROUP_LABELS = {
    "front-matter": "Front Matter",
    "daily-office": "The Daily Office",
    "the-litany": "The Litany",
    "holy-communion": "Holy Communion",
    "occasional-offices": "Occasional Offices",
    "ordinal": "The Ordinal",
}
GROUP_ORDER = [
    "front-matter",
    "daily-office",
    "the-litany",
    "holy-communion",
    "occasional-offices",
    "ordinal",
]
SERVICE_LABELS = {
    "daily-office/morning-prayer": "Morning Prayer",
    "daily-office/evening-prayer": "Evening Prayer",
    "the-litany/litany": "The Litany",
    "holy-communion/holy-communion": "Holy Communion",
    "front-matter/preface": "The Preface",
    "front-matter/concerning-the-service": "Concerning the Service of the Church",
    "front-matter/of-ceremonies": "Of Ceremonies",
    "front-matter/ratification": "Ratification",
    "occasional-offices/public-baptism": "Publick Baptism",
    "occasional-offices/private-baptism": "Private Baptism",
    "occasional-offices/baptism-riper-years": "Baptism of Riper Years",
    "occasional-offices/confirmation": "Confirmation",
    "occasional-offices/catechism": "The Catechism",
    "occasional-offices/matrimony": "Matrimony",
    "occasional-offices/visitation-sick": "The Visitation of the Sick",
    "occasional-offices/burial": "The Burial of the Dead",
    "occasional-offices/churching": "The Churching of Women",
    "occasional-offices/commination": "A Commination",
    "ordinal/preface": "The Preface (Ordinal)",
    "ordinal/ordering-deacons": "The Ordering of Deacons",
    "ordinal/ordering-priests": "The Ordering of Priests",
    "ordinal/consecration-bishops": "The Consecration of Bishops",
}
# Book order within a group, when known. Unknown services sort after, by label.
SERVICE_ORDER = {
    "daily-office/morning-prayer": 0,
    "daily-office/evening-prayer": 1,
    "front-matter/preface": 0,
    "front-matter/concerning-the-service": 1,
    "front-matter/of-ceremonies": 2,
    "front-matter/ratification": 3,
    "occasional-offices/public-baptism": 0,
    "occasional-offices/private-baptism": 1,
    "occasional-offices/baptism-riper-years": 2,
    "occasional-offices/confirmation": 3,
    "occasional-offices/catechism": 4,
    "occasional-offices/matrimony": 5,
    "occasional-offices/visitation-sick": 6,
    "occasional-offices/burial": 7,
    "occasional-offices/churching": 8,
    "occasional-offices/commination": 9,
    "ordinal/preface": 0,
    "ordinal/ordering-deacons": 1,
    "ordinal/ordering-priests": 2,
    "ordinal/consecration-bishops": 3,
}


def titlecase_slug(slug: str) -> str:
    small = {"of", "the", "for", "and", "a", "an", "in", "to"}
    words = slug.replace("_", " ").replace("-", " ").split()
    out = []
    for i, w in enumerate(words):
        out.append(w if (w in small and i > 0) else (w[:1].upper() + w[1:]))
    return " ".join(out)


def group_label(group: str) -> str:
    return GROUP_LABELS.get(group, titlecase_slug(group))


def service_label(service_id: str) -> str:
    if service_id in SERVICE_LABELS:
        return SERVICE_LABELS[service_id]
    return titlecase_slug(service_id.split("/", 1)[-1])


# ---------------------------------------------------------------------------
# Git plumbing (read-only; never touches the working tree)
# ---------------------------------------------------------------------------


class Git:
    def __init__(self, repo: str):
        self.repo = repo

    def _run(self, args, check=True):
        p = subprocess.run(
            ["git", "-C", self.repo, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if check and p.returncode != 0:
            raise RuntimeError(
                "git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace"))
            )
        return p

    def text(self, args) -> str:
        """Decode git output as UTF-8 without universal-newline translation."""
        return self._run(args).stdout.decode("utf-8")

    def ok(self, args) -> bool:
        return self._run(args, check=False).returncode == 0

    def tags(self):
        out = self.text(["tag", "--list", "v*"]).splitlines()
        tags = [t.strip() for t in out if re.fullmatch(r"v\d{3,4}", t.strip())]
        # Sorted by year — the corpus is linear per line, so year order matches
        # first-parent order; the LINE of a tag is derived from ancestry below.
        return sorted(tags, key=lambda t: int(t[1:]))

    def resolve(self, name):
        for cand in (name, f"refs/heads/{name}", f"origin/{name}", f"refs/remotes/origin/{name}"):
            p = self._run(["rev-parse", "--verify", "--quiet", cand + "^{commit}"], check=False)
            if p.returncode == 0:
                return p.stdout.decode().strip()
        return None

    def is_ancestor(self, tag, tip) -> bool:
        return self.ok(["merge-base", "--is-ancestor", tag, tip])

    def commit_date(self, ref) -> str:
        return self.text(["show", "-s", "--format=%cI", ref]).strip()

    def tag_message(self, tag) -> str:
        return self.text(["tag", "-l", "--format=%(contents)", tag])

    def ls_service_files(self, tag, tree):
        prefix = f"{TEXTS}/{tree}/"
        out = self.text(["ls-tree", "-r", "--name-only", tag, "--", prefix]).splitlines()
        services = []
        for path in out:
            path = path.strip()
            if path.endswith(".md") and path.startswith(prefix):
                services.append(path[len(prefix):-3])
        return set(services)

    def file_exists(self, tag, path) -> bool:
        return self.ok(["cat-file", "-e", f"{tag}:{path}"])

    def show_file(self, tag, path) -> str:
        return self.text(["show", f"{tag}:{path}"])

    def repo_name(self):
        p = self._run(["config", "--get", "remote.origin.url"], check=False)
        if p.returncode == 0:
            url = p.stdout.decode().strip()
            m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?/?$", url)
            if m:
                return m.group(1)
        return DEFAULT_REPO_NAME


# ---------------------------------------------------------------------------
# Markdown parse contract (spec §4.1) — runs in the builder, not the browser.
# ---------------------------------------------------------------------------

_SPEECH_RE = re.compile(r"^\*\*\s*(.+?)\s*\*\*\s*(.*)$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def parse_service_markdown(text: str, year: int | None = None) -> dict:
    """Parse one service .md into the structured shape of spec §3.2.

    Returns {present, title, meta:{acknowledgment, verify}, units:[...]}.
    Each unit carries its governing ``##`` anchor. VERIFY notes are recorded in
    ``meta.verify`` and attached to the nearest following unit (spec §4.1/§13).
    """
    title = None
    units = []
    meta_verify = []
    acknowledgment = None
    cur_anchor = None
    pending_verify = []

    def emit(kind, txt, anchor, speaker=None, level=None):
        u = {"anchor": anchor, "kind": kind, "text": txt}
        if speaker is not None:
            u["speaker"] = speaker
        if level is not None:
            u["level"] = level
        if pending_verify:
            u["verify"] = pending_verify[:]
            pending_verify.clear()
        units.append(u)

    def flush_comment(comment: str):
        nonlocal acknowledgment
        inner = comment.strip()
        if inner.startswith("<!--"):
            inner = inner[4:]
        if inner.endswith("-->"):
            inner = inner[:-3]
        inner = inner.strip()
        up = inner.upper()
        if up.startswith("BCP 1662"):
            acknowledgment = "BCP 1662"
        elif up.startswith("VERIFY"):
            pending_verify.append(inner)
            meta_verify.append(inner)
        # any other comment is metadata and dropped

    buf = None  # accumulates a multi-line <!-- ... --> comment
    pending_speaker = None  # a standalone `**Speaker.**` label awaiting its spoken line
    for raw in text.split("\n"):
        line = raw.rstrip("\r")
        if buf is not None:
            buf += "\n" + line
            if "-->" in line:
                flush_comment(buf)
                buf = None
            continue
        s = line.strip()
        if s == "":
            continue
        if s.startswith("<!--"):
            if "-->" in s:
                flush_comment(s)
            else:
                buf = s
            continue
        hm = _HEADING_RE.match(line)
        if hm:
            pending_speaker = None
            htext = hm.group(2).strip()
            level = len(hm.group(1))
            if level == 1:
                if title is None:
                    title = htext
                emit("title", htext, None)
            elif level == 2:
                cur_anchor = htext  # `##` opens a section and sets the anchor
                emit("heading", htext, cur_anchor, level=2)
            else:
                # `###`+ is a sub-heading: it stays under the current `##` anchor
                # (never a section key) so it can't collide with a `##` of the
                # same name (e.g. 1979 Rite Two repeats Rite One section names).
                emit("heading", htext, cur_anchor, level=level)
            continue
        if line.startswith(">"):
            emit("rubric", line[1:].lstrip(), cur_anchor)
            continue
        m = _SPEECH_RE.match(line)
        if m:
            speaker = m.group(1).strip().rstrip(".").strip()
            rest = m.group(2).strip()
            pending_speaker = None  # a new label supersedes any unresolved one
            if rest == "":
                pending_speaker = speaker  # words are on following line(s)
            else:
                emit("speech", rest, cur_anchor, speaker=speaker)
            continue
        # Plain spoken line. If a standalone speaker label is pending, this line
        # is that speaker's words (rubrics in between stay rubrics and don't
        # consume the label).
        if pending_speaker is not None:
            emit("speech", s, cur_anchor, speaker=pending_speaker)
            pending_speaker = None
        else:
            emit("text", s, cur_anchor)

    if buf is not None:  # unterminated comment — treat the buffer as its content
        flush_comment(buf + "-->")
    # Any VERIFY note with no following unit (trailing) is surfaced as a note unit
    # so the scholarship is never silently dropped.
    for note in pending_verify:
        units.append({"anchor": cur_anchor, "kind": "note", "text": note})

    if acknowledgment is None and year == 1662:
        acknowledgment = "BCP 1662"  # belt-and-braces hard rule (spec §13)

    return {
        "present": True,
        "title": title,
        "meta": {"acknowledgment": acknowledgment, "verify": meta_verify},
        "units": units,
    }


def heading_sequence(parsed: dict):
    # Only `##` (level-2) headings are section anchors; `###`+ are sub-headings.
    return [u["text"] for u in parsed["units"] if u["kind"] == "heading" and u.get("level", 2) == 2]


def merge_anchor_order(sequences):
    """Merge per-edition heading sequences into one canonical order.

    Order-preserving greedy merge: each anchor is inserted relative to its last
    matched neighbour, so 1552's penitential opening lands before "The Lordes
    Prayer" even though the earliest edition (1549) lacks it. (Spec §3.1/§5.2.)
    """
    canonical = []
    for seq in sequences:
        idx = 0
        for a in seq:
            if a in canonical:
                idx = canonical.index(a) + 1
            else:
                canonical.insert(idx, a)
                idx += 1
    return canonical


# ---------------------------------------------------------------------------
# Provenance from the published SOURCES.md / NOTICE.md (spec §13)
# ---------------------------------------------------------------------------


def _table_rows(text: str):
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if re.fullmatch(r":?-{2,}:?", cells[0].replace(" ", "")):
            continue  # separator row
        yield cells


def parse_notice_copyright(notice_text: str):
    """year -> copyright status string, from the NOTICE.md summary table.

    First matching table wins: the per-edition summary table is the first
    year-keyed table in the file, so later tables (e.g. scope/omissions) that
    re-list years without a status cannot clobber it.
    """
    out = {}
    for cells in _table_rows(notice_text):
        m = re.fullmatch(r"(\d{4})", cells[0])
        if not m or len(cells) < 3:
            continue
        year = int(m.group(1))
        if year in out:
            continue
        out[year] = re.sub(r"\*\*", "", cells[2]).strip()
    return out


def parse_sources_urls(sources_text: str):
    """year -> source URL (or None when the row is 'derived from ...').

    First-table-wins (see parse_notice_copyright): the English/Scottish/American
    per-edition source tables come first, so a later scope/omissions table that
    re-lists the daily-office editions without a URL cannot null them out.
    """
    out = {}
    for cells in _table_rows(sources_text):
        m = re.fullmatch(r"(\d{4})", cells[0])
        if not m or len(cells) < 2:
            continue
        year = int(m.group(1))
        if year in out:
            continue
        url_m = re.search(r"https?://[^\s<>|)]+", cells[1])
        out[year] = url_m.group(0) if url_m else None
    return out


def parse_retrieved(sources_text: str):
    m = re.search(r"retriev\w+.*?(\d{4}-\d{2}-\d{2})", sources_text, re.IGNORECASE)
    return m.group(1) if m else None


def parse_wave_note(notice_text: str):
    """Latest rebuild-log bullet from NOTICE.md, cleaned to one line."""
    lines = notice_text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if "Rebuild log" in l)
    except StopIteration:
        return None
    last = None
    for l in lines[start + 1:]:
        st = l.strip()
        if st.startswith("- "):
            last = st[2:]
        elif st.startswith("#"):
            break
        elif last is not None and st and not st.startswith("-"):
            last += " " + st  # continuation line of the same bullet
    if not last:
        return None
    note = re.sub(r"\*\*", "", last)
    note = re.sub(r"\s+", " ", note).strip()
    if len(note) > 200:  # it's a colophon caption, not the whole rebuild-log entry
        note = note[:199].rstrip() + "…"
    return note


# ---------------------------------------------------------------------------
# Core build
# ---------------------------------------------------------------------------


def clean_desc(tag_message: str):
    stripped = (tag_message or "").strip()
    first = stripped.splitlines()[0] if stripped else ""
    return re.sub(r"^\d{4}\s*[—–-]\s*", "", first).strip() or None


def build(repo: str, authoring: str | None = None):
    g = Git(repo)
    tags = g.tags()
    if not tags:
        raise SystemExit("No v* tags found — nothing to build.")

    tips = {}
    for _line, branch in LINES:
        sha = g.resolve(branch)
        if sha:
            tips[branch] = sha
    if "main" not in tips:
        raise SystemExit("Could not resolve the 'main' branch tip.")

    # Line assignment from ancestry: earliest line whose tip has the tag.
    tag_line = {}
    tag_branch = {}
    for tag in tags:
        for line_id, branch in LINES:
            tip = tips.get(branch)
            if tip and g.is_ancestor(tag, tip):
                tag_line[tag] = line_id
                tag_branch[tag] = branch
                break
        else:
            tag_line[tag] = "english"
            tag_branch[tag] = "main"

    year_of = {t: int(t[1:]) for t in tags}

    # Presence, observed per tag from git ls-tree. `present_at` keys on the
    # normalized tree (spec §3.1), but service DISCOVERY unions both trees so an
    # original-only service is never silently dropped.
    present_norm = {t: g.ls_service_files(t, "normalized") for t in tags}
    present_orig = {t: g.ls_service_files(t, "original") for t in tags}
    all_seen = [s for sets in (present_norm, present_orig) for v in sets.values() for s in v]
    all_services = sorted(set(all_seen))

    # Build per-service payloads.
    services_out = {}
    for service in all_services:
        editions = {}
        norm_parsed_by_tag = {}
        acks = {}
        for tag in tags:
            entry = {
                "year": year_of[tag],
                "line": tag_line[tag],
                "branch": tag_branch[tag],
                "trees": {},
            }
            for tree in TREES:
                path = f"{TEXTS}/{tree}/{service}.md"
                have = service in (present_norm[tag] if tree == "normalized" else present_orig[tag])
                if not have:
                    entry["trees"][tree] = {"present": False}
                    continue
                parsed = parse_service_markdown(g.show_file(tag, path), year_of[tag])
                entry["trees"][tree] = parsed
                if tree == "normalized":
                    norm_parsed_by_tag[tag] = parsed
                if parsed["meta"]["acknowledgment"]:
                    acks[tag] = parsed["meta"]["acknowledgment"]
            editions[tag] = entry

        canonical = merge_anchor_order(
            [heading_sequence(norm_parsed_by_tag[t]) for t in tags if t in norm_parsed_by_tag]
        )
        services_out[service] = {
            "service": service,
            "label": service_label(service),
            "canonical_anchors": canonical,
            "editions": editions,
            "_acks": acks,  # internal; stripped before emit
        }

    # ---- Provenance (edition-level; published layer only) ----
    notice_text = g.show_file("main", "NOTICE.md") if g.file_exists("main", "NOTICE.md") else ""
    sources_text = g.show_file("main", "SOURCES.md") if g.file_exists("main", "SOURCES.md") else ""
    copyright_by_year = parse_notice_copyright(notice_text)
    url_by_year = parse_sources_urls(sources_text)
    retrieved = parse_retrieved(sources_text)
    wave_note = parse_wave_note(notice_text)

    # Which tags carry the BCP 1662 acknowledgment anywhere (belt-and-braces + observed).
    ack_tags = {t for svc in services_out.values() for t in svc["_acks"]}
    ack_tags |= {t for t in tags if year_of[t] == 1662}

    repo_name = g.repo_name()

    # ---- Optional authoring enrichment (off by default; never required) ----
    desc_override = {}
    feature_by_service = {}
    if authoring:
        desc_override, feature_by_service = _load_authoring(authoring)

    # ---- index.json ----
    # Newest branch-tip commit instant, compared as real datetimes (a string max
    # over %cI would be wrong if two tips carried different UTC offsets).
    tip_dates = [g.commit_date(sha) for sha in tips.values()]
    built = max(tip_dates, key=_parse_iso, default=None)
    built = _to_utc_z(built) if built else None

    lines_out = []
    for line_id, branch in LINES:
        line_tags = sorted([t for t in tags if tag_line[t] == line_id], key=lambda t: year_of[t])
        eds = []
        for t in line_tags:
            y = year_of[t]
            ed = {
                "tag": t,
                "year": y,
                "label": str(y),
                "desc": desc_override.get(y) or clean_desc(g.tag_message(t)),
                "acknowledgment": "BCP 1662" if t in ack_tags else None,
                "copyright": copyright_by_year.get(y),
                "source_url": url_by_year.get(y),
                "retrieved": retrieved,
                "status": None,
            }
            eds.append(ed)
        lines_out.append(
            {"id": line_id, "label": LINE_LABEL[line_id], "branch": branch, "editions": eds}
        )

    # ---- service_groups ----
    groups = {}
    for service in all_services:
        grp = service.split("/", 1)[0]
        groups.setdefault(grp, []).append(service)

    def group_sort_key(grp):
        return (GROUP_ORDER.index(grp) if grp in GROUP_ORDER else len(GROUP_ORDER), grp)

    def service_sort_key(sid):
        return (SERVICE_ORDER.get(sid, 10_000), service_label(sid))

    service_groups = []
    for grp in sorted(groups, key=group_sort_key):
        svcs = []
        for sid in sorted(groups[grp], key=service_sort_key):
            present_at = sorted(
                [t for t in tags if sid in present_norm[t]], key=lambda t: year_of[t]
            )
            entry = {
                "id": sid,
                "label": service_label(sid),
                "file": sid.replace("/", "__") + ".json",
                "present_at": present_at,
            }
            if sid in feature_by_service:
                entry["feature_editions"] = feature_by_service[sid]
            svcs.append(entry)
        service_groups.append({"label": group_label(grp), "services": svcs})

    index = {
        "repo": repo_name,
        "built": built,
        "wave_note": wave_note,
        "lines": lines_out,
        "service_groups": service_groups,
        "notice": {
            "bcp1662_ack": "BCP 1662",
            "notice_url": f"https://github.com/{repo_name}/blob/main/NOTICE.md" if notice_text else None,
            "sources_url": f"https://github.com/{repo_name}/blob/main/SOURCES.md" if sources_text else None,
        },
    }

    # Strip internal fields and attach optional feature_editions to service files.
    files = {"index.json": index}
    for service, payload in services_out.items():
        feats = feature_by_service.get(service)
        payload.pop("_acks", None)
        if feats:
            payload["feature_editions"] = feats
        files[payload["service"].replace("/", "__") + ".json"] = payload

    return files


def _parse_iso(iso: str) -> datetime:
    iso = iso.strip()
    if iso.endswith("Z"):  # Python < 3.11 fromisoformat rejects a trailing 'Z'
        iso = iso[:-1] + "+00:00"
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _to_utc_z(iso: str) -> str:
    return _parse_iso(iso).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_authoring(authoring_dir: str):
    """Optional enrichment from editions.yaml IF present (spec §3.1). Never required."""
    path = os.path.join(authoring_dir, "editions.yaml")
    if not os.path.isfile(path):
        return {}, {}
    try:
        import yaml  # lazy: only the enrichment path needs PyYAML
    except ImportError:
        sys.stderr.write("warning: --authoring given but PyYAML missing; skipping enrichment\n")
        return {}, {}
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    desc, feats = {}, {}
    for ed in data.get("editions", []) or []:
        year = ed.get("year") or ed.get("id")
        if year and ed.get("tag_message"):
            desc[int(year)] = clean_desc(ed["tag_message"])
        for sid in ed.get("feature_editions", []) or []:
            feats.setdefault(sid, [])
    return desc, feats


# ---------------------------------------------------------------------------
# Serialization + emit / check
# ---------------------------------------------------------------------------


def dumps(obj) -> str:
    """Deterministic JSON: sorted keys, UTF-8, 2-space indent, trailing newline."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_files(files: dict, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    for name, obj in files.items():
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(dumps(obj))


def check_files(files: dict, out_dir: str) -> int:
    """Assert a fresh build is byte-identical to what is already in out_dir."""
    problems = []
    existing = set(f for f in os.listdir(out_dir) if f.endswith(".json")) if os.path.isdir(out_dir) else set()
    fresh = set(files)
    for missing in sorted(fresh - existing):
        problems.append(f"missing on disk: {missing}")
    for extra in sorted(existing - fresh):
        problems.append(f"stale on disk (not produced by a fresh build): {extra}")
    for name in sorted(fresh & existing):
        want = dumps(files[name])
        with open(os.path.join(out_dir, name), "r", encoding="utf-8") as fh:
            got = fh.read()
        if want != got:
            problems.append(f"byte mismatch: {name}")
    if problems:
        sys.stderr.write("--check FAILED:\n  " + "\n  ".join(problems) + "\n")
        return 1
    print(f"--check OK: {len(fresh)} files byte-identical in {out_dir}")
    return 0


# ---------------------------------------------------------------------------
# Minimal JSON-Schema (draft 2020-12 subset) validator — stdlib only.
# Supports exactly the keywords used by our two schemas.
# ---------------------------------------------------------------------------


class SchemaError(Exception):
    pass


def _resolve_ref(root, ref):
    if not ref.startswith("#/"):
        raise SchemaError(f"unsupported $ref: {ref}")
    node = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        node = node[part]
    return node


def _validate(node, schema, root, path, errors):
    if "$ref" in schema:
        _validate(node, _resolve_ref(root, schema["$ref"]), root, path, errors)
        return

    if "const" in schema and node != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {node!r}")
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{path}: {node!r} not in enum {schema['enum']!r}")

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(node, t) for t in types):
            errors.append(f"{path}: expected type {schema['type']}, got {type(node).__name__}")
            return

    if isinstance(node, dict):
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in node:
                errors.append(f"{path}: missing required property '{req}'")
        addl = schema.get("additionalProperties", True)
        for k, v in node.items():
            if k in props:
                _validate(v, props[k], root, f"{path}.{k}", errors)
            elif addl is False:
                errors.append(f"{path}: additional property '{k}' not allowed")
            elif isinstance(addl, dict):
                _validate(v, addl, root, f"{path}.{k}", errors)
        if "propertyNames" in schema:
            for k in node:
                _validate(k, schema["propertyNames"], root, f"{path}:key({k})", errors)
        if "minProperties" in schema and len(node) < schema["minProperties"]:
            errors.append(f"{path}: fewer than {schema['minProperties']} properties")

    if isinstance(node, list) and "items" in schema:
        for i, item in enumerate(node):
            _validate(item, schema["items"], root, f"{path}[{i}]", errors)

    if isinstance(node, str):
        if "pattern" in schema and not re.search(schema["pattern"], node):
            errors.append(f"{path}: {node!r} does not match /{schema['pattern']}/")
        if "minLength" in schema and len(node) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")

    if "oneOf" in schema:
        matches = 0
        for sub in schema["oneOf"]:
            sub_errors = []
            _validate(node, sub, root, path, sub_errors)
            if not sub_errors:
                matches += 1
        if matches != 1:
            errors.append(f"{path}: matched {matches} of oneOf (want exactly 1)")

    for sub in schema.get("allOf", []):
        _validate(node, sub, root, path, errors)

    if "if" in schema:
        cond_errors = []
        _validate(node, schema["if"], root, path, cond_errors)
        branch = "then" if not cond_errors else "else"
        if branch in schema:
            _validate(node, schema[branch], root, path, errors)


def _is_type(node, t):
    if t == "object":
        return isinstance(node, dict)
    if t == "array":
        return isinstance(node, list)
    if t == "string":
        return isinstance(node, str)
    if t == "integer":
        return isinstance(node, int) and not isinstance(node, bool)
    if t == "number":
        return isinstance(node, (int, float)) and not isinstance(node, bool)
    if t == "boolean":
        return isinstance(node, bool)
    if t == "null":
        return node is None
    return False


def validate_against_schema(obj, schema) -> list:
    errors = []
    _validate(obj, schema, schema, "$", errors)
    return errors


def validate_files(files: dict, schema_dir: str) -> int:
    index_schema_path = os.path.join(schema_dir, "index.schema.json")
    service_schema_path = os.path.join(schema_dir, "service.schema.json")
    if not (os.path.isfile(index_schema_path) and os.path.isfile(service_schema_path)):
        sys.stderr.write(f"schema files not found under {schema_dir}\n")
        return 2
    with open(index_schema_path, encoding="utf-8") as fh:
        index_schema = json.load(fh)
    with open(service_schema_path, encoding="utf-8") as fh:
        service_schema = json.load(fh)

    # Prefer the reference `jsonschema` validator when available; fall back to
    # the built-in stdlib validator otherwise (keeps the default path dependency-free).
    ext = None
    try:
        import jsonschema  # type: ignore

        ext = jsonschema
    except ImportError:
        pass

    failures = 0
    for name, obj in files.items():
        schema = index_schema if name == "index.json" else service_schema
        if ext is not None:
            validator = ext.Draft202012Validator(schema)
            errs = ["/".join(map(str, e.path)) + ": " + e.message for e in validator.iter_errors(obj)]
        else:
            errs = validate_against_schema(obj, schema)
        if errs:
            failures += 1
            sys.stderr.write(f"SCHEMA FAIL {name}:\n  " + "\n  ".join(errs[:20]) + "\n")
    if failures:
        sys.stderr.write(f"schema validation failed for {failures} file(s)\n")
        return 2
    engine = "jsonschema" if ext else "builtin"
    print(f"schema validation OK ({len(files)} files, {engine} validator)")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the BCP viewer data artifact (git-only).")
    ap.add_argument("--repo", default=".", help="Repository path (default: .)")
    ap.add_argument("--out", default="viewer/data", help="Output directory (default: viewer/data)")
    ap.add_argument("--check", action="store_true", help="Rebuild and assert byte-identical output; do not write.")
    ap.add_argument("--authoring", metavar="DIR", default=None,
                    help="Optional enrichment from editions.yaml IF present (off by default).")
    ap.add_argument("--no-validate", action="store_true", help="Skip JSON Schema validation.")
    ap.add_argument("--schema-dir", default=None, help="Schema directory (default: <out>/schema).")
    args = ap.parse_args(argv)

    files = build(args.repo, authoring=args.authoring)
    schema_dir = args.schema_dir or os.path.join(args.out, "schema")

    rc = 0
    if not args.no_validate:
        rc = validate_files(files, schema_dir)
        if rc != 0:
            return rc

    if args.check:
        return check_files(files, args.out)

    write_files(files, args.out)
    print(f"wrote {len(files)} files to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
