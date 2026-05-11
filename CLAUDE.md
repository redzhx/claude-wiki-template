# Wiki Template — Schema & Workflow Instructions

This wiki is maintained entirely by Claude Code. No API key or Python scripts needed — just open this repo in Claude Code and talk to it.

## Schema Reference Files

Detailed specs are in `.claude/schema/` — read them on demand, not upfront:

| File | When to read |
|------|-------------|
| `.claude/schema/card-types.md` | Before any ingest or card creation |
| `.claude/schema/page-format.md` | Before creating/updating any wiki page |
| `.claude/schema/workflows.md` | For full workflow steps |

---

<!-- CONFIGURABLE: Set your wiki's output language.
     Default is English. For Chinese, add rules like:
     "All wiki page body text MUST be written in Chinese (中文)."
     For other languages, adjust accordingly. -->

## Output Language

All wiki page body text is written in **English** by default. To change this, edit the language configuration and translate the section headers in schema files.

<!-- CONFIGURABLE: If your wiki uses a non-English language, add H1 title language rules here.
     Example for Chinese: concept card H1 must use Chinese or bilingual; foreign person cards use English or bilingual. -->

---

## Slash Commands

| Command | What to say |
|---|---|
| `/wiki-ingest` | `ingest raw/my-article.md` |
| `/wiki-query` | `query: what are the main themes?` |
| `/wiki-synthesis` | `synthesize [[PageName]]` or `synthesize "theme" from [[Card1]], [[Card2]]` |
| `/wiki-health` | `health` (fast, every session) |
| `/wiki-lint` | `lint the wiki` (expensive, periodic) |
| `/wiki-graph` | `build the knowledge graph` |

Or just describe what you want in plain language.

---

## Directory Layout

```
raw/          # Immutable source documents — never modify these
wiki/         # Claude owns this layer entirely
  index.md    # Catalog of all pages — update on every ingest
  log.md      # Reverse chronological record (newest first)
  overview.md # Living synthesis across all sources
  sources/    # One summary page per source document
  entities/   # People (人物卡), events (事件卡)
  concepts/   # Terminology (术语卡), insight (新知卡), basics (基础卡),
              #   actions (行动卡), schemas (图示卡), index cards (索引卡)
  atoms/      # Quotes (金句卡), new words (新词卡) — atomic knowledge fragments
  syntheses/  # Synthesis cards (综述卡) — structured multi-card analysis
  query/      # Saved query answers (问答) — Q&A format
  types/      # Type & card_type definition pages (linked from frontmatter)
  archive/    # Versioned snapshots of updated pages (excluded from graph)
graph/        # Auto-generated graph data
tools/        # Standalone Python scripts
  health.py   # Structural checks (deterministic, no LLM calls)
  lint.py     # Content quality checks (uses LLM for semantic analysis)
  build_graph.py  # Knowledge graph generation
.claude/schema/   # Claude Code workflow specs (not wiki content)
  card-types.md   # 11 card type templates + extraction guidelines
  page-format.md  # Frontmatter, 关联 format, domain tags, index/log format
  workflows.md    # Full workflow steps for ingest/query/synthesis/lint/health/graph
```

<!-- CONFIGURABLE: Rename subdirectories and card types to match your own system.
     The 11 card types (based on 卡片大法) are the default preset. -->

---

## Naming Conventions

### Raw Source Files (`raw/`)

Format: `<type-prefix>-<short-description>.md`

| Type | Prefix | Example |
|------|--------|---------|
| Paper | `paper` | `paper-2017-attention-is-all-you-need.md` |
| Book / Chapter | `book` | `book-erta-ch03-deliberate-practice.md` |
| Article / Blog | `article` | `article-example-topic.md` |
| Lecture Notes | `lecture` | `lecture-cogsci-week05-working-memory.md` |

Rules:
- All lowercase kebab-case
- Papers may include year: `paper-2024-...`
- Books include chapter number: `book-...-ch03-...`

### Book Ingestion Strategy

**Split by chapter, ingest in order.** Do not ingest an entire book at once.

```
raw/book-erta-deliberate-practice/
  book-erta-ch01-introduction.md
  book-erta-ch02-mental-representations.md
  ...
```

After all chapters are ingested, use the Synthesis Workflow to produce a whole-book overview.

### Wiki Pages

- Source slugs: `kebab-case` matching source filename
- Entity pages: `TitleCase.md` (e.g. `OpenAI.md`, `SamAltman.md`)
- Concept pages: `TitleCase.md` (e.g. `ReinforcementLearning.md`, `RAG.md`)
- Atom pages: `kebab-case.md` (e.g. `slow-is-smooth-smooth-is-fast.md`)
- Synthesis pages: `kebab-case.md` (e.g. `paul-graham-overview.md`)

---

## Workflows (Summary)

Full steps for each workflow are in `.claude/schema/workflows.md`. Read it before executing.

### Ingest
Triggered by: *"ingest <file>"* or `/wiki-ingest`
**Read `.claude/schema/card-types.md` and `.claude/schema/page-format.md` before starting.**
High-level: read source → write source page → update index/overview → archive existing pages → create/update entity+concept+atom cards → update log → validate.

### Query
Triggered by: *"query: <question>"* or `/wiki-query`
High-level: read index → read relevant pages → synthesize answer with `[[wikilink]]` citations → offer to save.

### Synthesis
Triggered by: *"synthesize [[PageName]]"* or *"synthesize 'theme' from [[Card1]], [[Card2]]"* or `/wiki-synthesis`
High-level: collect related cards → choose grouping dimension → extract verbatim fact sentences → write synthesis page → update index + log.

### Health
Triggered by: *"health"* or `/wiki-health`
Run: `python tools/health.py` — zero LLM calls, safe every session.

### Lint
Triggered by: *"lint the wiki"* or `/wiki-lint`
Run: `python tools/lint.py` — uses LLM, run every 10-15 ingests.

### Graph
Triggered by: *"build the knowledge graph"* or `/wiki-graph`
Run: `python tools/build_graph.py` — outputs `graph/graph.json` + `graph/graph.html`.
