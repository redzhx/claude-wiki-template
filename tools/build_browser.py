#!/usr/bin/env python3
"""Build the card browser data file from the knowledge graph.

Usage:
    python tools/build_browser.py              # Generate browser data
    python tools/build_browser.py --open       # Open browser in default browser

This script ensures:
1. graph/graph.json exists (runs build_graph.py if needed)
2. browser/data.js is generated (enriched data bundle for the card browser)
"""

from __future__ import annotations

import json
import re
import webbrowser
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).parent.parent
GRAPH_JSON = REPO_ROOT / "graph" / "graph.json"
BROWSER_DIR = REPO_ROOT / "browser"
WIKI_ARCHIVE = REPO_ROOT / "wiki" / "archive"

# Regex to match archive filenames: <Name>-V<version>.md
ARCHIVE_RE = re.compile(r"^(.+)-V(\d+)\.md$")


def ensure_graph_json() -> bool:
    """Check if graph.json exists, print instructions if not."""
    if GRAPH_JSON.exists():
        return True
    print("graph/graph.json not found. Run 'python tools/build_graph.py' first.")
    print("Or ask Claude Code: 'build the knowledge graph'")
    return False


def bilingual_path_for(node_id: str) -> Path | None:
    """Return the bilingual/zh file path for a raw node if it exists, else None.

    Checks for these suffixes in order (first found wins):
    - -zh.md (pure Chinese translation, highest priority)
    - -bilingual.md (bilingual English+Chinese, existing convention)

    Uses only the basename (last path component) for flat lookup in raw/bilingual/,
    so raw files in subdirectories (e.g. raw/report-v1/report.md) still find
    their bilingual counterpart at raw/bilingual/report-zh.md.
    """
    if not node_id.startswith("raw/") or "->" in node_id:
        return None
    stem = node_id[len("raw/"):].replace(" ", "-")
    # Use only the filename part for flat bilingual directory lookup
    stem = stem.rsplit("/", 1)[-1]
    for suffix in ("-zh", "-bilingual"):
        bilingual = REPO_ROOT / "raw" / "bilingual" / f"{stem}{suffix}.md"
        if bilingual.exists():
            return bilingual
    # Fallback: try removing arXiv version suffix (e.g. .20014v1)
    if stem.count(".") == 1:
        base = stem.rsplit(".", 1)[0]
        for suffix in ("-zh", "-bilingual"):
            bilingual = REPO_ROOT / "raw" / "bilingual" / f"{base}{suffix}.md"
            if bilingual.exists():
                return bilingual
    return None


def _parse_frontmatter_date(markdown: str) -> str | None:
    """Parse the 'updated' date from YAML frontmatter, or fall back to 'created'.

    Scans all frontmatter lines, preferring 'updated' over 'created'
    (since 'updated' may come after 'created' in the YAML).
    """
    if not markdown.startswith("---"):
        return None
    end = markdown.find("---", 3)
    if end == -1:
        return None
    updated = None
    created = None
    for line in markdown[3:end].splitlines():
        line = line.strip()
        if line.startswith("updated:"):
            val = line[len("updated:"):].strip().strip('"').strip("'")
            if val:
                updated = val
        if line.startswith("created:"):
            val = line[len("created:"):].strip().strip('"').strip("'")
            if val:
                created = val
    return updated or created


def archives_for_wiki_path(wiki_path: str) -> list[dict] | None:
    """Return sorted archive version dicts for a wiki page, newest first.

    Matches wiki/archive/<stem>-V<N>.md against the page's filename stem.
    Returns None if no archives found.
    """
    if not wiki_path.startswith("wiki/") or not WIKI_ARCHIVE.is_dir():
        return None
    p = Path(wiki_path)
    stem = p.stem  # e.g. "DarioAmodei" from "wiki/entities/DarioAmodei.md"
    results = []
    for f in WIKI_ARCHIVE.iterdir():
        if not f.is_file() or f.suffix != ".md":
            continue
        m = ARCHIVE_RE.match(f.name)
        if m and m.group(1) == stem:
            try:
                version = int(m.group(2))
            except ValueError:
                continue
            content = f.read_text(encoding="utf-8")
            # Parse updated date from frontmatter
            date = _parse_frontmatter_date(content)
            results.append({
                "version": version,
                "filename": f.name,
                "markdown": content,
                "updated": date,
            })
    if not results:
        return None
    results.sort(key=lambda x: x["version"], reverse=True)
    return results


