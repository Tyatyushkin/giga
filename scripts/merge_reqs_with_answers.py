#!/usr/bin/env python3
"""Помощник: объединяет REQ из основного файла и ответы в _answers.md в единый индекс."""

import argparse
import json
import re
import sys
from pathlib import Path

REQ_ID = re.compile(r"\*\*([A-Z]{2,4}-\d{1,3})\.?\*\*")
LIST_ITEM = re.compile(r"^\s*[-*]\s+\*\*([A-Z]{2,4}-\d{1,3})\.?\*\*\s*(.*)$")
ANSWER_RE = re.compile(
    r"(Q-?\d+)[:\-]?\s*[:\-]?\s*(.+?)\s*\*\*Ответ\*\*:\s*(.+)", re.DOTALL
)
SHORT_QUESTION = re.compile(
    r"^.*?\*\*Q-\d+[^*]*\*\*\s*:\s*([^?]+)\?", re.DOTALL
)


def clean(text: str) -> str:
    text = text.replace("<br>", " ").replace("<br/>", " ")
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .;")


def parse_answers(path: Path) -> list[dict]:
    records: list[dict] = []
    section = "Ответы на уточняющие вопросы"
    text = path.read_text(encoding="utf-8")
    blocks = text.split("## ")
    for block in blocks:
        if not block.strip():
            continue
        lines = block.strip().splitlines()
        question_line = lines[0].strip() if lines else ""
        answer_text = "\n".join(lines[1:]).strip()

        # Extract Q-id
        q_match = SHORT_QUESTION.search(question_line)
        if not q_match:
            continue
        q_id = q_match.group(1).strip()
        q_title = q_match.group(2).strip()

        # Extract answer
        a_match = ANSWER_RE.search(block)
        answer = a_match.group(3).strip() if a_match else answer_text

        # Build combined text
        combined = f"{q_title}? {answer}"

        # Assign free number
        existing_ids = set()
        reqindex_path = Path("output/suites/_reqindex.json")
        if reqindex_path.exists():
            data = json.loads(reqindex_path.read_text())
            existing_ids = {r["id"] for r in data.get("reqIndex", [])}
        free = 100
        while f"REQ-{free:02d}" in existing_ids:
            free += 1
        req_id = f"REQ-{free:02d}"

        records.append({
            "id": req_id,
            "text": combined,
            "source": f"_answers.md § {section}",
            "_answer": answer,
            "_q_id": q_id,
            "_q_title": q_title,
        })
    return records


def main():
    sources = ["input/requirements/knox-demo.md", "input/requirements/_answers.md"]
    files = [Path(s) for s in sources]

    # 1) Parse main requirements
    records = []
    section = ""
    for raw in files[0].read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", raw)
        if heading:
            section = heading.group(2).strip()
            continue
        item = LIST_ITEM.match(raw)
        if item:
            records.append({
                "id": item.group(1),
                "text": clean(item.group(2)),
                "source": f"{files[0].name} § {section}",
            })

    # 2) Parse answers
    answers = parse_answers(files[1])

    # 3) Merge
    for a in answers:
        records.append({
            "id": a["id"],
            "text": a["text"],
            "source": a["source"],
        })

    out = Path("output/suites/_reqindex_merged.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "requirementsSource": [str(f) for f in files],
                "reqIndex": [
                    {"id": r["id"], "text": r["text"], "source": r["source"]}
                    for r in records
                ],
                "answerMap": [
                    {"req_id": a["id"], "q_id": a["_q_id"], "q_title": a["_q_title"], "answer": a["_answer"]}
                    for a in answers
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Мердж: {len(records)} записей, {len(answers)} ответов → {out}")


if __name__ == "__main__":
    main()
