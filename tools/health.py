#!/usr/bin/env python3
from __future__ import annotations

"""
Structural health checks for the wiki.

Unlike lint.py (which includes expensive LLM-powered semantic analysis),
health.py is purely deterministic — zero API calls, fast enough to run
every session.

Usage:
    python tools/health.py              # print report to stdout
    python tools/health.py --save       # also save to wiki/health-report.md
    python tools/health.py --json       # machine-readable output

Checks:
  - Empty / stub files (pages with no real content beyond frontmatter)
  - Frontmatter integrity (required fields present)
  - Index sync (wiki/index.md entries vs actual files on disk)
  - Log coverage (source pages without a corresponding log entry)
  - Broken wikilinks ([[Target]] or [[Target|display]] pointing to non-existent pages)
  - Missing relations section (entity/concept/atom pages)

Design boundary:
  health.py = structural integrity, deterministic, run every session
  lint.py   = content quality, semantic (LLM), run every 10-15 ingests
"""

import re
import sys
import json
import argparse
from pathlib import Path
from datetime import date

from config_loader import (
    wiki_dir, index_file, log_file,
    excluded_dirs, excluded_files, relation_required_dirs,
    stub_threshold, required_fields_all, required_fields_card, card_dirs,
    valid_types, valid_card_types, type_display_names, relations_header,
)

WIKI_DIR = wiki_dir()
INDEX_FILE = index_file()
LOG_FILE = log_file()


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


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


def content_pages_requiring_relations() -> list[Path]:
    """Pages that MUST have a relations section: from config."""
    dirs = relation_required_dirs()
    return [
        p for p in WIKI_DIR.rglob("*.md")
        if len(p.relative_to(WIKI_DIR).parts) > 1
        and p.relative_to(WIKI_DIR).parts[0] in dirs
    ]


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter (--- ... ---) from content."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].strip()
    return content.strip()


def extract_wikilink_target(raw_link: str) -> str:
    """Extract the target from [[target|display]] pipe format."""
    return raw_link.split("|")[0].strip()


def find_wikilink_targets(content: str) -> list[str]:
    """Extract all wikilink targets from content, handling pipe aliases."""
    return [
        extract_wikilink_target(m)
        for m in re.findall(r'\[\[([^\]]+)\]\]', content)
    ]


# ── Check: Empty / Stub files ───────────────────────────────────────

def check_empty_files(pages: list[Path]) -> list[dict]:
    """Find wiki pages that are empty or contain only frontmatter / minimal content."""
    threshold = stub_threshold()
    results = []
    for p in pages:
        raw = read_file(p)
        body = strip_frontmatter(raw)
        if len(body) < threshold:
            results.append({
                "path": str(p.relative_to(Path(__file__).parent.parent)),
                "total_bytes": len(raw),
                "body_bytes": len(body),
                "status": "empty" if len(body) == 0 else "stub",
            })
    results.sort(key=lambda x: x["body_bytes"])
    return results


# ── Check: Index sync ───────────────────────────────────────────────

def _parse_index_links(index_content: str) -> set[str]:
    """Extract markdown link targets from index.md."""
    return set(re.findall(r'\[.*?\]\(([^)]+\.md)\)', index_content))


def check_index_sync(pages: list[Path]) -> dict:
    """Compare wiki/index.md entries against actual files on disk."""
    ex_dirs = excluded_dirs()
    ex_files = excluded_files()
    index_content = read_file(INDEX_FILE)
    index_links = _parse_index_links(index_content)

    index_paths = set()
    for link in index_links:
        link_path = Path(link)
        if link_path.name in ex_files:
            continue
        if len(link_path.parts) > 1 and link_path.parts[0] in ex_dirs:
            continue
        resolved = (WIKI_DIR / link).resolve()
        index_paths.add(resolved)

    repo_root = Path(__file__).parent.parent
    disk_paths = {p.resolve() for p in pages}

    in_index_not_on_disk = [
        str(p.relative_to(repo_root)) for p in sorted(index_paths - disk_paths)
        if repo_root in p.parents or p == repo_root
    ]
    on_disk_not_in_index = [
        str(p.relative_to(repo_root)) for p in sorted(disk_paths - index_paths)
    ]

    return {
        "in_index_not_on_disk": in_index_not_on_disk,
        "on_disk_not_in_index": on_disk_not_in_index,
    }


