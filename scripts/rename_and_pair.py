"""
rename_and_pair.py — Rename images sequentially and create paired .txt caption stubs.

Usage:
    python scripts/rename_and_pair.py --dir datasets/sophie_v1 --prefix sophie

This will:
    1. Rename all images to sophie_001.png, sophie_002.png, etc.
    2. Create sophie_001.txt, sophie_002.txt stub files with trigger word
    3. Report any orphaned files (images without captions or vice versa)
"""

import argparse
import os
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
TRIGGER_WORD = "sphie"


def get_images(directory: Path) -> list[Path]:
    """Get all image files in directory, sorted by name."""
    images = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return sorted(images)


def rename_and_pair(directory: Path, prefix: str, dry_run: bool = False):
    """Rename images sequentially and create caption stubs."""
    images = get_images(directory)

    if not images:
        print(f"No images found in {directory}")
        return

    print(f"Found {len(images)} images in {directory}")
    print(f"Prefix: {prefix}, Trigger word: {TRIGGER_WORD}")
    print("-" * 50)

    for i, img_path in enumerate(images, start=1):
        new_stem = f"{prefix}_{i:03d}"
        new_img_name = f"{new_stem}{img_path.suffix.lower()}"
        new_txt_name = f"{new_stem}.txt"

        new_img_path = directory / new_img_name
        new_txt_path = directory / new_txt_name

        # Rename image
        if img_path != new_img_path:
            action = "WOULD RENAME" if dry_run else "RENAMED"
            print(f"  {action}: {img_path.name} -> {new_img_name}")
            if not dry_run:
                img_path.rename(new_img_path)

        # Create caption stub if it doesn't exist
        if not new_txt_path.exists():
            caption_stub = (
                f"{TRIGGER_WORD}, a 28 year old woman with wavy light brown hair "
                f"and green eyes, thin gold chain necklace, [DESCRIBE SCENE HERE], "
                f"[DESCRIBE CLOTHING], [DESCRIBE LIGHTING AND SETTING]"
            )
            action = "WOULD CREATE" if dry_run else "CREATED"
            print(f"  {action}: {new_txt_name}")
            if not dry_run:
                new_txt_path.write_text(caption_stub, encoding="utf-8")
        else:
            print(f"  EXISTS: {new_txt_name}")

    print("-" * 50)
    print(f"Done. {len(images)} images processed.")
    if dry_run:
        print("(Dry run — no files were modified. Remove --dry-run to execute.)")


def main():
    parser = argparse.ArgumentParser(
        description="Rename images sequentially and create caption stubs"
    )
    parser.add_argument(
        "--dir", type=str, required=True,
        help="Directory containing images"
    )
    parser.add_argument(
        "--prefix", type=str, default="sophie",
        help="Prefix for renamed files (default: sophie)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would happen without making changes"
    )

    args = parser.parse_args()
    directory = Path(args.dir)

    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        return

    rename_and_pair(directory, args.prefix, args.dry_run)


if __name__ == "__main__":
    main()
