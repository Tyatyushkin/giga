#!/usr/bin/env python3
"""Inline a shared skill into a command prompt at the right heading depth.

Commands include skills with `!{python3 scripts/include_skill.py <name> --level N}`.
A plain `cat` would work, except for one thing that matters: the skill's own `#` title
outranks the `### Фаза N` heading it is nested under, so the phase looks like it ended
and the gate looks like a new top-level document. That is exactly the wrong impression
to give about a step that must not be skipped.

This script strips the YAML frontmatter and shifts every heading so the skill's top
heading lands at `--level`, leaving the command's own outline intact.

Exit codes: 0 = written to stdout, 2 = no such skill (loud, never a silent empty include).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

SKILL_DIR = Path(__file__).resolve().parent.parent / ".gigacode" / "skills"
HEADING = re.compile(r"^(#{1,6})\s")
FENCE = re.compile(r"^\s*(```|~~~)")


def strip_frontmatter(lines: list[str]) -> list[str]:
    if not lines or lines[0].strip() != "---":
        return lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[i + 1:]
    return lines  # unterminated frontmatter: leave the file alone rather than eat it


def main() -> int:
    ap = argparse.ArgumentParser(description="Подставить скилл в команду на нужной глубине")
    ap.add_argument("name", help="имя скилла без .md, например human-gate")
    ap.add_argument("--level", type=int, default=2,
                    help="уровень, на который встаёт верхний заголовок скилла (по умолчанию 2)")
    args = ap.parse_args()

    path = SKILL_DIR / f"{args.name}.md"
    if not path.is_file():
        sys.stderr.write(f"include_skill: нет скилла {path}\n")
        print(f"> **ОШИБКА ВКЛЮЧЕНИЯ:** скилл `{args.name}` не найден в `{SKILL_DIR}`. "
              f"Не выполняйте эту фазу — процедура не загружена.")
        return 2

    lines = strip_frontmatter(path.read_text(encoding="utf-8").split("\n"))

    in_fence = False
    tops = []
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence and (m := HEADING.match(line)):
            tops.append(len(m.group(1)))
    shift = args.level - min(tops) if tops else 0

    in_fence = False
    out = []
    for line in lines:
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence and (m := HEADING.match(line)):
            depth = min(6, max(1, len(m.group(1)) + shift))
            line = "#" * depth + line[len(m.group(1)):]
        out.append(line)

    print("\n".join(out).strip("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
