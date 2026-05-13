#!/usr/bin/env python3
from __future__ import annotations

"""
Lint the wiki for content quality issues.

Usage:
    python tools/lint.py
    python tools/lint.py --save          # save lint report to wiki/lint-report.md

Checks:
  - Orphan pages (no inbound wikilinks from other pages)
  - Broken wikilinks (pointing to pages that don't exist)
  - Missing entity pages (entities mentioned in 3+ pages but no page)
  - Sparse pages (low outbound link density)
  - Graph-aware: hub stubs, fragile bridges, isolated communities
  - Semantic (LLM): contradictions, stale content, data gaps
"""

import re
import sys
import json
import argparse
import statistics
from pathlib import Path
from collections import defaultdict
from datetime import date
import os

from config_loader import (
    wiki_dir, index_file, log_file, changelog_file, graph_json as graph_json_path,
    excluded_dirs, excluded_files, relations_header,
    lint_min_outbound, lint_hub_min_chars, lint_missing_entity_min,
    lint_sample_size, lint_truncate_chars,
    llm_model_env, llm_default_model, llm_max_tokens,
)

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = wiki_dir()
GRAPH_JSON = graph_json_path()
CHANGELOG_FILE = changelog_file()


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def call_llm(prompt: str, max_tokens: int | None = None) -> str:
    try:
        from litellm import completion
    except ImportError:
        print("Error: litellm not installed. Run: pip install litellm")
        sys.exit(1)

    model = os.getenv(llm_model_env(), llm_default_model())
    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens or llm_max_tokens(),
    )
    return response.choices[0].message.content


def all_wiki_pages() -> list[Path]:
    """All .md content pages in wiki/, excluding meta/archive/types."""
    ex_dirs = excluded_dirs()
    ex_files = excluded_files()
    pages = []
    for p in WIKI_DIR.rglob("*.md"):
        if p.name in ex_files:
            continue
        rel = p.relative_to(WIKI_DIR)
        if len(rel.parts) > 1 and rel.parts[0] in ex_dirs:
            continue
        pages.append(p)
    return pages


def extract_wikilinks(content: str) -> list[str]:
    """Extract wikilink targets, handling [[Target|display]] pipe aliases."""
    raw = re.findall(r'\[\[([^\]]+)\]\]', content)
    return [link.split("|")[0].strip() for link in raw]


def _all_page_stems() -> set[str]:
    """All .md file stems in wiki/ (including archive/types), for link validation."""
    return {p.stem.lower() for p in WIKI_DIR.rglob("*.md")}


def page_name_to_path(name: str, pages: list[Path] | None = None) -> list[Path]:
    """Try to resolve a [[WikiLink]] to a file path."""
    if pages is None:
        pages = all_wiki_pages()
    candidates = []
    lower_name = name.lower()
    for p in pages:
        if p.stem.lower() == lower_name:
            candidates.append(p)
    return candidates


def find_orphans(pages: list[Path]) -> list[Path]:
    inbound = defaultdict(int)
    for p in pages:
        content = read_file(p)
        for link in extract_wikilinks(content):
            resolved = page_name_to_path(link)
            for r in resolved:
                inbound[r] += 1
    return [p for p in pages if inbound[p] == 0]


def find_broken_links(pages: list[Path]) -> list[tuple[Path, str]]:
    broken = []
    all_stems = _all_page_stems()
    for p in pages:
        content = read_file(p)
        for link in extract_wikilinks(content):
            if link.lower() not in all_stems:
                broken.append((p, link))
    return broken


def find_missing_entities(pages: list[Path]) -> list[str]:
    """Find entity-like names mentioned in N+ pages but lacking their own page."""
    threshold = lint_missing_entity_min()
    mention_counts: dict[str, int] = defaultdict(int)
    existing_pages = _all_page_stems()
    for p in pages:
        content = read_file(p)
        links = extract_wikilinks(content)
        for link in links:
            if link.lower() not in existing_pages:
                mention_counts[link] += 1
    return [name for name, count in mention_counts.items() if count >= threshold]


