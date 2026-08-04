---
dc:title: "Markdown: No Hard Line Wraps"
dcterms:version: "0.1.0"
dc:creator: "Christopher Steel"
dc:description: "House rule: do not hard-wrap prose paragraphs at a fixed column; let lines run to their natural length and wrap only inside code blocks."
dcterms:created: "2026-07-31"
dcterms:modified: "2026-07-31"
dc:format: "text/markdown"
dc:language: "en"
sat:language_bcp47: "en"
dc:identifier: "markdown--no-hard-line-wraps"
dcterms:rightsHolder: "Christopher Steel"
dc:rights: >
  Copyright 2026 Christopher Steel.
  SPDX-License-Identifier: AGPL-3.0-or-later
sat:uuid: ""
sat:version_at_creation: "0.1.4"
sat:migration_status: pre-sat
sat:changelog:
  - version: "0.1.0"
    date: "2026-07-31"
    author: "Christopher Steel"
    notes: "Initial draft. Drafted by Claude Sonnet 5 during a SAT content-ingress design session, prompted by a hard-wrap formatting inconsistency observed in that session's own ADR output — the rule already existed in the versioned-documents style guide but had no automa/ai-collaboration entry to intercept it at generation time."
---

# Markdown: No Hard Line Wraps

Version: 0.1.0
Status: Draft
Style Guide: style-guide--versioned-documents-in-unrendered-markdown

## The rule

Do not insert manual line breaks within a prose paragraph at 80 characters or any other fixed column. Write each paragraph as one continuous line of source text and let the renderer wrap it at display time. Hard line breaks are correct only inside code blocks, where they are part of the content itself.

This directive exists so an AI collaborator follows the rule by default, at generation time, rather than depending on a style guide having already been consulted. The versioned-documents style guide already states this rule for the documents it governs; this automa entry makes it apply before any style guide has been chosen, the same way the other markdown defaults do for their own rules.

## License

This document, *Markdown: No Hard Line Wraps*, by **Christopher Steel**, with AI assistance from **Claude Sonnet 5 (Anthropic)**, is licensed under the [GNU Affero General Public License v3.0 or later](https://www.gnu.org/licenses/agpl-3.0.html).
