#!/usr/bin/env python3
"""Build the card browser data directly from wiki files.

Usage:
    python tools/build_browser.py              # Generate browser data
    python tools/build_browser.py --open       # Open browser after build

Reads wiki pages directly, merges raw source content into source page nodes
(as foldable <details> blocks), and generates sharded content files for
lazy loading in the browser.

No longer depends on graph.json or build_graph.py.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import webbrowser
from pathlib import Path
from datetime import date
from collections import defaultdict

try:
    import yaml as _yaml
except ImportError:
    _yaml = None

from config_loader import (
    wiki_dir, graph_dir, log_file, changelog_file,
)

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = wiki_dir()
RAW_DIR = REPO_ROOT / "raw"
BROWSER_DIR = REPO_ROOT / "browser"
CONTENT_DIR = BROWSER_DIR / "content"
WIKI_ARCHIVE = WIKI_DIR / "archive"
WIKI_CONFIG_PATH = REPO_ROOT / "wiki.config.yaml"


def _load_wiki_config() -> dict:
    """Load wiki.config.yaml for domain-specific settings."""
    if WIKI_CONFIG_PATH.exists() and _yaml is not None:
        try:
            cfg = _yaml.safe_load(WIKI_CONFIG_PATH.read_text(encoding="utf-8"))
            return cfg if isinstance(cfg, dict) else {}
        except _yaml.YAMLError:
            pass
    return {}


_wiki_config = _load_wiki_config()

# Wiki type colors (source, entity, concept, synthesis, atom, query, overview, raw_source)
_wiki_types = _wiki_config.get("wiki_types", {})
TYPE_COLORS = {k: v for k, v in _wiki_types.items() if isinstance(v, str)}
TYPE_COLORS.setdefault("raw_source", "#6366f1")
TYPE_COLORS.setdefault("unknown", "#9E9E9E")

# Source types (paper, article, book, report, policy, thinktank)
_source_types = _wiki_config.get("source_types", {})
RAW_TYPE_META = {
    st: {
        "icon": info.get("icon", "📄") if isinstance(info, dict) else "📄",
        "label": info.get("label", st) if isinstance(info, dict) else st,
        "color": info.get("color", "#999999") if isinstance(info, dict) else "#999999",
    }
    for st, info in _source_types.items() if isinstance(info, dict)
}


def infer_raw_type(filename: str, fm: dict) -> str:
    """Infer raw source type from frontmatter or filename prefix (config-driven)."""
    fm_type = fm.get("type", "")
    if fm_type and fm_type in RAW_TYPE_META:
        return fm_type
    for prefix in RAW_TYPE_META:
        if filename.startswith(f"{prefix}-"):
            return prefix
    return "article"


# Card type colors (person, event, insight, terminology, etc.)
_card_types = _wiki_config.get("card_types", {})
CARD_TYPE_COLORS = {
    ct: info["color"]
    for ct, info in _card_types.items()
    if isinstance(info, dict) and "color" in info
}

ARCHIVE_RE = re.compile(r"^(.+)-V(\d+)\.md$")


# ── File utils ──────────────────────────────────────────────────────────

def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


# ── Page collection ─────────────────────────────────────────────────────

def all_wiki_pages() -> list[Path]:
    return sorted(
        p for p in WIKI_DIR.rglob("*.md")
        if p.name not in ("log.md", "lint-report.md")
        and "archive/" not in str(p.relative_to(WIKI_DIR))
        and "types/" not in str(p.relative_to(WIKI_DIR))
    )


def all_raw_pages() -> list[Path]:
    pages = []
    if RAW_DIR.exists():
        pages.extend(RAW_DIR.glob("*.md"))
        for subdir in RAW_DIR.iterdir():
            if subdir.is_dir() and subdir.name != "bilingual":
                pages.extend(subdir.glob("*.md"))
    return sorted(pages)


# ── Frontmatter parsing ─────────────────────────────────────────────────

def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown. Returns empty dict on failure."""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    fm_text = content[3:end]
    if _yaml is not None:
        try:
            result = _yaml.safe_load(fm_text)
            return result if isinstance(result, dict) else {}
        except _yaml.YAMLError:
            pass
    # Fallback: basic line-by-line parser
    result = {}
    current_list = None
    for line in fm_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if current_list is not None:
            if stripped.startswith("- "):
                result.setdefault(current_list, []).append(stripped[2:].strip().strip('"').strip("'"))
                continue
            else:
                current_list = None
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val == "":
                current_list = key
            else:
                result[key] = val
    return result


