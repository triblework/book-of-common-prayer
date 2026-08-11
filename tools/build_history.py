#!/usr/bin/env python3
"""Replay the whole edition genealogy into a git history — history as a build artifact.

The published branches (main, scottish, american) and every ``vYYYY`` tag are
OUTPUTS of this builder, deterministically regenerated from the authoring layer:

    editions.yaml     -- the DAG: editions, branches, parents, tags, present/absent
    editions/<year>/  -- per-edition service text this edition ADDS or CHANGES
    repo-root/        -- files stamped identically into every published commit
    tools/            -- the canonical tooling, stamped into every commit

Why a builder at all (spec §2): completing an early edition's services *changes
that edition's commit*, so making ``git diff v1549 v1552`` show a real
liturgical change means rewriting history. A deterministic builder is what makes
rewriting safe, repeatable, and auditable.

Determinism (spec §2.5): same authoring input => identical published ``texts/``
trees AND identical commit SHAs. Commit timestamps and author/committer identity
are pinned from ``editions.yaml``; each commit is stamped one second after the
previous one in topological order.

Inheritance / absence model (spec §2.4), per edition, per service:
    1. editions/<year>/<service>.md exists      -> use it (authored/changed here)
    2. else service is in this edition's absent: -> delete it (clean removal diff)
    3. else                                      -> inherit the parent's file
After resolution every `present:` service must exist and no `absent:` service may.

Modes:
    (default)     build the graph in a scratch repo; print a summary + the exact
                  publish commands. Touches no live ref.
    --check       build, then assert every LIVE tag's texts/ tree is byte-identical
                  to the freshly built tree. Exit nonzero on any mismatch. This is
                  the history-level analog of `normalize.py --check`.
    --dry-run     build, run checks, print intended ref updates; touch nothing.
    --publish     build, run checks, then import the built graph into the live repo
                  and move main/scottish/american + tags to it. Prints (does NOT
                  run) the `git push --force-with-lease` + tag-push commands, so
                  the final outward step stays a human decision (spec §2.6).

Usage:
    build_history.py [--authoring DIR] [--target DIR] [--live-repo DIR]
                     [--check | --dry-run | --publish] [--keep]

Dependencies: Python stdlib + PyYAML.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    sys.stderr.write(
        "build_history.py requires PyYAML. Install it with:\n"
        "    python3 -m pip install pyyaml\n"
    )
    raise


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def run(cmd: list[str], cwd: Path, env: dict | None = None, capture: bool = False) -> str:
    """Run a git/other command, raising on failure."""
    full_env = dict(os.environ)
    full_env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env:
        full_env.update(env)
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=full_env,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or "") if capture else ""
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(cmd)}\n{detail}")
    return result.stdout if capture else ""


def git(cwd: Path, *args: str, capture: bool = False, env: dict | None = None) -> str:
    return run(["git", *args], cwd=cwd, env=env, capture=capture)


def service_src(authoring: Path, year: int, service: str) -> Path:
    return authoring / "editions" / str(year) / f"{service}.md"


def service_dst(worktree: Path, service: str) -> Path:
    return worktree / "texts" / "original" / f"{service}.md"


# ---------------------------------------------------------------------------
# editions.yaml loading + validation (topological order, unique tags, DAG sanity)
# ---------------------------------------------------------------------------
def load_editions(authoring: Path) -> dict:
    data = yaml.safe_load((authoring / "editions.yaml").read_text(encoding="utf-8"))
    editions = data.get("editions") or []
    seen_ids: set = set()
    seen_tags: set = set()
    order: list = []
    for ed in editions:
        eid = ed["id"]
        tag = ed["tag"]
        if eid in seen_ids:
            raise SystemExit(f"editions.yaml: duplicate edition id {eid!r}")
        if tag in seen_tags:
            raise SystemExit(f"editions.yaml: duplicate tag {tag!r}")
        parent = ed.get("parent")
        if parent is not None and parent not in seen_ids:
            raise SystemExit(
                f"editions.yaml: edition {eid!r} lists parent {parent!r} that is "
                "not defined earlier (list must be topologically ordered)."
            )
        present = set(ed.get("present") or [])
        absent = set(ed.get("absent") or [])
        clash = present & absent
        if clash:
            raise SystemExit(
                f"editions.yaml: edition {eid!r} has service(s) in both present "
                f"and absent: {sorted(clash)}"
            )
        seen_ids.add(eid)
        seen_tags.add(tag)
        order.append(ed)
    return data


# ---------------------------------------------------------------------------
# materialize one edition's texts/original tree in the worktree (spec §2.4)
# ---------------------------------------------------------------------------
def materialize_edition(authoring: Path, worktree: Path, ed: dict) -> None:
    year = ed["year"]
    present = list(ed.get("present") or [])
    absent = list(ed.get("absent") or [])

    # 1/3: authored files override or add; unauthored non-absent files are already
    # present in the worktree (inherited from the parent checkout) -> untouched.
    edition_dir = authoring / "editions" / str(year)
    if edition_dir.is_dir():
        for src in sorted(edition_dir.rglob("*.md")):
            service = src.relative_to(edition_dir).with_suffix("").as_posix()
            dst = service_dst(worktree, service)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)

    # 2: explicit deletions.
    for service in absent:
        dst = service_dst(worktree, service)
        if dst.exists():
            dst.unlink()

    # 4: post-resolution validation.
    for service in present:
        if not service_dst(worktree, service).exists():
            raise SystemExit(
                f"build: edition {year} declares present service {service!r} but no "
                f"file resolved (neither authored in editions/{year}/ nor inherited)."
            )
    for service in absent:
        if service_dst(worktree, service).exists():
            raise SystemExit(
                f"build: edition {year} declares absent service {service!r} but a "
                "file still exists after resolution."
            )


def stamp_repo_files(authoring: Path, worktree: Path) -> None:
    """Copy repo-root/ and tools/ into the worktree — identical bytes every commit."""
    root_src = authoring / "repo-root"
    for src in sorted(root_src.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(root_src)
        dst = worktree / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    tools_dst = worktree / "tools"
    if tools_dst.exists():
        shutil.rmtree(tools_dst)
    shutil.copytree(authoring / "tools", tools_dst)


def run_pipeline(worktree: Path) -> None:
    """sentence_split (in place) then normalize (regenerate normalized/)."""
    py = sys.executable
    if (worktree / "texts" / "original").is_dir():
        run([py, "tools/sentence_split.py", "texts/original"], cwd=worktree)
    run([py, "tools/normalize.py"], cwd=worktree)


# ---------------------------------------------------------------------------
# build the whole graph into `target`
# ---------------------------------------------------------------------------
def build(authoring: Path, target: Path) -> dict:
    data = load_editions(authoring)
    meta = data.get("meta") or {}
    scaffold = data.get("scaffold") or {}
    editions = data["editions"]

    name = meta.get("author_name", "BCP History Builder")
    email = meta.get("author_email", "build@localhost")
    base = datetime.fromisoformat(meta.get("base_date", "2026-08-11T00:00:00+00:00"))
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)

    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    git(target, "init", "-q", "-b", "main")
    git(target, "config", "user.name", name)
    git(target, "config", "user.email", email)
    git(target, "config", "commit.gpgsign", "false")

    tick = [0]

    def commit(branch: str, message: str) -> str:
        stamp = (base + timedelta(seconds=tick[0])).strftime("%Y-%m-%dT%H:%M:%S%z")
        tick[0] += 1
        env = {
            "GIT_AUTHOR_NAME": name,
            "GIT_AUTHOR_EMAIL": email,
            "GIT_COMMITTER_NAME": name,
            "GIT_COMMITTER_EMAIL": email,
            "GIT_AUTHOR_DATE": stamp,
            "GIT_COMMITTER_DATE": stamp,
        }
        git(target, "add", "-A")
        git(target, "commit", "-q", "-m", message, env=env)
        sha = git(target, "rev-parse", "HEAD", capture=True).strip()
        git(target, "branch", "-f", branch, sha)
        return sha

    def reset_worktree_to(sha: str) -> None:
        # Pristine parent state: reset tracked files, drop any untracked leftovers.
        git(target, "checkout", "-q", "-B", "__build", sha)
        git(target, "reset", "-q", "--hard", sha)
        git(target, "clean", "-fdq")

    # ---- scaffold commit (repo-root + tools; empty texts/) ----
    scaffold_branch = scaffold.get("branch", "main")
    git(target, "checkout", "-q", "--orphan", "__build")
    git(target, "clean", "-fdq")
    stamp_repo_files(authoring, target)
    scaffold_sha = commit(scaffold_branch, scaffold.get("commit_message", "Scaffold"))

    commit_by_id: dict = {}
    branch_tip: dict = {scaffold_branch: scaffold_sha}
    tags: list = []

    for ed in editions:
        parent = ed.get("parent")
        start_sha = scaffold_sha if parent is None else commit_by_id[parent]
        # branch_from is a sanity anchor: for a branch's first edition it must be
        # the parent's tag/commit. We start from the parent commit uniformly.
        reset_worktree_to(start_sha)
        materialize_edition(authoring, target, ed)
        stamp_repo_files(authoring, target)
        run_pipeline(target)
        sha = commit(ed["branch"], ed["commit_message"])
        # annotated tag
        stamp = git(target, "log", "-1", "--format=%aI", sha, capture=True).strip()
        git(
            target, "tag", "-a", ed["tag"], "-m", ed["tag_message"], sha,
            env={"GIT_COMMITTER_DATE": stamp},
        )
        commit_by_id[ed["id"]] = sha
        branch_tip[ed["branch"]] = sha
        tags.append(ed["tag"])

    # tidy up the temp build branch
    try:
        git(target, "checkout", "-q", branch_tip.get("main", scaffold_sha))
        git(target, "branch", "-q", "-D", "__build")
    except SystemExit:
        pass

    return {
        "meta": meta,
        "editions": editions,
        "scaffold_sha": scaffold_sha,
        "commit_by_id": commit_by_id,
        "branch_tip": branch_tip,
        "tags": tags,
    }


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def texts_tree(repo: Path, ref: str) -> str | None:
    """Return `git ls-tree -r <ref> -- texts` (mode SHA path per line), or None."""
    try:
        return git(repo, "ls-tree", "-r", ref, "--", "texts", capture=True)
    except SystemExit:
        return None


def check_against_live(target: Path, live_repo: Path, built: dict) -> int:
    """Assert every live tag's texts/ tree matches the freshly built tree."""
    problems: list[str] = []
    built_tags = set(built["tags"])
    live_tags = set(
        t for t in git(live_repo, "tag", capture=True).splitlines() if t.strip()
    )

    missing_live = built_tags - live_tags
    extra_live = live_tags - built_tags
    if missing_live:
        problems.append(f"tags built but absent in live repo: {sorted(missing_live)}")
    if extra_live:
        problems.append(f"tags in live repo but not built: {sorted(extra_live)}")

    for tag in sorted(built_tags & live_tags):
        built_tree = texts_tree(target, tag)
        live_tree = texts_tree(live_repo, tag)
        if built_tree != live_tree:
            problems.append(f"texts/ tree MISMATCH at {tag}")

    if problems:
        sys.stderr.write(
            "build_history.py --check: published history is NOT reproducible from "
            "authoring.\n" + "\n".join(f"  - {p}" for p in problems) + "\n"
        )
        return 1
    sys.stdout.write(
        f"build_history.py --check: OK — all {len(built_tags)} tags' texts/ trees "
        "are byte-identical to the freshly built graph.\n"
    )
    return 0


