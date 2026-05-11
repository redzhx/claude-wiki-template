# Wiki Template — Schema & Workflow Instructions

This wiki is maintained entirely by your coding agent. No API key or Python scripts needed — just open this repo in Codex, OpenCode, or any agent that reads this file, and talk to it.

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

Detailed specs are in `.claude/schema/` — read them on demand, not upfront:

| File | When to read |
|------|-------------|
| `.claude/schema/card-types.md` | Before any ingest or card creation |
| `.claude/schema/page-format.md` | Before creating/updating any wiki page |
| `.claude/schema/workflows.md` | For full workflow steps |

<!-- CONFIGURABLE: Set your wiki's output language.
     See docs/LANGUAGE.md for adapting to different languages. -->

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
  health.py   # Structural checks (deterministic, no LLM calls)
  lint.py     # Content quality checks (uses LLM for semantic analysis)
  build_graph.py  # Knowledge graph generation
.claude/schema/   # Workflow specs (not wiki content)
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

- `type` determines the directory (`entities/`, `concepts/`, `atoms/`, etc.)
- `card_type` determines the template and self-validation rules (required for entity, concept, atom pages)
- `aliases` lists alternative names; add variants here instead of creating duplicate pages
- `sources` is a YAML list of `[[wikilink]]` entries pointing to source pages
- Use `[[PageName]]` wikilinks to link to other wiki pages

---

## Connections Format (关联)

**Every entity, concept, and atom page MUST end with a `## 关联` section.**

4 relationship types: `#backs` (supports), `#challenges` (challenges), `#extends` (extends), `#applies` (applies).

---

## Ingest Workflow

Triggered by: *"ingest <file>"*

**Before starting: Read `.claude/schema/card-types.md` and `.claude/schema/page-format.md`**

**Supported formats:** `.md` ingested directly. Non-markdown files (`.pdf`, `.docx`, `.pptx`, `.xlsx`, `.html`, `.txt`, `.csv`, `.json`, `.xml`, `.rst`, `.rtf`, `.epub`, `.ipynb`, `.yaml`, `.yml`, `.tsv`, `.wav`, `.mp3`) auto-converted via markitdown. Use `--no-convert` to skip.

Steps (in order):
1. Read the source document fully (auto-convert if non-markdown)
2. Read `wiki/index.md` and `wiki/overview.md` for current wiki context
3. Write `wiki/sources/<slug>.md` — use the source page format
4. Update `wiki/index.md` — add entry under Sources section
5. Update `wiki/overview.md` — revise synthesis if warranted
6. **Check for existing pages that will be updated** — archive before modifying
7. **Cross-reference scan** — search existing wiki for overlapping terms/concepts
8. **Top-down extraction** — core insight → evidence → people → quotes → actions → free notes
9. Update/create entity pages (person, event)
10. Update/create concept pages — scan for insight candidates FIRST
11. Extract quotes and new words → atom pages (only when genuinely striking)
12. **Alias deduplication** — add variant names to existing page aliases
13. Flag contradictions with existing wiki content
14. Prepend to `wiki/log.md`: `## [YYYY-MM-DD] ingest | <Title>`
15. **Post-ingest validation** — check for broken wikilinks, verify index coverage

### Source Page Format

```markdown
---
title: "Source Title"
type: source
tags: []
date: YYYY-MM-DD
source_file: raw/...
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Source Title

## Summary
2–4 sentence summary.

## Key Claims
- Claim 1
- Claim 2

## Key Quotes
> "Quote here" — context

## Connections
- [[EntityName]] — #extends how they relate
- [[ConceptName]] — #backs how it connects

## Contradictions
- Contradicts [[OtherPage]] on: ...
```

### Domain-Specific Templates

#### Diary / Journal Template
```markdown
---
title: "YYYY-MM-DD Diary"
type: source
tags: [diary]
date: YYYY-MM-DD
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# YYYY-MM-DD Diary

## Event Summary
## Key Decisions
## Energy & Mood
## Connections
## Shifts & Contradictions
```

#### Meeting Notes Template
```markdown
---
title: "Meeting Title"
type: source
tags: [meeting]
date: YYYY-MM-DD
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Meeting Title

## Goal
## Key Discussions
## Decisions Made
## Action Items
```

---

## Query Workflow

Triggered by: *"query: <question>"*

Steps:
1. Read `wiki/index.md` to identify relevant pages
2. Read those pages (up to ~10 most relevant)
3. Synthesize an answer with inline citations as `[[PageName]]` wikilinks
4. Ask the user if they want the answer saved as `wiki/query/<slug>.md`

---

## Synthesis Workflow

Triggered by: *"synthesize [[PageName]]"* or *"synthesize 'theme' from [[Card1]], [[Card2]]"*

Two modes:
- **Mode 1**: from a seed card — AI auto-collects related cards
- **Mode 2**: from user-provided card list + theme

Steps:
1. Collect related cards (grep for seed card's title/aliases across wiki/)
2. Choose a grouping dimension (timeline, theme, causal chain, debate, etc.)
3. Group into 4±3 groups
4. Extract verbatim fact sentences from each card
5. Write to `wiki/syntheses/<slug>.md`
6. Update index and log

---

## Lint Workflow

Triggered by: *"lint"*

Check for:
- **Orphan pages** — wiki pages with no inbound `[[links]]`
- **Broken links** — `[[WikiLinks]]` pointing to non-existent pages
- **Contradictions** — claims that conflict across pages
- **Stale summaries** — pages not updated after newer sources
- **Missing entity pages** — entities mentioned in 3+ pages but lacking their own page
- **Data gaps** — questions the wiki can't answer; suggest new sources

Output a lint report and ask if the user wants it saved to `wiki/lint-report.md`.

---

## Health Workflow

Triggered by: *"health"*

Run: `python tools/health.py` (or `python tools/health.py --json` for machine-readable output)

Fast structural integrity checks — **zero LLM calls**, safe to run every session:
- **Empty / stub files** — pages with no content beyond frontmatter
- **Index sync** — `wiki/index.md` entries vs actual files on disk
- **Log coverage** — source pages missing a corresponding `ingest` entry in `wiki/log.md`

### Health vs Lint Boundary

| Dimension | `health` | `lint` |
|---|---|---|
| **Scope** | Structural integrity | Content quality |
| **LLM calls** | Zero | Yes (semantic analysis) |
| **Cost** | Free | Tokens |
| **Frequency** | Every session, before other work | Every 10-15 ingests |
| **Tool** | `tools/health.py` | `tools/lint.py` |
| **Run order** | First (pre-flight) | After health passes |

> Run `health` first — linting an empty file wastes tokens.

---

## Graph Workflow

Triggered by: *"build graph"*

First try: `python tools/build_graph.py`

If Python/deps unavailable, build manually:
1. Search for all `[[wikilinks]]` across wiki pages
2. Build nodes (one per page) and edges (one per link)
3. Infer implicit relationships not captured by wikilinks
4. Write `graph/graph.json` + `graph/graph.html`

---

## Naming Conventions

- Source slugs: `kebab-case` matching source filename
- Entity pages: `TitleCase.md` (e.g. `OpenAI.md`, `SamAltman.md`)
- Concept pages: `TitleCase.md` (e.g. `ReinforcementLearning.md`, `RAG.md`)
- Atom pages: `kebab-case.md`
- Synthesis pages: `kebab-case.md`

## Log Format

`## [YYYY-MM-DD] <operation> | <title>`

Operations: `ingest`, `query`, `synthesis`, `lint`, `graph`, `health`
