#!/usr/bin/env python3
"""Re-fetch full text for articles that only have summaries.
Uses multiple scraping methods with fallbacks.
"""

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

try:
    from trafilatura import extract
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False


def scrape_trafilatura(url: str) -> str | None:
    """Try trafilatura first (best results for articles)."""
    if not TRAFILATURA_AVAILABLE:
        return None
    try:
        resp = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; WikiBot/1.0)'
        })
        resp.raise_for_status()
        text = extract(resp.text, output_format='markdown', include_links=True)
        return text.strip() if text and len(text) > 200 else None
    except Exception:
        return None


def scrape_simple(url: str) -> str | None:
    """Simple fallback: fetch HTML and extract text content."""
    try:
        resp = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; WikiBot/1.0)'
        })
        resp.raise_for_status()
        html = resp.text
        # Remove scripts and styles
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        # Extract text
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text if len(text) > 500 else None
    except Exception:
        return None


SCRAPERS = [
    ('trafilatura', scrape_trafilatura),
    ('simple', scrape_simple),
]


def refetch_source(source_file: Path) -> bool:
    """Re-fetch full text for a single source file."""
    content = source_file.read_text(encoding='utf-8')
    if not content.startswith('---'):
        print(f"  SKIP (no frontmatter): {source_file.name}")
        return False

    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"  SKIP (malformed): {source_file.name}")
        return False

    frontmatter = parts[1]
    body = parts[2]

    # Skip if body is already substantial
    if len(body.strip()) > 1000:
        print(f"  SKIP (already has content): {source_file.name}")
        return False

    # Parse URL from frontmatter
    url_match = re.search(r'^url:\s*(.+)$', frontmatter, re.MULTILINE)
    if not url_match:
        print(f"  SKIP (no URL): {source_file.name}")
        return False

    url = url_match.group(1).strip()
    print(f"  Fetching: {url}")

    for name, scraper in SCRAPERS:
        print(f"    Trying {name}...")
        text = scraper(url)
        if text:
            # Insert fetched text into body
            new_content = f"---{parts[1]}---\n\n{text}"
            source_file.write_text(new_content, encoding='utf-8')
            print(f"    OK ({len(text)} chars)")
            return True
        time.sleep(1)

    print(f"    FAILED (all scrapers)")
    return False


def main():
    raw_dir = Path(__file__).resolve().parent.parent / 'raw'
    sources = sorted(raw_dir.glob('*.md'))

    success = 0
    skipped = 0
    failed = 0

    for f in sources:
        # Skip bilingual files
        if '-bilingual' in f.stem or f.stem.endswith('-zh'):
            continue
        print(f"\n{'='*60}")
        print(f"Source: {f.name}")
        if refetch_source(f):
            success += 1
        else:
            # Check if it was skipped vs failed
            content = f.read_text(encoding='utf-8')
            if not content.startswith('---'):
                skipped += 1
            elif len(content.split('---', 2)[2].strip()) > 1000:
                skipped += 1
            else:
                failed += 1

    print(f"\n{'='*60}")
    print(f"Done: {success} fetched, {skipped} skipped, {failed} failed")


if __name__ == '__main__':
    main()
