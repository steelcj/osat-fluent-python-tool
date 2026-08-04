---
dc:title: "Commit and Versioning Workflow"
dcterms:version: "0.3.0"
dc:creator: "Christopher Steel"
dc:description: "Practical workflow for commits and version bumps: initial commit, and every subsequent release after that."
dcterms:created: "2026-07-24"
dcterms:modified: "2026-08-02"
dc:format: "text/markdown"
dc:language: "en"
sat:language_bcp47: "en"
dc:identifier: "commit-and-versioning-workflow"
dcterms:rightsHolder: "Christopher Steel"
dc:rights: >
  Copyright 2026 Christopher Steel.
  SPDX-License-Identifier: AGPL-3.0-or-later
sat:uuid: ""
sat:repository: "sat-doc-automa"
sat:path: "en/docs/guides/devops/"
sat:version_at_creation: "0.4.0"
sat:migration_status: pre-sat
sat:changelog:
  - version: "0.3.0"
    date: "2026-08-02"
    author: "Christopher Steel"
    notes: >
      Added the fourth ceremony step, "Publish the release," now that
      publish-release.py exists and is validated: deterministic tarball
      (built twice, refused on any byte difference), SHA256SUMS,
      optional GPG signature that never blocks when absent, published
      through a provider backend detected from the remote (gh for
      GitHub; a plain directory as the narrowest backend). Stated the
      maintainer-side requirements and their guarantors. Added
      publish-release.py to the initial-commit file listing, extended
      Troubleshooting with the publish refusals, and corrected the
      "It your push refuses" typo. Added sat:repository and sat:path
      to the frontmatter per the session's metadata convention. This
      version drafted with Claude Fable 5 (Anthropic); the License
      continues to name the models that produced the majority of the
      current text, per the mixed-model attribution decision.
  - version: "0.2.0"
    date: "2026-07-28"
    author: "Christopher Steel"
    notes: >
      Replaced the manual "Version bump workflow" (bump, stage, review,
      write the commit by hand, tag, push, as five separate steps) with
      cut-release.py, now that it exists and has been validated: write
      CHANGELOG.md's Unreleased entries by hand as work happens, then run
      one command that bumps VERSION via bump-version.py, rolls
      Unreleased into a dated version heading, commits surgically,
      guards, and tags. Added cut-release.py to the initial-commit file
      listing. Renamed the section from "Version bump workflow" to
      "Release workflow" to match what it now does.
  - version: "0.1.3"
    date: "2026-07-XX"
    author: "Christopher Steel"
    notes: "Reorganized and restored en/docs. (Placeholder date — not confirmed against the actual commit history.)"
  - version: "0.1.2"
    date: "2026-07-XX"
    author: "Christopher Steel"
    notes: "Minor edits. (Placeholder date — not confirmed against the actual commit history.)"
  - version: "0.1.1"
    date: "2026-07-25"
    author: "Christopher Steel"
    notes: "Compliance pass per ROADMAP.md Milestone 0.3.0. Replaced the em dash in the initial-commit example message with a comma, per Markdown: Use Commas, Not Em Dashes; a template the reader copies is not exempt from the rule."
  - version: "0.1.0"
    date: "2026-07-24"
    author: "Christopher Steel"
    notes: "Initial draft. Generalized from the osat-fluent-rclone-tool workflow into a project-neutral guide."
---

# Commit and Versioning Workflow

Version: 0.3.0
Status: Draft
Style Guide: style-guide--versioned-documents-in-unrendered-markdown

## Abstract

Two paths, one for the first commit and one for every release after it, because they do not follow the same steps or produce the same kind of commit message.

## Which workflow

```mermaid
flowchart TD
    A[Has this repository already had its first commit?]
    A -->|No| B[Initial commit workflow]
    A -->|Yes| C[Release workflow]
    click B "#initial-commit-workflow"
    click C "#release-workflow"
```

GitHub's mermaid renderer strips click links, so on github.com the chart is visual only; the section headings below are the actual navigation.

