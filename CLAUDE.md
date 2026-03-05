# CLAUDE.md — Sophie AI Influencer (MVP)

## What Is This Project

This is the MVP/proof-of-concept for **Alter**, a network of AI-native influencer avatars. The first avatar is **Sophie**, an AI interior design influencer. The goal is to demonstrate that we can create a consistent, engaging AI personality that produces content and provides personalized value (room makeover visualizations) at scale.

**This MVP does NOT include the automated AI engagement capabilities.** We are building the visual identity, content pipeline, and a manual "Wizard of Oz" demo of the killer feature (room inpainting). The AI engagement layer will be faked for the demo.

## Tech Context

- **Developer:** Beto — MBA student + entrepreneur, bilingual (ES/EN), comfortable with terminal/git/pip
- **Local Machine:** Windows, NVIDIA GPU with < 8GB VRAM
- **Image Generation:** ComfyUI (local, with --lowvram --force-fp16 flags) + Flux Dev fp8
- **LoRA Training:** RunPod cloud (RTX 4090, ~$0.44/hr)
- **Video/Voice:** HeyGen or D-ID + ElevenLabs (external tools, not scriptable)
- **Languages:** Python for scripts, JSON for ComfyUI workflows

## Project Structure

```
sophie-ai-influencer/
├── CLAUDE.md                    # You are here
├── README.md                    # Project overview
├── notebooks/
│   └── generate_dataset_colab.ipynb  # Upload to Google Colab to generate dataset
├── docs/
│   ├── brand-bible.md           # Sophie's identity, visual specs, personality
│   └── content-calendar.md      # Content plan for MVP demo
├── prompts/
│   ├── base-prompts.yaml        # Core image generation prompts for Sophie
│   ├── feed-prompts.yaml        # Instagram feed content prompts
│   ├── story-prompts.yaml       # Instagram stories prompts
│   └── inpainting-prompts.yaml  # Room makeover prompts
├── scripts/
│   ├── caption_dataset.py       # Auto-caption images for LoRA training
│   ├── prepare_dataset.py       # Validate & organize dataset files
│   ├── rename_and_pair.py       # Rename images + create paired .txt stubs
│   └── test_lora_strengths.py   # Generate comparison grid at different strengths
├── config/
│   ├── runpod-fluxgym.md        # Step-by-step RunPod training instructions
│   ├── training-params.yaml     # LoRA hyperparameters
│   └── comfyui-setup.md         # Local ComfyUI installation checklist
├── datasets/
│   └── sophie_v1/               # Training images + caption .txt files go here
└── output/
    ├── feed/                    # Generated Instagram feed images
    ├── stories/                 # Generated Instagram stories images
    └── video/                   # Talking head video assets
```

## Key Commands

```bash
# Prepare dataset (validate images + captions are paired)
python scripts/prepare_dataset.py --dir datasets/sophie_v1

# Auto-caption images (generates .txt files with trigger word)
python scripts/caption_dataset.py --dir datasets/sophie_v1 --trigger "sphie"

# Rename images sequentially and create caption stubs
python scripts/rename_and_pair.py --dir datasets/sophie_v1 --prefix "sophie"
```

## Rules for Claude Code

1. **All scripts must be Python 3.10+ compatible** and run on Windows
2. **Use only standard library + these pip packages:** Pillow, PyYAML, requests
3. **Never hardcode paths** — use argparse or relative paths from project root
4. **Prompts go in YAML files**, not hardcoded in scripts
5. **All user-facing text should be in English** (Beto is bilingual, but the influencer content targets English-speaking audiences). Comments in code can be English or Spanish.
6. **ComfyUI workflows are JSON files** — Claude Code can generate and modify these
7. **Don't try to call external APIs** (HeyGen, ElevenLabs, RunPod) from scripts — those are manual steps. Document them in markdown instead.

## Current Phase

**PHASE 1: Identity & Dataset Preparation**
- [x] Project structure created
- [x] Brand Bible finalized
- [x] Base prompts defined (35 prompts in base-prompts.yaml)
- [x] Feed prompts defined (10 posts in feed-prompts.yaml)
- [x] Story prompts defined (5 frames in story-prompts.yaml)
- [x] Inpainting prompts defined (5 styles in inpainting-prompts.yaml)
- [x] Training params configured (training-params.yaml)
- [x] All scripts tested and working (prepare_dataset, rename_and_pair, caption_dataset)
- [x] Expanded prompts generated (output/expanded_*.txt — ready to paste into ComfyUI)
- [x] Dependencies installed (Pillow, PyYAML, requests)
- [x] Colab notebook created for dataset generation (notebooks/generate_dataset_colab.ipynb)
- [ ] ~~ComfyUI installed locally~~ (SKIPPED: GPU 3GB VRAM + 6GB RAM + 27GB disk = impossible)
- [ ] Dataset images generated (via Google Colab — Flux.1-schnell on free T4 GPU)
- [ ] Dataset captioned and validated
- [ ] LoRA trained on RunPod

## The "Alter" Parent Project (Context Only)

Sophie is one avatar in a larger network called "Alter." The other avatars (Liam/Tech, Maya/Skincare, Kaito/Gaming, Elena/Finance, Marcus/Fitness, Jett/Music, Zara/Travel) are NOT in scope for this MVP. They share the same "Trojan Horse" strategy: 80% entertainment content to build a fanbase, 20% AI-powered utility that drives conversions.

Sophie's "Superhuman Ability" is **Predictive In-Painting**: users upload a photo of their room, and Sophie generates an "After" image with the client's furniture seamlessly placed. For the MVP, this is done manually via ComfyUI inpainting, not automated.
