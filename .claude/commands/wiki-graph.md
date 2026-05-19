Build the wiki knowledge graph [DEPRECATED].

This command is deprecated. Use `build_browser.py` instead, which includes all graph edge functionality directly without the intermediate `graph/graph.json` file.

Usage: /wiki-graph

For backward compatibility only:
  python tools/build_graph.py

## Recommended: Build the Card Browser Instead

The card browser (`browser/index.html`) includes full graph functionality:
- Parses all `[[wikilinks]]` → deterministic graph edges (no intermediate JSON file)
- Generates node metadata, previews, and connection data
- Outputs `browser/data.js` + `browser/content/` markdown shards
- Excludes `wiki/archive/` and `wiki/types/`

To build the browser:
```bash
python tools/build_browser.py
```

This script:
- Reads wiki files directly (no `graph.json` dependency)
- Builds complete edge graph from `[[wikilinks]]`
- Generates content bundle for instant card loading
- Creates standalone `raw_source` cards for every source file

## Auto-Build Hook

The PostToolUse hook in `.claude/settings.json` automatically runs `build_browser.py` after every wiki file edit, so manual rebuilds are rarely needed.

---

## Legacy Graph Build (Deprecated)

`build_graph.py` is preserved for backward compatibility but no longer actively maintained:

```bash
python tools/build_graph.py              # Full build with semantic inference
python tools/build_graph.py --no-infer   # Skip semantic inference for speed
python tools/build_graph.py --browser    # Build graph + browser data in one command
```

Legacy output: `graph/graph.json` + `graph/graph.html`
