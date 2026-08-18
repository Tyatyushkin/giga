---
description: Run only the qa-designer for one journey — write test cases from an existing suite plan.
---

Delegate to the `qa-designer` subagent via the `agent` tool. Do not write cases yourself.

Arguments: {{args}} (one or more journey ids, e.g. `J01` or `J01 J02 J03`; optionally a review file
path for a fix iteration of a single journey)

If I name several journeys, launch **one `qa-designer` per journey and emit all of those `agent`
calls in a single message** so they run concurrently. Each prompt names only its own journey and its
own case directory — designers must not share directories, and a designer that touches another
journey's files is a bug worth reporting to me.

Existing suite plans:

!{ls -1 output/suites/ 2>/dev/null || echo "NO SUITE PLANS — run /e2e:analyze first"}

Existing reviews:

!{ls -1 output/reviews/ 2>/dev/null || echo "no reviews yet"}

Prompt each subagent with:
- the suite plan path for its journey
- the requirement file paths (source of truth), including `input/requirements/_answers.md` if present
- `docs/format.md` and `templates/test-case.md`
- the output directory `output/cases/<JOURNEY_ID>/`
- the boundary line: "you own `<JOURNEY_ID>` only; do not read or write any other journey's directory"
- if a review path was given: "fix iteration, address every BLOCKER, keep diffs minimal"

When they finish, report per journey: files written, step count of the main case, number of variants,
gaps and questions raised, and the linter result.

Then list the gaps and questions the designers raised while writing steps — these are new, the
analyst did not have them — and ask me whether to answer them now (into
`input/requirements/_answers.md`) or carry them into the review as declared gaps.

Ask via the question protocol below — mode B, you compose the options yourself:

!{python3 scripts/include_skill.py human-gate --level 2}
