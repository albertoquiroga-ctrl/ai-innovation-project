"""
expand_prompts.py — Expand YAML prompts into ready-to-paste text for ComfyUI.

Usage:
    python scripts/expand_prompts.py --file prompts/base-prompts.yaml
    python scripts/expand_prompts.py --file prompts/feed-prompts.yaml
    python scripts/expand_prompts.py --file prompts/base-prompts.yaml --output output/expanded_prompts.txt

Replaces {identity_anchor} with the actual description so you can
copy-paste directly into ComfyUI without manual editing.
"""

import argparse
from pathlib import Path

import yaml


def expand_prompts(yaml_path: Path, output_path: Path | None = None):
    """Read YAML file and expand all prompts with identity_anchor."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    identity_anchor = data.get("identity_anchor", "").strip()
    negative = data.get("negative", "").strip()
    lines = []

    lines.append(f"# Expanded prompts from: {yaml_path.name}")
    lines.append(f"# Generated — copy-paste into ComfyUI\n")

    if negative:
        lines.append("=" * 60)
        lines.append("NEGATIVE PROMPT (use for all):")
        lines.append("=" * 60)
        lines.append(negative)
        lines.append("")

    # Handle base-prompts.yaml (dataset_prompts key)
    if "dataset_prompts" in data:
        for item in data["dataset_prompts"]:
            name = item.get("name", "unnamed")
            prompt = item.get("prompt", "").strip()
            prompt = prompt.replace("{identity_anchor}", identity_anchor)
            lines.append("-" * 60)
            lines.append(f"[{name}]")
            lines.append("-" * 60)
            lines.append(prompt)
            lines.append("")

    # Handle feed-prompts.yaml (feed_posts key)
    if "feed_posts" in data:
        for item in data["feed_posts"]:
            post_id = item.get("id", "unnamed")
            concept = item.get("concept", "")
            prompt = item.get("prompt", "").strip()
            prompt = prompt.replace("{identity_anchor}", identity_anchor)
            caption = item.get("caption_idea", "")
            lines.append("-" * 60)
            lines.append(f"[{post_id}] {concept}")
            lines.append(f"  Caption: {caption}")
            lines.append("-" * 60)
            lines.append(prompt)
            lines.append("")

    # Handle story-prompts.yaml (story_frames key)
    if "story_frames" in data:
        for item in data["story_frames"]:
            story_id = item.get("id", "unnamed")
            concept = item.get("concept", "")
            prompt = item.get("prompt", "").strip()
            prompt = prompt.replace("{identity_anchor}", identity_anchor)
            lines.append("-" * 60)
            lines.append(f"[{story_id}] {concept}")
            lines.append("-" * 60)
            lines.append(prompt)
            lines.append("")

    # Handle inpainting-prompts.yaml (styles key)
    if "styles" in data:
        for style_name, style_data in data["styles"].items():
            desc = style_data.get("description", "")
            prompt = style_data.get("prompt", "").strip()
            lines.append("-" * 60)
            lines.append(f"[{style_name}] {desc}")
            lines.append("-" * 60)
            lines.append(prompt)
            lines.append("")

    text = "\n".join(lines)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
        print(f"Wrote {len(lines)} lines to {output_path}")
    else:
        print(text)


def main():
    parser = argparse.ArgumentParser(
        description="Expand YAML prompts into ready-to-paste text"
    )
    parser.add_argument("--file", required=True, help="Path to YAML prompt file")
    parser.add_argument("--output", default=None, help="Output .txt file (optional)")
    args = parser.parse_args()

    yaml_path = Path(args.file)
    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found")
        return

    output_path = Path(args.output) if args.output else None
    expand_prompts(yaml_path, output_path)


if __name__ == "__main__":
    main()
