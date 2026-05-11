# Contributing

This template is designed for bi-directional improvement: the template benefits from improvements made in downstream projects, and downstream projects benefit from upstream template updates.

## How to Contribute

### Bug Fixes
- Fix the bug in your project fork
- Open a PR against this template repo with the fix
- Describe the problem and how your fix addresses it

### Workflow Improvements
- If you improve an ingest/lint/health/graph workflow, extract the generic part
- Ensure it works with the default template configuration
- Open a PR with a clear description of the improvement

### New Card Types or Patterns
- If you develop a new card type or extraction pattern that's generally useful
- Add it behind a `<!-- CONFIGURABLE -->` marker
- Document it in the card-types.md file

### Tool Improvements
- Improvements to `health.py`, `lint.py`, `build_graph.py` are welcome
- Ensure they read from `config.yaml` for parameterization
- Keep the tools zero-assumption about wiki content

## Guidelines

- **Keep it generic** — contributions should work for any knowledge domain
- **Config-driven** — new features should be configurable via `tools/config.yaml`
- **English base** — schema files and tool UI should default to English; language-specific content goes in `<!-- CONFIGURABLE -->` markers
- **Document** — update relevant docs when adding features

## Versioning

The template uses semantic versioning:
- **Major**: breaking changes to wiki format or tool APIs
- **Minor**: new features, new card types, workflow improvements
- **Patch**: bug fixes, documentation

## Relationship to Downstream Projects

This template is the canonical source for the wiki infrastructure. Projects built on it (like Cognitive Atlas) are downstream consumers. When you improve the infrastructure in your project, consider upstreaming the generic part back here.
