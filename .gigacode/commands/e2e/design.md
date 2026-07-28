---
description: Run only the qa-designer for one journey — write test cases from an existing suite plan.
---

Delegate to the `qa-designer` subagent via the `agent` tool. Do not write cases yourself.

Arguments: {{args}} (journey id, e.g. `J01`; optionally a review file path for a fix iteration)

Existing suite plans:

!{ls -1 output/suites/ 2>/dev/null || echo "NO SUITE PLANS — run /e2e:analyze first"}

Existing reviews:

!{ls -1 output/reviews/ 2>/dev/null || echo "no reviews yet"}

Prompt the subagent with:
- the suite plan path for the requested journey
- the requirement file paths (source of truth)
- `docs/format.md` and `templates/test-case.md`
- the output directory `output/cases/<JOURNEY_ID>/`
- if a review path was given: "fix iteration, address every BLOCKER, keep diffs minimal"

When it finishes, report: files written, step count of the main case, number of variants, gaps and
questions raised, and the linter result.