def extract_frontmatter_type(fm: dict) -> str:
    value = fm.get("type", "unknown")
    if isinstance(value, str):
        m = re.match(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', value)
        return m.group(1) if m else value
    return str(value)


def extract_frontmatter_card_type(fm: dict) -> str | None:
    value = fm.get("card_type")
    return str(value) if value else None


def extract_frontmatter_description(fm: dict) -> str | None:
    val = fm.get("description")
    return str(val)[:220] if val else None


def extract_frontmatter_date(fm: dict) -> str | None:
    return fm.get("updated") or fm.get("created") or fm.get("published") or fm.get("date")


def extract_frontmatter_created(fm: dict) -> str | None:
    val = fm.get("created")
    return str(val) if val else None


def extract_frontmatter_updated(fm: dict) -> str | None:
    val = fm.get("updated")
    return str(val) if val else None


def extract_frontmatter_source_file(fm: dict) -> str | None:
    val = fm.get("source_file")
    return str(val) if val else None


def extract_frontmatter_source_url(fm: dict) -> str | None:
    val = fm.get("source_url")
    return str(val) if val else None


def extract_frontmatter_image(fm: dict) -> str | None:
    val = fm.get("image")
    return str(val) if val else None


def rewrite_wiki_image_path(image_path: str, wiki_file: Path) -> str | None:
    """Rewrite a relative image path for browser display (resolves from browser/index.html)."""
    if not image_path:
        return None
    if image_path.startswith(("http://", "https://", "data:", "file://", "/")):
        return image_path
    return f"images/{Path(image_path).name}"


def extract_frontmatter_tags(fm: dict) -> list[str]:
    tags = fm.get("tags", [])
    if isinstance(tags, list):
        return [str(t) for t in tags]
    if isinstance(tags, str):
        return [t.strip() for t in tags.split(",") if t.strip()]
    return []


def extract_frontmatter_sources(fm: dict) -> list[str]:
    """Extract source wikilinks from frontmatter. Returns list of page slugs."""
    sources = fm.get("sources", [])
    if isinstance(sources, list):
        result = []
        for s in sources:
            s = str(s)
            m = re.match(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', s)
            result.append(m.group(1) if m else s)
        return result
    if isinstance(sources, str):
        m = re.match(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', sources)
        return [m.group(1)] if m else [sources]
    return []


def extract_frontmatter_aliases(fm: dict) -> list[str]:
    aliases = fm.get("aliases", [])
    if isinstance(aliases, list):
        return [str(a) for a in aliases]
    return []


def find_chinese_alias(aliases: list[str]) -> str | None:
    """Find the first alias that contains Chinese characters (CJK Unified Ideographs)."""
    for a in aliases:
        if re.search(r'[一-鿿]', a):
            return a
    return None


def extract_frontmatter_score(fm: dict) -> int | None:
    """Extract optional score (1-10) from frontmatter. Returns None if missing or invalid."""
    val = fm.get("score")
    if val is None:
        return None
    try:
        score = int(val)
        if 1 <= score <= 10:
            return score
    except (ValueError, TypeError):
        pass
    return None


# ── Wikilink extraction ─────────────────────────────────────────────────

def extract_wikilinks(content: str) -> list[str]:
    return list(set(re.findall(r'\[\[([^\]]+)\]\]', content)))


# ── Page ID ─────────────────────────────────────────────────────────────

def page_id(path: Path) -> str:
    return path.relative_to(WIKI_DIR).as_posix().replace(".md", "")


# ── Bilingual lookup ────────────────────────────────────────────────────

def bilingual_path_for(raw_path: Path) -> Path | None:
    """Return bilingual/zh file path for a raw file if it exists."""
    stem = raw_path.stem.replace(" ", "-")
    for suffix in ("-zh", "-bilingual"):
        candidate = RAW_DIR / "bilingual" / f"{stem}{suffix}.md"
        if candidate.exists():
            return candidate
    if stem.count(".") == 1:
        base = stem.rsplit(".", 1)[0]
        for suffix in ("-zh", "-bilingual"):
            candidate = RAW_DIR / "bilingual" / f"{base}{suffix}.md"
            if candidate.exists():
                return candidate
    return None


# ── Image path rewriting ────────────────────────────────────────────────

def rewrite_wiki_images(content: str, wiki_file: Path) -> str:

    def replace_md(match):
        alt = match.group(1)
        src = match.group(2)
        if src.startswith(("http://", "https://", "data:", "file://", "/")):
            return match.group(0)
        return f"![{alt}](images/{Path(src).name})"

    content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_md, content)
    content = re.sub(
        r'^(image:)\s*"([^"]+)"',
        lambda m: f'{m.group(1)} "images/{Path(m.group(2)).name}"' if not m.group(2).startswith(
            ("http://", "https://", "data:", "file://", "/")
        ) else m.group(0),
        content, flags=re.MULTILINE,
    )
    return content


def rewrite_raw_images(content: str, raw_file: Path) -> str:

    def replace(match):
        alt = match.group(1)
        src = match.group(2)
        if src.startswith(("http://", "https://", "data:", "file://", "/")):
            return match.group(0)
        return f"![{alt}](images/{Path(src).name})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace, content)


# ── Archive lookup ──────────────────────────────────────────────────────

def _parse_frontmatter_date_from_text(markdown: str) -> str | None:
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
    if not wiki_path.startswith("wiki/") or not WIKI_ARCHIVE.is_dir():
        return None
    p = Path(wiki_path)
    stem = p.stem
    # Wiki subdir (e.g. "concepts", "entities") mirrors under archive/
    wiki_subdir = p.parent.name if p.parent != WIKI_DIR else None

    def _collect(dir_path):
        results = []
        if not dir_path.is_dir():
            return results
        for f in dir_path.iterdir():
            if not f.is_file() or f.suffix != ".md":
                continue
            m = ARCHIVE_RE.match(f.name)
            if m and m.group(1) == stem:
                try:
                    version = int(m.group(2))
                except ValueError:
                    continue
                content = f.read_text(encoding="utf-8")
                dt = _parse_frontmatter_date_from_text(content)
                results.append({
                    "version": version,
                    "filename": f.name,
                    "markdown": content,
                    "updated": dt,
                })
        return results

    # Look in mirrored subdir first, then fall back to flat archive root
    if wiki_subdir:
        results = _collect(WIKI_ARCHIVE / wiki_subdir)
        if results:
            results.sort(key=lambda x: x["version"])
            return results
    results = _collect(WIKI_ARCHIVE)
    if results:
        results.sort(key=lambda x: x["version"])
        return results
    return None
    results.sort(key=lambda x: x["version"], reverse=True)
    return results


# ── Raw source nodes ────────────────────────────────────────────────────

def build_raw_source_nodes() -> list[dict]:
    """Build lightweight nodes for raw source files (the 'library' view).

    Each raw .md file (excluding bilingual/) becomes a type:raw_source node
    with no edges. Content prefers bilingual/zh translation over original.
    A footer links to the matching sources/X summary page if one exists.
    """
    # Build raw-to-source mapping by matching stems
    raw_to_source = {}
    for p in WIKI_DIR.rglob("*.md"):
        pid = page_id(p)
        if not pid.startswith("sources/"):
            continue
        fm = parse_frontmatter(p.read_text(encoding="utf-8"))
        sf = extract_frontmatter_source_file(fm)
        if sf:
            raw_to_source[sf.replace(".md", "")] = pid
        else:
            raw_to_source[p.stem.lower()] = pid

    nodes = []
    for raw_path in all_raw_pages():
        raw_rel = raw_path.relative_to(RAW_DIR).as_posix().replace(".md", "")
        raw_with_prefix = f"raw/{raw_rel}"
        content = read_file(raw_path)
        fm = parse_frontmatter(content)

        # Determine title
        title = fm.get("title", "")
        if not title or not isinstance(title, str):
            title = raw_path.stem.replace("-", " ").replace("_", " ")

        # Determine raw type
        raw_type = infer_raw_type(raw_path.name, fm)
        raw_meta = RAW_TYPE_META.get(raw_type, RAW_TYPE_META["article"])

        # Determine date
        pub_date = fm.get("published") or fm.get("date") or fm.get("created") or ""

        # Content: bilingual > zh > original
        bilingual = bilingual_path_for(raw_path)
        display_content = read_file(bilingual) if bilingual else content
        display_content = rewrite_raw_images(display_content, raw_path)

        # Find matching source page
        source_id = raw_to_source.get(raw_with_prefix) or raw_to_source.get(raw_path.stem.lower())
        # Also try with hyphens (spaces → hyphens normalization)
        if not source_id:
            source_id = raw_to_source.get(raw_with_prefix.replace(" ", "-"))

        # Footer: link to sources/X summary
        if source_id:
            display_content += f'\n\n---\n📝 **查看概要**: [[{source_id}]]'

        # Preview (from display content, excluding frontmatter)
        body = re.sub(r"^---\n.*?\n---\n?", "", display_content, flags=re.DOTALL)
        preview_lines = [ln.strip() for ln in body.splitlines()
                        if ln.strip() and not ln.strip().startswith('#')]
        preview = " ".join(preview_lines[:3])[:220]

        # Tags
        tags = extract_frontmatter_tags(fm)
        if raw_type:
            tags.append(f"source:{raw_type}")

        source_url = extract_frontmatter_source_url(fm)

        # Bilingual label for raw source cards
        if title and not re.search(r'[一-鿿]', str(title)):
            zh_alias = find_chinese_alias(extract_frontmatter_aliases(fm))
            if zh_alias:
                title = f"{title}（{zh_alias}）"

        node = {
            "id": f"raw_source/{raw_rel}".replace(" ", "-").replace("(", "").replace(")", ""),
            "label": str(title),
            "type": "raw_source",
            "card_type": f"[[{raw_type}]]",
            "color": raw_meta["color"],
            "path": str(raw_path.relative_to(REPO_ROOT)),
            "preview": preview,
            "tags": tags,
            "sources": [source_id] if source_id else [],
            "date": str(pub_date) if pub_date else "",
            "source_url": source_url,
            "_markdown": display_content,  # full content with frontmatter (bilingual preferred)
            "connections": [],
            "connection_count": 0,
            "score": extract_frontmatter_score(fm),
        }
        nodes.append(node)

    return nodes


# ── Main build ──────────────────────────────────────────────────────────

def build():
    """Main build pipeline. Returns True on success."""
    print("Collecting wiki pages...")
    wiki_pages = all_wiki_pages()
    print(f"  Found {len(wiki_pages)} wiki pages")

    # Build raw_source nodes (standalone library cards, no edges)
    print("Building raw source library...")
    raw_source_nodes = build_raw_source_nodes()
    print(f"  {len(raw_source_nodes)} raw source documents")

    # Build stem → page_id map for edge resolution
    stem_to_id = {}
    for p in wiki_pages:
        stem_to_id[p.stem.lower()] = page_id(p)

    # Also build alias → page_id map
    alias_to_id = {}
    for p in wiki_pages:
        content = read_file(p)
        fm = parse_frontmatter(content)
        for alias in extract_frontmatter_aliases(fm):
            alias_to_id[alias.lower()] = page_id(p)

    # Build nodes
    print("Building nodes...")
    nodes = []
    for p in wiki_pages:
        content = read_file(p)
        fm = parse_frontmatter(content)
        pid = page_id(p)

        node_type = extract_frontmatter_type(fm)
        card_type = extract_frontmatter_card_type(fm)
        label = fm.get("title", p.stem) if isinstance(fm.get("title"), str) else p.stem

        # Bilingual label: if title is English and Chinese alias exists, append "（中文）"
        if not re.search(r'[一-鿿]', str(label)):
            zh_alias = find_chinese_alias(extract_frontmatter_aliases(fm))
            if zh_alias:
                label = f"{label}（{zh_alias}）"

        # Body without frontmatter for preview
        body = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL)
        description = extract_frontmatter_description(fm)
        if description:
            preview = description[:220]
        else:
            preview_lines = [ln.strip() for ln in body.splitlines()
                           if ln.strip() and not ln.strip().startswith('#')]
            preview = " ".join(preview_lines[:3])[:220]

        # Color priority: card_type > type > unknown
        color = (CARD_TYPE_COLORS.get(card_type) if card_type
                 else TYPE_COLORS.get(node_type, TYPE_COLORS["unknown"]))
        if color is None:
            color = TYPE_COLORS.get(node_type, TYPE_COLORS["unknown"])

        # Full markdown for content shard (with image paths rewritten)
        display_markdown = rewrite_wiki_images(content, p)

        node = {
            "id": pid,
            "label": str(label),
            "type": node_type,
            "color": color,
            "path": str(p.relative_to(REPO_ROOT)),
            "preview": preview,
            "tags": extract_frontmatter_tags(fm),
            "sources": extract_frontmatter_sources(fm),
            "aliases": extract_frontmatter_aliases(fm),
            "_markdown": display_markdown,  # goes to content shard, removed before data.js
        }
        if card_type:
            node["card_type"] = card_type
        date_val = extract_frontmatter_date(fm)
        if date_val:
            node["date"] = str(date_val)
        created_val = extract_frontmatter_created(fm)
        if created_val:
            node["created"] = str(created_val)
        updated_val = extract_frontmatter_updated(fm)
        if updated_val:
            node["updated"] = str(updated_val)
        source_url = extract_frontmatter_source_url(fm)
        if source_url:
            node["source_url"] = source_url
        image = rewrite_wiki_image_path(extract_frontmatter_image(fm), p)
        if image:
            node["image"] = image
        score = extract_frontmatter_score(fm)
        if score is not None:
            node["score"] = score
        nodes.append(node)

    # Append raw_source nodes (standalone library, no edges)
    nodes.extend(raw_source_nodes)

    # Build edges from wikilinks
    print("Building edges...")
    edges = []
    seen_edges = set()
    for p in wiki_pages:
        content = read_file(p)
        src = page_id(p)
        for link in extract_wikilinks(content):
            # target: strip alias after |, lowercase for lookup
            target_name = link.split("|")[0].strip()
            target_lower = target_name.lower()
            # Resolve target: stem map first, then alias map
            target = stem_to_id.get(target_lower) or alias_to_id.get(target_lower)
            if target and target != src:
                key = (src, target)
                if key not in seen_edges:
                    seen_edges.add(key)
                    edges.append({
                        "id": f"{src}->{target}:EXTRACTED",
                        "from": src,
                        "to": target,
                        "type": "EXTRACTED",
                        "color": "#555555",
                        "confidence": 1.0,
                    })

    # Compute degree centrality
    print("Computing centrality...")
    degree = defaultdict(int)
    for e in edges:
        degree[e["from"]] += 1
        degree[e["to"]] += 1

    # Non-source nodes for ranking
    non_source_degrees = {nid: d for nid, d in degree.items()
                          if not nid.startswith("sources/")}
    ranked = sorted(non_source_degrees.items(), key=lambda x: -x[1])
    total_non_source = len(ranked)

    # Build adjacency for each node
    adjacency = defaultdict(list)
    for e in edges:
        src, tgt = e["from"], e["to"]
        adjacency[src].append({"to": tgt, "type": e["type"], "title": e.get("title", "")})
        adjacency[tgt].append({"to": src, "type": e["type"], "title": e.get("title", "")})

    # Enrich nodes with connections
    for node in nodes:
        nid = node["id"]
        node["connections"] = adjacency.get(nid, [])
        node["connection_count"] = len(node["connections"])

    # Build summary stats
    types = {}
    card_types = {}
    all_tags = defaultdict(int)
    for node in nodes:
        t = node.get("type", "unknown")
        types[t] = types.get(t, 0) + 1
        ct = node.get("card_type", "")
        if ct:
            card_types[ct] = card_types.get(ct, 0) + 1
        for tag in node.get("tags", []):
            all_tags[tag] += 1

    summary = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "types": dict(types),
        "card_types": dict(card_types),
        "tags": dict(all_tags),
        "built": date.today().isoformat(),
    }

    # Attach archive versions
    archive_count = 0
    for node in nodes:
        wiki_path = node.get("path", "")
        archives = archives_for_wiki_path(wiki_path)
        if archives:
            node["archives"] = archives
            archive_count += 1
    if archive_count:
        print(f"Archive versions attached: {archive_count} node(s)")

    # ── Copy images to browser ──────────────────────────────────────────

    IMAGES_DIR = BROWSER_DIR / "images"
    # Clean and recreate images directory
    if IMAGES_DIR.exists():
        shutil.rmtree(IMAGES_DIR)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all image references from wiki nodes (frontmatter + body)
    image_sources = set()  # (repo_relative_path, absolute_src_path)
    for node in nodes:
        wiki_path = node.get("path", "")
        if not wiki_path:
            continue
        p = REPO_ROOT / wiki_path
        if not p.exists():
            continue
        # Frontmatter image
        content = read_file(p)
        fm = parse_frontmatter(content) if content.startswith("---") else {}
        fm_image = extract_frontmatter_image(fm)
        if fm_image and not fm_image.startswith(("http://", "https://", "data:", "file://", "/")):
            src = (p.parent / fm_image).resolve()
            if src.exists():
                image_sources.add((f"{p.parent.relative_to(REPO_ROOT).as_posix()}/{fm_image}", src))
        # Body images in markdown
        for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", content):
            src = m.group(2)
            if not src.startswith(("http://", "https://", "data:", "file://", "/")):
                abs_src = (p.parent / src).resolve()
                if abs_src.exists():
                    image_sources.add((abs_src.relative_to(REPO_ROOT).as_posix(), abs_src))

    # Also collect images from raw source nodes
    for node in raw_source_nodes:
        raw_path = node.get("path", "")
        if not raw_path:
            continue
        p = REPO_ROOT / raw_path
        if not p.exists():
            continue
        content = read_file(p)
        for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", content):
            src = m.group(2)
            if not src.startswith(("http://", "https://", "data:", "file://", "/")):
                abs_src = (p.parent / src).resolve()
                if abs_src.exists():
                    image_sources.add((abs_src.relative_to(REPO_ROOT).as_posix(), abs_src))

    # Copy images, handling name collisions
    seen_names = {}
    for rel_path, abs_src in sorted(image_sources):
        name = abs_src.name
        if name in seen_names:
            # Avoid collision: prefix with parent dir
            stem, ext = name.rsplit(".", 1) if "." in name else (name, "")
            unique_name = f"{abs_src.parent.name}-{name}"
            print(f"  Image collision: {name} -> {unique_name}")
            name = unique_name
        seen_names[name] = abs_src
        dst = IMAGES_DIR / name
        if not dst.exists():
            shutil.copy2(abs_src, dst)

    # Update image paths in nodes and _markdown to use images/<name>
    # Build a lookup: old relative path -> new images/ name
    path_map = {}
    for rel_path, abs_src in image_sources:
        name = abs_src.name
        if name not in seen_names or seen_names[name] != abs_src:
            stem, ext = name.rsplit(".", 1) if "." in name else (name, "")
            name = f"{abs_src.parent.name}-{name}"
        # Map various forms of the old path
        path_map[f"../{rel_path}"] = f"images/{name}"
        # Also map the original relative path as stored in data.js node["image"]
        path_map[rel_path] = f"images/{name}"

    for node in nodes:
        # Fix frontmatter image in node metadata
        img = node.get("image")
        if img and img in path_map:
            node["image"] = path_map[img]
        elif img and not img.startswith(("http://", "https://", "data:", "file://", "/")):
            # Try basename lookup
            img_name = Path(img).name
            node["image"] = f"images/{img_name}"
        # Fix images in _markdown
        md = node.get("_markdown", "")
        if md:
            for old, new in path_map.items():
                md = md.replace(old, new)
            node["_markdown"] = md

    for node in raw_source_nodes:
        md = node.get("_markdown", "")
        if md:
            for old, new in path_map.items():
                md = md.replace(old, new)
            node["_markdown"] = md

    print(f"Images copied: {len(image_sources)} files -> browser/images/")

    # ── Write output ───────────────────────────────────────────────────

    BROWSER_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    # Write content shards + build bundle
    print("Writing content shards...")
    content_count = 0
    bundle = {}
    for node in nodes:
        markdown = node.pop("_markdown", None)
        if not markdown:
            continue
        slug = node["id"].replace("/", "-")
        shard = {"markdown": markdown}
        shard_path = CONTENT_DIR / f"{slug}.json"
        shard_path.write_text(
            json.dumps(shard, separators=(',', ':'), ensure_ascii=False),
            encoding="utf-8",
        )
        bundle[node["id"]] = markdown
        content_count += 1
    print(f"  {content_count} content shards written to browser/content/")

    # Write combined content bundle for fast bulk loading
    bundle_path = CONTENT_DIR / "bundle.json"
    bundle_path.write_text(
        json.dumps(bundle, separators=(',', ':'), ensure_ascii=False),
        encoding="utf-8",
    )
    bundle_size = bundle_path.stat().st_size / 1024
    print(f"  Combined bundle: browser/content/bundle.json ({bundle_size:.0f} KB)")

    # Write data.js (config + metadata only, no markdown)
    browser_data = {
        "summary": summary,
        "nodes": nodes,
        "edges": edges,
    }
    config_json = json.dumps(_wiki_config, separators=(',', ':'), ensure_ascii=False)
    data_json = json.dumps(browser_data, separators=(',', ':'), ensure_ascii=False)
    data_js = f"window.__BROWSER_CONFIG__ = {config_json};\nwindow.__BROWSER_DATA__ = {data_json};\n"
    data_js_path = BROWSER_DIR / "data.js"
    data_js_path.write_text(data_js, encoding="utf-8")
    print(f"Generated: browser/data.js ({len(nodes)} nodes, {len(edges)} edges)")

    # ── Print summary ──────────────────────────────────────────────────

    print(f"\nBrowser Summary:")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Edges: {len(edges)}")
    print(f"  Types: {types}")
    print(f"  Card Types: {card_types}")

    # Centrality ranking for source pages (for interestingness analysis)
    print(f"\n=== Source Node Centrality ===")
    source_ranked = sorted(
        [(nid, d) for nid, d in degree.items() if nid.startswith("sources/")],
        key=lambda x: -x[1],
    )
    for i, (nid, d) in enumerate(source_ranked):
        node = next((n for n in nodes if n["id"] == nid), None)
        label = node["label"] if node else nid
        pct = (i + 1) / max(len(source_ranked), 1) * 100
        print(f"  {nid}: degree={d}, rank={i+1}/{len(source_ranked)} (top {pct:.1f}%) [{label}]")

    print(f"\n  Non-source node count: {total_non_source}")
    print(f"  Open: browser/index.html")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build card browser data")
    parser.add_argument("--open", action="store_true", help="Open browser in default browser")
    args = parser.parse_args()

    ok = build()
    if ok and args.open:
        index_path = BROWSER_DIR / "index.html"
        webbrowser.open(f"file://{index_path.resolve()}")


if __name__ == "__main__":
    main()
