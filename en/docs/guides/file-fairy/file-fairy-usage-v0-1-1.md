---
dc:title: "file-fairy Usage"
dcterms:version: "0.1.1"
dc:creator: "Christopher Steel"
dc:contributor: "Claude Fable 5 (Anthropic) — drafting assistance"
dc:description: "Operator guide for file-fairy: the manifest concepts, the plan, status, and apply verbs, the sync modes, retraction, managed blocks, conflict resolution, and the receive-then-commit pattern that precedes a release. Canonical here in sat-doc-automa and distributed to file-fairy by the fairy itself."
dcterms:created: "2026-08-03"
dcterms:modified: "2026-08-03"
dc:format: "text/markdown"
dc:language: "en"
sat:language_bcp47: "en"
dc:relation: "commit-and-versioning-workflow, decision--file-fairy-manifest-declared-sync-policy, decision--manifest-organization-one-key-per-axis"
dc:identifier: "file-fairy-usage"
dcterms:rightsHolder: "Christopher Steel"
dc:rights: >
  Copyright 2026 Christopher Steel.
  SPDX-License-Identifier: AGPL-3.0-or-later
sat:uuid: ""
sat:repository: "sat-doc-automa"
sat:path: "en/docs/guides/devops/"
sat:version_at_creation: "0.1.4"
sat:migration_status: pre-sat
sat:changelog:
  - version: "0.1.1"
    date: "2026-08-03"
    author: "Christopher Steel"
    notes: "Manifest filenames updated to the ff-manifest-<target>.yaml convention in every example."
  - version: "0.1.0"
    date: "2026-08-03"
    author: "Christopher Steel"
    notes: "Initial guide, written against file-fairy 0.3.0 plus managed blocks. Covers concepts, verbs, sync modes, retraction, blocks, conflicts, and the receive-then-commit pattern observed at the fairy's own 0.2.0 release. Resolves the fairy roadmap's usage-guide item."
---

# file-fairy Usage

Version: 0.1.1
Status: Draft
Style Guide: style-guide--technical-documentation-for-technologists

## Abstract

file-fairy (`ff`) distributes shared conventions from a canonical source repository, this one, to the repositories that adopt them, driven by a per-target YAML manifest, with a plan you read before anything is written and a state file that tells upstream changes apart from local edits. This guide covers operating it: the concepts, the verbs, the sync modes, retraction, managed blocks, conflicts, and where a fairy run fits in the release workflow. The fairy's own design law lives in its repository under `en/docs/decisions/sync/`; this guide is about using it.

## Install and run

The fairy is a single Python script depending only on PyYAML. Today it runs most easily from the file-fairy checkout's own venv, and invocation from a target repository is a known friction, tracked on the fairy's ROADMAP with a per-machine install (`pipx`) as the first candidate. Until that lands:

```bash
cd ~/2-areas/development/file-fairy
VERSION=$(cat VERSION)
/usr/bin/env python3 -m venv --prompt "file-fairy-${VERSION}" ".venv-file-fairy-${VERSION}"
source ".venv-file-fairy-${VERSION}/bin/activate"
pip install .
```

The manifests live in sat-doc-automa's root, one per target repository, so the working directory for a run is the sat-doc-automa checkout:

```bash
cd ~/2-areas/development/sat-doc-automa
ff ff-manifest-file-fairy.yaml          # bare manifest means apply
ff plan ff-manifest-sat.yaml            # read-only, always safe
```

## Concepts

A **manifest** declares what belongs in one target repository: named **groups** of items, each item a source path in this repository and a dest path in the target, at `source == dest` per the standard layout, so drift is detectable by comparing the same path in both places. The manifest is governance documentation as much as configuration; groups carry descriptions and notes explaining why each file travels.

The **state file**, `.file-fairy-state.yaml` in the target's root, records per item the source and dest checksums as of the last successful apply. It is what lets the fairy tell "source changed upstream" apart from "target changed locally", and it is the target's file; do not edit it, and do commit it.

An item's full story is told by its keys, one per question: `state` for what the path should be (`file`, or `absent` for retraction), `source` for where its bytes come from, `sync_mode` for who wins when desired and actual disagree, and `block` items for regions inside files the target owns.

## The verbs

`plan` (alias `status`) computes and prints what would change, writes nothing, and is always safe to run. `apply` shows the plan, asks for confirmation (`--yes` skips it), copies, and updates the state file. Read a plan top down; the sections are ordered by how much attention they deserve:

```text
RETRACT   declared absent; will be deleted
CONFLICT  target changed locally since last sync
MISSING SOURCE  file does not exist upstream
NEW       not yet synced
UPDATE    source changed since last sync
present   seed_if_missing; the target owns it
retired   declared absent; already gone
unchanged
```

