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

### H1 Title Language Rules

<!-- CONFIGURABLE: Adjust per your wiki's language. Example rules for Chinese:
     concept cards → Chinese or bilingual, foreign person cards → English, Chinese person cards → Chinese, etc. -->

| Card Type | H1 Language |
|-----------|-------------|
| concept (terminology/insight/action/schema/basic/index) | Use wiki's primary language or bilingual |
| person (人物卡, foreign) | Original language or bilingual |
| person (人物卡, native) | Use wiki's primary language |
| event (事件卡) | Primary language or bilingual |
| atom (quote/new-word) | Preserve original quote language |
| source | Original title (add translation in parentheses if helpful) |

When a term is widely known by its English name (e.g., "AGI", "Transformer"), keep English as primary and add translation in parentheses or `aliases`.

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
| `/wiki-bilingual` | `bilingual raw/article-foo.md` (if bilingual feature enabled) |

Or just describe what you want in plain language.

---

## Bilingual Reading (Optional)

<!-- CONFIGURABLE: Enable this section if your wiki ingests sources in a non-primary language
     and you want parallel bilingual reading versions. -->

Create bilingual (native/primary language + original) versions of source files for personal reading. Bilingual files live in `raw/bilingual/` and are **never ingested** into the wiki — they are reading aids only.

### Translation Principles

- Paragraph-level translation, preserving original paragraph boundaries
- Technical terms preserved in original language
- Markdown formatting (bold, italic, links, lists) preserved
- Section headers rendered bilingually: `## English / Translation`
- Code blocks and images preserved verbatim

### Bilingual File Format

Bilingual files are named `<original-stem>-bilingual.md`. See `.claude/commands/wiki-bilingual.md` for the full specification. Key elements:
- YAML frontmatter with `original`, `original_url`, `skip_ingest: true`
- Bilingual H1
- Body: translated paragraph (normal text) followed by `> original` (blockquote)
- Link back to original in header blockquote

### Browser Display

Both `build_graph.py` and `build_browser.py` independently check for display content substitution for raw nodes that have a bilingual/translation file at `raw/bilingual/<slug>-<lang>.md`. The browser is a derived view of `graph/graph.json` — every ingest, bilingual creation, or card change must be followed by a graph rebuild.

---

## Directory Layout

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
raw/          # Manual source documents only (e.g., books, reports, PDFs)
  <source-dir>/   # Versioned subdirectories for sources with embedded images
  bilingual/  # Bilingual/translation reading files (derived, never ingested)
wiki/         # Claude owns this layer entirely
  index.md    # Catalog of all pages — update on every ingest
  log.md      # Wiki card ingestion record (ingest/batch/synthesis only)
  overview.md # Living synthesis across all sources
  sources/    # One summary page per source document
  entities/   # People, events
  concepts/   # Terminology, insight, basics, actions, schemas, index cards
  atoms/      # Quotes, new words — atomic knowledge fragments
  syntheses/  # Synthesis cards — structured multi-card analysis
  query/      # Saved query answers — Q&A format
  types/      # Type & card_type definition pages (linked from frontmatter)
  archive/    # Versioned snapshots of updated pages (excluded from graph)
graph/        # Auto-generated graph data
  graph.html  # Interactive graph visualization
browser/      # Card browser web app (static, filterable)
  index.html  # Main card browser — open in browser to explore
changelog.md  # Project-level changes: graph rebuilds, tool updates (not wiki content)
tools/        # Standalone Python scripts
  build_graph.py  # Knowledge graph generation
  build_browser.py # Card browser data generation
  health.py       # Structural checks (deterministic, no LLM calls)
  lint.py         # Content quality checks (uses LLM for semantic analysis)
.claude/schema/   # Claude Code workflow specs (not wiki content)
  card-types.md   # 11 card type templates + extraction guidelines
  page-format.md  # Frontmatter, 关联 format, domain tags, index/log format
  workflows.md    # Full workflow steps for ingest/query/synthesis/lint/health/graph
