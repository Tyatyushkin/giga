---
description: Run only the requirements-analyst — produce journey / suite plans from requirements.
---

Delegate to the `requirements-analyst` subagent via the `agent` tool. Do not analyse yourself.

Arguments: {{args}} (requirements path or glob; default `input/requirements/*.md`)

Available requirement files:

!{ls -1 input/requirements/ 2>/dev/null || echo "NO REQUIREMENTS FOUND"}

Build the prompt by the briefing protocol below — row `requirements-analyst`.

!{python3 scripts/include_skill.py subagent-briefing --level 2}

When it finishes, read `output/suites/_index.json` and the produced plans, then show me a table:
journey id, title, stages, functional areas crossed, variants, gaps, questions, plan path. Flag any
journey with fewer than 5 stages, fewer than 3 areas, or with no data carried between stages — those
are grouping mistakes and should be sent back.

## Then run the requirements gate

Follow the procedure below. Two things are specific to this command:

- pass `--parallel 1 --unit journey` to `build_gate_questions.py` — this command launches no
  designers, so В2 (parallelism) and В3 (ownership) do not apply here;
- **skip Step 5** (`gate_check.py`) — it gates the launch of designers, and this command stops at
  the gate.

Everything else applies as written: all five lists in full, the verbatim payload, the «отвечу
сейчас» branch, and re-running the analyst once answers exist.

!{python3 scripts/include_skill.py requirements-gate --level 3}

The question protocol the gate refers to:

!{python3 scripts/include_skill.py human-gate --level 3}
