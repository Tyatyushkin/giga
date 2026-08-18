---
description: Run only the test-critic — review generated cases against requirements and issue a fix list.
---

Delegate to the `test-critic` subagent via the `agent` tool. Do not review the cases yourself and do
not defend the designer's choices.

Arguments: {{args}} (one or more journey ids, e.g. `J01` or `J01 J02 J03`; optionally the iteration
number)

If I name several journeys, launch **one `test-critic` per journey and emit all of those `agent`
calls in a single message** so they run concurrently. One critic never reviews two journeys.

Cases currently on disk:

!{find output/cases -name '*.md' 2>/dev/null | sort || echo "NO CASES — run /e2e:design first"}

Build each prompt by the briefing protocol below — row `test-critic`. From iteration 2 on,
add the `review_scope.py` wording verbatim.

!{python3 scripts/include_skill.py subagent-briefing --level 2}

When they finish, print each verdict line and blocker list verbatim, then one summary line per
journey: `J01 iter2: BLOCKER 1, MAJOR 3, MINOR 2`. If any verdict is FIX_REQUIRED, give me the exact
`/e2e:design` invocation — with all failing journey ids in one call — that starts the fix iteration.

Finally, list the requirements the critics found unchecked and the questions still open, per journey.
Do not bury them in the review file: if coverage is incomplete, say which `REQ-XX` and ask me whether
to answer the blocking questions now or accept the gap.

Ask via the question protocol below — mode B, you compose the options yourself:

!{python3 scripts/include_skill.py human-gate --level 2}