Uppercase sections want your eyes; lowercase sections are the fairy telling you it is leaving things alone on purpose.

## Sync modes

Declared in the manifest at group level, inherited by the group's items, or per item, overriding the group. Absent means `mirror`. Per the sync-policy decision, intent lives in the manifest, at the granularity of the file, never in a CLI flag.

| `sync_mode` | Dest missing | Source changed | Locally edited |
| --- | --- | --- | --- |
| `mirror` (default) | create | overwrite | protect: conflict, skipped |
| `seed_if_missing` | create | do nothing | do nothing |
| `overwrite` | create | overwrite | overwrite |
| `reference_only` | never touch | never touch | never touch |

Choosing: `mirror` for shared documents and scripts the target should hold current but might legitimately need to fork for a moment, the conflict tells you it happened. `seed_if_missing` for files each target owns after birth, `VERSION`, a starting `CHANGELOG.md`. `overwrite` for files the target never gets a vote on. `reference_only` for declaring something belongs in the picture without ever copying it, style guides are cited, not copied.

## Retraction

`state: absent` declares a path the target must not hold; if present it is deleted at apply, shown first in the plan. Retraction is manifest-declared, never a flag, and applies whether or not the fairy ever synced the path. When a shared document is renamed in this repository, the retraction of the old path rides the same manifest change as the new row, which is the discipline that keeps orphans extinct.

```yaml
  retired:
    items:
      - state: absent
        dest: en/docs/guides/devops/superseded-doc-v0-1-0.md
```

## Managed blocks

A block item makes the fairy own one marker-delimited region inside a file the target otherwise owns. The markers are HTML comments, invisible wherever the markdown renders:

```yaml
  claude-md:
    items:
      - block: claude-md-signpost
        source: en/docs/automa/claude-md/claude-md-signpost-block.md
        dest: CLAUDE.md
        anchor: BOF
```

Inside the markers, the region follows the item's `sync_mode` with the region as the unit: a hand-edit inside the markers is a `mirror` conflict, and the fairy meeting an existing, differing region for the first time is also a conflict, never a silent clobber. Outside the markers the file belongs entirely to the target, add anything, the fairy will never touch it. Absent markers insert the block at `anchor` (`EOF` default, `BOF` for top of file); an absent dest file is created holding only the block.

## Conflicts

A conflict means the target changed something the manifest says this repository owns. Three resolutions, in order of preference: fold the target's improvement upstream into this repository and re-apply, the whole fleet gets it; discard the local edit deliberately with `ff apply MANIFEST --force`, a one-off that overwrites conflicts this run only; or decide the target should never keep local edits for that item and declare `sync_mode: overwrite` in the manifest, the standing form of force. What a conflict never means is editing the state file to make the message go away.

## Where a run fits: receive, then commit, then release

A fairy run in a target repository is its own commit, before any release work, so the arrivals are separable from the target's own changes in history. The pattern, as run at file-fairy's own 0.2.0 release:

```bash
ff ff-manifest-file-fairy.yaml          # from the sat-doc-automa checkout
cd ~/2-areas/development/file-fairy
git add -A && git commit -m "Receive the release ceremony from sat-doc-automa"
python3 cut-release.py minor
```

Everything after that commit is the commit-and-versioning workflow's four steps: write the changelog entries, cut, push, publish.

## Troubleshooting

If apply refuses with conflicts, that is the tool working; see Conflicts above. If plan shows `MISSING SOURCE`, the manifest names a source path this repository no longer has, usually a rename that has not reached the manifest yet; fix the manifest row, and add a retraction for the old dest. If a block item fails with "malformed fairy block markers", the dest has a begin without an end or a duplicate pair; repair the markers by hand, the fairy refuses to guess. If a manifest key fails as "scheduled but not yet implemented", the schema knows the feature and the fairy does not yet; see the manifest-organization decision's implementation order.

## License

This document, *file-fairy Usage*, by **Christopher Steel**, with AI assistance from **Claude Fable 5 (Anthropic)**, is licensed under the [GNU Affero General Public License v3.0 or later](https://www.gnu.org/licenses/agpl-3.0.html).

## Changelog

| Version | Status | Notes |
|---------|--------|-------|
| 0.1.1 | Draft | Manifest filenames updated to the ff-manifest-<target>.yaml convention in every example. |
| 0.1.0 | Draft | Initial guide against file-fairy 0.3.0 plus managed blocks: concepts, verbs, sync modes, retraction, blocks, conflicts, receive-then-commit, troubleshooting. |
