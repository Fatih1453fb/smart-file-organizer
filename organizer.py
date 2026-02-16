#!/usr/bin/env python3
"""
Smart File Organizer
====================
A command-line utility that automatically organizes files in a given directory
into categorized sub-folders based on their file extensions.

Usage:
    python organizer.py /path/to/folder

Author: Fatih Kurucay
"""

import os
import shutil
import sys

# ---------------------------------------------------------------------------
# Configuration – file extension → category mapping
# ---------------------------------------------------------------------------
# Add or remove extensions here to customise the organizer.

EXTENSION_MAP: dict[str, str] = {
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".svg": "Images",
    ".webp": "Images",
    ".ico": "Images",
    ".tiff": "Images",
    ".heic": "Images",
    # Videos
    ".mp4": "Videos",
    ".avi": "Videos",
    ".mkv": "Videos",
    ".mov": "Videos",
    ".wmv": "Videos",
    ".flv": "Videos",
    ".webm": "Videos",
    # PDFs
    ".pdf": "PDFs",
    # Documents
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".rtf": "Documents",
    ".odt": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".csv": "Documents",
    # Code
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".html": "Code",
    ".css": "Code",
    ".java": "Code",
    ".c": "Code",
    ".cpp": "Code",
    ".h": "Code",
    ".rb": "Code",
    ".go": "Code",
    ".rs": "Code",
    ".php": "Code",
    ".swift": "Code",
    ".kt": "Code",
    ".sh": "Code",
    ".json": "Code",
    ".xml": "Code",
    ".yaml": "Code",
    ".yml": "Code",
    ".sql": "Code",
    ".md": "Code",
}

# Every category that can appear as a destination folder.
CATEGORIES: list[str] = [
    "Images",
    "Videos",
    "PDFs",
    "Documents",
    "Code",
    "Others",
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def validate_path(path: str) -> str:
    """Validate that *path* exists , is a directory, and is accessible.

    Returns the resolved absolute path on success.
    Prints a user-friendly error and exits on failure.
    """
    abs_path = os.path.abspath(path)

    if not os.path.exists(abs_path):
        print(f"❌ Error: The path '{abs_path}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(abs_path):
        print(f"❌ Error: '{abs_path}' is not a directory.")
        sys.exit(1)

    if not os.access(abs_path, os.R_OK | os.W_OK):
        print(f"❌ Error: Insufficient permissions for '{abs_path}'.")
        sys.exit(1)

    return abs_path


def create_category_folders(base_path: str) -> None:
    """Create category sub-folders inside *base_path* if they don't exist."""
    for category in CATEGORIES:
        folder = os.path.join(base_path, category)
        os.makedirs(folder, exist_ok=True)


def get_category(filename: str) -> str:
    """Return the category name for *filename* based on its extension.

    Falls back to ``"Others"`` when the extension is not recognised.
    """
    _, ext = os.path.splitext(filename)
    return EXTENSION_MAP.get(ext.lower(), "Others")


def is_hidden_or_system(filename: str) -> bool:
    """Return ``True`` if *filename* looks like a hidden or system file.

    Hidden files on Unix-like systems start with a dot (e.g. ``.DS_Store``).
    """
    return filename.startswith(".")


def resolve_duplicate(destination_folder: str, filename: str) -> str:
    """Return a unique file path inside *destination_folder*.

    If ``filename`` already exists there, a numeric suffix is appended
    before the extension (e.g. ``photo_1.jpg``, ``photo_2.jpg``, …).
    """
    dest = os.path.join(destination_folder, filename)

    if not os.path.exists(dest):
        return dest

    name, ext = os.path.splitext(filename)
    counter = 1

    while os.path.exists(dest):
        new_name = f"{name}_{counter}{ext}"
        dest = os.path.join(destination_folder, new_name)
        counter += 1

    return dest


def organize_files(base_path: str) -> dict[str, int]:
    """Move every non-hidden file in *base_path* into its category folder.

    Returns a dictionary mapping each category name to the number of files
    that were moved into it.
    """
    # Initialise counters for every category.
    summary: dict[str, int] = {cat: 0 for cat in CATEGORIES}

    for entry in os.listdir(base_path):
        src = os.path.join(base_path, entry)

        # Skip directories (including the category folders themselves).
        if os.path.isdir(src):
            continue

        # Skip hidden / system files (e.g. .DS_Store).
        if is_hidden_or_system(entry):
            continue

        category = get_category(entry)
        dest_folder = os.path.join(base_path, category)
        dest_path = resolve_duplicate(dest_folder, entry)

        try:
            shutil.move(src, dest_path)
            summary[category] += 1
        except PermissionError:
            print(f"⚠️  Permission denied – could not move '{entry}'. Skipping.")
        except OSError as e:
            print(f"⚠️  OS error moving '{entry}': {e}. Skipping.")

    return summary


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def print_summary(summary: dict[str, int]) -> None:
    """Print a clean summary table of the organising results."""
    total = sum(summary.values())

    if total == 0:
        print("\nℹ️  No files to organise – the folder is already clean.")
        return

    # Table dimensions
    cat_width = max(len(c) for c in summary) + 2  # padding
    count_width = 8

    border = "+" + "-" * cat_width + "+" + "-" * count_width + "+"
    header = f"|{'Category':^{cat_width}}|{'Count':^{count_width}}|"

    print(f"\n{'📂 Organisation Summary':^{cat_width + count_width + 3}}")
    print(border)
    print(header)
    print(border)

    for category, count in summary.items():
        if count > 0:
            print(f"| {category:<{cat_width - 2}} | {count:>{count_width - 3}} |")

    print(border)
    print(f"| {'Total':<{cat_width - 2}} | {total:>{count_width - 3}} |")
    print(border)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse arguments, validate input, and run the organiser."""

    # --- 1. Check command-line arguments -----------------------------------
    if len(sys.argv) != 2:
        print("Usage: python organizer.py /path/to/folder")
        sys.exit(1)

    target_path = sys.argv[1]

    # --- 2. Validate the supplied path -------------------------------------
    target_path = validate_path(target_path)
    print(f"🔍 Scanning: {target_path}\n")

    # --- 3. Create destination folders -------------------------------------
    create_category_folders(target_path)

    # --- 4. Organise files -------------------------------------------------
    summary = organize_files(target_path)

    # --- 5. Display results ------------------------------------------------
    print_summary(summary)
    print("\n✅ Done! Files have been organised successfully.")


if __name__ == "__main__":
    main()
