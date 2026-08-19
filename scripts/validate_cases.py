#!/usr/bin/env python3
"""Deterministic linter for e2e test cases produced by the qa-designer agent.

Checks structure, placeholders, step numbering, expected-result observability,
step atomicity, test-data usage and Markdown/JSON parity.

Usage:
    python3 scripts/validate_cases.py output/cases
    python3 scripts/validate_cases.py output/cases/J01-onboarding --json output/reviews/J01-lint.json

Exit code 0 = no blockers, 1 = blockers found, 2 = nothing to check.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "Общая информация",
    "Предусловия",
    "Тестовые данные",
    "Шаги",
    "Постусловия",
    "Выявленные пробелы",
    "Уточняющие вопросы",
]

# Sections that may legitimately contain only "—"
SOFT_SECTIONS = {"Выявленные пробелы", "Уточняющие вопросы"}

REQUIRED_FIELDS = [
    "ID",
    "Название",
    "Цель",
    "Приоритет",
    "Journey",
    "Вариант от",
    "Покрываемые требования",
]

VALID_PRIORITIES = {"критический", "высокий", "средний", "низкий"}

# Words that describe "it worked" without naming anything observable.
VAGUE = [
    "успешно",
    "успешный",
    "корректно",
    "корректный",
    "правильно",
    "работает",
    "без ошибок",
    "ошибок нет",
    "как ожидается",
    "как ожидалось",
    "ожидаемо",
    "выполнено",
    "нормально",
    "всё хорошо",
    "все хорошо",
    "соответствует ожиданиям",
    "должно работать",
    "ok",
    "ок",
]

# Text that means the author left a hole.
PLACEHOLDERS = [
    "todo",
    "tbd",
    "xxx",
    "заполнить",
    "любой трек",
    "какой-нибудь",
    "какой-либо",
    "n/a",
    "нужно уточнить у себя",
]

# An unfilled slot is a *pair* of angle brackets around a short label:
# <название плейлиста>, <track>. A lone "<" is arithmetic — «время отклика < 2 сек»,
# «лимит < 100» — and blocking it made every comparison a false BLOCKER, which the
# critic is forbidden to argue with (docs/critic-rubric.md), so a correct case lost
# a whole design+review iteration.
PLACEHOLDER_SLOT = re.compile(r"<[^<>\s][^<>]{0,58}>")

# Markers of more than one action inside a single step.
MULTI_ACTION = [
    " и затем ",
    " затем ",
    " после чего ",
    ", после этого ",
    " и после ",
    ";",
]

MIN_MAIN_STEPS = 8

# Ceiling on how far one stage may be unrolled into steps. Measured density on every
# main case on disk: 1.25 and 1.38 and 1.75 (Knox, three runs on one corpus) and 1.58
# (the Звук reference in examples/). Two is above all four with margin, so the rule
# guards against runaway expansion instead of enforcing a house style — the floor had
# no counterpart until three runs turned 8 stages into 10, 11 and 14 steps.
MAX_STEPS_PER_STAGE = 2

MIN_EXPECTED_LEN = 20
VAGUE_SHORT_CELL = 60


class Finding:
    def __init__(self, severity: str, rule: str, file: str, location: str, message: str, fix: str):
        self.severity = severity
        self.rule = rule
        self.file = file
        self.location = location
        self.message = message
        self.fix = fix

    def as_dict(self) -> dict:
        return {
            "severity": self.severity,
            "rule": self.rule,
            "file": self.file,
            "location": self.location,
            "message": self.message,
            "fix": self.fix,
        }

    def __str__(self) -> str:
        return f"[{self.severity}] {self.file} :: {self.location} :: {self.message} → {self.fix}"


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = None
    buffer: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current = m.group(1).strip()
            buffer = []
        else:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer).strip()
    return sections


def parse_table(block: str) -> list[list[str]]:
    """Return data rows of the first Markdown table in the block."""
    rows: list[list[str]] = []
    seen_header = False
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if rows:
                break
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if re.fullmatch(r"[-: ]+", "".join(cells).replace("|", "")) and set("".join(cells)) <= set("-: "):
            seen_header = True
            continue
        if not seen_header:
            continue
        rows.append(cells)
    return rows


def parse_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"^\s*[-*]\s*\*\*(.+?):\*\*\s*(.*)$", line)
        if m:
            fields[m.group(1).strip()] = m.group(2).strip()
    return fields


def has_placeholder(value: str) -> str | None:
    low = value.lower()
    for p in PLACEHOLDERS:
        # Word boundaries, same as vague_hit: a bare substring match turned every
        # Admin API URL into a BLOCKER — «admi·n/a·pi» contains "n/a" — and the
        # designer worked around the linter with code spans instead of writing cases.
        if re.search(rf"(?<![a-zа-я0-9]){re.escape(p)}(?![a-zа-я0-9])", low):
            return p
    slot = PLACEHOLDER_SLOT.search(value)
    if slot:
        return slot.group(0)
    return None


def vague_hit(value: str) -> str | None:
    low = value.lower()
    for w in VAGUE:
        if re.search(rf"(?<![а-яa-z]){re.escape(w)}(?![а-яa-z])", low):
            return w
    return None


def normalize_cell(value: str) -> str:
    """Markdown cell and JSON string, reduced to comparable text.

    Strips emphasis markers and collapses whitespace — nothing more. The point is to
    catch a JSON twin whose *content* drifted from the Markdown, not to punish a
    designer for `**bold**`. Anything this normalization cannot equate is a real
    difference in wording, and per the format contract the two must be
    «содержательно идентичны».
    """
    return " ".join(value.replace("**", "").replace("`", "").replace("*", "").split())


def section_is_empty(body: str) -> bool:
    stripped = re.sub(r"[-*\s—\d.]", "", body)
    return stripped == ""


def plan_for(case_path: Path, override: str | None) -> Path | None:
    """The suite plan that owns this case, or None when it cannot be located.

    Two layouts are recognised: a run tree (output/cases/<JID>/ beside
    output/suites/<JID>.md) and the self-contained example directory, which keeps
    its plan next to the cases as _suite-plan.md.
    """
    if override:
        p = Path(override)
        return p if p.is_file() else None
    jid = case_path.parent.name
    candidates = [
        case_path.parent.parent.parent / "suites" / f"{jid}.md",
        Path("output/suites") / f"{jid}.md",
        case_path.parent / "_suite-plan.md",
    ]
    return next((c for c in candidates if c.is_file()), None)


def stage_count(plan: Path) -> int | None:
    """Rows of the plan's «Этапы» table — the same table validate_plans.py reads."""
    m = re.search(r"^##\s+Этапы\s*$(.*?)(?=^##\s|\Z)", plan.read_text(encoding="utf-8"),
                  re.M | re.S)
    if not m:
        return None
    rows = sum(1 for line in m.group(1).splitlines() if re.match(r"^\|\s*\d+\s*\|", line))
    return rows or None