def verify_built_tips(target: Path, built: dict) -> int:
    """Run the per-push invariants on each published branch tip in the freshly
    built repo. This is the publish precondition for a CONTENT wave, where texts
    change on purpose (so a live byte-identity `--check` does NOT apply — that is
    only for the migration / tools-only rebuild)."""
    py = sys.executable
    problems: list[str] = []
    for branch in built["branch_tip"]:
        try:
            git(target, "checkout", "-q", branch)
        except SystemExit:
            problems.append(f"cannot checkout {branch}")
            continue
        for cmd, label in (
            ([py, "tools/normalize.py", "--check"], "normalize"),
            ([py, "tools/sentence_split.py", "--check", "texts"], "sentence_split"),
            ([py, "tools/verify_index.py", "--check"], "verify_index"),
        ):
            r = subprocess.run(cmd, cwd=str(target),
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            if r.returncode != 0:
                problems.append(f"{branch}: {label} --check failed\n{(r.stderr or '').strip()}")
    if problems:
        sys.stderr.write("build_history.py --publish: built tips fail invariants.\n"
                         + "\n".join(f"  - {p}" for p in problems) + "\n")
        return 1
    sys.stdout.write("build_history.py --publish: built tips pass "
                     "normalize/sentence_split/verify_index.\n")
    return 0


def print_summary(built: dict, target: Path, live_repo: Path | None) -> None:
    sys.stdout.write("Built graph (SHAs are NOT part of the interface; tags + diffs are):\n")
    sys.stdout.write(f"  scaffold: {built['scaffold_sha'][:12]}\n")
    for ed in built["editions"]:
        sha = built["commit_by_id"][ed["id"]]
        sys.stdout.write(f"  {ed['tag']:<7} {ed['branch']:<9} {sha[:12]}  {ed['commit_message']}\n")
    sys.stdout.write("\nBranch tips:\n")
    for br, sha in built["branch_tip"].items():
        sys.stdout.write(f"  {br:<9} {sha[:12]}\n")
    sys.stdout.write(f"\nScratch build repo: {target}\n")
    if live_repo:
        sys.stdout.write(
            "\nTo publish (spec §2.6 — run these yourself after --check is green):\n"
            f"  git -C {live_repo} fetch {target} 'refs/*:refs/*'   # import built objects\n"
            "  git push --force-with-lease origin main scottish american\n"
            "  git push --force origin --tags   # tags were re-created at new commits\n"
        )


# ---------------------------------------------------------------------------
# publish (mutates the LIVE repo's local refs; push stays manual)
# ---------------------------------------------------------------------------
def publish(target: Path, live_repo: Path, built: dict) -> int:
    # Import built commits/tags into the live repo, then move branch refs.
    git(live_repo, "fetch", "-q", str(target),
        "refs/heads/*:refs/heads/__built/*", "+refs/tags/*:refs/tags/*")
    for br, sha in built["branch_tip"].items():
        built_sha = git(live_repo, "rev-parse", f"__built/{br}", capture=True).strip()
        git(live_repo, "update-ref", f"refs/heads/{br}", built_sha)
    # clean the temporary namespace
    for br in built["branch_tip"]:
        try:
            git(live_repo, "update-ref", "-d", f"refs/heads/__built/{br}")
        except SystemExit:
            pass
    sys.stdout.write(
        "Published locally: main/scottish/american and all tags now point at the "
        "built graph.\nRun the push commands printed above to update origin.\n"
    )
    return 0


def main(argv: list[str]) -> int:
    tools_dir = Path(__file__).resolve().parent
    default_authoring = tools_dir.parent
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--authoring", default=str(default_authoring),
                        help="authoring content root (editions.yaml, editions/, repo-root/, tools/)")
    parser.add_argument("--target", default=None,
                        help="scratch dir to build into (default: a temp dir)")
    parser.add_argument("--live-repo", default=None,
                        help="git repo holding the live tags to check/publish against")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="assert live tags' texts/ trees match the rebuild")
    mode.add_argument("--dry-run", action="store_true",
                      help="build + check + print intended ref updates; touch nothing")
    mode.add_argument("--publish", action="store_true",
                      help="build, check, and move live local refs (push stays manual)")
    parser.add_argument("--keep", action="store_true",
                        help="keep the scratch build repo instead of deleting it")
    args = parser.parse_args(argv)

    authoring = Path(args.authoring).resolve()
    if not (authoring / "editions.yaml").is_file():
        raise SystemExit(f"no editions.yaml under {authoring}")

    live_repo = Path(args.live_repo).resolve() if args.live_repo else None
    tmp_created = False
    if args.target:
        target = Path(args.target).resolve()
    else:
        target = Path(tempfile.mkdtemp(prefix="bcp-build-"))
        tmp_created = True

    try:
        built = build(authoring, target)

        rc = 0
        # --check / --dry-run compare the rebuild to the LIVE tags (byte-identity):
        # the reproducibility guarantee for the migration and tools-only rebuilds.
        if args.check or args.dry_run:
            if not live_repo:
                raise SystemExit("--check/--dry-run require --live-repo")
            rc = check_against_live(target, live_repo, built)

        # --publish is for a CONTENT wave: texts change on purpose, so it does NOT
        # require live byte-identity; it gates on the per-push invariants instead.
        if args.publish:
            if not live_repo:
                raise SystemExit("--publish requires --live-repo")
            rc = verify_built_tips(target, built)
            if rc != 0:
                sys.stderr.write("Refusing to publish: built tips failed invariants.\n")
                return rc
            print_summary(built, target, live_repo)
            return publish(target, live_repo, built)

        if not args.check:  # default and --dry-run both print a summary
            print_summary(built, target, live_repo)
        return rc
    finally:
        if tmp_created and not args.keep:
            shutil.rmtree(target, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
