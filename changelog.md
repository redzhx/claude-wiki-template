# Changelog

All project-level changes (graph rebuilds, tool updates, infrastructure changes) are recorded here in reverse chronological order.

## [2026-05-19] feat | Multi-source contribution rule in card-types.md

### Added
- **多源贡献规则章节** — 在 `card-types.md` 模板与提取指南之间新增独立章节，规定当卡片有 2+ 来源时需在 `## 关联` 前添加 `## 来源贡献`，写明每个来源的贡献内容

## [2026-05-19] fix | Detail panel layout on wide screens

### Fixed
- **宽屏详情页内容偏右**：将 `#panel-body-wrapper` 从居中布局改为左对齐（`justify-content: flex-start`）+ 64px 左内边距，body 与 sidebar 之间增加 24px 间距

## [2026-05-14] sync | Backport improvements from ai-observatory project

Synced all generic improvements from the active project back to the template.

### Added
- **Bilingual reading workflow** — new `/wiki-bilingual` command (`.claude/commands/wiki-bilingual.md`), directory layout and CLAUDE.md documentation
- **Card browser** — `browser/index.html` static web app, `tools/build_browser.py` for data generation, config in `tools/config.yaml`
- **Controversy detection** — 6-point quality checklist in Ingest workflow (preprint, small sample, COI, limitations, speculation, replication)
- **Post-ingest validation** — 3 mandatory sub-checks: broken outgoing links, index sync, bilingual link verification
- **Filename normalization** — `tools/normalize_filenames.py`
- **Type definition pages** — `wiki/types/` now has all 17 type/card_type definition pages
- `changelog.md` — project-level change tracking (graph rebuilds, tool updates)

### Enhanced
- **CLAUDE.md** — H1 title language rules, development conventions (Python env, source path validation, auto-build hook, bilingual filenames), detailed workflow summaries with Build Browser entry
- **settings.json** — PostToolUse hook auto-rebuilds graph+browser after wiki file edits
- **card-types.md** — narrative source extraction guide, action card detection beyond numbered steps, event card `## 概述` section, quote floor rule (3+ key quotes → at least one quote card), index card Timeline Variant, extraction checklist step 9 for narrative sources
- **workflows.md** — ingest step 0 (filename normalization), source_file validation + subdirectory convention, narrative-specific extraction in top-down framework, enhanced quote extraction density check, enhanced source page format with `## 争议标注` and `## 分析` sections, Graph Build Conventions (raw discovery, matching, display substitution, image rewriting)
- **wiki-ingest.md** — added validation steps, narrative source extraction guidance, bilingual detection, graph+browser rebuild
- **wiki-graph.md** — `--browser`/`--no-infer` flags, append to `changelog.md`
- **tools/build_graph.py** — raw source scanning, bilingual display substitution, image path rewriting, source_url extraction, enhanced frontmatter parsing
- **tools/health.py** — single-file outgoing link check, source file path validation, archive integrity check
- **tools/lint.py** — self-contradiction detection, suspicious assertions, changelog.md support
- **tools/config.yaml** — changelog_file, browser_dir/browser_data, browser config, density targets for policy/report

