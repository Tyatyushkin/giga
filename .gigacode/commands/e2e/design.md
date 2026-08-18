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

Build each prompt by the briefing protocol below — row `qa-designer`. If a review path was
given, it is a fix iteration: use the fix-iteration wording verbatim.

!{python3 scripts/include_skill.py subagent-briefing --level 2}

When they finish, report per journey: files written, step count of the main case, number of variants,
gaps and questions raised, and the linter result.

Then list the gaps and questions the designers raised while writing steps — these are new, the
analyst did not have them — and ask me whether to answer them now (into
`input/requirements/_answers.md`) or carry them into the review as declared gaps.

Ask via the question protocol below — mode B, you compose the options yourself:

!{python3 scripts/include_skill.py human-gate --level 2}
