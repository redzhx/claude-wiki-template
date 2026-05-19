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

**Browser display**: When the `title` is in one language and `aliases` contains a translation in another script, the card browser automatically renders `"Original (Translation)"` bilingual titles. Always include a translation in `aliases` for cross-language content.

---

## Domain Context

<!-- CONFIGURABLE: Define what your wiki tracks. This section helps Claude understand the scope
     when reading, querying, and synthesizing content. Each domain anchors on a dimension
     of the subject being tracked. -->

| Domain | Tracking |
|--------|----------|
| Domain 1 | Sub-topics to track |
| Domain 2 | Sub-topics to track |
| Domain 3 | Sub-topics to track |

When ingesting, tag pages with the most specific domain tags available (see domain taxonomy in `.claude/schema/page-format.md`).

---

## Slash Commands

| Command | What to say |
|---|---|
| `/wiki-ingest` | `ingest raw/my-article.md` |
| `/wiki-query` | `query: what are the main themes?` |
| `/wiki-synthesis` | `synthesize [[PageName]]` or `synthesize "theme" from [[Card1]], [[Card2]]` |
| `/wiki-health` | `health` (fast, every session) |
| `/wiki-lint` | `lint the wiki` (expensive, periodic) |
| `/wiki-bilingual` | `bilingual raw/article-foo.md` |

Or just describe what you want in plain language.

---

## Bilingual Reading

Create bilingual (native/primary language + original) versions of source files for personal reading. Bilingual files live in `raw/bilingual/` and are **never ingested** into the wiki — they are reading aids only.

### Translation Principles

- Paragraph-level translation, preserving original paragraph boundaries
- Technical terms preserved in original language
- Markdown formatting (bold, italic, links, lists) preserved
- Section headers rendered bilingually: `## English / Translation`
- Code blocks and images preserved verbatim

### Bilingual File Format

Bilingual files are named `<original-stem>-bilingual.md`. Pure native language versions use `-<lang>.md` suffix (e.g., `-zh.md` for Chinese). See `.claude/commands/wiki-bilingual.md` for full specification. Key elements:
- YAML frontmatter with `original`, `original_url`, `skip_ingest: true`
- Bilingual H1
- Body: translated paragraph (normal text) followed by `> original` (blockquote)
- Link back to original in header blockquote

### Link Strategy

Original files get a bidirectional link to their bilingual version:
- `raw/` files: `> 📖 [Bilingual Version](bilingual/<name>-bilingual.md)` appended at bottom

### Browser Display

`build_browser.py` reads wiki files directly and generates the card browser.

**Source pages** (`wiki/sources/`): Summary only. Links to the full bilingual/original text point to standalone `raw_source` cards for reading. Wiki pages form the knowledge graph with edges from wikilinks.

**Raw source library** (`type: raw_source`): Standalone cards for every `raw/*.md` file. No graph edges — these are a browsable library sorted by date/type. Content uses bilingual > native > original preference. Each card links to its `sources/X` summary page. Filter by type via the "📰 原文" sidebar button.

Content is sharded: `browser/data.js` contains metadata only (labels, previews, connections — everything needed for the card grid). Full markdown is stored in two tiers:
- `browser/content/bundle.json` — combined JSON object `{nodeId: markdown}` for fast bulk loading (~2-3MB, gzipped ~500KB)
- `browser/content/<id-slug>.json` — individual per-node shards as fallback (loaded individually when bundle misses)

The browser loads `bundle.json` once after page init, making all subsequent card selections instant.

- `python tools/build_browser.py` rebuilds the browser
- `/wiki-bilingual`: runs `build_browser.py` automatically at the end
- Every ingest or card change should be followed by a browser rebuild to appear in the browser (auto-build hook handles this)

---

## Directory Layout

```
raw/          # Source documents: papers, articles, books, reports, etc.
              # Each file gets a raw_source card in the browser (sorted library view)
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
  archive/    # Versioned snapshots of updated pages (mirrors wiki subdirs, excluded from graph)
browser/      # Card browser web app (static, filterable)
  index.html  # Main card browser — open in browser to explore
  data.js     # Node metadata + edges (auto-generated, no markdown body)
  content/    # Per-node markdown shards (wiki + raw_source, auto-generated, lazy-loaded by browser)
changelog.md  # Project-level changes (not wiki content)
tools/        # Standalone Python scripts
  build_browser.py # Card browser data generation (reads wiki directly)
  build_graph.py  # [DEPRECATED] Knowledge graph generation + vis.js visualization
  health.py       # Structural checks (deterministic, no LLM calls)
  lint.py         # Content quality checks (uses LLM for semantic analysis)
.claude/schema/   # Claude Code workflow specs (not wiki content)
  card-types.md   # 11 card type templates + extraction guidelines
  page-format.md  # Frontmatter, relations format, domain tags, index/log format
  workflows.md    # Full workflow steps for ingest/query/synthesis/lint/health
```

<!-- CONFIGURABLE: Rename subdirectories and card types to match your own system.
     The 11 card types (based on 卡片大法) are the default preset. -->

---

## Naming Conventions

### Raw Source Files

Format: `<type-prefix>[-year]-<short-description>.md`

