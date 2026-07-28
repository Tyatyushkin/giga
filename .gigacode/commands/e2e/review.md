---
description: Run only the test-critic — review generated cases against requirements and issue a fix list.
---

Delegate to the `test-critic` subagent via the `agent` tool. Do not review the cases yourself and do
not defend the designer's choices.

Arguments: {{args}} (journey id, e.g. `J01`; optionally the iteration number)

Cases currently on disk:

!{find output/cases -name '*.md' 2>/dev/null | sort || echo "NO CASES — run /e2e:design first"}

Prompt the subagent with:
- the case directory, the suite plan path, the requirement file paths
- `docs/critic-rubric.md`, `docs/quality-criteria.md`, `docs/format.md`
- the review output path `output/reviews/<JOURNEY_ID>-iter<N>.md`
- the instruction to run `scripts/validate_cases.py` first and merge its findings

When it finishes, print the verdict line and the blocker list verbatim. If the verdict is
FIX_REQUIRED, tell me the exact `/e2e:design` invocation that will start the fix iteration.