# ── Check: Log coverage ────────────────────────────────────────────

def _parse_logged_sources(log_content: str) -> set[str]:
    """Extract source page slugs referenced in log.md."""
    slugs = set()
    for target in find_wikilink_targets(log_content):
        slugs.add(Path(target).stem.lower())
    for link in re.findall(r'\(sources/([^)]+\.md)\)', log_content):
        slugs.add(Path(link).stem.lower())
    return slugs


def check_log_coverage(pages: list[Path]) -> list[dict]:
    """Find source pages that have no corresponding entry in log.md."""
    log_content = read_file(LOG_FILE)
    logged_slugs = _parse_logged_sources(log_content)

    source_dir = WIKI_DIR / "sources"
    if not source_dir.exists():
        return []

    missing = []
    for p in sorted(source_dir.glob("*.md")):
        slug = p.stem.lower()
        if slug not in logged_slugs:
            content = read_file(p)
            title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
            fm_title = title_match.group(1).strip() if title_match else p.stem
            missing.append({
                "path": str(p.relative_to(Path(__file__).parent.parent)),
                "slug": p.stem,
                "title": fm_title,
            })

    return missing


# ── Check: Broken wikilinks ────────────────────────────────────────

def _parse_frontmatter_aliases(content: str) -> list[str]:
    """Parse aliases from frontmatter, handling both single-line and multi-line formats."""
    aliases = []
    alias_section_match = re.search(r'^aliases:\s*(.*?)(?=\n\w+:|\n---|\Z)', content, re.MULTILINE | re.DOTALL)
    if not alias_section_match:
        return aliases

    alias_section = alias_section_match.group(1).strip()

    if alias_section.startswith('['):
        for alias in re.findall(r'"([^"]+)"|\'([^\']+)\'', alias_section):
            a = (alias[0] or alias[1]).strip()
            if a:
                aliases.append(a)
    else:
        lines_after_aliases = alias_section.split('\n')
        for line in lines_after_aliases:
            line = line.strip()
            if line.startswith('-'):
                alias_str = line[1:].strip().strip('"\'')
                if alias_str:
                    aliases.append(alias_str)

    return aliases


def _build_valid_targets() -> set[str]:
    """Build set of all valid wikilink targets (page stems + aliases + type names)."""
    targets = set()

    for p in WIKI_DIR.rglob("*.md"):
        targets.add(p.stem)
        content = read_file(p)
        for alias in _parse_frontmatter_aliases(content):
            targets.add(alias)

    # Type names from config
    targets.update(valid_types())
    targets.update(valid_card_types())
    targets.update(type_display_names())

    return targets


def check_broken_wikilinks(pages: list[Path]) -> list[dict]:
    """Find wikilinks that point to non-existent pages."""
    valid_targets = _build_valid_targets()

    results = []
    for p in pages:
        content = read_file(p)
        targets = find_wikilink_targets(content)
        for target in targets:
            if target not in valid_targets:
                results.append({
                    "page": str(p.relative_to(Path(__file__).parent.parent)),
                    "broken_link": target,
                })

    return results


def check_file_broken_outgoing(file_path: str) -> list[str]:
    """Check all outgoing wikilinks from a single file. Returns broken target names.

    Designed for use in automated hooks — minimal output, no config dependency.
    """
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return []
    valid_targets = _build_valid_targets()
    broken = []
    for target in find_wikilink_targets(read_file(p)):
        if target not in valid_targets:
            broken.append(target)
    return broken


# ── Check: Missing relations section ─────────────────────────────────

def check_missing_relations(pages: list[Path] | None = None) -> list[dict]:
    """Find entity/concept/atom pages missing the required relations section."""
    if pages is None:
        pages = content_pages_requiring_relations()

    header = relations_header()
    results = []
    for p in pages:
        content = read_file(p)
        if header not in content:
            results.append({
                "path": str(p.relative_to(Path(__file__).parent.parent)),
                "page": p.stem,
            })

    return results


# ── Check: Frontmatter integrity ─────────────────────────────────────

