---
dc:title: "Collaboration: Energy Conservation in AI Collaborations"
dcterms:version: "0.2.0"
dc:creator: "Christopher Steel"
dc:description: "Standing directive and Universal Cake evaluation: AI collaborators ask before computationally intensive operations. Includes sourced impact projections for adoption at organizational and industry scale."
dcterms:created: "2026-07-24"
dcterms:modified: "2026-07-25"
dc:format: "text/markdown"
dc:language: "en"
sat:language_bcp47: "en"
dc:identifier: "collaboration--energy-conservation-in-ai-collaborations"
dcterms:rightsHolder: "Christopher Steel"
dc:rights: >
  Copyright 2026 Christopher Steel.
  SPDX-License-Identifier: AGPL-3.0-or-later
sat:uuid: ""
sat:version_at_creation: "0.4.0"
sat:migration_status: pre-sat
sat:changelog:
  - version: "0.2.0"
    date: "2026-07-25"
    author: "Christopher Steel"
    notes: >
      Compliance pass per ROADMAP.md Milestone 0.3.0. Corrected the
      one-team-of-ten water arithmetic (2,000 queries/day is approximately
      33 litres/day, not 3.3) and the annual and industry-scale figures that
      follow from it, and made the working-day basis of the per-year figures
      explicit. Brought the citations into the Citation Anchor Pair workflow
      and corrected the Epoch AI in-text citation to match its reference
      entry, filed under You, J. (2025). Applied copy-edits: today's, life
      giving, and terminal periods on the Reality bullets. Set the Placement
      prose and the Reality heading to match the settled ai-collaboration name.
  - version: "0.1.0"
    date: "2026-07-24"
    author: "Christopher Steel"
    notes: "Initial draft. Establishes the collaboration format directory under automa, the UC matrix evaluation across four pillars, and sourced impact projections for adoption at scale."
---

# Collaboration: Energy Conservation in AI Collaborations

Version: 0.2.0
Status: Draft
Style Guide: style-guide--versioned-documents-in-unrendered-markdown

## Abstract

A standing directive for AI collaborators: ask before performing computationally intensive operations rather than assuming permission. This document states the rule, evaluates it against the Universal Cake framework across four pillars, and projects the concrete reductions in energy, water, bandwidth, time, and cognitive load if the practice is adopted beyond a single project, grounded in published per-query consumption data rather than hypothetical estimates.

## The reality

In today's very human world, the following are true:

- Compute is never "free".
- Bandwidth is never "free".
- Clean water is a life giving and limited resource.
- Clean air is a life giving and limited resource.
- Clean food requires clean air and clean water.

## The rule

AI collaborators must ask before performing computationally intensive operations. This includes rebuilding repositories, repackaging archives, running full test suites, bulk file transformations, downloading large artifacts, creating and destroying test environments, and any operation that consumes meaningful compute, energy, or time that could be avoided if the operation turns out to be unnecessary or premature.

The question is short: "May I rebuild this?" The answer takes seconds.

## What counts as computationally intensive

The threshold is judgment, not a fixed rule, but these are reliably on the wrong side of it:

- Rebuilding or repackaging an entire repository or archive
- Running a full test suite or end-to-end validation pass
- Bulk file operations across many documents (renaming, reformatting, migrating)
- Downloading large artifacts (release tarballs, language models, datasets)
- Creating and destroying test environments (users, virtual environments, containers)
- Any operation the collaborator would describe as "let me just do this real quick" before spending several minutes on it

Single-file edits, reading files, short shell commands for verification, and search queries are not computationally intensive and do not require permission.

## The cost of a single unnecessary operation

Published data gives us real numbers rather than vague appeals to "be mindful."

