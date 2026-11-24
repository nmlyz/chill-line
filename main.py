#!/usr/bin/env python3
"""One Line, One Chill -- submission generator.

Builds the entry for the "One Line, One Chill" bounty: a single
sentence of horror, at most 200 characters long, written to
``entry.txt`` inside the output directory (``/output`` by default,
``OUTPUT_DIR`` overrides it).

The generator is deliberately boring on purpose. It assembles the
line, checks it against every rule of the brief, renders it to
bytes, writes it atomically, and then reads the file back to prove
the bytes on disk are exactly the bytes it intended to write.
Running the script twice produces byte-identical output.
"""

import argparse
import os
import tempfile
from pathlib import Path

ENTRY_TEXT = (
    "My fitness tracker logged 4,000 steps at 3 a.m. while I was "
    "in bed, and the route ended at my bedroom door."
)

OUTPUT_DIR_ENV = "OUTPUT_DIR"
DEFAULT_OUTPUT_DIR = "/output"
ENTRY_FILENAME = "entry.txt"
MAX_LINE_LENGTH = 200


def compose_line() -> str:
    """Return the submission line, exactly as it must appear."""
    return ENTRY_TEXT


def check_no_newlines(line: str) -> None:
    """The entry must be one line, so no line breaks are allowed."""
    if "\n" in line or "\r" in line:
        raise ValueError("line must not contain a newline")


def check_length(line: str) -> None:
    """The brief caps the line at 200 characters."""
    if not 1 <= len(line) <= MAX_LINE_LENGTH:
        raise ValueError("line must be 1-200 characters")


def check_shape(line: str) -> None:
    """No leading/trailing space, and one sentence ending in a period."""
    if line.strip() != line or not line.strip():
        raise ValueError("line must not be blank or padded with whitespace")
    if not line.endswith("."):
        raise ValueError("line must be a single sentence ending with a period")


def validate_line(line: str) -> None:
    """Run every brief rule against the line before anything is written."""
    check_no_newlines(line)
    check_length(line)
    check_shape(line)


def render_payload(line: str) -> bytes:
    """Encode the line as UTF-8 bytes with exactly one trailing newline."""
    return (line + "\n").encode("utf-8")


def parse_args(argv=None) -> argparse.Namespace:
    """Parse command-line options.

    ``--output-dir`` overrides the output directory for this run only;
    without it the ``OUTPUT_DIR`` environment variable (or ``/output``)
    decides where the entry is written.
    """
    parser = argparse.ArgumentParser(
        description="Write the One Line, One Chill entry to entry.txt."
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="directory to write entry.txt into (default: $OUTPUT_DIR or /output)",
    )
    return parser.parse_args(argv)


def resolve_output_dir(cli_dir=None) -> Path:
    """Resolve the output directory, creating it if needed."""
    chosen = cli_dir or os.environ.get(OUTPUT_DIR_ENV, DEFAULT_OUTPUT_DIR)
    output_dir = Path(chosen)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_entry(payload: bytes, output_dir: Path) -> Path:
    """Write the payload atomically: temp file in the same directory,
    then rename over the entry, so a half-written file never appears."""
    entry_path = output_dir / ENTRY_FILENAME
    fd, temp_name = tempfile.mkstemp(
        dir=output_dir, prefix=ENTRY_FILENAME + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        os.chmod(temp_name, 0o644)
        os.replace(temp_name, entry_path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
    return entry_path


def verify_written(entry_path: Path, payload: bytes) -> None:
    """Read the file back and confirm the bytes match the payload."""
    actual = entry_path.read_bytes()
    if actual != payload:
        raise ValueError(
            f"{entry_path} does not match the intended payload "
            f"({len(actual)} bytes on disk, {len(payload)} expected)"
        )


def main(argv=None) -> None:
    args = parse_args(argv)
    line = compose_line()
    validate_line(line)
    payload = render_payload(line)
    output_dir = resolve_output_dir(args.output_dir)
    entry_path = write_entry(payload, output_dir)
    verify_written(entry_path, payload)


if __name__ == "__main__":
    main()