| Type | Prefix | Date in filename? | Example |
|------|--------|-------------------|---------|
| Academic Paper | `paper` | Year required | `paper-2025-gpt4-technical-report.md` |
| Article / Blog | `article` | No | `article-example-topic.md` |
| Book / Chapter | `book` | No | `book-example-ch03-deliberate-practice.md` |
| Industry Report | `report` | No | `report-organization-title.md` |
| Policy Document | `policy` | No | `policy-eu-regulation.md` |
| Think Tank Output | `thinktank` | No | `thinktank-org-statement.md` |

<!-- CONFIGURABLE: Add/remove source types as needed for your wiki's domain.
     Common additional types: lecture, whitepaper, tutorial, case-study -->

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
- A mismatch causes `build_browser.py` to fail silently when merging full-text content into source nodes.

### Auto-Build Hook
- `.claude/settings.json` has a PostToolUse hook that auto-runs `build_browser.py` after every Write/Edit to files under `wiki/`.
- This makes browser rebuild automatic after wiki edits, card creation, and ingests. Non-wiki edits (tools, raw sources, config) do NOT trigger the hook.

### Bilingual Filename Normalization
- Raw filenames may contain spaces (e.g., `paper-2026-Title With Spaces-1234.md`); bilingual filenames always use hyphens (`paper-2026-Title-With-Spaces-1234-bilingual.md`).
- `build_browser.py` has a `bilingual_path_for()` function that normalizes spaces→hyphens and checks for both `-<lang>.md` and `-bilingual.md` suffixes (`-<lang>` takes priority). Any new tool that looks up bilingual files must apply the same normalization.
- arXiv filenames may have a version suffix (e.g., `2602.20014v1`). The `bilingual_path_for()` fallback strips `.v1`/`.v2` so version and versionless stem lookups both work.
- Nested raw files (e.g., `raw/report-v1/report.md`) are looked up by basename only in `raw/bilingual/` — the flat directory structure means `raw/report-v1/report.md` finds `raw/bilingual/report-<lang>.md`.

---

## Deployment

The card browser is deployed as a static site on **Cloudflare Pages** at the project's custom domain.

### Key Facts

| Item | Detail |
|---|---|
| **Platform** | Cloudflare Pages (free tier) |
| **Private repo** | Supported (GitHub Pages requires public repos) |
| **Custom domain** | Subdomain of the project's domain (e.g., `project.your-domain.com`) |
| **Build output** | `browser/` directory (fully static, no build step on CI) |
| **Auto-deploy** | On push to production branch |
| **SSL** | Auto-provisioned and auto-renewed by Cloudflare |
| **ICP备案** | Not required with Cloudflare infrastructure |

### Build Lifecycle

1. `python tools/build_browser.py` generates all browser files locally:
   - `browser/data.js` — metadata + edges
   - `browser/content/*.json` — individual markdown shards
   - `browser/content/bundle.json` — combined bundle for fast loading
2. The PostToolUse hook auto-runs the build after every wiki edit
3. Cloudflare Pages auto-deploys when changes are pushed to the repo

### SEO & Privacy

- `browser/index.html` includes `<meta name="robots" content="noindex, nofollow">` to prevent search engine indexing
- `browser/robots.txt` has `Disallow: /` for all crawlers

### Performance Optimizations

- **Bundle loading**: `bundle.json` (~2-3MB, gzipped ~500KB) loaded once after init — eliminates per-card HTTP round-trips
- **Security**: All external links get `rel="noopener noreferrer"` to prevent tab-napping and referer leakage
- **Mobile responsive**: Panel switches to full-screen overlay at ≤860px viewport width

Full workflow details in `.claude/schema/workflows.md`.

---

## Workflows (Summary)

Full steps for each workflow are in `.claude/schema/workflows.md`. Read it before executing.

### Ingest
Triggered by: *"ingest <file>"* or `/wiki-ingest`
**Read `.claude/schema/card-types.md` and `.claude/schema/page-format.md` before starting.**
High-level: read source → write source page → update index/overview → archive existing pages → create/update entity+concept+atom cards → **add `## 来源贡献` for multi-source cards** → update log → validate → **rebuild browser**.
Finish with: `python tools/build_browser.py`.
**Note**: A PostToolUse hook in `.claude/settings.json` automatically runs `build_browser.py` after every wiki file write/edit. Manual build is still needed when only raw source files or bilingual content changes (hook only triggers on `wiki/` path edits).

### Query
Triggered by: *"query: <question>"* or `/wiki-query`
High-level: read index → read relevant pages → synthesize answer with `[[wikilink]]` citations → offer to save.

### Synthesis
Triggered by: *"synthesize [[PageName]]"* or *"synthesize 'theme' from [[Card1]], [[Card2]]"* or `/wiki-synthesis`
High-level: collect related cards → choose grouping dimension → extract verbatim fact sentences → write synthesis page → update index + log.

### Health
Triggered by: *"health"* or `/wiki-health`
Run: `python tools/health.py` — zero LLM calls, safe every session.
Checks: empty/stub pages, frontmatter integrity, index sync, log coverage, broken wikilinks, missing relations sections, **raw source files missing `published` date**.

### Lint
Triggered by: *"lint the wiki"* or `/wiki-lint`
Run: `python tools/lint.py` — uses LLM, run every 10-15 ingests.

### Build Browser
Triggered by: *"build the browser"* or `python tools/build_browser.py`
Reads wiki files directly, generates `browser/data.js` (metadata + edges) and `browser/content/*.json` (per-node markdown shards). Raw source files get standalone `raw_source` cards accessible from source page links.
**Auto-build**: A PostToolUse hook triggers browser rebuild after every wiki file change.
