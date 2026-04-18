from __future__ import annotations

import shutil
import sys


def show_with_pager(text: str, prompt: str | None = None) -> None:
    if not sys.stdout.isatty() or not sys.stdin.isatty():
        print(text)
        return

    lines = text.splitlines()
    if not lines:
        return

    page_size = max(shutil.get_terminal_size((80, 24)).lines - 2, 1)
    prompt_text = prompt or "-- More -- (Enter: next, q: quit)"

    index = 0
    while index < len(lines):
        chunk = lines[index : index + page_size]
        print("\n".join(chunk))
        index += page_size
        if index >= len(lines):
            break

        answer = input(prompt_text).strip().lower()
        if answer == "q":
            break

