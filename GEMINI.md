# Wiki Template — Schema & Workflow Instructions

This wiki is maintained entirely by Gemini CLI. No API key or Python scripts needed — just open this repo with `gemini` and talk to it.

## How to Use

Describe what you want in plain English:
- *"Ingest this file: raw/papers/my-paper.md"*
- *"What does the wiki say about transformer models?"*
- *"Check the wiki for orphan pages and contradictions"*
- *"Build the knowledge graph"*

Or use shorthand triggers:
- `ingest <file>` → runs the Ingest Workflow
- `query: <question>` → runs the Query Workflow
- `synthesize [[PageName]]` → runs the Synthesis Workflow
- `health` → runs the Health Workflow (fast, every session)
- `lint` → runs the Lint Workflow (expensive, periodic)
- `build graph` → runs the Graph Workflow

---

## Schema Reference Files

Detailed specs are in `.claude/schema/` — read them on demand:

| File | When to read |
|------|-------------|
| `.claude/schema/card-types.md` | Before any ingest or card creation |
| `.claude/schema/page-format.md` | Before creating/updating any wiki page |
| `.claude/schema/workflows.md` | For full workflow steps |

---

## Directory Layout

```
raw/          # Immutable source documents — never modify these
wiki/         # Agent owns this layer entirely
  index.md    # Catalog of all pages — update on every ingest
  log.md      # Append-only chronological record
  overview.md # Living synthesis across all sources
  sources/    # One summary page per source document
  entities/   # People, events
  concepts/   # Terminology, insight, action, schema, basic, index-card
  atoms/      # Quotes, new words — atomic knowledge fragments
  syntheses/  # Structured multi-card analysis
  query/      # Saved query answers
  types/      # Type & card_type definition pages
  archive/    # Versioned snapshots of updated pages (excluded from graph)
graph/        # Auto-generated graph data
tools/        # Standalone Python scripts
```

---

## Page Format

Every wiki page uses this frontmatter:

```yaml
---
title: "Page Title"
aliases: []
type: source | entity | concept | synthesis | query | atom
card_type: person | event | terminology | insight | action | schema | basic | index-card | quote | new-word
tags: []
sources:
  - "[[source-slug]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
revisions: []
---
```

Use `[[PageName]]` wikilinks to link to other wiki pages.

**Every entity, concept, and atom page MUST end with a `## 关联` section** with 4 relationship types: `#backs`, `#challenges`, `#extends`, `#applies`.

---

## Ingest Workflow

Triggered by: *"ingest <file>"*

**Before starting: Read `.claude/schema/card-types.md` and `.claude/schema/page-format.md`**

Supported formats: `.md` ingested directly. Non-markdown files auto-converted via markitdown. Use `--no-convert` to skip.

1. Read source document fully (auto-convert if non-markdown)
2. Read `wiki/index.md` and `wiki/overview.md` for context
3. Write `wiki/sources/<slug>.md` (source page format)
4. Update `wiki/index.md` — add entry under Sources
5. Update `wiki/overview.md` — revise synthesis if warranted
6. Archive existing pages that will be updated (→ `wiki/archive/`)
7. Cross-reference scan — search existing wiki for overlapping terms
8. Top-down extraction: core insight → evidence → people → quotes → actions → free notes
9. Update/create entity pages (person, event)
10. Update/create concept pages — scan for insight candidates FIRST
11. Extract quotes and new words → atom pages
12. Alias deduplication — add variants to existing page aliases
13. Flag contradictions with existing wiki content
14. Prepend to `wiki/log.md`: `## [YYYY-MM-DD] ingest | <Title>`
15. Post-ingest validation — check broken wikilinks, verify index coverage

### Source Page Format

```markdown
---
title: "Source Title"
type: source
tags: []
date: YYYY-MM-DD
source_file: raw/...
---

## Summary
2–4 sentence summary.

## Key Claims
- Claim 1

## Key Quotes
> "Quote here"

## Connections
- [[EntityName]] — how they relate

## Contradictions
- Contradicts [[OtherPage]] on: ...
```

---

## Query Workflow

Triggered by: *"query: <question>"*

1. Read `wiki/index.md` — identify relevant pages
2. Read those pages
3. Synthesize answer with `[[PageName]]` citations
4. Offer to save as `wiki/query/<slug>.md`

---

## Synthesis Workflow

Triggered by: *"synthesize [[PageName]]"* or *"synthesize 'theme' from [[Card1]], [[Card2]]"*

Two modes: from a seed card (auto-collect related cards) or from user-provided card list.
Collect cards → choose grouping dimension (4±3 groups) → extract verbatim fact sentences → write to `wiki/syntheses/<slug>.md` → update index and log.

---

## Lint Workflow

Triggered by: *"lint"*

Check for: orphan pages, broken links, contradictions, stale content, missing entity pages, data gaps.
Output a lint report, offer to save to `wiki/lint-report.md`.

---

## Health Workflow

Triggered by: *"health"*

Run: `python tools/health.py` (or `python tools/health.py --json` for machine-readable output)

Fast structural checks — **zero LLM calls**, safe every session:
- Empty/stub files, index sync, log coverage.

| Dimension | `health` | `lint` |
|---|---|---|
| **Scope** | Structural integrity | Content quality |
| **LLM calls** | Zero | Yes |
| **Frequency** | Every session | Every 10-15 ingests |
| **Tool** | `tools/health.py` | `tools/lint.py` |

> Run `health` first — linting an empty file wastes tokens.

---

## Graph Workflow

Triggered by: *"build graph"*

Try `python tools/build_graph.py` first. If unavailable, build graph.json and graph.html manually from wikilinks.

---

## Naming Conventions

- Source slugs: `kebab-case`
- Entity/Concept pages: `TitleCase.md`
- Atom/Synthesis pages: `kebab-case.md`

## Log Format

`## [YYYY-MM-DD] <operation> | <title>`

Operations: `ingest`, `query`, `synthesis`, `lint`, `graph`, `health`
