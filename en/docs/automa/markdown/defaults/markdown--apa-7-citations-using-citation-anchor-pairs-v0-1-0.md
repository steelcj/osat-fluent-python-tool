---
dc:title: "Markdown: APA 7 Citations Using Citation Anchor Pairs"
dcterms:version: "0.1.0"
dc:creator: "Christopher Steel"
dc:description: "House rule: cite every source in markdown documents using a Citation Anchor Pair, an in-text anchor and a reference anchor, with a return link from the reference to the citation."
dcterms:created: "2026-07-25"
dcterms:modified: "2026-07-25"
dc:format: "text/markdown"
dc:language: "en"
sat:language_bcp47: "en"
dc:identifier: "markdown--apa-7-citations-using-citation-anchor-pairs"
dcterms:rightsHolder: "Christopher Steel"
dc:rights: >
  Copyright 2026 Christopher Steel.
  SPDX-License-Identifier: AGPL-3.0-or-later
sat:uuid: ""
sat:version_at_creation: "0.4.0"
sat:migration_status: pre-sat
sat:changelog:
  - version: "0.1.0"
    date: "2026-07-25"
    author: "Christopher Steel"
    notes: >
      First versioned form. Migrated from an unversioned system prompt
      snippet (apa-7-cap-workflow-system-prompt.md) into the
      sat-doc-automa repository. Brought to full versioned-document
      standard: frontmatter added, version block added, Abstract,
      License, and Changelog sections added, the em dash in the title
      replaced with a colon, and the outer code fence and duplicated H1
      removed. The required-sections list was aligned with the seven
      sections named in Web-Ready Unrendered Markdown Using APA 7, in
      place of the three named in the original snippet. Citation
      mechanics otherwise unchanged.
---

# Markdown: APA 7 Citations Using Citation Anchor Pairs

Version: 0.1.0
Status: Draft
Style Guide: style-guide--versioned-documents-in-unrendered-markdown

## Abstract

This directive states how sources are cited in markdown documents: in APA 7 form, using the Citation Anchor Pair (CAP) workflow, so that a reader can move from an in-text citation to its reference entry and back again in the rendered document. It carries the full mechanics, anchor naming, both citation forms, the reference entry format, and the required document sections, so that it can be followed without reference to any other document. The reasoning behind these conventions, and their relationship to CommonMark and GitHub Flavoured Markdown, is set out in *Web-Ready Unrendered Markdown Using APA 7* in this repository's style guides.

## The rule

Every source cited in a markdown document carries exactly two anchors, an in-text anchor at the citation and a reference anchor at the reference entry, linked to each other in both directions. This pair is the Citation Anchor Pair. Reference entries follow full APA 7 formatting.

## Anchor naming

Anchor identifiers are lowercase, hyphen-separated, and derived from the source being cited. A citation of the Pulumi documentation uses `pulumi-docs` as its base identifier, giving `apa-pulumi-docs-citation` and `apa-pulumi-docs-reference`.

Repeated citations of the same source append a counter to the in-text anchor:

- First citation: `apa-pulumi-docs-citation`
- Second citation: `apa-pulumi-docs-citation-2`
- Third citation: `apa-pulumi-docs-citation-3`

The reference anchor is always singular, regardless of how many times the source is cited. Its return link points to the first in-text citation only.

## In-text citation format

Narrative citation:

```markdown
<a name="apa-pulumi-docs-citation"></a>[Pulumi (2024)](#apa-pulumi-docs-reference)
```

Parenthetical citation:

```markdown
<a name="apa-pulumi-docs-citation"></a>([Pulumi, 2024](#apa-pulumi-docs-reference))
```

## Reference entry format

```markdown
<a name="apa-pulumi-docs-reference"></a>Pulumi. (2024). *Pulumi documentation*. Pulumi Inc. https://www.pulumi.com/docs/
[Return to citation](#apa-pulumi-docs-citation)
```

Every reference entry has a return link, and every return link points at a real in-text anchor. A reference without a return link, or a return link pointing at an anchor that does not exist, is an incomplete pair.

Entries are listed alphabetically by author surname or, for organisational authors, by organisation name.

## URLs and DOIs

- Always use live hyperlinks, never bare URLs in prose
- Prefer DOIs (`https://doi.org/...`) when available
- No trailing period after a URL or DOI
- Include a retrieval date only for undated or frequently changing content

## Resources section

The Resources section appears before the References section and groups sources by topic, for example Primary Standards or Implementation Guides. Bullets link to the internal `#...-reference` anchors. Raw URLs are not used in the Resources list.

```markdown
## Resources

### Infrastructure as Code
- [Pulumi Documentation](#apa-pulumi-docs-reference)
- [HashiCorp Terraform Documentation](#apa-terraform-docs-reference)
```

## Mermaid diagrams

Where a document includes a Mermaid diagram:

- Use dual-readable node formatting, so the node text is legible both rendered and in source
- Do not use escaped `\n` characters in node labels
- Omit `securityLevel` unless it is genuinely required
- Give every node an accessible label

## Required sections

A document generated under this directive contains the following sections, in this order:

1. Title and version block
2. Abstract
3. Sources and Acknowledgements
4. Body sections
5. Resources, grouped by topic and anchor-linked
6. References, full APA 7 entries with CAP anchors and return links
7. Changelog

The Sources and Acknowledgements section names the standards the document derives from and carries their first citations. The References section is omitted only when the document cites nothing at all, in which case the Resources section is omitted with it.

## License

This document, *Markdown: APA 7 Citations Using Citation Anchor Pairs*, by **Christopher Steel**, with AI assistance from **Claude Opus 5 (Anthropic)**, is licensed under the [GNU Affero General Public License v3.0 or later](https://www.gnu.org/licenses/agpl-3.0.html).

## Changelog

| Version | Status | Notes |
|---------|--------|-------|
| 0.1.0 | Draft | First versioned form, migrated from an unversioned system prompt snippet; brought to full versioned-document standard; em dash in title replaced with a colon; outer code fence and duplicated H1 removed; required-sections list aligned with the APA 7 style guide; citation mechanics unchanged |
