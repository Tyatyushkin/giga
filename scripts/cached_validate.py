#!/usr/bin/env python3
"""Cached wrapper around validate_cases.py for the critic.

Implements W5: between iterations of the same journey the only files that change
are the kейсы. We hash them and reuse the lint result if nothing changed. The
critic still gets a fresh report for changed files; unchanged ones keep their
cached finding set.

Usage:
    python3 scripts/cached_validate.py <cases_dir> [--json <out>]

Exit codes match validate_cases.py (0 = no blockers, 1 = blockers).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def fingerprint(cases_dir: Path) -> dict[str, str]:
    """Map relative path → short hash for every .md and .json under cases_dir.

    Excludes cache and lint output: hashing them would invalidate the cache on
    every run. Only case files (`*.md`/`*.json` excluding `.lint-cache.json`).
    """
    fp: dict[str, str] = {}
    for p in sorted(cases_dir.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix not in (".md", ".json"):
            continue
        if p.name.startswith("_"):
            continue
        # Skip cache and lint artefacts so they don't poison the fingerprint.
        if p.name in (".lint-cache.json", "lint.json"):
            continue
        try:
            fp[str(p.relative_to(cases_dir))] = file_hash(p)
        except OSError:
            continue
    return fp


def load_cache(cases_dir: Path) -> tuple[dict, dict]:
    cache_path = cases_dir / ".lint-cache.json"
    if not cache_path.is_file():
        return {}, {}
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}, {}
    return cache.get("fingerprint", {}), cache.get("report", {})


def save_cache(cases_dir: Path, fp: dict[str, str], report: dict) -> None:
    cache_path = cases_dir / ".lint-cache.json"
    cache_path.write_text(
        json.dumps({"fingerprint": fp, "report": report}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run_lint(cases_dir: Path, json_out: Path | None) -> tuple[int, dict]:
    here = Path(__file__).resolve().parent
    validator = here / "validate_cases.py"
    cmd = [sys.executable, str(validator), str(cases_dir)]
    if json_out is not None:
        cmd.extend(["--json", str(json_out)])
    cmd.append("--quiet")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    sys.stderr.write(proc.stderr)
    sys.stdout.write(proc.stdout)

    report: dict = {}
    if json_out is not None and json_out.is_file():
        try:
            report = json.loads(json_out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report = {}
    return proc.returncode, report


def main() -> int:
    ap = argparse.ArgumentParser(description="Cached lint wrapper for the critic")
    ap.add_argument("cases_dir", help="папка с кейсами, например output/cases/J01-...")
    ap.add_argument("--json", dest="json_out", help="куда записать JSON-отчёт")
    args = ap.parse_args()

    cases_dir = Path(args.cases_dir)
    if not cases_dir.is_dir():
        sys.stderr.write(f"cached_validate: не директория: {cases_dir}\n")
        return 2

    current_fp = fingerprint(cases_dir)
    cached_fp, cached_report = load_cache(cases_dir)
    json_out = Path(args.json_out) if args.json_out else None

    if current_fp and current_fp == cached_fp and cached_report:
        print(f"[cached] lint без изменений ({len(current_fp)} файлов), использую кэш")
        if json_out is not None:
            json_out.parent.mkdir(parents=True, exist_ok=True)
            json_out.write_text(
                json.dumps(cached_report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        counts = cached_report.get("counts", {})
        if counts.get("BLOCKER", 0):
            return 1
        return 0

    print(f"[fresh] lint ({len(current_fp)} файлов изменились или кэш отсутствует)")
    rc, report = run_lint(cases_dir, json_out)
    if report:
        save_cache(cases_dir, current_fp, report)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