def _extract_frontmatter(content: str) -> tuple[str | None, str]:
    """Extract frontmatter block and body from a page."""
    if not content.startswith("---"):
        return None, content
    end = content.find("---", 3)
    if end == -1:
        return None, content
    return content[3:end].strip(), content[end + 3:]


def _fm_has_field(fm: str, field: str) -> bool:
    """Check if a YAML frontmatter block has a non-empty value for the given field."""
    if re.search(rf'^{field}:\s*$', fm, re.MULTILINE):
        after = fm[re.search(rf'^{field}:\s*$', fm, re.MULTILINE).end():]  # type: ignore
        if re.search(r'^\s*-\s+', after, re.MULTILINE):
            return True
        return False

    mo = re.search(rf'^{field}:\s*(.+)$', fm, re.MULTILINE)
    if mo:
        val = mo.group(1).strip()
        if val and val not in ('[]', '""', "''"):
            return True

    return False


def check_frontmatter(pages: list[Path]) -> list[dict]:
    """Check that all pages have required frontmatter fields."""
    results = []
    req_all = required_fields_all()
    req_card = required_fields_card()
    card_dirs_set = card_dirs()

    for p in pages:
        content = read_file(p)
        fm, _ = _extract_frontmatter(content)

        if fm is None:
            results.append({
                "path": str(p.relative_to(Path(__file__).parent.parent)),
                "page": p.stem,
                "issue": "Missing frontmatter (--- delimiter)",
            })
            continue

        rel_path = p.relative_to(WIKI_DIR)
        dir_name = rel_path.parts[0] if len(rel_path.parts) > 1 else None

        required = list(req_all)
        if dir_name in card_dirs_set:
            required.extend(req_card)

        missing = [f for f in required if not _fm_has_field(fm, f)]

        if missing:
            results.append({
                "path": str(p.relative_to(Path(__file__).parent.parent)),
                "page": p.stem,
                "issue": f"Missing required frontmatter fields: {', '.join(missing)}",
            })

    return results


# ── Check: Source file path validation ────────────────────────────────

def check_source_file_paths() -> list[dict]:
    """Verify that source_file frontmatter in source pages points to an actual file."""
    source_dir = WIKI_DIR / "sources"
    results = []
    if not source_dir.exists():
        return results

    repo_root = Path(__file__).parent.parent
    for p in sorted(source_dir.glob("*.md")):
        content = read_file(p)
        fm, _ = _extract_frontmatter(content)
        if fm is None:
            continue

        sf_match = re.search(r'^source_file:\s*(.+)$', fm, re.MULTILINE)
        if not sf_match:
            results.append({
                "page": str(p.relative_to(repo_root)),
                "issue": "Missing `source_file` field in frontmatter",
            })
            continue

        source_path = sf_match.group(1).strip().strip('"\'')
        full_path = repo_root / source_path
        if not full_path.exists():
            results.append({
                "page": str(p.relative_to(repo_root)),
                "issue": f"source_file `{source_path}` not found on disk",
            })

    return results


# ── Check: Archive integrity ────────────────────────────────────────

def check_archive_integrity() -> dict:
    """Verify that revisions in live pages have corresponding archive files and vice versa."""
    archive_dir = WIKI_DIR / "archive"
    repo_root = Path(__file__).parent.parent
    missing_files = []
    orphaned_files = []

    if not archive_dir.exists():
        return {"missing_files": missing_files, "orphaned_files": orphaned_files}

    # Collect all revision references from live pages
    referenced = set()  # set of archive filenames
    for p in all_wiki_pages():
        content = read_file(p)
        fm, _ = _extract_frontmatter(content)
        if fm is None:
            continue
        for m in re.finditer(r'\[\[([^\]]+?)-V(\d+)\]\]', fm):
            page_stem = m.group(1)
            version = m.group(2)
            expected = f"{page_stem}-V{version}.md"
            referenced.add(expected)

    # Check each referenced file exists
    for ref in sorted(referenced):
        if not (archive_dir / ref).exists():
            # Look up which page references it
            missing_files.append({
                "archive_file": ref,
                "issue": f"referenced in revisions but missing from wiki/archive/",
            })

    # Check for orphaned files in archive (not referenced by any live page)
    for f in sorted(archive_dir.iterdir()):
        if not f.is_file() or f.suffix != ".md":
            continue
        if f.name not in referenced:
            orphaned_files.append({
                "archive_file": f.name,
                "issue": "exists in wiki/archive/ but not referenced by any live page's revisions field",
            })

    return {"missing_files": missing_files, "orphaned_files": orphaned_files}


