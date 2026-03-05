"""
prepare_dataset.py — Validate and analyze a LoRA training dataset.

Usage:
    python scripts/prepare_dataset.py --dir datasets/sophie_v1

Checks:
    1. Every image has a matching .txt caption file
    2. Every caption starts with the trigger word
    3. Image resolution is adequate (>= 512px on shortest side)
    4. No duplicate images (by file hash)
    5. Reports dataset statistics
"""

import argparse
import hashlib
import os
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
TRIGGER_WORD = "sphie"
MIN_RESOLUTION = 512


def file_hash(path: Path) -> str:
    """Compute MD5 hash of a file for duplicate detection."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_dataset(directory: Path):
    """Run all validation checks on the dataset."""
    images = sorted([
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ])
    captions = sorted([
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() == ".txt"
    ])

    image_stems = {f.stem for f in images}
    caption_stems = {f.stem for f in captions}

    errors = []
    warnings = []
    stats = {
        "total_images": len(images),
        "total_captions": len(captions),
        "resolutions": [],
        "caption_lengths": [],
    }

    print(f"\n{'='*60}")
    print(f"  DATASET VALIDATION: {directory}")
    print(f"{'='*60}\n")

    # --- Check 1: Unpaired files ---
    images_without_captions = image_stems - caption_stems
    captions_without_images = caption_stems - image_stems

    if images_without_captions:
        for stem in sorted(images_without_captions):
            errors.append(f"Missing caption for: {stem}")

    if captions_without_images:
        for stem in sorted(captions_without_images):
            warnings.append(f"Orphaned caption (no image): {stem}.txt")

    # --- Check 2: Caption content ---
    for cap_file in captions:
        text = cap_file.read_text(encoding="utf-8").strip()
        stats["caption_lengths"].append(len(text.split()))

        if not text.lower().startswith(TRIGGER_WORD.lower()):
            errors.append(
                f"Caption missing trigger word '{TRIGGER_WORD}': {cap_file.name}"
            )

        if "[DESCRIBE" in text or "TODO" in text.upper():
            warnings.append(f"Caption has unfilled placeholder: {cap_file.name}")

        if len(text.split()) < 10:
            warnings.append(f"Caption very short ({len(text.split())} words): {cap_file.name}")

    # --- Check 3: Image resolution ---
    if HAS_PIL:
        for img_file in images:
            try:
                with Image.open(img_file) as img:
                    w, h = img.size
                    stats["resolutions"].append((w, h))
                    min_side = min(w, h)
                    if min_side < MIN_RESOLUTION:
                        warnings.append(
                            f"Low resolution ({w}x{h}): {img_file.name}"
                        )
            except Exception as e:
                errors.append(f"Cannot open image {img_file.name}: {e}")
    else:
        warnings.append("Pillow not installed — skipping resolution checks. Run: pip install Pillow")

    # --- Check 4: Duplicate detection ---
    hashes = {}
    for img_file in images:
        h = file_hash(img_file)
        if h in hashes:
            warnings.append(
                f"Duplicate image: {img_file.name} == {hashes[h]}"
            )
        else:
            hashes[h] = img_file.name

    # --- Report ---
    print(f"  Images:   {stats['total_images']}")
    print(f"  Captions: {stats['total_captions']}")
    print(f"  Paired:   {len(image_stems & caption_stems)}")

    if stats["resolutions"]:
        widths = [r[0] for r in stats["resolutions"]]
        heights = [r[1] for r in stats["resolutions"]]
        print(f"  Resolution range: {min(widths)}x{min(heights)} to {max(widths)}x{max(heights)}")

    if stats["caption_lengths"]:
        avg_len = sum(stats["caption_lengths"]) / len(stats["caption_lengths"])
        print(f"  Avg caption length: {avg_len:.0f} words")

    if errors:
        print(f"\n  ❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    • {e}")

    if warnings:
        print(f"\n  ⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    • {w}")

    if not errors and not warnings:
        print(f"\n  ✅ Dataset looks good!")

    # --- Verdict ---
    print(f"\n{'='*60}")
    if errors:
        print("  VERDICT: ❌ Fix errors before training")
    elif warnings:
        print("  VERDICT: ⚠️  Review warnings, but trainable")
    else:
        print("  VERDICT: ✅ Ready for training!")
    print(f"{'='*60}\n")

    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate a LoRA training dataset"
    )
    parser.add_argument(
        "--dir", type=str, required=True,
        help="Directory containing dataset images and captions"
    )
    args = parser.parse_args()
    directory = Path(args.dir)

    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        return

    is_valid = validate_dataset(directory)
    exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
