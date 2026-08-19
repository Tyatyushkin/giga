#!/usr/bin/env python3
"""Конвертирует TC-*.json в TC-*.md по схеме из docs/format.md.

Использование:
    python3 scripts/json_to_md.py output/cases/J01-*/TC-*.json

Аргументы:
    --dry-run   — показать результат без записи файлов
    --quiet     — без вывода в stdout

JSON-кейс обязан содержать поля из схемы docs/format.md:
    id, title, goal, priority, journeyId, variantOf, requirements,
    preconditions, testData, steps, postconditions, gaps, clarifyingQuestions.

Каждый входной JSON порождает соответствующий MD-файл с тем же именем,
но расширением .md (overwrites если существует).
"""

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "id", "title", "goal", "priority", "journeyId",
    "steps", "preconditions", "postconditions",
]


def _field(value, fallback="—"):
    """Форматирует значение поля: None/пустой → '—'."""
    if value is None:
        return fallback
    if isinstance(value, list):
        # Обе ветки возвращали fallback, поэтому непустой список рендерился как «—».
        # Ни одно поле шапки сейчас не список, но `requirements` им является —
        # первое же его появление здесь молча стёрло бы содержимое.
        return ", ".join(str(v).strip() for v in value if str(v).strip()) or fallback
    return str(value).strip() or fallback


def _steps_table(steps):
    """Генерирует markdown-таблицу шагов."""
    if not steps:
        return "Шаги не определены.\n"

    lines = []
    lines.append("| № | Действие пользователя | Тестовые данные | Ожидаемый результат |")
    lines.append("|---:|---|---|---|")
    for s in steps:
        n = s.get("number", s.get("step", ""))
        action = s.get("action", "")
        td = s.get("testData", "") or s.get("test_data", "") or ""
        er = s.get("expectedResult", "") or s.get("expected_result", "") or ""
        lines.append(f"| {n} | {action} | {td} | {er} |")
    return "\n".join(lines) + "\n"


def _preconditions(preconds):
    """Форматирует список предусловий."""
    if not preconds:
        return "Не определены.\n"
    return "\n".join(f"- {p}" for p in preconds) + "\n"


def _postconditions(postconds):
    """Форматирует список постусловий."""
    if not postconds:
        return "Не определены.\n"
    return "\n".join(f"- {p}" for p in postconds) + "\n"


def _test_data_table(data):
    """Генерирует markdown-таблицу тестовых данных."""
    if not data:
        return "Не определены.\n"

    lines = []
    lines.append("| Параметр | Значение | Комментарий |")
    lines.append("|---|---|---|")
    for row in data:
        name = row.get("name", row.get("param", ""))
        value = row.get("value", "")
        comment = row.get("comment", "")
        lines.append(f"| {name} | {value} | {comment} |")
    return "\n".join(lines) + "\n"


def _gaps_list(gaps):
    if not gaps:
        return "Не выявлены.\n"
    return "\n".join(f"- {g}" for g in gaps) + "\n"


def _questions_list(questions):
    if not questions:
        return "Не выявлены.\n"
    return "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions)) + "\n"


def _requirements_line(reqs):
    """Форматирует список требований для поля Overview."""
    if not reqs:
        return "—"
    return ", ".join(reqs)


def json_to_md(data):
    """Конвертирует JSON-кейс в Markdown по шаблону docs/format.md."""
    lines = []

    # ── Заголовок ──
    lines.append("# E2E тест-кейс\n")

    # ── Общая информация ──
    lines.append("## Общая информация\n")

    variant_of = _field(data.get("variantOf"))
    reqs_line = _requirements_line(data.get("requirements", []))

    lines.append("- **ID:** " + _field(data.get("id")))
    lines.append("- **Название:** " + _field(data.get("title")))
    lines.append("- **Цель:** " + _field(data.get("goal")))
    lines.append("- **Приоритет:** " + _field(data.get("priority")))
    lines.append("- **Journey:** " + _field(data.get("journeyId")))
    lines.append("- **Вариант от:** " + variant_of)
    lines.append("- **Покрываемые требования:** " + reqs_line)
    lines.append("")

    # ── Предусловия ──
    lines.append("## Предусловия\n")
    lines.append(_preconditions(data.get("preconditions", [])))

    # ── Тестовые данные ──
    lines.append("## Тестовые данные\n")
    lines.append(_test_data_table(data.get("testData", [])))

    # ── Шаги ──
    lines.append("## Шаги\n")
    lines.append(_steps_table(data.get("steps", [])))

    # ── Постусловия ──
    lines.append("## Постусловия\n")
    lines.append(_postconditions(data.get("postconditions", [])))

    # ── Выявленные пробелы ──
    lines.append("## Выявленные пробелы\n")
    lines.append(_gaps_list(data.get("gaps", [])))

    # ── Уточняющие вопросы ──
    lines.append("## Уточняющие вопросы\n")
    lines.append(_questions_list(data.get("clarifyingQuestions", [])))

    return "\n".join(lines)


def validate(data, source_file):
    """Проверяет обязательные поля. Возвращает список проблем."""
    problems = []
    for field in REQUIRED_FIELDS:
        if field not in data or not data[field]:
            problems.append(f"  Пропущено поле: {field} ({source_file})")
    return problems


def main():
    parser = argparse.ArgumentParser(
        description="Конвертирует TC-*.json в TC-*.md по схеме docs/format.md"
    )
    parser.add_argument(
        "json_files",
        nargs="+",
        help="Путь(я) к JSON-файлам кейсов (glob поддерживается)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать результат без записи файлов",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Ничего не писать; сравнить существующий .md с тем, что дал бы конвертер. "
             "Код 1, если расходятся или .md отсутствует",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Не выводить результаты в stdout",
    )
    args = parser.parse_args()

    import glob

    all_files = []
    for pattern in args.json_files:
        expanded = glob.glob(pattern)
        if not expanded:
            print(f"⚠️  Нет файлов по шаблону: {pattern}", file=sys.stderr)
            continue
        all_files.extend(expanded)

    if not all_files:
        print("❌ Файлы не найдены", file=sys.stderr)
        sys.exit(1)

    ok_count = 0
    fail_count = 0

    for jf in sorted(all_files):
        try:
            data = json.load(open(jf, encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"❌ Ошибка чтения {jf}: {exc}", file=sys.stderr)
            fail_count += 1
            continue

        problems = validate(data, jf)
        if problems:
            print(f"⚠️  Проблемы в {jf}:", file=sys.stderr)
            for p in problems:
                print(p, file=sys.stderr)

        md_content = json_to_md(data)
        md_path = Path(jf).with_suffix(".md")

        if args.check:
            # Проверка «конвертер запускали?» обязана быть неразрушающей: запуск —
            # это и есть проверяемое действие, и запись стирает улику.
            if not md_path.is_file():
                print(f"❌ {md_path} отсутствует — конвертер не запускали", file=sys.stderr)
                fail_count += 1
                continue
            if md_path.read_text(encoding="utf-8") != md_content:
                print(f"❌ {md_path} расходится с {jf} — конвертер не запускали "
                      f"после правки JSON", file=sys.stderr)
                fail_count += 1
                continue
        elif args.dry_run:
            if not args.quiet:
                print(f"\n=== {jf} → {md_path} ===\n{md_content}")
        else:
            md_path.write_text(md_content, encoding="utf-8")

        ok_count += 1

    if not args.quiet:
        verb = "Сверено" if args.check else "Конвертировано"
        mark = "❌" if fail_count else "✅"
        print(f"{mark} {verb}: {ok_count}, Ошибок: {fail_count}")

    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())