# ── Check: Bilingual link consistency ────────────────────────────────

def _resolve_bilingual_file(raw_stem: str) -> Path | None:
    """Find the bilingual/zh file for a given raw stem.

    Checks suffixes in priority order: -zh.md first, then -bilingual.md.
    Strips arXiv version suffix (.v1/.v2) as a fallback.
    """
    bilingual_dir = Path(__file__).parent.parent / "raw" / "bilingual"
    for suffix in ("-zh", "-bilingual"):
        candidate = bilingual_dir / f"{raw_stem}{suffix}.md"
        if candidate.exists():
            return candidate
    # Fallback: strip arXiv version suffix (e.g. .20014v1 → .20014)
    if raw_stem.count(".") == 1:
        base = raw_stem.rsplit(".", 1)[0]
        for suffix in ("-zh", "-bilingual"):
            candidate = bilingual_dir / f"{base}{suffix}.md"
            if candidate.exists():
                return candidate
    return None


def check_bilingual_links() -> list[dict]:
    """Check that source pages link to existing bilingual versions and vice versa."""
    raw_dir = Path(__file__).parent.parent / "raw"
    bilingual_dir = raw_dir / "bilingual"
    source_dir = WIKI_DIR / "sources"
    repo_root = Path(__file__).parent.parent
    results = []

    if not bilingual_dir.exists() or not source_dir.exists():
        return results

    for p in sorted(source_dir.glob("*.md")):
        content = read_file(p)
        fm, body = _extract_frontmatter(content)
        if fm is None:
            continue

        sf_match = re.search(r'^source_file:\s*(.+)$', fm, re.MULTILINE)
        if not sf_match:
            continue

        source_path = sf_match.group(1).strip().strip('"\'')
        raw_file = repo_root / source_path

        raw_stem = raw_file.stem.replace(" ", "-")
        bilingual_file = _resolve_bilingual_file(raw_stem)

        if not bilingual_file:
            continue

        bilingual_basename = bilingual_file.name

        # Check source page has 📖 link
        has_link = any(kw in body for kw in ("中英双语版", "中文版", "bilingual"))
        if not has_link:
            results.append({
                "page": str(p.relative_to(repo_root)),
                "issue": f"Bilingual version exists at raw/bilingual/{bilingual_basename} but no link in `## 源文件` section",
            })

        # Check raw file has backlink
        if raw_file.exists():
            raw_content = read_file(raw_file)
            has_backlink = "bilingual" in raw_content.lower() and any(
                kw in raw_content for kw in ("中英双语版", "中文版")
            )
            if not has_backlink:
                results.append({
                    "page": str(raw_file.relative_to(repo_root)),
                    "issue": f"Bilingual version exists but raw file missing backlink to bilingual/{bilingual_basename}",
                })

    return results


# ── Check: Raw source files missing published date ────────────────────

def check_raw_source_dates() -> list[dict]:
    """Check raw source files for missing `published` date in frontmatter.

    Scans raw/**/*.md recursively (skips bilingual/).
    For paper-type files, also checks that the filename contains a year.
    """
    raw_dir = Path(__file__).parent.parent / "raw"
    results = []

    source_files: list[Path] = []
    for f in raw_dir.rglob("*.md"):
        rel = f.relative_to(raw_dir)
        if len(rel.parts) > 1 and rel.parts[0] == "bilingual":
            continue
        source_files.append(f)

    for f in source_files:
        content = read_file(f)
        fm, _ = _extract_frontmatter(content)

        if fm is None:
            results.append({
                "path": str(f.relative_to(Path(__file__).parent.parent)),
                "issue": "Missing frontmatter",
            })
            continue

        has_published = bool(re.search(r'^published:\s*\S', fm, re.MULTILINE))
        is_paper = f.stem.startswith("paper-")
        has_year_in_name = bool(re.search(r'\d{4}', f.stem))

        issues = []
        if not has_published:
            issues.append("missing `published` field in frontmatter")
        if is_paper and not has_year_in_name:
            issues.append("paper filename missing year (expected: paper-YYYY-...)")

        if issues:
            results.append({
                "path": str(f.relative_to(Path(__file__).parent.parent)),
                "issue": "; ".join(issues),
            })

    return sorted(results, key=lambda x: x["path"])


