# Claude Wiki Template

A Claude Code-powered personal wiki template. Drop source documents into `raw/`, tell Claude to ingest them, and get a structured, interlinked knowledge base with health checks, linting, and an interactive knowledge graph — all maintained by AI.

## Features

- **Schema-driven card types** — 11 card types (terminology, insight, action, schema, person, event, quote, new-word, index-card, basic, synthesis) with templates and self-validation rules
- **6 automated workflows** — Ingest, Query, Synthesis, Health, Lint, Graph
- **Knowledge graph** — Extracted + inferred edges, Louvain community detection, interactive vis.js visualization
- **Health checks** — Deterministic structural validation (zero LLM calls)
- **Lint checks** — LLM-powered content quality analysis (contradictions, gaps, stale content)
- **Multi-agent support** — `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` for Claude Code, Codex/OpenCode, and Gemini CLI
- **Configurable** — Card types, domain tags, language, colors all configurable via `tools/config.yaml`

## Prerequisites

```bash
pip install -r requirements.txt
```

Optional for PDF conversion:
```bash
pip install arxiv2markdown marker-pdf pymupdf4llm
```

## Getting Started

### Create a new project from this template

**Option 1: GitHub "Use this template" (recommended)**

1. Click the green **"Use this template"** button → **"Create a new repository"**
2. Name your repo, create it
3. `git clone` to your local machine

**Option 2: Manual copy**

```bash
git clone git@github.com:redzhx/claude-wiki-template.git my-project
cd my-project
rm -rf .git && git init && git add -A && git commit -m "init"
```

### Minimal configuration (5 minutes)

1. **Language** — if your wiki is non-English, read `docs/LANGUAGE.md` and update `CLAUDE.md` with your language rules. Update `type_display_names` in `tools/config.yaml`.
2. **Domain tags** — edit the domain tag taxonomy in `.claude/schema/page-format.md` to match your field.
3. **Drop a source** — put a document in `raw/` (Markdown, PDF, DOCX, etc.)
4. **Ingest** — open Claude Code and say `ingest raw/your-file.md`
5. **Query** — ask `query: what are the key insights?`

### Deep customization

If you want to change card types (add, remove, rename the 11 built-in types), follow the step-by-step guide in `docs/CUSTOMIZATION.md`.

## Directory Layout

```
raw/          # Your source documents — never modified by AI
wiki/         # AI-maintained knowledge layer
  index.md    # Catalog of all pages
  log.md      # Chronological operation log
  overview.md # Living cross-source synthesis
  sources/    # One summary per source document
  entities/   # People, events
  concepts/   # Terminology, insight, action, schema, etc.
  atoms/      # Quotes, new words
  syntheses/  # Multi-card structured analysis
  query/      # Saved Q&A
  types/      # Type definitions
  archive/    # Versioned page snapshots
graph/        # Auto-generated knowledge graph
tools/        # Python scripts (health, lint, graph, ingest, etc.)
.claude/      # Claude Code schema, commands, and settings
```

## Daily Use

Just talk to Claude Code in your project root. No API keys or scripts needed — Claude reads the schema files and follows the workflows.

| You say | What happens |
|---|---|
| `ingest raw/some-file.md` | Extract knowledge cards from a source document |
| `query: what are the main themes?` | Answer questions grounded in your knowledge base |
| `synthesize [[Card]]` | Create a structured multi-card synthesis |
| `health` | Fast structural integrity check (run every session, zero LLM cost) |
| `lint the wiki` | Deep content quality analysis — contradictions, gaps, stale pages |
| `build the knowledge graph` | Generate interactive vis.js knowledge graph (`graph/graph.html`) |

## Customization

See [docs/CUSTOMIZATION.md](docs/CUSTOMIZATION.md) for:
- Changing card types
- Customizing domain tags
- Adjusting extraction density targets
- Configuring colors and LLM models

See [docs/LANGUAGE.md](docs/LANGUAGE.md) for adapting to non-English wikis.

## Contributing

Improvements to the template infrastructure are welcome. See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## License

MIT
