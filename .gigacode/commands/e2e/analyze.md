---
description: Run only the requirements-analyst — produce journey / suite plans from requirements.
---

Delegate to the `requirements-analyst` subagent via the `agent` tool. Do not analyse yourself.

Arguments: {{args}} (requirements path or glob; default `input/requirements/*.md`)

Available requirement files:

!{ls -1 input/requirements/ 2>/dev/null || echo "NO REQUIREMENTS FOUND"}

Prompt the subagent with:
- the exact requirement file paths to read
- the contract files: `docs/format.md`, `QWEN.md`, `templates/suite-plan.md`
- the output directory: `output/suites/`

When it finishes, read the produced plans and show me a table: journey id, title, stages, functional
areas crossed, variants, gaps, questions. Flag any journey with fewer than 5 stages or with no data
carried between stages — those are grouping mistakes and should be sent back.