A typical AI query consumes approximately 0.3 watt-hours of electricity (<a name="apa-you-citation"></a>[You, 2025](#apa-you-reference); <a name="apa-toolpod-citation"></a>[Toolpod, 2026](#apa-toolpod-reference)). Larger models and longer exchanges consume more: Claude 3 Opus benchmarks at approximately 4 watt-hours per 400-token exchange (<a name="apa-energycosts-citation"></a>[EnergyCosts.co.uk, 2026](#apa-energycosts-reference)), and coding agents like Claude Code can consume the equivalent of thousands of typical queries in a single session (<a name="apa-willison-citation"></a>[Willison, 2026](#apa-willison-reference)).

Each query also consumes water. Direct cooling alone accounts for approximately 0.3 milliliters per query (Altman, cited in <a name="apa-axis-citation"></a>[Axis Intelligence, 2026](#apa-axis-reference)). When indirect water use from electricity generation is included, a 20-to-50-query conversation consumes roughly 500 milliliters, about one standard bottle of water (<a name="apa-li-citation"></a>[Li et al., 2023](#apa-li-reference)).

A computationally intensive operation in a collaboration session, rebuilding a repository, repackaging an archive, running a test suite, is not one query. It is dozens to hundreds of tool calls, file operations, and model invocations chained together. A single unnecessary rebuild of the kind this directive exists to prevent can easily consume 50 to 200 queries' worth of compute, roughly 15 to 800 watt-hours of electricity and 15 to 60 milliliters of direct cooling water, plus the bandwidth to transfer the results.

## What adoption at scale would reduce

These projections use the published per-query figures above and a conservative assumption: that a typical AI-assisted development session includes two computationally intensive operations that could have been avoided by asking first. The actual number varies by workflow, but "two unnecessary rebuilds per session" is consistent with the pattern that prompted this directive. The per-year figures assume a 260-day working year.

### One team of ten

Ten developers, each running one AI collaboration session per workday, each session containing two avoidable intensive operations averaging 100 queries' worth of compute each.

- **Energy**: 10 people x 2 operations x 100 queries x 0.3 Wh = 600 Wh per day, roughly 156 kWh per year (260 working days), equivalent to running a domestic refrigerator for two months (<a name="apa-willison-citation-2"></a>[Willison, 2026](#apa-willison-reference)).
- **Water**: at the comprehensive scope of roughly 500 mL per 30-query conversation (<a name="apa-li-citation-2"></a>[Li et al., 2023](#apa-li-reference)), two 100-query operations per person per day is approximately 33 liters per day across the team, over 8,500 liters per year (260 working days), enough to fill a 150-litre bathtub more than fifty times.
- **Bandwidth**: each rebuild or repackage cycle typically transfers 10 to 50 MB of artifacts. Twenty unnecessary transfers per day across the team is 200 to 1,000 MB per day, meaningful for anyone on a metered, mobile, or intermittent connection.
- **Time**: each unnecessary operation takes 2 to 10 minutes of wall-clock time during which the human waits. Twenty per day across the team is 40 to 200 minutes of dead time daily.

### One thousand teams

Scale the team figures by 1,000 and the numbers become infrastructure-grade:

- **Energy**: 156,000 kWh per year, enough to power roughly 14 US homes for a year.
- **Water**: approximately 8,500,000 liters per year, over three Olympic swimming pools.
- **Bandwidth**: 200 to 1,000 GB per day of unnecessary transfers.
- **Time**: 40,000 to 200,000 minutes of developer wait time per day, 700 to 3,300 person-hours daily.

### Industry-wide

Generative AI platforms currently serve on the order of 2.5 billion queries per day (<a name="apa-ieee-citation"></a>[IEEE Spectrum, 2025](#apa-ieee-reference)). If even 1% of those queries belong to collaborative development sessions, and 10% of the compute in those sessions is avoidable, the reduction from this single practice would be on the order of tens of thousands of kilowatt-hours per day, tens of thousands of liters of water per day, and hundreds of thousands of minutes of human wait time. These are conservative figures; the actual share of collaborative development in total AI usage is growing as coding agents become more common (<a name="apa-willison-citation-3"></a>[Willison, 2026](#apa-willison-reference)).

## Universal Cake evaluation

This directive scores across four pillars simultaneously, which is why it belongs in the framework rather than as a standalone tip.

### Sustainability (reduce)

"Reduce" sits at the top of the reduce/reuse/recycle hierarchy because it is the only strategy that prevents resource consumption rather than mitigating it after the fact. An unnecessary rebuild that is avoided does not need its energy offset or its water reclaimed. It simply never consumed either. This is a stronger environmental position than efficiency, it is avoidance, the highest-priority strategy in the waste hierarchy, applied to computation.

### Inclusive (economic and cognitive accessibility)

Unnecessary computation is not free for the human either. It consumes bandwidth, which matters for someone on a metered, slow, or intermittent connection, exactly the people the Inclusive pillar's "does it work on a slow connection" question is about. A 20 MB archive repackaged and re-downloaded three times in a session because nobody asked "is this premature?" is 60 MB of bandwidth that served no purpose, and for someone paying per-megabyte or working from a mobile hotspot, that is a real, excludable cost.

Cognitive load compounds alongside the wasted time. Each unnecessary operation interrupts the collaborator's train of thought, forces a context switch to verify the output was correct, and adds noise to the session history that makes it harder to find the work that actually mattered. For someone using assistive technology to navigate a conversation, the additional irrelevant output is a proportionally larger burden.

### Agency (sovereignty)

An AI collaborator that consumes resources without asking is making a resource-spending decision on behalf of the person who bears the cost. The AI optimizes for its own metric, appearing responsive, at the expense of the human's resources: energy, bandwidth, time, money, and attention. Asking first returns the decision to the person who actually pays for it. This is a direct instance of the vendor-and-user power asymmetry the evaluation framework already measures.

### Transparency

The cost of computation is invisible by default. The person does not see the water, the electricity, or the GPU hours. Making the cost visible by naming it at the moment the decision is made, "this will rebuild the whole project, shall I proceed?", is itself an act of transparency about a cost that is otherwise entirely hidden. This is the same principle behind the evaluation framework's information-asymmetry measurement, applied to the collaboration process itself.

## Why this is a negative-cost investment

Asking permission before an expensive operation is not a bottleneck. It is what makes the collaboration sustainable enough to continue at all.

This is also a bridging investment in trust. A collaborator, human or AI, that acts first and shows the result afterward is optimizing for speed at the cost of the relationship's capacity to continue. A collaborator that asks first is moving at the speed of trust, which is slower per turn and faster per project, because it avoids the rework, the wasted energy, and the erosion of confidence that uninvited action causes over time.

A project that evaluates its tools for environmental impact but does not apply the same scrutiny to its own working methods has a gap between what it measures and what it practices. This directive closes that gap.

## Placement

This is the first directive in the `ai-collaboration` format directory under `automa/`. The same `defaults/` and `examples/` structure used for markdown directives applies here.

```bash
en/docs/automa/ai-collaboration/defaults/
en/docs/automa/ai-collaboration/examples/
```

## License

This document, *Collaboration: Energy Conservation in AI Collaborations*, by **Christopher Steel**, with AI assistance from **Claude Sonnet 4.6 (Anthropic)**, is licensed under the [GNU Affero General Public License v3.0 or later](https://www.gnu.org/licenses/agpl-3.0.html).

## References

<a name="apa-axis-reference"></a>Axis Intelligence. (2026). *AI data center water usage statistics 2026*. https://axis-intelligence.com/ai-data-center-water-usage-statistics/
[Return to citation](#apa-axis-citation)

<a name="apa-energycosts-reference"></a>EnergyCosts.co.uk. (2026). *How much energy does Anthropic's Claude AI consume?*. Network Equity Ltd. https://www.energycosts.co.uk/articles/anthropic-claude-ai-energy/
[Return to citation](#apa-energycosts-citation)

<a name="apa-ieee-reference"></a>IEEE Spectrum. (2025). *AI energy use: The hidden cost of ChatGPT queries*. https://spectrum.ieee.org/ai-energy-use
[Return to citation](#apa-ieee-citation)

<a name="apa-li-reference"></a>Li, P., Yang, J., Islam, M. A., & Ren, S. (2023). Making AI less "thirsty": Uncovering and addressing the secret water footprint of AI models. *arXiv preprint arXiv:2304.03271*. https://arxiv.org/abs/2304.03271
[Return to citation](#apa-li-citation)

<a name="apa-toolpod-reference"></a>Toolpod. (2026). *AI energy consumption: How much power does AI use?*. https://toolpod.dev/blog/ai-energy-consumption-environmental-impact
[Return to citation](#apa-toolpod-citation)

<a name="apa-willison-reference"></a>Willison, S. (2026). *Electricity use of AI coding agents*. Simon Willison's Weblog. https://simonwillison.net/tags/ai-energy-usage/
[Return to citation](#apa-willison-citation)

<a name="apa-you-reference"></a>You, J. (2025). *How much energy does ChatGPT use?*. Epoch AI. https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use
[Return to citation](#apa-you-citation)

## Changelog

| Version | Status | Notes |
|---------|--------|-------|
| 0.2.0 | Draft | Compliance pass: corrected the one-team-of-ten water arithmetic (33 L/day, not 3.3) and the figures that scale from it, made the 260-working-day basis explicit, brought citations into the CAP workflow, corrected the Epoch AI citation to match the You (2025) reference, and applied the roadmap copy-edits |
| 0.1.0 | Draft | Initial draft |