## Initial commit workflow

Use this once, the first time the repository is committed.

### Verify the branch

```bash
git status
```

If not on `main`:

```bash
git checkout -b main
```

### Stage and review

```bash
git add .
git status
```

The `git status` output after staging is used directly in the commit body. At initial commit this is the full file listing, every file is new. This full listing is expected only here; ordinary releases produce a much shorter list.

### Commit

Summary line, then the staged file list from `git status`:

```bash
git commit -m "Initial commit, v0.1.0

	new file:   VERSION
	new file:   README.md
	new file:   CHANGELOG.md
	new file:   bump-version.py
	new file:   cut-release.py
	new file:   publish-release.py
	new file:   en/docs/README.md
"
```

### Tag and push

Use `-u` on this first push only:

```bash
git tag v0.1.0
git push -u origin main
git push origin v0.1.0
```

Every future release goes through the release workflow below.

## Release workflow

Use this for every release after the initial commit.

### Write the changelog entries

As work happens, add entries to `CHANGELOG.md`'s `## [Unreleased]` section by hand, under `### Added`, `### Changed`, or `### Removed` as appropriate. This is a separate concern from cutting the release itself: `cut-release.py` reads what's already there, it never writes changelog prose.

### Ensure for and edit the CHANGELOG.md

```bash
typora CHANGELOG.md
```

Content example:

```markdown
# Changelog

All notable changes to the uc-radar repository are recorded here. This is the repository-level changelog: it records what each tagged release contained and why. Each document additionally carries its own changelog, in its frontmatter and in a Changelog table, for changes internal to that document.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions track the `VERSION` file and the git tags. Dates are ISO 8601.

## [Unreleased]

### Added

- Shared zone received from sat-doc-automa via file-fairy: the release-ceremony scripts, the devops guides, the markdown and AI-collaboration automa, the license blocks, and the CLAUDE.md signpost block. Synced inventory in .file-fairy-state.yaml.
```

### Cut the release

```bash
python3 cut-release.py patch
```

Or `minor`, `major`, `patch`or an explicit version. This calls `bump-version.py` to write `VERSION`, rolls `CHANGELOG.md`'s `Unreleased` section into a dated `## [X.Y.Z] - YYYY-MM-DD` heading, leaves a fresh empty `Unreleased` above it, commits `VERSION` and `CHANGELOG.md` surgically, never `git add .`, guards that `HEAD:VERSION` matches, tags, and guards the tag. It stops before push.

Output example:

```bash
VERSION: 0.1.3 -> 0.1.4
CHANGELOG.md: [Unreleased] -> ## [0.1.4] - 2026-07-28
[main b03266b] release 0.1.4
 2 files changed, 3 insertions(+), 1 deletion(-)

[RELEASE] 0.1.3 -> 0.1.4, tagged v0.1.4.
  Nothing pushed. Push when ready:
    git push && git push origin v0.1.4
```

### Push

Pushing stays a deliberate, separate act. cut-release.py never does it for you.

Run the push command

```bash
git push && git push origin v0.1.4
```

output example:

```bash
Enumerating objects: 19, done.
Counting objects: 100% (19/19), done.
Delta compression using up to 8 threads
Compressing objects: 100% (10/10), done.
Writing objects: 100% (12/12), 6.24 KiB | 6.24 MiB/s, done.
Total 12 (delta 3), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (3/3), completed with 2 local objects.
To github.com:steelcj/sat-doc-automa.git
   cb48d31..b03266b  main -> main
Enumerating objects: 1, done.
Counting objects: 100% (1/1), done.
Writing objects: 100% (1/1), 169 bytes | 169.00 KiB/s, done.
Total 1 (delta 0), reused 0 (delta 0), pack-reused 0
To github.com:steelcj/sat-doc-automa.git
 * [new tag]         v0.1.4 -> v0.1.4
```

### Publish the release

After the tag is pushed, publish the release artifacts. Dry-run first to see exactly what would be built and published, then run for real:

