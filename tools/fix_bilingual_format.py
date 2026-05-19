#!/usr/bin/env python3
"""
Fix bilingual file format: split inline EN+CN lines into proper
separated format (English in blockquote, Chinese as normal text).

Strategy: find the start of the first *significant* CJK run (>= MIN_CJK_RUN chars)
and split the line at that position. Small CJK fragments embedded in English
(e.g., book titles like '接触') are kept with the English side.

Usage:
  python tools/fix_bilingual_format.py raw/bilingual/<file>-bilingual.md
"""

import re
import sys
from pathlib import Path

CJK_RE = re.compile(
    r'[一-鿿㐀-䶿豈-﫿'   # CJK Unified Ideographs
    r'　-〿＀-￯'                   # CJK Symbols & Punctuation, Half/Fullwidth Forms
    r'㐀-䶿豈-﫿]+'                 # CJK Extension A, B
)

# Minimum consecutive CJK characters to trigger a split
MIN_CJK_RUN = 4


def has_significant_cjk(text: str) -> int | None:
    """Find the start position of the first significant CJK run."""
    for m in CJK_RE.finditer(text):
        run = m.group()
        if len(run) >= MIN_CJK_RUN:
            return m.start()
    return None


def fix_line(line: str) -> str:
    stripped = line.rstrip()

    # Skip headers, code blocks, blockquotes, list markers
    if not stripped or stripped.startswith(('#', '>', '```', '```', '- ', '* ')):
        return line

    # Check if line already has blockquote English
    if '> ' in stripped:
        return line

    pos = has_significant_cjk(stripped)
    if pos is None:
        return line

    # Split: everything before the CJK run is English, from there is Chinese
    en_part = stripped[:pos].strip()
    cn_part = stripped[pos:].strip()

    if not en_part or not cn_part:
        return line

    # If en_part already ends with sentence-ending punctuation, keep as-is
    # (protects lines that are purely Chinese with minor Latin abbreviations)
    return f'{cn_part}\n> {en_part}'


def fix_file(filepath: Path) -> int:
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    fixed = [fix_line(l) for l in lines]
    new_content = '\n'.join(fixed)
    if new_content != content:
        filepath.write_text(new_content, encoding='utf-8')
        return sum(1 for a, b in zip(lines, fixed) if a != b)
    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: fix_bilingual_format.py <bilingual-file.md> [more-files...]")
        sys.exit(1)

    total_fixed = 0
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.exists():
            print(f"SKIP (not found): {p}")
            continue
        n = fix_file(p)
        total_fixed += n
        print(f"{'OK' if n else '  '}: {p} ({n} lines fixed)")

    print(f"\nTotal lines fixed: {total_fixed}")


if __name__ == '__main__':
    main()