def check_link_density(pages: list[Path]) -> list[dict]:
    """Find pages with fewer than min_outbound outgoing wikilinks."""
    min_out = lint_min_outbound()
    results = []
    for p in pages:
        content = read_file(p)
        links = extract_wikilinks(content)
        unique_links = set(link.lower() for link in links)
        if len(unique_links) < min_out:
            results.append({
                "path": str(p.relative_to(REPO_ROOT)),
                "outbound_links": len(unique_links),
                "links": sorted(unique_links),
            })
    results.sort(key=lambda x: x["outbound_links"])
    return results


# ── Graph-aware checks ──────────────────────────────────────────────

def load_graph_data() -> dict | None:
    """Load graph.json if it exists. Returns None if missing."""
    if not GRAPH_JSON.exists():
        return None
    try:
        return json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        print("  [warn] graph.json is corrupted — skipping graph-aware checks")
        return None


def _build_degree_map(graph_data: dict) -> dict[str, int]:
    degrees: dict[str, int] = {}
    for node in graph_data.get("nodes", []):
        degrees[node["id"]] = 0
    for edge in graph_data.get("edges", []):
        degrees[edge["from"]] = degrees.get(edge["from"], 0) + 1
        degrees[edge["to"]] = degrees.get(edge["to"], 0) + 1
    return degrees


def _build_community_map(graph_data: dict) -> dict[str, int]:
    return {
        node["id"]: node.get("group", -1)
        for node in graph_data.get("nodes", [])
    }


def check_hub_stubs(graph_data: dict, pages: list[Path]) -> list[dict]:
    """Find god nodes (degree > mean+2std) with suspiciously short content."""
    min_chars = lint_hub_min_chars()
    degrees = _build_degree_map(graph_data)
    deg_values = list(degrees.values())
    if len(deg_values) < 2:
        return []

    mean_deg = statistics.mean(deg_values)
    std_deg = statistics.stdev(deg_values)
    threshold = mean_deg + 2 * std_deg

    node_to_path: dict[str, Path] = {}
    for p in pages:
        nid = p.relative_to(WIKI_DIR).as_posix().replace(".md", "")
        node_to_path[nid] = p

    results = []
    for node_id, deg in degrees.items():
        if deg <= threshold:
            continue
        path = node_to_path.get(node_id)
        if not path:
            continue
        content_len = len(read_file(path))
        if content_len < min_chars:
            results.append({
                "node_id": node_id,
                "degree": deg,
                "content_len": content_len,
                "path": str(path.relative_to(REPO_ROOT)),
            })
    return sorted(results, key=lambda x: x["degree"], reverse=True)


def check_fragile_bridges(graph_data: dict) -> list[dict]:
    """Find community pairs connected by only 1 edge."""
    comm_map = _build_community_map(graph_data)
    cross_comm: dict[tuple[int, int], list[dict]] = {}

    for edge in graph_data.get("edges", []):
        ca = comm_map.get(edge["from"], -1)
        cb = comm_map.get(edge["to"], -1)
        if ca < 0 or cb < 0 or ca == cb:
            continue
        key = (min(ca, cb), max(ca, cb))
        cross_comm.setdefault(key, []).append(edge)

    return [
        {
            "comm_a": pair[0],
            "comm_b": pair[1],
            "bridge_from": edges[0]["from"],
            "bridge_to": edges[0]["to"],
        }
        for pair, edges in sorted(cross_comm.items())
        if len(edges) == 1
    ]


def check_isolated_communities(graph_data: dict) -> list[dict]:
    """Find communities with zero external edges (knowledge silos)."""
    comm_map = _build_community_map(graph_data)

    comm_members: dict[int, list[str]] = {}
    for node_id, comm_id in comm_map.items():
        if comm_id < 0:
            continue
        comm_members.setdefault(comm_id, []).append(node_id)

    has_external = set()
    for edge in graph_data.get("edges", []):
        ca = comm_map.get(edge["from"], -1)
        cb = comm_map.get(edge["to"], -1)
        if ca >= 0 and cb >= 0 and ca != cb:
            has_external.add(ca)
            has_external.add(cb)

    results = []
    for comm_id, members in sorted(comm_members.items()):
        if len(members) < 2:
            continue
        if comm_id not in has_external:
            results.append({
                "community_id": comm_id,
                "node_count": len(members),
                "members": members[:10],
            })
    return results


