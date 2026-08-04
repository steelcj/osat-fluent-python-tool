#!/usr/bin/env python3
#
# source
#   project: sat-doc-automa
#   path: normalize-metadata.py
#
"""
normalize-metadata.py, convert frontmatter keys from the dcterms:
dialect to the dc: family, per ADR-028 and the SAT Metadata Key
Specification, as the first authoring-dialect normalization of the
metadata ingress and egress pipelines.

Only the frontmatter block is touched, the region between the opening
'---' and its closing '---'; body prose and code examples are never
modified, so documents ABOUT namespaces keep their examples intact.
Only keys at the start of a line are renamed.

Converted (Dublin Core Elements 1.1 equivalents exist):
    dcterms:title -> dc:title, and likewise creator, contributor,
    subject, description, publisher, type, format, language,
    identifier, source, relation, rights, coverage, date.

Left unchanged, deliberately:
    dcterms:created, dcterms:modified, dcterms:rightsHolder, the
    ADR-028 exceptions with no dc: equivalent;
    dcterms:version, the flagged local extension, pending its own
    key decision (sat:version is the standing candidate);
    every sat: key.

Provenance for this in-repo normalization is git itself: run, review
the diff, commit surgically. The parent commit holds every original
byte; the commit message records tool, date, and rule.

Usage:
    normalize-metadata.py            dry run: report what would change
    normalize-metadata.py --apply    rewrite the files
    normalize-metadata.py PATH ...   limit to the given files or dirs
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

MAPPABLE = (
    "title", "creator", "contributor", "subject", "description",
    "publisher", "type", "format", "language", "identifier",
    "source", "relation", "rights", "coverage", "date",
)


def split_frontmatter(text: str):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[:i + 1], lines[i + 1:]
    return None


def normalize(text: str):
    parts = split_frontmatter(text)
    if parts is None:
        return text, 0
    fm, body = parts
    count = 0
    out = []
    for line in fm:
        new = line
        for name in MAPPABLE:
            prefix = f"dcterms:{name}:"
            if line.startswith(prefix):
                new = "dc:" + line[len("dcterms:"):]
                count += 1
                break
        out.append(new)
    return "".join(out) + "".join(body), count


def targets(args):
    paths = [Path(a) for a in args] if args else [ROOT]
    for p in paths:
        if p.is_file():
            yield p
        else:
            yield from sorted(p.rglob("*.md"))


def main() -> int:
    argv = sys.argv[1:]
    apply = "--apply" in argv
    argv = [a for a in argv if a != "--apply"]

    changed_files = 0
    changed_keys = 0
    for path in targets(argv):
        text = path.read_text(encoding="utf-8")
        new, count = normalize(text)
        if count:
            changed_files += 1
            changed_keys += count
            rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
            print(f"  {rel}: {count} key(s)")
            if apply:
                path.write_text(new, encoding="utf-8")

    verb = "converted" if apply else "would convert"
    print(f"[normalize-metadata] {verb} {changed_keys} key(s) "
          f"in {changed_files} file(s)")
    if not apply and changed_files:
        print("[normalize-metadata] dry run; re-run with --apply, "
              "review the diff, commit surgically")
    return 0


if __name__ == "__main__":
    sys.exit(main())
