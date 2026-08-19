#!/usr/bin/env python3
"""Convert Markdown e2e test cases to JSON siblings.

Companion of W2: qa-designer writes only Markdown; the orchestrator invokes this
script to (re)generate the matching `*.json` files. Designed to mirror the schema
in `docs/format.md` and stay byte-stable for `validate_cases.py`'s parity check.

Usage:
    python3 scripts/md_to_case_json.py output/cases/<JOURNEY_DIR>
    python3 scripts/md_to_case_json.py output/cases

Exit codes:
    0  all .md files have matching .json
    1  conversion errors (file logged)
    2  nothing to do
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


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


def parse_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"^\s*[-*]\s*\*\*(.+?):\*\*\s*(.*)$", line)
        if m:
            fields[m.group(1).strip()] = m.group(2).strip()
    return fields


def parse_table(block: str) -> list[list[str]]:
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


def parse_bullets(block: str) -> list[str]:
    items: list[str] = []
    for line in block.splitlines():
        m = re.match(r"^\s*[-*]\s+(.+)$", line)
        if m:
            items.append(m.group(1).strip())
    return items


def parse_numbered(block: str) -> list[str]:
    items: list[str] = []
    for line in block.splitlines():
        m = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if m:
            items.append(m.group(1).strip())
    return items


def split_requirements(value: str) -> list[str]:
    return [v.strip() for v in re.split(r"[,;]\s*", value) if v.strip()]


def convert(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    sections = split_sections(text)
    info = parse_fields(sections.get("Общая информация", ""))

    case_id = info.get("ID", "")
    variant_of = info.get("Вариант от", "—").strip()
    if variant_of in ("—", "-", "", "None", "null"):
        variant_of = None

    data_rows = parse_table(sections.get("Тестовые данные", ""))
    test_data = [
        {"name": r[0], "value": r[1] if len(r) > 1 else "", "comment": r[2] if len(r) > 2 else ""}
        for r in data_rows
        if len(r) >= 2 and r[0] and r[1]
    ]

    step_rows = parse_table(sections.get("Шаги", ""))
    steps = []
    for row in step_rows:
        if len(row) != 4:
            continue
        num, action, data, expected = row
        steps.append({
            "number": int(num.strip().rstrip(".") or 0),
            "action": action,
            "testData": data,
            "expectedResult": expected,
            "requirements": [],
        })

    return {
        "id": case_id,
        "title": info.get("Название", ""),
        "goal": info.get("Цель", ""),
        "priority": info.get("Приоритет", "").lower().rstrip("."),
        "journeyId": info.get("Journey", ""),
        "variantOf": variant_of,
        "requirements": split_requirements(info.get("Покрываемые требования", "")),
        "preconditions": parse_bullets(sections.get("Предусловия", "")),
        "testData": test_data,
        "steps": steps,
        "postconditions": parse_bullets(sections.get("Постусловия", "")),
        "gaps": parse_bullets(sections.get("Выявленные пробелы", "")),
        "clarifyingQuestions": parse_numbered(sections.get("Уточняющие вопросы", "")),
    }


def collect(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if target.suffix == ".md" else []
    return sorted(
        p for p in target.rglob("*.md")
        if not p.name.startswith("_") and "review" not in p.name.lower()
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="MD → JSON conversion for e2e cases")
    ap.add_argument("target", help="file or directory containing .md cases")
    args = ap.parse_args()

    target = Path(args.target)
    if not target.exists():
        sys.stderr.write(f"md_to_case_json: путь не найден: {target}\n")
        return 2

    files = collect(target)
    if not files:
        print(f"md_to_case_json: нет .md кейсов в {target}", file=sys.stderr)
        return 2

    errors = 0
    for md in files:
        json_path = md.with_suffix(".json")
        try:
            payload = convert(md)
            json_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"{md.name} → {json_path.name} ({len(payload['steps'])} шагов)")
        except Exception as exc:
            errors += 1
            sys.stderr.write(f"[error] {md}: {exc}\n")

    if errors:
        return 1
    print(f"ok: {len(files)} файл(ов), {errors} ошибок")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
