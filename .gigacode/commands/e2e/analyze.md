---
description: Run only the requirements-analyst — produce journey / suite plans from requirements.
---

Delegate to the `requirements-analyst` subagent via the `agent` tool. Do not analyse yourself.

Arguments: {{args}} (requirements path or glob; default `input/requirements/*.md`)

Available requirement files:

!{ls -1 input/requirements/ 2>/dev/null || echo "NO REQUIREMENTS FOUND"}

Prompt the subagent with:
- the exact requirement file paths to read (include `input/requirements/_answers.md` if it exists)
- the contract files: `docs/format.md`, `QWEN.md`, `templates/suite-plan.md`
- the output directory: `output/suites/`, and the machine index `output/suites/_index.json`

When it finishes, read `output/suites/_index.json` and the produced plans, then show me a table:
journey id, title, stages, functional areas crossed, variants, gaps, questions, plan path. Flag any
journey with fewer than 5 stages, fewer than 3 areas, or with no data carried between stages — those
are grouping mistakes and should be sent back.

## Then tell me what is missing, explicitly

Before I do anything with these plans, print in full — items, not counts:

1. **Непокрытые требования** — every `REQ-XX` in no stage, with the analyst's reason.
2. **Пробелы** — silence, contradiction, ambiguity, each with the quoted requirement text.
3. **Блокирующие вопросы** — ordered by how many stages and variants each one blocks.
4. **Этапы без требования** — stages marked `БЕЗ ТРЕБОВАНИЯ`.

If a list is empty, say so — «непокрытых требований нет» is a result, not a reason to stay silent.

Then ask me, with the interactive question tool your runtime exposes (`ask_user_question` /
`AskUserQuestion` / equivalent, or a numbered list and a stopped turn if there is none):
«Как поступить с пробелами?» — *Продолжить к /e2e:design* / *Я отвечу на вопросы сейчас* /
*Остановиться, поправлю требования*.

If I answer the questions, write them into `input/requirements/_answers.md` (Russian, numbered, each
answer quoting its question) and re-run the analyst with that file added to its inputs.
