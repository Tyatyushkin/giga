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

Prompt each subagent with:
- its case directory, its suite plan path, the requirement file paths
  (including `input/requirements/_answers.md` if present — answers there rank as requirements)
- `docs/critic-rubric.md`, `docs/quality-criteria.md`, `docs/format.md`
- the review output path `output/reviews/<JOURNEY_ID>-iter<N>.md`
- the state output path `output/state/<JOURNEY_ID>.json`, and "never write `output/state.json`"
- the instruction to run `scripts/validate_cases.py` first and merge its findings

When they finish, print each verdict line and blocker list verbatim, then one summary line per
journey: `J01 iter2: BLOCKER 1, MAJOR 3, MINOR 2`. If any verdict is FIX_REQUIRED, give me the exact
`/e2e:design` invocation — with all failing journey ids in one call — that starts the fix iteration.

Finally, list the requirements the critics found unchecked and the questions still open, per journey.
Do not bury them in the review file: if coverage is incomplete, say which `REQ-XX` and ask me whether
to answer the blocking questions now or accept the gap.
