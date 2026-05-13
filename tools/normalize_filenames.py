#!/usr/bin/env python3
"""Normalize filenames under raw/ — replace spaces with hyphens, strip special chars.

Also fixes:
- bilingual files' ``original`` YAML field
- raw files' ``📖`` bilingual backlink
- ``?`` in filenames (breaks shell / ``bilingual_path_for()`` lookup)

Usage:
    python tools/normalize_filenames.py          # dry-run (show what would change)
    python tools/normalize_filenames.py --apply   # execute changes
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAW = REPO / "raw"
BILINGUAL = RAW / "bilingual"


def safe_name(name: str) -> str:
    """Replace spaces with hyphens, remove ``?``."""
    name = name.replace(" ", "-")
    name = name.replace("?", "")
    return name


def collect_renames(src_dir: Path) -> list[tuple[Path, Path]]:
    """Find files under *src_dir* whose names need normalizing (recursive)."""
    renames: list[tuple[Path, Path]] = []
    for p in sorted(src_dir.rglob("*"), key=lambda x: (x.is_dir(), str(x))):
        if not p.is_file():
            continue
        new_name = safe_name(p.name)
        if new_name != p.name:
            renames.append((p, p.with_name(new_name)))
    return renames


def update_bilingual_original(p: Path, old_raw: Path, new_raw: Path) -> bool:
    """Update the ``original:`` YAML field in a bilingual file."""
    text = p.read_text(encoding="utf-8")
    # The original field stores the raw-relative path as a YAML string
    old_ref = str(old_raw.relative_to(REPO))
    new_ref = str(new_raw.relative_to(REPO))
    if old_ref not in text:
        # Also try with quotes
        old_ref_q = f'"{old_ref}"'
        new_ref_q = f'"{new_ref}"'
        if old_ref_q not in text:
            return False
        old_ref, new_ref = old_ref_q, new_ref_q
    if old_ref not in text:
        return False
    text = text.replace(old_ref, new_ref, 1)
    p.write_text(text, encoding="utf-8")
    return True


def update_bilingual_backlink(p: Path, old_bilingual_name: str, new_bilingual_name: str) -> bool:
    """Update the ``📖`` backlink at the bottom of a raw source file."""
    text = p.read_text(encoding="utf-8")
    old_link = f"bilingual/{old_bilingual_name}"
    new_link = f"bilingual/{new_bilingual_name}"
    if old_link not in text:
        return False
    text = text.replace(old_link, new_link)
    p.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    apply = "--apply" in sys.argv

    raw_renames = [r for r in collect_renames(RAW) if BILINGUAL not in r[0].parents]
    bil_renames = collect_renames(BILINGUAL)

    # Build old→new maps for quick lookup
    raw_map = {old: new for old, new in raw_renames}
    bil_map = {old: new for old, new in bil_renames}
    all_renames = raw_renames + bil_renames

    if not all_renames:
        print("✓ No filenames need normalizing.")
        return

    print(f"Found {len(all_renames)} file(s) to rename:\n")
    for old, new in all_renames:
        print(f"  {old.relative_to(REPO)}")
        print(f"  → {new.relative_to(REPO)}\n")

    if not apply:
        print("--- dry-run (pass --apply to execute) ---")
        return

    # ---- execute renames ----
    for old, new in all_renames:
        if old.exists():
            old.rename(new)
            print(f"  renamed: {old.name} → {new.name}")

    # ---- fix content references ----
    fix_count = 0

    # 1) Fix bilingual original fields — for each renamed raw file, update the
    #    corresponding bilingual file's ``original:`` YAML field.
    for old_raw, new_raw in raw_map.items():
        stem = new_raw.stem
        for suffix in ("-zh", "-bilingual"):
            bil_file = BILINGUAL / f"{stem}{suffix}.md"
            if bil_file.exists():
                if update_bilingual_original(bil_file, old_raw, new_raw):
                    print(f"  fixed original: {bil_file.name}")
                    fix_count += 1

    # 2) Fix backlinks in raw files — for every bilingual rename, scan all raw
    #    files and update any ``📖`` link that still points to the old name.
    for old_bil, new_bil in bil_map.items():
        for raw_file in RAW.rglob("*.md"):
            if not raw_file.is_file() or BILINGUAL in raw_file.parents:
                continue
                continue
            if update_bilingual_backlink(raw_file, old_bil.name, new_bil.name):
                print(f"  fixed backlink: {raw_file.name} → {new_bil.name}")
                fix_count += 1

    print(f"\nDone. {len(all_renames)} file(s) renamed, {fix_count} content reference(s) fixed.")


if __name__ == "__main__":
    main()
