---
dc:title: "Markdown: License Statement Templates"
dcterms:version: "0.3.1"
dc:creator: "Christopher Steel"
dc:description: "Templates for the License section of documents and projects: general content, code, and code documentation, with and without AI assistance attribution."
dcterms:created: "2026-07-23"
dcterms:modified: "2026-07-24"
dc:format: "text/markdown"
dc:language: "en"
sat:language_bcp47: "en"
dc:identifier: "markdown--license-statement-templates"
dcterms:rightsHolder: "Christopher Steel"
dc:rights: >
  Copyright 2026 Christopher Steel.
  SPDX-License-Identifier: AGPL-3.0-or-later
sat:uuid: ""
sat:version_at_creation: "0.4.0"
sat:migration_status: pre-sat
sat:changelog:
  - version: "0.3.1"
    date: "2026-07-24"
    author: "Christopher Steel"
    notes: "Recreated in the sat-doc-automa repository; normalized the Style Guide reference to the versionless slug per the versioned-documents guide's own version block convention."
  - version: "0.3.0"
    date: "2026-07-24"
    author: "Christopher Steel"
    notes: "Dropped the 'Default:' title segment: default status is designated by the defaults/ directory, not repeated in the title. Identifier and filename updated to match. Rule content unchanged."
  - version: "0.2.0"
    date: "2026-07-24"
    author: "Christopher Steel"
    notes: "Retitled with the 'Markdown: Default:' prefix and relocated to en/docs/markdown/defaults/, establishing the per-format defaults directory structure. Identifier updated to match. Rule content unchanged."
  - version: "0.1.0"
    date: "2026-07-23"
    author: "Christopher Steel"
    notes: >
      First versioned form. Consolidates three previously separate,
      unversioned example files (general content, code documentation, code)
      into one template document, and adds the AI-assistance attribution
      variant already in consistent practice across the project's versioned
      documents.
---

# Markdown: License Statement Templates

Version: 0.3.1
Status: Draft
Style Guide: style-guide--versioned-documents-in-unrendered-markdown

## Purpose

These are the standard templates for the License section of any document or project. Replace the bracketed placeholders; keep everything else, including punctuation and emphasis, exactly as written. Choose the variant matching the content type and the license actually in use.

## General content

For prose documents, guides, and other general content, licensed under Creative Commons:

```markdown
## License

This document, *[Document Title]*, by **[Author Name]**, is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

![CC License](https://mirrors.creativecommons.org/presskit/buttons/88x31/svg/by.svg)
```

## Code documentation

For documentation accompanying code, licensed to match the code it documents:

```markdown
## License

This document, *[Document Title]*, by **[Author Name]**, with AI assistance from **Claude (Anthropic)**, is licensed under the [GNU General Public License v3.0 or later](https://www.gnu.org/licenses/gpl-3.0.html).
```

## Code

For software projects, in the project README:

```markdown
## License

This software, *[Project Name]*, by **[Author Name]**, is licensed under the [GNU General Public License v3.0 or later (GPL-3.0-or-later)](https://www.gnu.org/licenses/gpl-3.0.html).

You may redistribute and/or modify this software under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See the `LICENSE` file included with this project for the full license text.

[![License: GPL v3+](https://img.shields.io/badge/License-GPLv3%2B-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
```

## Versioned documents with AI assistance

For versioned documents in this and related repositories, licensed under AGPL, with AI assistance attributed by model:

```markdown
## License

This document, *[Document Title]*, by **[Author Name]**, with AI assistance from **Claude Sonnet 4.6 (Anthropic)**, is licensed under the [GNU Affero General Public License v3.0 or later](https://www.gnu.org/licenses/agpl-3.0.html).
```

## Notes on use

The AI-assistance attribution names the specific model when known ("Claude Sonnet 4.6 (Anthropic)") rather than the generic "Claude (Anthropic)"; prefer the specific form in new documents. When a project includes a `LICENSE` file, the full verbatim license text belongs there; the License section in a document or README states the licensing and links to the canonical license URL, it does not reproduce the full text.

## License

This document, *Markdown: License Statement Templates*, by **Christopher Steel**, with AI assistance from **Claude Sonnet 4.6 (Anthropic)**, is licensed under the [GNU Affero General Public License v3.0 or later](https://www.gnu.org/licenses/agpl-3.0.html).

## Changelog

| Version | Status | Notes |
|---------|--------|-------|
| 0.3.1 | Draft | Recreated in sat-doc-automa; Style Guide reference normalized to the versionless slug |
| 0.3.0 | Draft | Dropped the 'Default:' title segment, default status now designated by the defaults/ directory; identifier and filename updated; rule content unchanged |
| 0.2.0 | Draft | Retitled with the 'Markdown: Default:' prefix and relocated to en/docs/markdown/defaults/; identifier updated; rule content unchanged |
| 0.1.0 | Draft | First versioned form; consolidates three separate unversioned example files and adds the AI-assistance variant already in consistent practice |
