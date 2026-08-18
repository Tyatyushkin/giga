#!/usr/bin/env python3
"""Keep pytest.ini's marker registry in step with the journeys that exist.

`pytest.ini` runs with `--strict-markers`, and the writers are told to stamp every test
with `@pytest.mark.J<NN>` for its journey. The registry is a single repo-level file the
sub-agents may not touch, which is right — but nothing was adding the marker either, so
a run that produced J03 collected zero tests and failed with

    'J03' not found in `markers` configuration option

Every journey directory was green on its own; the failure only appeared when all of them
were collected together, which is the same shape as the module-name collision the naming
scheme fixes. This closes it deterministically instead of asking the orchestrator to
remember.

Usage:
    python3 scripts/sync_markers.py            # add whatever is missing
    python3 scripts/sync_markers.py --check    # report only, exit 1 if out of step

Exit codes: 0 = registry covers every journey, 1 = markers missing (--check),
            2 = no journey index to read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

JOURNEY_MARKER = re.compile(r"^J\d{2}$")
MARKER_LINE = re.compile(r"^\s{4}(?P<name>[A-Za-z_][A-Za-z0-9_]*):")


def journeys_from_index(index: Path) -> list[tuple[str, str]]:
    """(marker, description) for every journey the analyst produced."""
    data = json.loads(index.read_text(encoding="utf-8"))
    out = []
    for j in data.get("journeys", []):
        jid = str(j.get("id") or "")
        m = re.match(r"^(J\d{2})", jid)
        if not m:
            continue
        title = str(j.get("title") or "").strip()
        # One line in an ini file: no newlines, and short enough to stay readable.
        title = " ".join(title.split())
        if len(title) > 70:
            title = title[:70].rsplit(" ", 1)[0].rstrip(" ,:;—-") + "…"
        out.append((m.group(1), f"Journey {m.group(1)} — {title}" if title else f"Journey {m.group(1)}"))
    return out


def registered(ini_lines: list[str]) -> tuple[dict[str, int], int]:
    """Registered marker name -> its line index, and the index just past the block."""
    names: dict[str, int] = {}
    start = None
    end = None
    for i, line in enumerate(ini_lines):
        if re.match(r"^markers\s*=", line):
            start = i
            continue
        if start is not None:
            if (m := MARKER_LINE.match(line)):
                names[m.group("name")] = i
                end = i
            elif line.strip() == "":
                continue
            else:
                break
    if start is None:
        raise SystemExit("sync_markers: в pytest.ini нет блока `markers =`")
    return names, (end if end is not None else start) + 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Синхронизировать маркеры journey с pytest.ini")
    ap.add_argument("--index", default="output/suites/_index.json")
    ap.add_argument("--ini", default="pytest.ini")
    ap.add_argument("--check", action="store_true", help="только проверить, ничего не писать")
    args = ap.parse_args()

    index, ini = Path(args.index), Path(args.ini)
    if not index.is_file():
        sys.stderr.write(f"sync_markers: нет индекса journey: {index}\n")
        return 2
    if not ini.is_file():
        sys.stderr.write(f"sync_markers: нет {ini}\n")
        return 2

    wanted = journeys_from_index(index)
    if not wanted:
        sys.stderr.write(f"sync_markers: в {index} нет journey с id вида J<NN>\n")
        return 2

    lines = ini.read_text(encoding="utf-8").split("\n")
    have, insert_at = registered(lines)

    # This script owns the J<NN> lines outright — add them and keep their text true to
    # the index. Descriptions drift otherwise: J02 described a journey from an older
    # corpus long after the analyst had regrouped. Markers that are not J<NN>
    # (stub, browser, blocker) belong to the human and are never touched.
    missing = [(n, d) for n, d in wanted if n not in have]
    outdated = [(n, d) for n, d in wanted
                if n in have and lines[have[n]] != f"    {n}: {d}"]
    orphan = sorted(n for n in have if JOURNEY_MARKER.match(n)
                    and n not in {n for n, _ in wanted})

    for name, _ in wanted:
        mark = "НЕТ    " if name in {n for n, _ in missing} else (
            "устарел" if name in {n for n, _ in outdated} else "есть   ")
        print(f"[markers] {mark} {name}")
    if orphan:
        print(f"[markers] маркеры без journey: {', '.join(orphan)} — не удаляю, "
              f"прогон их не использует")

    if not missing and not outdated:
        print("[markers] реестр совпадает с индексом journey")
        return 0

    if args.check:
        if missing:
            print(f"[markers] не хватает: {', '.join(n for n, _ in missing)}")
            print("[markers] прогон pytest упадёт на сборке — --strict-markers включён")
        if outdated:
            print(f"[markers] описание разошлось с индексом: "
                  f"{', '.join(n for n, _ in outdated)}")
        return 1

    for name, desc in outdated:
        lines[have[name]] = f"    {name}: {desc}"
    for name, desc in missing:
        lines.insert(insert_at, f"    {name}: {desc}")
        insert_at += 1
    ini.write_text("\n".join(lines), encoding="utf-8")
    if missing:
        print(f"[markers] добавлено: {', '.join(n for n, _ in missing)}")
    if outdated:
        print(f"[markers] описание обновлено: {', '.join(n for n, _ in outdated)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
