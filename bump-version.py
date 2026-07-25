#!/usr/bin/env python3
# bump-version.py
"""
bump-version.py, bump this repository's version.

Updates the VERSION file in this script's own directory. Nothing else.
Document version lines and changelogs are a separate concern, updated by
hand as part of each document's own version bump, so that this script
stays a single-purpose tool that cannot half-update a repository.

Usage:
    bump-version.py patch          0.1.0 -> 0.1.1
    bump-version.py minor          0.1.1 -> 0.2.0
    bump-version.py major          0.2.0 -> 1.0.0
    bump-version.py 0.3.2          set an explicit version
"""
import re
import sys
from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parent / "VERSION"


def fail(msg: str) -> None:
    print(f"[BUMP ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def read_current() -> str:
    try:
        text = VERSION_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        fail(f"VERSION file not found at {VERSION_FILE}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", text):
        fail(f"VERSION file does not contain a semantic version: {text!r}")
    return text


def next_version(current: str, arg: str) -> str:
    if re.fullmatch(r"\d+\.\d+\.\d+", arg):
        return arg
    major, minor, patch = (int(p) for p in current.split("."))
    if arg == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if arg == "minor":
        return f"{major}.{minor + 1}.0"
    if arg == "major":
        return f"{major + 1}.0.0"
    fail(f"Expected patch, minor, major, or an explicit x.y.z, got {arg!r}")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    current = read_current()
    new = next_version(current, sys.argv[1])
    if new == current:
        fail(f"version is already {current}; nothing to bump")
    VERSION_FILE.write_text(new + "\n", encoding="utf-8")
    print(f"VERSION: {current} -> {new}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
