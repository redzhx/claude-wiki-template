# Customization Guide

This template is designed to be customized for your own knowledge domain.

## Quick Customization

### 1. Card Types

The default 11 card types come from Yang Zhiping's Card Method (卡片大法). To customize:

1. Edit `.claude/schema/card-types.md` — rename, add, or remove card types
2. Edit `.claude/schema/page-format.md` — update type names and directory mappings
3. Edit `tools/config.yaml` — update `valid_types`, `valid_card_types`, `type_display_names`
4. Update `wiki/types/` — create definition pages for your new types
5. Update `CLAUDE.md` — adjust directory layout descriptions

### 2. Domain Tags

Edit the domain tag taxonomy in `.claude/schema/page-format.md` (Domain Tags section) and ensure tags match your field.

### 3. Directory Names

If you rename wiki subdirectories:
1. Update `CLAUDE.md` directory layout
2. Update `tools/config.yaml` — `wiki_dir`, `excluded_dirs`, `relation_required_dirs`, `card_dirs`
3. Update `.claude/schema/page-format.md` — type-to-directory mapping
4. Rename the actual directories

### 4. Language

See [LANGUAGE.md](LANGUAGE.md) for full language adaptation guide. Quick steps:
- Translate section headers in `.claude/schema/` files
- Update `CLAUDE.md` output language rules
- Update `type_display_names` in `tools/config.yaml`

### 5. Frontmatter Schema

If you need different required fields, edit `tools/config.yaml`:
- `required_fields_all` — fields required on every page
- `required_fields_card` — additional fields for entity/concept/atom pages

### 6. Graph Colors

Edit `type_colors` and `card_type_colors` in `tools/config.yaml`.

### 7. LLM Configuration

Edit `llm` section in `tools/config.yaml`:
- `model_env` — environment variable for model selection
- `default_model` — fallback model
- `max_tokens` — default token limit

### 8. Extraction Density

Edit `density_targets` in `tools/config.yaml` to match your desired extraction thoroughness.

## Tool Configuration

All Python tools read from `tools/config.yaml` via `tools/config_loader.py`. The config loader provides sensible defaults if the YAML file is missing, but installing `pyyaml` and maintaining the config file is recommended.

### Tools that use config

| Tool | Config keys used |
|------|-----------------|
| `health.py` | wiki_dir, excluded_dirs, excluded_files, relation_required_dirs, stub_threshold_chars, required_fields_*, card_dirs, valid_*, type_display_names, relations_header |
| `lint.py` | wiki_dir, excluded_dirs, excluded_files, lint.*, llm.*, relations_header |
| `build_graph.py` | wiki_dir, graph_dir, type_colors, card_type_colors, llm.* |