def check_case(path: Path, findings: list[Finding], stages: int | None = None) -> None:
    name = str(path)
    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)

    def add(sev, rule, loc, msg, fix):
        findings.append(Finding(sev, rule, name, loc, msg, fix))

    # --- structure -------------------------------------------------------
    for required in REQUIRED_SECTIONS:
        if required not in sections:
            add("BLOCKER", "missing-section", f"## {required}",
                "Обязательный раздел отсутствует",
                f"Добавить раздел «{required}» по docs/format.md")
            continue
        body = sections[required]
        if section_is_empty(body) and required not in SOFT_SECTIONS:
            add("BLOCKER", "empty-section", f"## {required}",
                "Обязательный раздел пуст",
                "Заполнить раздел конкретным содержанием")

    # --- header fields ---------------------------------------------------
    fields = parse_fields(sections.get("Общая информация", ""))
    for f in REQUIRED_FIELDS:
        value = fields.get(f)
        if value is None:
            add("BLOCKER", "missing-field", f"Общая информация / {f}",
                "Поле отсутствует", f"Добавить поле **{f}:**")
        elif value in ("", "…") or (has_placeholder(value) and f != "Вариант от"):
            add("BLOCKER", "placeholder-field", f"Общая информация / {f}",
                f"Поле не заполнено или содержит заглушку: '{value}'",
                "Подставить конкретное значение")

    priority = fields.get("Приоритет", "").strip().lower().rstrip(".")
    if priority and priority not in VALID_PRIORITIES and "|" not in priority:
        add("MINOR", "priority-value", "Общая информация / Приоритет",
            f"Нестандартное значение приоритета: '{priority}'",
            "Использовать: Критический / Высокий / Средний / Низкий")

    case_id = fields.get("ID", "").strip()
    is_variant = fields.get("Вариант от", "—").strip() not in ("—", "-", "", "None")
    if case_id and not re.fullmatch(r"TC-J\d{2}-\d{2}", case_id):
        add("MINOR", "id-format", "Общая информация / ID",
            f"ID '{case_id}' не соответствует шаблону TC-J<NN>-<NN>",
            "Переименовать по docs/format.md")
    if case_id.endswith("-00") and is_variant:
        add("MAJOR", "variant-flag", "Общая информация / Вариант от",
            "Основной кейс помечен как вариант",
            "Поставить «—» в поле «Вариант от»")
    if case_id and not case_id.endswith("-00") and not is_variant:
        add("MAJOR", "variant-flag", "Общая информация / Вариант от",
            "Кейс-вариант не ссылается на основной кейс",
            "Указать «Вариант от: TC-J<NN>-00»")

    # --- test data -------------------------------------------------------
    data_rows = parse_table(sections.get("Тестовые данные", ""))
    data_values: list[str] = []
    for i, row in enumerate(data_rows, start=1):
        if len(row) < 2:
            add("MAJOR", "data-table", f"Тестовые данные / строка {i}",
                "Строка таблицы данных неполна",
                "Формат: | Параметр | Значение | Комментарий |")
            continue
        param, value = row[0], row[1]
        if not param or not value:
            add("BLOCKER", "data-empty", f"Тестовые данные / строка {i}",
                "Пустой параметр или значение", "Указать конкретное значение")
            continue
        ph = has_placeholder(value)
        if ph:
            add("BLOCKER", "data-placeholder", f"Тестовые данные / {param}",
                f"Значение содержит заглушку '{ph}': {value}",
                "Подставить конкретное, стабильное значение")
        else:
            data_values.append(value)
    if not data_rows:
        add("BLOCKER", "data-missing", "Тестовые данные",
            "Таблица тестовых данных отсутствует",
            "Добавить таблицу | Параметр | Значение | Комментарий |")

    # --- steps -----------------------------------------------------------
    step_rows = parse_table(sections.get("Шаги", ""))
    if not step_rows:
        add("BLOCKER", "steps-missing", "Шаги",
            "Таблица шагов отсутствует или не распознана",
            "Использовать таблицу | № | Действие | Тестовые данные | Ожидаемый результат |")
        return

    if not is_variant and len(step_rows) < MIN_MAIN_STEPS:
        add("BLOCKER", "steps-too-few", "Шаги",
            f"В основном кейсе {len(step_rows)} шагов, минимум {MIN_MAIN_STEPS} — это не сквозной сценарий",
            "Развернуть путь до полного journey по suite-плану")

    if not is_variant and stages:
        ceiling = MAX_STEPS_PER_STAGE * stages
        if len(step_rows) > ceiling:
            add("MAJOR", "steps-too-many", "Шаги",
                f"В основном кейсе {len(step_rows)} шагов на {stages} этапов плана "
                f"({len(step_rows) / stages:.2f} на этап), потолок {ceiling}",
                "Свести шаги, дробящие одно наблюдаемое, обратно в один шаг — "
                "или обосновать этапами: потолок считается от плана")

    steps_text = " ".join(" ".join(r) for r in step_rows).lower()
    # Markdown markers stripped for substring matching below: a value written as
    # `https://host:8443` in the data table appears inside `https://host:8443/path`
    # in a step, and the trailing backtick made the literal token miss. Third
    # instance of a linter rule reporting a defect the case does not have —
    # after "<" arithmetic and "n/a" inside admi·n/a·pi.
    steps_text_plain = normalize_cell(steps_text).lower()

    for idx, row in enumerate(step_rows, start=1):
        loc = f"Шаги / шаг {idx}"
        if len(row) != 4:
            add("BLOCKER", "step-columns", loc,
                f"В строке {len(row)} колонок вместо 4",
                "Привести строку к формату из docs/format.md")
            continue
        num, action, data, expected = row
        num_clean = num.strip().rstrip(".")
        if not num_clean.isdigit() or int(num_clean) != idx:
            add("BLOCKER", "step-numbering", loc,
                f"Нарушена нумерация шагов: '{num}' на позиции {idx}",
                "Пронумеровать шаги подряд с 1")
        if not action:
            add("BLOCKER", "step-empty-action", loc, "Пустое действие пользователя",
                "Описать одно конкретное действие")
        if not expected:
            add("BLOCKER", "step-empty-expected", loc, "Пустой ожидаемый результат",
                "Описать наблюдаемый результат")
            continue

        ph = has_placeholder(action) or has_placeholder(expected)
        if ph:
            add("BLOCKER", "step-placeholder", loc,
                f"Шаг содержит заглушку '{ph}'",
                "Заменить на конкретное значение или вынести в пробелы")

        vw = vague_hit(expected)
        if vw:
            if len(expected) < VAGUE_SHORT_CELL:
                add("BLOCKER", "vague-expected", loc,
                    f"Расплывчатый ожидаемый результат («{vw}») без наблюдаемого признака: {expected}",
                    "Указать экран, элемент, текст, состояние, счётчик или порядок")
            else:
                add("MAJOR", "vague-wording", loc,
                    f"В ожидаемом результате есть оценочное слово «{vw}»",
                    "Убрать оценку, оставить наблюдаемый признак")
        elif len(expected) < MIN_EXPECTED_LEN:
            add("MAJOR", "expected-too-short", loc,
                f"Слишком короткий ожидаемый результат: {expected}",
                "Дополнить наблюдаемым признаком")

        low_action = action.lower()
        for marker in MULTI_ACTION:
            if marker in low_action:
                add("MAJOR", "step-not-atomic", loc,
                    f"В одном шаге несколько действий (маркер '{marker.strip()}')",
                    "Разбить на отдельные шаги")
                break
        else:
            if low_action.count(" и ") >= 2:
                add("MAJOR", "step-not-atomic", loc,
                    "В одном шаге несколько действий (два и более союза «и»)",
                    "Разбить на отдельные шаги")

        if not data:
            add("MINOR", "step-data-empty", loc,
                "Колонка тестовых данных пуста",
                "Указать значение или «—»")

    # --- data usage & continuity ----------------------------------------
    used = 0
    for value in data_values:
        token = normalize_cell(value).lower().strip()
        if len(token) < 3:
            continue
        if token in steps_text_plain:
            used += 1
        else:
            add("MAJOR", "data-unused", "Тестовые данные",
                f"Значение не используется ни в одном шаге: {value}",
                "Использовать значение в шагах или убрать из таблицы")
    if data_values and used == 0:
        add("BLOCKER", "no-data-continuity", "Шаги",
            "Ни одно тестовое значение не встречается в шагах — сценарий не связан данными",
            "Ссылаться на конкретные значения из таблицы данных")

    if len(step_rows) >= 6 and data_values:
        tail = " ".join(" ".join(r) for r in step_rows[len(step_rows) // 2:]).lower()
        if not any(v.lower() in tail for v in data_values if len(v) >= 3):
            add("MAJOR", "weak-continuity", "Шаги",
                "Во второй половине сценария не переиспользуются данные из первой",
                "Проверять в поздних шагах объекты, созданные в ранних")

    # --- markdown / json parity -----------------------------------------
    json_path = path.with_suffix(".json")
    if not json_path.exists():
        add("MAJOR", "json-missing", str(json_path.name),
            "Нет JSON-версии кейса",
            "Сгенерировать JSON по docs/format.md")
    else:
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            add("BLOCKER", "json-invalid", str(json_path.name),
                f"JSON невалиден: {exc}", "Исправить синтаксис JSON")
        else:
            if data.get("id", "") != case_id:
                add("BLOCKER", "json-id-mismatch", str(json_path.name),
                    f"ID в JSON ('{data.get('id')}') не совпадает с Markdown ('{case_id}')",
                    "Синхронизировать JSON с Markdown")
            if len(data.get("steps", [])) != len(step_rows):
                add("BLOCKER", "json-steps-mismatch", str(json_path.name),
                    f"Шагов в JSON {len(data.get('steps', []))}, в Markdown {len(step_rows)}",
                    "Синхронизировать JSON с Markdown")
            else:
                # Same count is necessary, not sufficient: the id/count checks pass while
                # a step's wording silently diverges, and downstream the JSON is what the
                # pytest writer consumes. MAJOR, not BLOCKER — the normalization is
                # deliberately shallow, and a false BLOCKER costs a design+review
                # iteration (the O-05 lesson).
                fields = (("action", 1, "действие"),
                          ("testData", 2, "тестовые данные"),
                          ("expectedResult", 3, "ожидаемый результат"))
                for idx, (jstep, row) in enumerate(zip(data["steps"], step_rows), start=1):
                    if not isinstance(jstep, dict) or len(row) != 4:
                        continue
                    for key, col, label in fields:
                        md_val = normalize_cell(row[col])
                        js_val = normalize_cell(str(jstep.get(key, "")))
                        if md_val != js_val:
                            add("MAJOR", "json-step-drift",
                                f"{json_path.name} / шаг {idx}",
                                f"{label} в JSON расходится с Markdown: "
                                f"«{js_val[:60]}» ≠ «{md_val[:60]}»",
                                "Синхронизировать JSON с Markdown — содержательно идентичны")
                            break  # одного расхождения на шаг достаточно


def collect(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if target.suffix == ".md" else []
    return sorted(
        p for p in target.rglob("*.md")
        if not p.name.startswith("_") and "review" not in p.name.lower()
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint e2e test cases")
    ap.add_argument("target", nargs="?", default="output/cases", help="file or directory")
    ap.add_argument("--json", dest="json_out", help="write JSON report to this path")
    ap.add_argument("--quiet", action="store_true", help="only print the summary line")
    ap.add_argument("--plan", help="suite plan for the stage ceiling; found automatically "
                                   "at output/suites/<JOURNEY_ID>.md or <case dir>/_suite-plan.md")
    args = ap.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"validate_cases: path not found: {target}", file=sys.stderr)
        return 2

    files = collect(target)
    if not files:
        print(f"validate_cases: no .md cases under {target}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    unmeasured: set[str] = set()
    for f in files:
        plan = plan_for(f, args.plan)
        stages = stage_count(plan) if plan else None
        if stages is None:
            unmeasured.add(f.parent.name)
        check_case(f, findings, stages)

    counts = {"BLOCKER": 0, "MAJOR": 0, "MINOR": 0}
    for f in findings:
        counts[f.severity] += 1

    if not args.quiet:
        for severity in ("BLOCKER", "MAJOR", "MINOR"):
            for f in findings:
                if f.severity == severity:
                    print(f)

    print(
        f"checked {len(files)} case file(s): "
        f"BLOCKER {counts['BLOCKER']}, MAJOR {counts['MAJOR']}, MINOR {counts['MINOR']}"
    )
    if unmeasured:
        # Naming what went unchecked: a rule silently skipped reads as a rule that passed.
        print(f"  потолок шагов не проверен — план не найден: {', '.join(sorted(unmeasured))}")

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(
                {
                    "checkedFiles": [str(f) for f in files],
                    "counts": counts,
                    "findings": [f.as_dict() for f in findings],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"json report → {out}")

    return 1 if counts["BLOCKER"] else 0


if __name__ == "__main__":
    sys.exit(main())
