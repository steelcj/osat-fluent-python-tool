#!/usr/bin/env python3
# check-conformance.py
"""
check-conformance.py, report mechanically-detectable conformance issues.

Scans versioned markdown documents under en/docs and reports the findings
that a machine can detect without judgement, the class of issue collected
in ROADMAP.md: dotted filename version separators, missing required
frontmatter fields, a dc:identifier that does not match the filename
slug, em dashes in prose, asterisk bullets, and numbered headings.

This is a linter, not an autofixer. It changes nothing. It exits non-zero
if any issue is found, so it can gate a commit or run in CI.

Usage:
    check-conformance.py            check en/docs under this script's directory
    check-conformance.py PATH ...   check the given files or directories
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "en" / "docs"

REQUIRED_FIELDS = [
    "dc:title",
    "dcterms:version",
    "dc:creator",
    "dc:identifier",
    "dcterms:created",
    "dcterms:modified",
    "sat:uuid",
]

DOTTED_VERSION = re.compile(r"-v\d+\.\d+\.\d+")
HYPHEN_VERSION_SUFFIX = re.compile(r"-v\d+-\d+-\d+$")
NUMBERED_HEADING = re.compile(r"^#{1,6}\s+\d+([.)]|\s)")
ASTERISK_BULLET = re.compile(r"^\s*\*\s+\S")
IDENTIFIER_LINE = re.compile(r'^dc:identifier:\s*"?([^"\n]+)"?\s*$')


def split_frontmatter(text: str):
    """Return (frontmatter_lines, body_lines). Frontmatter is empty if absent."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], lines[i + 1:]
    return [], lines


def body_without_code(body_lines):
    """Yield (line_number, line) for body lines outside fenced code blocks."""
    in_fence = False
    for offset, line in enumerate(body_lines):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield offset, line


def slug_from_filename(name: str) -> str:
    stem = name[:-3] if name.endswith(".md") else name
    return re.sub(r"-v\d+[-.]\d+[-.]\d+$", "", stem)


def check_file(path: Path):
    issues = []
    name = path.name
    text = path.read_text(encoding="utf-8")
    fm_lines, body_lines = split_frontmatter(text)
    has_fm = bool(fm_lines)

    if DOTTED_VERSION.search(name):
        issues.append("filename uses dotted version separator; use hyphens (v0-1-0)")

    if has_fm:
        joined_fm = "\n".join(fm_lines)
        for field in REQUIRED_FIELDS:
            if not re.search(rf"^{re.escape(field)}:", joined_fm, re.MULTILINE):
                issues.append(f"missing required frontmatter field: {field}")

        identifier = None
        for line in fm_lines:
            m = IDENTIFIER_LINE.match(line)
            if m:
                identifier = m.group(1).strip()
                break
        if identifier is not None:
            expected = slug_from_filename(name)
            if identifier != expected:
                issues.append(
                    f"dc:identifier {identifier!r} does not match filename slug {expected!r}"
                )

    # Body checks, skipping fenced code blocks.
    for offset, line in body_without_code(body_lines):
        lineno = offset + len(fm_lines) + (2 if has_fm else 0) + 1
        if "—" in line:
            issues.append(f"line {lineno}: em dash in prose (use commas)")
        if ASTERISK_BULLET.match(line):
            issues.append(f"line {lineno}: asterisk bullet (use '-')")
        if NUMBERED_HEADING.match(line):
            issues.append(f"line {lineno}: numbered heading (see Markdown: No Heading Numbers)")

    return issues


def iter_markdown(targets):
    for target in targets:
        if target.is_dir():
            yield from sorted(target.rglob("*.md"))
        elif target.suffix == ".md":
            yield target


def main() -> int:
    args = sys.argv[1:]
    targets = [Path(a) for a in args] if args else [DOCS]
    files = list(iter_markdown(targets))
    if not files:
        print("[CONFORMANCE] no markdown files found", file=sys.stderr)
        return 1

    total = 0
    for path in files:
        issues = check_file(path)
        if issues:
            total += len(issues)
            resolved = path.resolve()
            rel = resolved.relative_to(ROOT) if ROOT in resolved.parents else path
            print(f"\n{rel}")
            for issue in issues:
                print(f"  - {issue}")

    print(f"\n[CONFORMANCE] {len(files)} files checked, {total} issue(s) found")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
