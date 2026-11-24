#!/usr/bin/env python3
"""One Line, One Chill -- submission generator.

Writes one line of horror to ``entry.txt`` inside OUTPUT_DIR
(default ``/output``). The output is deterministic: running the
script twice produces byte-identical files.
"""

import os
from pathlib import Path

LINE = "My fitness tracker logged 4,000 steps at 3 a.m. while I was in bed, and the route ended at my bedroom door."

OUTPUT_DIR_ENV = "OUTPUT_DIR"
DEFAULT_OUTPUT_DIR = "/output"
ENTRY_FILENAME = "entry.txt"
MAX_LINE_LENGTH = 200


def validate_line(line: str) -> None:
    """Check the line meets the submission rules before writing it."""
    if "\n" in line or "\r" in line:
        raise ValueError("line must not contain a newline")
    if not 1 <= len(line) <= MAX_LINE_LENGTH:
        raise ValueError("line must be 1-200 characters")
    if line.strip() != line or not line.strip():
        raise ValueError("line must not be only whitespace")
    if not line.endswith("."):
        raise ValueError("line must be a single sentence ending with a period")


def main() -> None:
    output_dir = Path(os.environ.get(OUTPUT_DIR_ENV, DEFAULT_OUTPUT_DIR))
    output_dir.mkdir(parents=True, exist_ok=True)

    validate_line(LINE)

    entry_path = output_dir / ENTRY_FILENAME
    entry_path.write_text(LINE + "\n", encoding="utf-8")
    os.chmod(entry_path, 0o644)


if __name__ == "__main__":
    main()