# ── Report Generation ───────────────────────────────────────────────

def run_health() -> dict:
    """Run all health checks, return structured results."""
    pages = all_wiki_pages()

    return {
        "date": date.today().isoformat(),
        "total_pages": len(pages),
        "empty_files": check_empty_files(pages),
        "index_sync": check_index_sync(pages),
        "log_coverage": check_log_coverage(pages),
        "broken_wikilinks": check_broken_wikilinks(pages),
        "missing_relations": check_missing_relations(),
        "frontmatter": check_frontmatter(pages),
        "raw_source_dates": check_raw_source_dates(),
        "source_file_paths": check_source_file_paths(),
        "archive_integrity": check_archive_integrity(),
        "bilingual_links": check_bilingual_links(),
    }


def format_report(results: dict) -> str:
    """Format health check results as markdown."""
    lines = [
        f"# Wiki Health Report — {results['date']}",
        "",
        f"Scanned {results['total_pages']} wiki pages. "
        "Checks are purely structural (no LLM calls).",
        "",
    ]

    # Empty / Stub Files
    empty = results["empty_files"]
    lines.append(f"## Empty / Stub Files ({len(empty)} found)")
    lines.append("")
    if empty:
        lines.append("| Page | Total Bytes | Body Bytes | Status |")
        lines.append("|---|---|---|---|")
        for ef in empty:
            icon = "RED" if ef["status"] == "empty" else "YELLOW"
            lines.append(f"| `{ef['path']}` | {ef['total_bytes']} | {ef['body_bytes']} | {icon} {ef['status']} |")
    else:
        lines.append("All pages have content beyond frontmatter. OK")
    lines.append("")

    # Frontmatter Integrity
    fm_issues = results["frontmatter"]
    lines.append(f"## Frontmatter Integrity ({len(fm_issues)} issues)")
    lines.append("")
    if fm_issues:
        lines.append("| Page | Issue |")
        lines.append("|---|---|")
        for fm in fm_issues[:30]:
            lines.append(f"| `{fm['path']}` | {fm['issue']} |")
        if len(fm_issues) > 30:
            lines.append(f"| ... | ({len(fm_issues) - 30} more) |")
    else:
        lines.append("All pages have complete frontmatter. OK")
    lines.append("")

    # Index Sync
    isync = results["index_sync"]
    stale = isync["in_index_not_on_disk"]
    missing = isync["on_disk_not_in_index"]
    total_issues = len(stale) + len(missing)
    lines.append(f"## Index Sync ({total_issues} issues)")
    lines.append("")

    if stale:
        lines.append("### Stale Index Entries (in index.md but no file on disk)")
        for s in stale:
            lines.append(f"- `{s}`")
        lines.append("")

    if missing:
        lines.append("### Missing from Index (file exists but not in index.md)")
        for m in missing:
            lines.append(f"- `{m}`")
        lines.append("")

    if not stale and not missing:
        lines.append("index.md is in sync with disk. OK")
        lines.append("")

    # Log Coverage
    log_missing = results["log_coverage"]
    lines.append(f"## Log Coverage ({len(log_missing)} source pages without log entry)")
    lines.append("")
    if log_missing:
        lines.append("These source pages have no corresponding entry in log.md:")
        lines.append("")
        for lm in log_missing:
            lines.append(f"- `{lm['path']}` — {lm['title']}")
    else:
        lines.append("All source pages have corresponding log entries. OK")
    lines.append("")

    # Broken Wikilinks
    broken = results["broken_wikilinks"]
    lines.append(f"## Broken Wikilinks ({len(broken)} found)")
    lines.append("")
    if broken:
        lines.append("| Page | Broken Link |")
        lines.append("|---|---|")
        for b in broken[:50]:
            lines.append(f"| `{b['page']}` | `[[{b['broken_link']}]]` |")
        if len(broken) > 50:
            lines.append(f"| ... | ({len(broken) - 50} more) |")
    else:
        lines.append("All wikilinks resolve to existing pages. OK")
    lines.append("")

    # Missing Relations Section
    no_rel = results["missing_relations"]
    header = relations_header()
    lines.append(f"## Missing {header} Section ({len(no_rel)} pages)")
    lines.append("")
    if no_rel:
        lines.append(f"Entity/concept/atom pages that lack the required `{header}` section:")
        lines.append("")
        for nr in no_rel:
            lines.append(f"- `{nr['path']}`")
    else:
        lines.append(f"All entity/concept/atom pages have a {header} section. OK")
    lines.append("")

    # Raw Source Dates
    date_issues = results.get("raw_source_dates", [])
    lines.append(f"## Missing `published` Date in Source Files ({len(date_issues)} issues)")
    lines.append("")
    if date_issues:
        lines.append("| File | Issue |")
        lines.append("|---|---|")
        for di in date_issues[:50]:
            lines.append(f"| `{di['path']}` | {di['issue']} |")
        if len(date_issues) > 50:
            lines.append(f"| ... | ({len(date_issues) - 50} more) |")
    else:
        lines.append("All raw source files have a `published` date in frontmatter. OK")
    lines.append("")

    # Source file path validation
    sf_issues = results.get("source_file_paths", [])
    lines.append(f"## Source File Path Validation ({len(sf_issues)} issues)")
    lines.append("")
    if sf_issues:
        lines.append("| Page | Issue |")
        lines.append("|---|---|")
        for sf in sf_issues:
            lines.append(f"| `{sf['page']}` | {sf['issue']} |")
    else:
        lines.append("All source_file paths resolve to existing files. OK")
    lines.append("")

    # Bilingual link consistency
    bl_issues = results.get("bilingual_links", [])
    lines.append(f"## Bilingual Link Consistency ({len(bl_issues)} issues)")
    lines.append("")
    if bl_issues:
        lines.append("| Page | Issue |")
        lines.append("|---|---|")
        for bl in bl_issues:
            lines.append(f"| `{bl['page']}` | {bl['issue']} |")
    else:
        lines.append("All bilingual links are consistent. OK")
    lines.append("")

    # Archive integrity
    ar = results.get("archive_integrity", {"missing_files": [], "orphaned_files": []})
    missing_ar = ar["missing_files"]
    orphaned_ar = ar["orphaned_files"]
    total_ar = len(missing_ar) + len(orphaned_ar)
    lines.append(f"## Archive Integrity ({total_ar} issues)")
    lines.append("")
    if missing_ar:
        lines.append("### Missing Archive Files (referenced in revisions but not on disk)")
        for m in missing_ar:
            lines.append(f"- `{m['archive_file']}` — {m['issue']}")
        lines.append("")
    if orphaned_ar:
        lines.append("### Orphaned Archive Files (on disk but not referenced by any live page)")
        for o in orphaned_ar:
            lines.append(f"- `{o['archive_file']}` — {o['issue']}")
        lines.append("")
    if not total_ar:
        lines.append("All revisions reference existing archive files; no orphaned files. OK")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Structural health checks for the wiki (deterministic, no LLM calls)"
    )
    parser.add_argument("--save", action="store_true",
                        help="Save report to wiki/health-report.md")
    parser.add_argument("--json", action="store_true",
                        help="Output machine-readable JSON instead of markdown")
    parser.add_argument("--check-file", type=str, metavar="PATH",
                        help="Check only broken outgoing wikilinks from a single file (for hook use)")
    args = parser.parse_args()

    if args.check_file:
        broken = check_file_broken_outgoing(args.check_file)
        if broken:
            for target in broken:
                print(f"BROKEN: {args.check_file} -> [[{target}]]", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    results = run_health()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        report = format_report(results)
        print(report)

        if args.save:
            report_path = WIKI_DIR / "health-report.md"
            report_path.write_text(report, encoding="utf-8")
            print(f"\nSaved: {report_path.relative_to(Path(__file__).parent.parent)}")