def build_browser_data():
    """Generate enriched browser data from graph.json.

    For raw source nodes, if a bilingual version exists at
    raw/bilingual/<stem>-bilingual.md, its content replaces the
    node's markdown field so the browser shows the bilingual text.
    This makes bilingual updates independent of build_graph.py.
    """
    if not ensure_graph_json():
        return False

    graph_data = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    # Substitute bilingual content for raw nodes that have bilingual files
    bilingual_count = 0
    for node in nodes:
        node_id = node.get("id", "")
        bilingual = bilingual_path_for(node_id)
        if bilingual:
            node["markdown"] = bilingual.read_text(encoding="utf-8")
            bilingual_count += 1
    if bilingual_count:
        print(f"Bilingual substitution: {bilingual_count} raw node(s) updated")

    # Attach archive versions to wiki nodes
    archive_count = 0
    for node in nodes:
        wiki_path = node.get("path", "")
        archives = archives_for_wiki_path(wiki_path)
        if archives:
            node["archives"] = archives
            archive_count += 1
    if archive_count:
        print(f"Archive versions attached: {archive_count} node(s)")

    # Build adjacency map for quick lookups
    adjacency = {}
    for edge in edges:
        src = edge.get("from", "")
        tgt = edge.get("to", "")
        if src not in adjacency:
            adjacency[src] = []
        if tgt not in adjacency:
            adjacency[tgt] = []
        adjacency[src].append({"to": tgt, "type": edge.get("type", ""), "title": edge.get("title", "")})
        adjacency[tgt].append({"to": src, "type": edge.get("type", ""), "title": edge.get("title", "")})

    enriched = []
    for node in nodes:
        node_id = node.get("id", "")
        enriched.append({
            **node,
            "connections": adjacency.get(node_id, []),
            "connection_count": len(adjacency.get(node_id, [])),
        })

    # Build summary stats
    types = {}
    card_types = {}
    all_tags = {}
    for node in enriched:
        t = node.get("type", "unknown")
        types[t] = types.get(t, 0) + 1
        ct = node.get("card_type", "")
        if ct:
            card_types[ct] = card_types.get(ct, 0) + 1

    summary = {
        "total_nodes": len(enriched),
        "total_edges": len(edges),
        "types": types,
        "card_types": card_types,
        "built": date.today().isoformat(),
    }

    # Write browser data
    browser_data = {
        "summary": summary,
        "nodes": enriched,
        "edges": edges,
    }

    BROWSER_DIR.mkdir(parents=True, exist_ok=True)
    data_json = json.dumps(browser_data, separators=(',', ':'), ensure_ascii=False)
    data_script = (
        f"<!-- Auto-generated by build_browser.py — {date.today().isoformat()} -->\n"
        f"<script>\n"
        f"window.__BROWSER_DATA__ = {data_json};\n"
        f"</script>\n"
    )

    index_path = BROWSER_DIR / "index.html"
    index_html = index_path.read_text(encoding="utf-8")
    # Strip any previous inline data blocks so only the latest remains
    index_html = re.sub(
        r"<!-- Auto-generated by build_browser\.py.*?\n</script>\n",
        "", index_html, flags=re.DOTALL,
    )

    marker = "<!-- Lightbox -->"
    if marker in index_html:
        index_html = index_html.replace(marker, f"{data_script}\n{marker}", 1)
        index_path.write_text(index_html, encoding="utf-8")
        print(f"Inline data in browser/index.html ({len(enriched)} nodes, {len(edges)} edges)")
    else:
        data_js_path = BROWSER_DIR / "data.js"
        data_js_path.write_text(f"window.__BROWSER_DATA__ = {data_json};\n", encoding="utf-8")
        print(f"Generated: browser/data.js ({len(enriched)} nodes, {len(edges)} edges)")

    # Print summary
    print(f"\nBrowser Summary:")
    print(f"  Nodes: {len(enriched)}")
    print(f"  Edges: {len(edges)}")
    print(f"  Types: {types}")
    print(f"  Card Types: {card_types}")
    print(f"  Open: browser/index.html")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build card browser data")
    parser.add_argument("--open", action="store_true", help="Open browser in default browser")
    args = parser.parse_args()

    ok = build_browser_data()
    if ok and args.open:
        index_path = BROWSER_DIR / "index.html"
        webbrowser.open(f"file://{index_path.resolve()}")


if __name__ == "__main__":
    main()
