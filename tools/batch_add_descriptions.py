#!/usr/bin/env python3
"""Batch add 'description' field to wiki card YAML frontmatter using index.md entries."""

import os
import re
import sys

WIKI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wiki')
INDEX_FILE = os.path.join(WIKI_DIR, 'index.md')

def parse_index():
    """Parse index.md to extract card paths and descriptions."""
    with open(INDEX_FILE, 'r') as f:
        content = f.read()

    entries = []
    # Match lines like: - [[path/to/page|Title]] — description
    # Assumes the first " — " after "]]" is the separator
    for line in content.split('\n'):
        # Skip empty lines and section headers
        if '—' not in line:
            continue
        match = re.match(r'- \[\[([^|]+)\|([^\]]+)\]\] — (.+)', line)
        if match:
            path = match.group(1).strip()
            description = match.group(3).strip()
            # Remove leading emoji tags (🔥, ⭐) followed by optional space
            description = re.sub(r'^[🔥⭐]\s*', '', description)
            entries.append((path, description))
    return entries

def add_description_to_card(filepath, description):
    """Add description to YAML frontmatter of a card file."""
    if not os.path.exists(filepath):
        return None  # file not found

    with open(filepath, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        return None  # no frontmatter

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None  # malformed

    frontmatter = parts[1]

    if 'description:' in frontmatter:
        return False  # already has description

    # Find the 'title:' line to insert description after it
    lines = frontmatter.split('\n')
    title_idx = None
    for i, line in enumerate(lines):
        if re.match(r'^title:', line):
            title_idx = i
            break

    if title_idx is None:
        return None  # no title field

    # Escape double quotes in description
    escaped_desc = description.replace('"', '\\"')
    new_line = f'description: "{escaped_desc}"'

    lines.insert(title_idx + 1, new_line)
    new_frontmatter = '\n'.join(lines)

    new_content = content.replace(parts[1], new_frontmatter)

    with open(filepath, 'w') as f:
        f.write(new_content)

    return True

def main():
    entries = parse_index()
    print(f"Found {len(entries)} entries in index")

    success = 0
    skipped_exists = 0
    skipped_not_found = 0
    skipped_no_title = 0

    for path, description in entries:
        filepath = os.path.join(WIKI_DIR, path + '.md')
        result = add_description_to_card(filepath, description)
        if result is True:
            print(f"  OK: {path}")
            success += 1
        elif result is False:
            skipped_exists += 1
        elif result is None:
            # Check if file exists
            if not os.path.exists(filepath):
                skipped_not_found += 1
            else:
                skipped_no_title += 1

    print(f"\nDone: {success} updated, {skipped_exists} already had description, "
          f"{skipped_not_found} files not found, {skipped_no_title} had no title field")

if __name__ == '__main__':
    main()
