"""
caption_dataset.py — Generate or fix caption files for LoRA training.

Usage:
    # Add trigger word to existing captions that are missing it
    python scripts/caption_dataset.py --dir datasets/sophie_v1 --trigger sphie --fix

    # Generate basic stub captions for images without .txt files
    python scripts/caption_dataset.py --dir datasets/sophie_v1 --trigger sphie --generate-stubs

What this does:
    --fix: Prepends trigger word to any caption that doesn't start with it
    --generate-stubs: Creates .txt files for images that don't have captions
"""

import argparse
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

# Sophie's consistent physical description for captions
IDENTITY_DESCRIPTION = (
    "a 28 year old woman with wavy light brown hair, green eyes, "
    "light freckles, thin gold chain necklace"
)


def fix_trigger_words(directory: Path, trigger: str):
    """Prepend trigger word to captions that don't start with it."""
    fixed = 0
    for txt_file in sorted(directory.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8").strip()
        if not text.lower().startswith(trigger.lower()):
            new_text = f"{trigger}, {text}"
            txt_file.write_text(new_text, encoding="utf-8")
            print(f"  FIXED: {txt_file.name}")
            fixed += 1
    print(f"\nFixed {fixed} captions.")


def generate_stubs(directory: Path, trigger: str):
    """Create .txt stub files for images missing captions."""
    created = 0
    for img_file in sorted(directory.iterdir()):
        if img_file.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        txt_path = img_file.with_suffix(".txt")
        if not txt_path.exists():
            stub = (
                f"{trigger}, {IDENTITY_DESCRIPTION}, "
                f"[DESCRIBE: outfit/clothing], [DESCRIBE: action/pose], "
                f"[DESCRIBE: setting/background], [DESCRIBE: lighting], "
                f"editorial photography"
            )
            txt_path.write_text(stub, encoding="utf-8")
            print(f"  CREATED: {txt_path.name}")
            created += 1

    print(f"\nCreated {created} caption stubs.")
    if created > 0:
        print("⚠️  Remember to edit the [DESCRIBE: ...] placeholders with actual descriptions!")


def show_stats(directory: Path, trigger: str):
    """Show current caption statistics."""
    images = [f for f in directory.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]
    captions = list(directory.glob("*.txt"))

    with_trigger = 0
    without_trigger = 0
    has_placeholders = 0

    for txt_file in captions:
        text = txt_file.read_text(encoding="utf-8").strip()
        if text.lower().startswith(trigger.lower()):
            with_trigger += 1
        else:
            without_trigger += 1
        if "[DESCRIBE" in text:
            has_placeholders += 1

    print(f"\n  Images: {len(images)}")
    print(f"  Captions: {len(captions)}")
    print(f"  Missing captions: {len(images) - len(captions)}")
    print(f"  With trigger '{trigger}': {with_trigger}")
    print(f"  Without trigger: {without_trigger}")
    print(f"  With placeholders to fill: {has_placeholders}")


def main():
    parser = argparse.ArgumentParser(description="Manage dataset captions")
    parser.add_argument("--dir", type=str, required=True, help="Dataset directory")
    parser.add_argument("--trigger", type=str, default="sphie", help="Trigger word")
    parser.add_argument("--fix", action="store_true", help="Add trigger word to captions missing it")
    parser.add_argument("--generate-stubs", action="store_true", help="Create stub captions for uncaptioned images")
    parser.add_argument("--stats", action="store_true", help="Show caption statistics only")

    args = parser.parse_args()
    directory = Path(args.dir)

    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        return

    if args.stats or (not args.fix and not args.generate_stubs):
        show_stats(directory, args.trigger)

    if args.fix:
        print("\nFixing trigger words...")
        fix_trigger_words(directory, args.trigger)

    if args.generate_stubs:
        print("\nGenerating caption stubs...")
        generate_stubs(directory, args.trigger)


if __name__ == "__main__":
    main()