```

<!-- CONFIGURABLE: Rename subdirectories and card types to match your own system.
     The 11 card types (based on 卡片大法) are the default preset. -->

---

## Naming Conventions

### Raw Source Files

Format: `<type-prefix>[-year]-<short-description>.md`

| Type | Prefix | Date in filename? | Example |
|------|--------|-------------------|---------|
| Academic Paper | `paper` | Year required | `paper-2025-technical-report.md` |
| Article / Blog | `article` | No | `article-example-topic.md` |
| Book / Chapter | `book` | No | `book-example-ch03-deliberate-practice.md` |
| Lecture Notes | `lecture` | No | `lecture-cogsci-week05.md` |
| Policy Document | `policy` | No | `policy-eu-regulation.md` |
| Report | `report` | No | `report-organization-title.md` |

Rules:
- All lowercase kebab-case
- Papers MUST include year in filename: `paper-YYYY-...`; the canonical publication date lives in frontmatter `published`
- All other types: publication date in frontmatter `published` only, NOT in filename
- Books include chapter number: `book-...-ch03-...`

**Subdirectory convention for sources with images**: Some sources (e.g., PDFs with embedded figures, reports with diagrams) are stored in `raw/<versioned-dir>/<filename>.md` alongside an `images/` subdirectory. This preserves relative image paths (`![](images/foo.jpg)`) and the graph builder rewrites them for browser display. The `source_file` field in the wiki source page must include the full relative path (e.g., `source_file: "raw/report-v1/report.md"`).

### Book Ingestion Strategy

**Split by chapter, ingest in order.** Do not ingest an entire book at once.

```
raw/book-example/
  book-example-ch01-introduction.md
  book-example-ch02-topic.md
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

## Development Conventions

### Python Environment
- Use `python3` (not `python`) on macOS — the `python` binary does not exist.
- In tools that shell out to another Python script, use `sys.executable` (not a hardcoded `python3`) to ensure the same interpreter is used.

### Source File Path Validation
- After creating or editing any source page (`wiki/sources/<slug>.md`), verify the `source_file` field in YAML frontmatter exists on disk as an actual file under `raw/`.
- A mismatch causes the graph builder to fail silently when linking source pages to raw nodes.

### Auto-Build Hook
- `.claude/settings.json` can have a PostToolUse hook that auto-runs graph+browser rebuild after every Write/Edit to files under `wiki/`.
- This makes graph+browser rebuild automatic after wiki edits, card creation, and ingests. Non-wiki edits (tools, raw sources, config) do NOT trigger the hook.
- For semantic inference (Pass 2), manually run `python tools/build_graph.py` (without `--no-infer`) or `/wiki-graph`.

### Bilingual Filename Normalization
- Raw filenames may contain spaces; bilingual filenames always use hyphens.
- Both `build_graph.py` and `build_browser.py` should normalize spaces→hyphens when looking up bilingual files.
- Nested raw files (e.g., `raw/report-v1/report.md`) are looked up by basename only in `raw/bilingual/`.

---

## Workflows (Summary)

Full steps for each workflow are in `.claude/schema/workflows.md`. Read it before executing.

### Ingest
Triggered by: *"ingest <file>"* or `/wiki-ingest`
**Read `.claude/schema/card-types.md` and `.claude/schema/page-format.md` before starting.**
High-level: read source → write source page → update index/overview → archive existing pages → create/update entity+concept+atom cards → update log → validate → **rebuild graph + browser**.
Finish with: `python tools/build_graph.py --no-infer && python tools/build_browser.py` (fast path), or a full `/wiki-graph` for semantic inference.
**Note**: A PostToolUse hook in `.claude/settings.json` can automatically run graph+browser rebuild after every wiki file write/edit. Manual build is still needed when only raw source files or bilingual content changes (hook only triggers on `wiki/` path edits).

### Query
Triggered by: *"query: <question>"* or `/wiki-query`
High-level: read index → read relevant pages → synthesize answer with `[[wikilink]]` citations → offer to save.

### Synthesis
Triggered by: *"synthesize [[PageName]]"* or *"synthesize 'theme' from [[Card1]], [[Card2]]"* or `/wiki-synthesis`
High-level: collect related cards → choose grouping dimension → extract verbatim fact sentences → write synthesis page → update index + log.

### Health
Triggered by: *"health"* or `/wiki-health`
Run: `python tools/health.py` — zero LLM calls, safe every session.
Checks: empty/stub pages, frontmatter integrity, index sync, log coverage, broken wikilinks, missing relations sections, raw source files missing `published` date.

### Lint
Triggered by: *"lint the wiki"* or `/wiki-lint`
Run: `python tools/lint.py` — uses LLM, run every 10-15 ingests.

### Graph
Triggered by: *"build the knowledge graph"* or `/wiki-graph`
Run: `python tools/build_graph.py` — outputs `graph/graph.json` + `graph/graph.html`.
Appends to `changelog.md` (not `wiki/log.md`).
**Auto-build**: A PostToolUse hook can trigger graph+browser rebuild after every wiki file change. The `--no-infer` flag is used in auto-build mode for speed; the full build with semantic inference requires manual `/wiki-graph`.

### Build Browser
Triggered by: *"build the browser"* or `python tools/build_browser.py`
Generates `browser/data.js` from graph data for the card browser web app.
