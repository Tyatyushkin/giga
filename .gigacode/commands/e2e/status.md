---
description: Show loop state — suites, cases, reviews, last verdict, unresolved questions.
---

Current artefacts:

!{echo "=== suites ==="; ls -1 output/suites/ 2>/dev/null; echo; echo "=== cases ==="; find output/cases -name '*.md' 2>/dev/null | sort; echo; echo "=== reviews ==="; ls -1 output/reviews/ 2>/dev/null; echo; echo "=== state ==="; cat output/state.json 2>/dev/null || echo "no state file"}

Linter over everything currently generated:

!{python3 scripts/validate_cases.py output/cases 2>&1 | tail -30}

Summarise for me in one short table: journey, cases, last iteration, last verdict, blockers left.
Then list the open clarifying questions gathered from the case files, deduplicated, ordered by how
many cases each one blocks. Do not re-run any agent.
