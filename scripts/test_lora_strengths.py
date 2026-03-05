"""
test_lora_strengths.py - Build a reproducible LoRA checkpoint/strength test plan.

This script does not generate images by itself. It creates a manifest that you can
use while testing in ComfyUI so you can compare checkpoints and strengths with a
consistent prompt and naming convention.

Usage examples:
    python scripts/test_lora_strengths.py \
        --checkpoints-dir output/loras \
        --output-dir output/lora_tests \
        --dry-run

    python scripts/test_lora_strengths.py \
        --checkpoints-dir output/loras \
        --output-dir output/lora_tests \
        --manifest output/lora_tests/manifest.json

    python scripts/test_lora_strengths.py \
        --checkpoints-dir output/loras \
        --checkpoints sophie_step600.safetensors,sophie_step800.safetensors \
        --strengths 0.5,0.6,0.7,0.8,0.9,1.0
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    yaml = importlib.import_module("yaml")
except ImportError:
    yaml = None

LORA_EXTENSIONS = {".safetensors", ".pt", ".ckpt"}
DEFAULT_PROMPT = (
    "sphie, a 28 year old woman with wavy light brown hair and green eyes, "
    "portrait photo, soft natural lighting, Canon EOS R5, 85mm f/1.4, "
    "neutral background, warm tones"
)
DEFAULT_STRENGTHS = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


@dataclass
class TestJob:
    """A single generation job in the checkpoint/strength grid."""

    checkpoint_name: str
    checkpoint_path: str
    strength_model: float
    strength_clip: float
    prompt: str
    output_image: str


def parse_strengths(raw: str) -> list[float]:
    """Parse and validate comma-separated strengths."""
    values = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            value = float(token)
        except ValueError as exc:
            raise ValueError(f"Invalid strength value '{token}'") from exc

        if value < 0:
            raise ValueError(f"Strength must be >= 0, got {value}")
        values.append(round(value, 3))

    if not values:
        raise ValueError("At least one strength must be provided")
    return values


def load_training_defaults(config_path: Path) -> tuple[str, list[float]]:
    """Load default prompt and strengths from config/training-params.yaml."""
    if not config_path.exists() or yaml is None:
        return DEFAULT_PROMPT, DEFAULT_STRENGTHS

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return DEFAULT_PROMPT, DEFAULT_STRENGTHS

    prompt = data.get("test_prompt") or DEFAULT_PROMPT
    strengths = data.get("test_strengths") or DEFAULT_STRENGTHS

    if not isinstance(prompt, str):
        prompt = DEFAULT_PROMPT

    if not isinstance(strengths, list):
        strengths = DEFAULT_STRENGTHS

    cleaned_strengths: list[float] = []
    for item in strengths:
        try:
            value = float(item)
        except (ValueError, TypeError):
            continue
        if value >= 0:
            cleaned_strengths.append(round(value, 3))

    if not cleaned_strengths:
        cleaned_strengths = DEFAULT_STRENGTHS

    return prompt.strip(), cleaned_strengths


def extract_training_step(file_name: str) -> int:
    """Extract an approximate step number from file names for natural sorting."""
    name = file_name.lower()

    for pattern in (r"step[_-]?(\d+)", r"s(\d{3,5})"):
        match = re.search(pattern, name)
        if match:
            return int(match.group(1))

    all_numbers = re.findall(r"(\d{3,5})", name)
    if all_numbers:
        return int(all_numbers[-1])

    return 10**9


def discover_checkpoints(checkpoints_dir: Path, explicit: list[str] | None) -> list[Path]:
    """Resolve checkpoint paths from explicit names or by scanning a folder."""
    if explicit:
        resolved = []
        missing = []
        for item in explicit:
            candidate = checkpoints_dir / item
            if candidate.exists() and candidate.suffix.lower() in LORA_EXTENSIONS:
                resolved.append(candidate)
            else:
                missing.append(item)

        if missing:
            missing_text = ", ".join(missing)
            raise FileNotFoundError(f"Could not find checkpoints: {missing_text}")
        return resolved

    if not checkpoints_dir.exists():
        raise FileNotFoundError(f"Checkpoints directory does not exist: {checkpoints_dir}")

    files = [
        path
        for path in checkpoints_dir.iterdir()
        if path.is_file() and path.suffix.lower() in LORA_EXTENSIONS
    ]

    files.sort(key=lambda p: (extract_training_step(p.name), p.name.lower()))
    return files


def build_jobs(
    checkpoints: list[Path],
    strengths: list[float],
    prompt: str,
    output_dir: Path,
    clip_strength: float | None,
) -> list[TestJob]:
    """Build the full checkpoint x strength matrix."""
    jobs: list[TestJob] = []

    for checkpoint in checkpoints:
        stem = checkpoint.stem
        for strength in strengths:
            clip = strength if clip_strength is None else clip_strength
            suffix = f"s{strength:.2f}".replace(".", "p")
            output_name = f"{stem}_{suffix}.png"

            jobs.append(
                TestJob(
                    checkpoint_name=checkpoint.name,
                    checkpoint_path=str(checkpoint),
                    strength_model=strength,
                    strength_clip=round(clip, 3),
                    prompt=prompt,
                    output_image=str(output_dir / output_name),
                )
            )

    return jobs


def write_manifest(manifest_path: Path, jobs: list[TestJob], metadata: dict[str, Any]) -> None:
    """Write manifest JSON with metadata and flat job list."""
    payload = {
        "metadata": metadata,
        "jobs": [job.__dict__ for job in jobs],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def print_summary(jobs: list[TestJob], manifest_path: Path, dry_run: bool) -> None:
    """Print a concise summary of the generated test matrix."""
    checkpoint_names = sorted({job.checkpoint_name for job in jobs})
    strengths = sorted({job.strength_model for job in jobs})

    print("\n" + "=" * 60)
    print("  LoRA STRENGTH TEST PLAN")
    print("=" * 60)
    print(f"  Checkpoints: {len(checkpoint_names)}")
    print(f"  Strengths:   {len(strengths)} -> {strengths}")
    print(f"  Total jobs:  {len(jobs)}")
    print(f"  Manifest:    {manifest_path}")
    print("=" * 60 + "\n")

    preview = jobs[: min(6, len(jobs))]
    print("Preview jobs:")
    for job in preview:
        print(
            f"  - {job.checkpoint_name} | model={job.strength_model:.2f} "
            f"| clip={job.strength_clip:.2f} | {Path(job.output_image).name}"
        )

    if len(jobs) > len(preview):
        print(f"  ... and {len(jobs) - len(preview)} more")

    if dry_run:
        print("\nDry run only: no manifest file was written.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a LoRA checkpoint/strength comparison manifest"
    )
    parser.add_argument(
        "--checkpoints-dir",
        type=str,
        default="output/loras",
        help="Directory containing LoRA checkpoints (.safetensors/.pt/.ckpt)",
    )
    parser.add_argument(
        "--checkpoints",
        type=str,
        default="",
        help="Optional comma-separated checkpoint names to test",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/lora_tests",
        help="Directory where test images should be saved",
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default="",
        help="Path to output JSON manifest (default: <output-dir>/manifest.json)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="",
        help="Prompt to use for all jobs (defaults from config/training-params.yaml)",
    )
    parser.add_argument(
        "--strengths",
        type=str,
        default="",
        help="Comma-separated strengths, e.g. 0.5,0.6,0.7",
    )
    parser.add_argument(
        "--clip-strength",
        type=float,
        default=None,
        help="Fixed CLIP strength for all jobs (default: same as model strength)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/training-params.yaml",
        help="Training config file used for default prompt/strengths",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview matrix without writing the manifest file",
    )

    args = parser.parse_args()

    checkpoints_dir = Path(args.checkpoints_dir)
    output_dir = Path(args.output_dir)
    config_path = Path(args.config)

    default_prompt, default_strengths = load_training_defaults(config_path)
    prompt = args.prompt.strip() if args.prompt else default_prompt

    try:
        strengths = parse_strengths(args.strengths) if args.strengths else default_strengths
    except ValueError as exc:
        raise SystemExit(f"Error: {exc}")

    explicit = [item.strip() for item in args.checkpoints.split(",") if item.strip()]

    try:
        checkpoints = discover_checkpoints(checkpoints_dir, explicit if explicit else None)
    except FileNotFoundError as exc:
        raise SystemExit(f"Error: {exc}")

    if not checkpoints:
        raise SystemExit(
            "Error: No checkpoints found. Add LoRA files to the checkpoints directory first."
        )

    jobs = build_jobs(
        checkpoints=checkpoints,
        strengths=strengths,
        prompt=prompt,
        output_dir=output_dir,
        clip_strength=args.clip_strength,
    )

    manifest_path = Path(args.manifest) if args.manifest else output_dir / "manifest.json"

    metadata = {
        "checkpoints_dir": str(checkpoints_dir),
        "output_dir": str(output_dir),
        "prompt": prompt,
        "strengths": strengths,
        "clip_strength": args.clip_strength,
        "notes": (
            "Use each manifest entry with the same seed/sampler in ComfyUI to compare "
            "identity consistency and overfitting across checkpoints and strengths."
        ),
    }

    if not args.dry_run:
        write_manifest(manifest_path=manifest_path, jobs=jobs, metadata=metadata)

    print_summary(jobs=jobs, manifest_path=manifest_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
