---
description: Show loop state — suites, cases, reviews, last verdict, unresolved questions.
---

Current artefacts:

!{echo "=== suites ==="; ls -1 output/suites/ 2>/dev/null; echo; echo "=== cases ==="; find output/cases -name '*.md' 2>/dev/null | sort; echo; echo "=== reviews ==="; ls -1 output/reviews/ 2>/dev/null; echo; echo "=== per-journey state ==="; for f in output/state/*.json; do [ -e "$f" ] && echo "--- $f" && cat "$f"; done 2>/dev/null || echo "no per-journey state"; echo; echo "=== aggregate state ==="; cat output/state.json 2>/dev/null || echo "no state file"}

Linter over everything currently generated:

!{python3 scripts/validate_cases.py output/cases 2>&1 | tail -30}

Summarise for me in one short table: journey, cases, last iteration, last verdict, blockers left,
and whether the journey is still active in the loop. If `output/state/*.json` and `output/state.json`
disagree, trust the per-journey files — they are written by the critics, the aggregate is a snapshot
the orchestrator refreshes between waves.

Then list, deduplicated and ordered by how many cases each one blocks:

- open clarifying questions gathered from the case files, plans and `uncoveredReqs` in the state files
- requirements no case checks

Mark each question answered if `input/requirements/_answers.md` already resolves it. Do not re-run
any agent.