```bash
python3 publish-release.py --dry-run
git co
```

Output example (dry run):

```bash
[publish-release] backend: dir, tag v0.1.4 verified locally and on origin
[publish-release] built: sat-doc-automa-0.1.4.tar.gz (62171 bytes, sha256 3b774f4a04e4feac…, deterministic)
[publish-release] dry run; nothing published. Artifacts left in dist/:
  sat-doc-automa-0.1.4.tar.gz
  SHA256SUMS
```

This builds a byte-stable tarball from `git archive` for the tag, builds it a second time and refuses to publish if the bytes differ (the determinism gate, checked on every run, not assumed), writes `SHA256SUMS`, optionally GPG-signs the checksum file, and publishes the artifacts through a provider backend detected from the `origin` URL: `gh` for GitHub remotes, or a plain directory with `--backend dir --target DIR`. On GitHub, the release notes are the changelog section this release rolled, so the entries written by hand in the first step are used twice, once in `CHANGELOG.md` and once as release notes, and never composed twice. Before touching any provider, it confirms the tag is actually on the remote with `git ls-remote`, which works identically over SSH or HTTPS against any provider.

Signing never blocks: when `gpg` or a secret key is absent, the release publishes unsigned with a printed note. `--sign` makes a missing key an error; `--no-sign` skips signing entirely.

Requirements, maintainer-side only, end users of a published tool need none of this: Python 3.8 or newer (osat-fluent-python-tool installs one where the platform lacks it), `git`, and, for GitHub remotes, `gh` installed from its official packages and authenticated once with `gh auth login`. `gpg` is optional, only needed for signed checksums. The script never reads, stores, logs, or echoes a credential; authentication belongs to the backend's own tooling and to the human. Validated on Linux; the script is pure Python with official `git` and `gh` installers on all three platforms, but a Windows run of the test suite is still pending, so Windows support is inferred, not verified. The reasoning behind this design, the shared-script form, the provider backends, and the connectivity split, is recorded in `decision--publish-release-shared-script-with-provider-interface` and `decision--gh-cli-for-release-asset-publishing` under `en/docs/decisions/devops/`.

#### Troubleshooting

If your cut refuses, rather than proceeding: `VERSION` already has uncommitted changes (a previous release was left half-done), `Unreleased` is empty (nothing written to release), or the target tag already exists (tags are never reused; fix forward with the next version number).

If your publish refuses, rather than proceeding: the tag for `VERSION` does not exist (cut first), the tag is not on the remote (push first; the refusal prints the commands), a release for the tag already exists (releases are never reused; fix forward), the two archive builds produced different bytes (do not publish; investigate), or `--sign` was given with no usable key.

## License

This document, *Commit and Versioning Workflow*, by **Christopher Steel**, with AI assistance from **Claude Sonnet 4.6 (Anthropic)** and **Claude Sonnet 5 (Anthropic)**, is licensed under the [GNU Affero General Public License v3.0 or later](https://www.gnu.org/licenses/agpl-3.0.html).

## Changelog

| Version | Status | Notes |
|---------|--------|-------|
| 0.3.0 | Draft | Added the "Publish the release" ceremony step for publish-release.py: deterministic tarball, SHA256SUMS, optional never-blocking GPG signature, provider backends. Stated maintainer-side requirements and guarantors. Extended Troubleshooting with the publish refusals and corrected its opening typo. Added publish-release.py to the initial-commit listing and sat:repository/sat:path to the frontmatter. |
| 0.2.0 | Draft | Replaced the manual version-bump workflow with cut-release.py; renamed the section to "Release workflow"; added cut-release.py to the initial-commit file listing |
| 0.1.3 | Draft | Reorganized and restored en/docs |
| 0.1.2 | Draft | Minor edits |
| 0.1.1 | Draft | Compliance pass: replaced the em dash in the initial-commit example message with a comma |
| 0.1.0 | Draft | Initial draft, generalized from the osat-fluent-rclone-tool workflow into a project-neutral guide |