def run_lint():
    pages = all_wiki_pages()
    today = date.today().isoformat()

    if not pages:
        print("Wiki is empty. Nothing to lint.")
        return ""

    print(f"Linting {len(pages)} wiki pages...")

    # Deterministic checks
    orphans = find_orphans(pages)
    broken = find_broken_links(pages)
    missing_entities = find_missing_entities(pages)

    print(f"  orphans: {len(orphans)}")
    print(f"  broken links: {len(broken)}")
    print(f"  missing entity pages: {len(missing_entities)}")

    # Link density check
    sparse_pages = check_link_density(pages)
    print(f"  sparse pages (< {lint_min_outbound()} outbound links): {len(sparse_pages)}")

    # Graph-aware checks
    graph_data = load_graph_data()
    hub_stubs: list[dict] = []
    fragile_bridges: list[dict] = []
    isolated_comms: list[dict] = []

    if graph_data and graph_data.get("nodes") and graph_data.get("edges"):
        print("  running graph-aware checks...")
        hub_stubs = check_hub_stubs(graph_data, pages)
        fragile_bridges = check_fragile_bridges(graph_data)
        isolated_comms = check_isolated_communities(graph_data)
        print(f"    hub stubs: {len(hub_stubs)}")
        print(f"    fragile bridges: {len(fragile_bridges)}")
        print(f"    isolated communities: {len(isolated_comms)}")
    elif graph_data:
        print("  [skip] graph.json has no data — skipping graph-aware checks")
    else:
        print("  [skip] no graph.json — run build_graph.py first for graph-aware checks")

    # Semantic checks via LLM
    sample_size = lint_sample_size()
    sample = pages[:sample_size]
    truncate = lint_truncate_chars()
    pages_context = ""
    for p in sample:
        rel = p.relative_to(REPO_ROOT)
        pages_context += f"\n\n### {rel}\n{read_file(p)[:truncate]}"

    print("  running semantic lint via API...")
    prompt = f"""You are linting a wiki knowledge base. Review the pages below and identify:
1. Self-contradictions within a single page (claims that conflict with other claims or attributions in the SAME page — e.g. the attribution section says a quote is from Kant, but the commentary section says Kant never used it)
2. Strong assertions about named entities that are likely false (e.g. "X never did Y" when the page itself attributes Y to X; "X was the first to..." without evidence)
3. Contradictions between pages (claims that conflict across different pages)
4. Stale content (summaries that newer sources have superseded)
5. Data gaps (important questions the wiki can't answer — suggest specific sources to find)
6. Concepts mentioned but lacking depth

Wiki pages (sample of {len(sample)} pages):
{pages_context}

Return a markdown lint report with these sections:
## Self-Contradictions (Within Page)
## Suspicious Assertions
## Contradictions (Between Pages)
## Stale Content
## Data Gaps & Suggested Sources
## Concepts Needing More Depth

Be specific — name the exact pages and claims involved. For self-contradictions, quote both conflicting statements verbatim.
"""
    semantic_report = call_llm(prompt)

    # Compose full report
    rel_header = relations_header()
    report_lines = [
        f"# Wiki Lint Report — {today}",
        "",
        f"Scanned {len(pages)} pages.",
        "",
        "## Structural Issues",
        "",
    ]

    if orphans:
        report_lines.append("### Orphan Pages (no inbound links)")
        for p in orphans:
            report_lines.append(f"- `{p.relative_to(REPO_ROOT)}`")
        report_lines.append("")

    if broken:
        report_lines.append("### Broken Wikilinks")
        for page, link in broken:
            report_lines.append(f"- `{page.relative_to(REPO_ROOT)}` links to `[[{link}]]` — not found")
        report_lines.append("")

    if missing_entities:
        report_lines.append(f"### Missing Entity Pages (mentioned {lint_missing_entity_min()}+ times but no page)")
        for name in missing_entities:
            report_lines.append(f"- `[[{name}]]`")
        report_lines.append("")

    if not orphans and not broken and not missing_entities and not sparse_pages:
        report_lines.append("No structural issues found.")
        report_lines.append("")

    if sparse_pages:
        report_lines.append(f"### Sparse Pages — Low Outbound Link Density ({len(sparse_pages)} pages)")
        report_lines.append(f"These pages have fewer than {lint_min_outbound()} outbound wikilinks:")
        report_lines.append("")
        report_lines.append("| Page | Outbound Links | Existing Links |")
        report_lines.append("|---|---|---|")
        for sp in sparse_pages:
            existing = ", ".join(f"`[[{l}]]`" for l in sp["links"]) if sp["links"] else "—"
            report_lines.append(f"| `{sp['path']}` | {sp['outbound_links']} | {existing} |")
        report_lines.append("")

    # Graph-Aware Issues
    report_lines.append("## Graph-Aware Issues")
    report_lines.append("")

    if not graph_data:
        report_lines.append("> [!tip]")
        report_lines.append("> Graph-aware checks were skipped. Run `python tools/build_graph.py` first, then re-run lint.")
        report_lines.append("")
    elif not graph_data.get("nodes") or not graph_data.get("edges"):
        report_lines.append("> [!tip]")
        report_lines.append("> Graph data is empty. Ingest sources and run `python tools/build_graph.py` to populate.")
        report_lines.append("")
    else:
        report_lines.append(f"### Hub Pages with Insufficient Content ({len(hub_stubs)} pages)")
        if hub_stubs:
            report_lines.append("These hub nodes carry disproportionate connectivity but have thin content:")
            report_lines.append("")
            report_lines.append("| Page | Degree | Content Length | Status |")
            report_lines.append("|---|---|---|---|")
            for hs in hub_stubs:
                status = "STUB" if hs["content_len"] < 250 else "THIN"
                report_lines.append(f"| `{hs['path']}` | {hs['degree']} | {hs['content_len']} chars | {status} |")
        else:
            report_lines.append("No hub stubs detected.")
        report_lines.append("")

        report_lines.append(f"### Fragile Bridges ({len(fragile_bridges)} community pairs)")
        if fragile_bridges:
            report_lines.append("These community connections rely on a single edge:")
            for fb in fragile_bridges:
                report_lines.append(f"- Community {fb['comm_a']} <-> Community {fb['comm_b']} via `{fb['bridge_from']}` -> `{fb['bridge_to']}`")
        else:
            report_lines.append("No fragile bridges.")
        report_lines.append("")

        report_lines.append(f"### Isolated Communities ({len(isolated_comms)} communities)")
        if isolated_comms:
            report_lines.append("These communities have zero external connections:")
            report_lines.append("")
            report_lines.append("| Community | Nodes | Members |")
            report_lines.append("|---|---|---|")
            for ic in isolated_comms:
                members_str = ", ".join(ic["members"][:5])
                if ic["node_count"] > 5:
                    members_str += ", ..."
                report_lines.append(f"| {ic['community_id']} | {ic['node_count']} | {members_str} |")
        else:
            report_lines.append("No isolated communities.")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")
    report_lines.append(semantic_report)

    report = "\n".join(report_lines)
    print("\n" + report)
    return report


def append_changelog(entry: str):
    existing = read_file(CHANGELOG_FILE) if CHANGELOG_FILE.exists() else ""
    CHANGELOG_FILE.write_text(entry.strip() + "\n\n" + existing, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lint the wiki for content quality issues")
    parser.add_argument("--save", action="store_true", help="Save lint report to wiki/lint-report.md")
    args = parser.parse_args()

    report = run_lint()

    if args.save and report:
        report_path = WIKI_DIR / "lint-report.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"\nSaved: {report_path.relative_to(REPO_ROOT)}")
        today = date.today().isoformat()
        append_changelog(f"## [{today}] lint | Wiki health check\n\nRan lint. See lint-report.md for details.")
