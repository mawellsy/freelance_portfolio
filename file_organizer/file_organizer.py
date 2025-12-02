#!/usr/bin/env python3
"""
File Organizer Script

This script organizes files inside a given folder into subfolders
based on file type (extension). It is designed as a simple, safe,
and reusable utility that can be used by non-technical clients.

Features:
- Categorizes files into folders (Images, Documents, Spreadsheets, Code, etc.)
- Creates target folders automatically if they do not exist
- Handles name conflicts by appending a numeric suffix
- Optional dry-run mode to preview changes without moving files
"""

import argparse
import os
import shutil
from collections import defaultdict
from pathlib import Path

# Mapping of categories to file extensions
CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf"},
    "Spreadsheets": {".xls", ".xlsx", ".csv"},
    "Presentations": {".ppt", ".pptx"},
    "Archives": {".zip", ".tar", ".gz", ".rar", ".7z"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".hpp", ".html", ".css"},
}


def detect_category(path: Path) -> str:
    """
    Return the category name for a given file path based on extension.
    If extension is unknown, return 'Other'.
    """
    ext = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"


def ensure_unique_path(target: Path) -> Path:
    """
    If 'target' already exists, append a numeric suffix before the extension
    (e.g., 'file_1.txt', 'file_2.txt', etc.) until a free name is found.
    """
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    parent = target.parent

    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def organize_folder(folder: Path, dry_run: bool = False, verbose: bool = True) -> dict:
    """
    Organize all files in 'folder' into category subfolders.

    Parameters
    ----------
    folder : Path
        The folder whose files will be organized.
    dry_run : bool
        If True, do not move files, only print what would happen.
    verbose : bool
        If True, print details to the console.

    Returns
    -------
    summary : dict
        A dictionary with counts per category.
    """
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Folder does not exist or is not a directory: {folder}")

    summary = defaultdict(int)

    # We only look at *files* directly inside the folder (no recursion)
    for item in folder.iterdir():
        if not item.is_file():
            continue  # skip directories

        category = detect_category(item)
        target_dir = folder / category
        target_dir.mkdir(exist_ok=True)

        target_path = target_dir / item.name
        target_path = ensure_unique_path(target_path)

        if verbose:
            action = "[DRY RUN]" if dry_run else "[MOVE]"
            print(f"{action} {item.name} -> {target_path.relative_to(folder)}")

        if not dry_run:
            shutil.move(str(item), str(target_path))

        summary[category] += 1

    return dict(summary)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organize files inside a folder into subfolders by type."
    )
    parser.add_argument(
        "folder",
        help="Path to the folder whose files you want to organize.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually moving any files.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run without printing detailed output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    folder_path = Path(args.folder).expanduser().resolve()

    verbose = not args.quiet

    if verbose:
        print(f"Organizing folder: {folder_path}")
        if args.dry_run:
            print("Mode: DRY RUN (no files will be moved)\n")

    summary = organize_folder(folder_path, dry_run=args.dry_run, verbose=verbose)

    if verbose:
        print("\nSummary:")
        if not summary:
            print("  No files found to organize.")
        else:
            for category, count in sorted(summary.items()):
                print(f"  {category}: {count} file(s)")


if __name__ == "__main__":
    main()
