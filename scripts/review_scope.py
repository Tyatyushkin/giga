#!/usr/bin/env python3
"""Decide what a fix iteration actually has to re-review.

On iteration 2+ the critic re-runs five passes and twelve criteria over *every* case,
including the ones nobody touched. With the usual "one blocker in one case out of five"
that is four fifths of the review stage spent re-confirming what was already confirmed.

This script narrows the scope — and, more importantly, narrows it *safely*. Skipping the
wrong case would silently weaken the gate the whole project rests on, so the rule is
fail-closed: anything it cannot prove unchanged goes back for a full review.

Invalidation rules
------------------
run id changed or absent        -> everything (a baseline from another run proves
                                   nothing about this one; absence means unknown)
requirements / answers changed  -> everything (behaviour was redefined)
suite plan changed              -> everything (the journey's scope moved)
rubric / criteria / format      -> everything (the rules of judgement moved)
main case changed               -> the main case AND every variant
                                   (variants inherit its preconditions — this is the
                                    trap a naive per-file hash diff would walk into)
variant changed                 -> that variant only
no baseline yet                 -> everything (first iteration)

Usage:
    python3 scripts/review_scope.py --journey J01-slug
    python3 scripts/review_scope.py --journey J01-slug --update   # stamp after review

Exit codes: 0 = scope written, 2 = journey/case directory missing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

# Changing any of these re-opens every case: they define behaviour or how it is judged.
# output/.run is here so a baseline cannot outlive the run that produced it — see
# scripts/start_run.py. Its absence is handled separately, and also means full review.
RUN_FILE = "output/.run"

GLOBAL_INPUTS = [
    RUN_FILE,
    "input/requirements",
    "docs/critic-rubric.md",
    "docs/quality-criteria.md",
    "docs/format.md",
]

MAIN_CASE = re.compile(r"TC-J\d{2}-00$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def hash_tree(target: Path) -> dict[str, str]:
    """Hash a file, or every .md/.json under a directory."""
    if target.is_file():
        return {str(target): digest(target)}
    if not target.is_dir():
        return {}
    out: dict[str, str] = {}
    for p in sorted(target.rglob("*")):
        if p.is_file() and p.suffix in (".md", ".json"):
            out[str(p)] = digest(p)
    return out


def current_run_id() -> str | None:
    """Read the run id verbatim, so invalidation does not rest on a hash alone."""
    path = Path(RUN_FILE)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("runId")
    except json.JSONDecodeError:
        return None


def global_fingerprint() -> dict[str, str]:
    fp: dict[str, str] = {}
    for entry in GLOBAL_INPUTS:
        fp.update(hash_tree(Path(entry)))
    return fp


def case_fingerprints(case_dir: Path) -> dict[str, str]:
    """One hash per case id, covering its Markdown and its JSON twin together."""
    cases: dict[str, list[str]] = {}
    for p in sorted(case_dir.glob("TC-*")):
        if p.suffix not in (".md", ".json"):
            continue
        cases.setdefault(p.stem, []).append(digest(p))
    return {cid: hashlib.sha256("".join(h).encode()).hexdigest()[:16]
            for cid, h in sorted(cases.items())}


def main() -> int:
    ap = argparse.ArgumentParser(description="Что нужно переревьюить на этой итерации")
    ap.add_argument("--journey", required=True, help="JOURNEY_ID, например J01-registration-…")
    ap.add_argument("--cases-dir", help="по умолчанию output/cases/<JOURNEY_ID>")
    ap.add_argument("--plan", help="по умолчанию output/suites/<JOURNEY_ID>.md")
    ap.add_argument("--baseline", help="по умолчанию output/reviews/<JOURNEY_ID>-hashes.json")
    ap.add_argument("--update", action="store_true",
                    help="записать текущие хеши как базу (делать ПОСЛЕ успешного ревью)")
    ap.add_argument("--json", dest="json_out", help="куда записать решение об объёме")
    args = ap.parse_args()

    jid = args.journey
    case_dir = Path(args.cases_dir or f"output/cases/{jid}")
    plan = Path(args.plan or f"output/suites/{jid}.md")
    baseline_path = Path(args.baseline or f"output/reviews/{jid}-hashes.json")

    if not case_dir.is_dir():
        sys.stderr.write(f"review_scope: нет каталога кейсов: {case_dir}\n")
        return 2

    current = {
        "journeyId": jid,
        "runId": current_run_id(),
        "global": global_fingerprint(),
        "plan": digest(plan) if plan.is_file() else None,
        "cases": case_fingerprints(case_dir),
    }
    if not current["cases"]:
        sys.stderr.write(f"review_scope: в {case_dir} нет кейсов TC-*\n")
        return 2

    baseline = None
    if baseline_path.is_file():
        try:
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            baseline = None  # fail closed: unreadable baseline means full review

    all_cases = sorted(current["cases"])
    reason_global: str | None = None

    if not Path(RUN_FILE).is_file():
        reason_global = ("нет идентификатора прогона (output/.run) — "
                         "неизвестно, к какому прогону относится база")
    elif baseline is None:
        reason_global = "базы нет — первая итерация или база нечитаема"
    elif baseline.get("runId") != current["runId"]:
        reason_global = (f"база от другого прогона ({baseline.get('runId')}), "
                         f"текущий {current['runId']}")
    elif baseline.get("global") != current["global"]:
        reason_global = "изменились требования или правила оценки"
    elif baseline.get("plan") != current["plan"]:
        reason_global = "изменился план сьюты"

    if reason_global:
        required = all_cases
        carried: list[str] = []
        per_case = {c: "полное ревью: " + reason_global for c in all_cases}
    else:
        old_cases = baseline.get("cases", {})
        changed = [c for c in all_cases if old_cases.get(c) != current["cases"][c]]
        # A changed main case moves the preconditions every variant inherits.
        main_changed = any(MAIN_CASE.search(c) for c in changed)
        per_case = {}
        required = []
        for c in all_cases:
            if c in changed:
                per_case[c] = "кейс изменён"
                required.append(c)
            elif main_changed and not MAIN_CASE.search(c):
                per_case[c] = "изменён основной кейс — вариант наследует его предусловия"
                required.append(c)
            elif c not in old_cases:
                per_case[c] = "новый кейс"
                required.append(c)
            else:
                per_case[c] = "не изменён — findings переносятся"
        carried = [c for c in all_cases if c not in required]

    decision = {
        "journeyId": jid,
        "globalInvalidation": reason_global,
        "reviewRequired": required,
        "carryForward": carried,
        "perCase": per_case,
        "savedShare": round(len(carried) / len(all_cases), 2) if all_cases else 0.0,
    }

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[scope] {jid}: кейсов {len(all_cases)}, "
          f"переревьюить {len(required)}, перенести {len(carried)}")
    if reason_global:
        print(f"[scope] полное ревью — {reason_global}")
    for c in all_cases:
        mark = "REVIEW " if c in required else "carry  "
        print(f"[scope]   {mark} {c} — {per_case[c]}")
    if not reason_global and carried:
        print("[scope] перенесённые findings обязаны попасть в отчёт дословно, "
              "с пометкой «перенесено с итерации N-1»")

    if args.update:
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[scope] база хешей обновлена → {baseline_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
