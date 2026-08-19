---
description: Run only the requirements-analyst — produce journey / suite plans from requirements.
---

Delegate to the `requirements-analyst` subagent via the `agent` tool. Do not analyse yourself.

Arguments: {{args}} (requirements path or glob; default `input/requirements/*.md`)

Available requirement files:

!{ls -1 input/requirements/ 2>/dev/null || echo "NO REQUIREMENTS FOUND"}

Prompt the subagent with:
- the exact requirement file paths to read (include `input/requirements/_answers.md` if it exists)
- the contract files: `docs/format.md`, `GIGACODE.md`, `templates/suite-plan.md`
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

## Then ask me — do not compose the question yourself

Build the question payload deterministically, the same way `/e2e:run` does:

```
python3 scripts/build_gate_questions.py --parallel 1 --unit journey
```

This writes `output/gate/questions.json`. Take the five lists above from its `lists` field, then pass
`gateQuestions` (here: only В1 — покрытие) to your runtime's interactive question tool
(`ask_user_question` / `AskUserQuestion`) **verbatim** — same `header`, same `question`, same options
in the same order. Do not reword them, do not add an «Другое» option, do not answer on my behalf, and
make the tool call the last action in your message.

If the tool call fails, repair it once (`header` ≤ 12 chars, `label` ≤ 5 words, ≤ 4 options) and retry.
If it fails again, print the **same options** as a numbered list, add «ответьте номером или своим
вариантом», and end your turn immediately. Never turn a multiple-choice gate into an open question.

Record my answer in `output/gate/answers.json` as
`{"coverage": "continue|answer-now|stop", "parallel": 1, "unit": "journey", "answers": []}`.

If I choose «Отвечу на вопросы сейчас», ask the `blockingQuestionPrompts` in batches of up to 4,
filling `options` yourself with 2–4 plausible **product** answers (mark any the requirements do not
confirm as «предположение»); free text comes back through «Другое». Then write
`input/requirements/_answers.md` (Russian, numbered, each answer quoting its question) and re-run the
analyst with that file added to its inputs.
