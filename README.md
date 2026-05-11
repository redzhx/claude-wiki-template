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

## Quick Start

1. **Use this template** — click "Use this template" on GitHub, or fork it
2. **Open in Claude Code** — `claude` in the project root
3. **Drop a source** — put a document in `raw/` (Markdown, PDF, DOCX, etc.)
4. **Ingest** — say `ingest raw/my-article.md`
5. **Query** — ask `query: what are the key insights?`
6. **Visualize** — say `build the knowledge graph`

## Prerequisites

```bash
pip install -r requirements.txt
```

Optional for PDF conversion:
```bash
pip install arxiv2markdown marker-pdf pymupdf4llm
```

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

## Workflows

| Command | What it does |
|---------|-------------|
| `ingest <file>` | Extract knowledge from a source into wiki cards |
| `query: <question>` | Answer questions from the knowledge base |
| `synthesize [[Card]]` | Create structured multi-card synthesis |
| `health` | Fast structural checks (run every session) |
| `lint the wiki` | Deep content quality analysis |
| `build the knowledge graph` | Generate interactive graph visualization |

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
