# Sophie — AI Interior Design Influencer (MVP)

> Part of the **Alter** AI-Native Influencer Network

Sophie is a hyper-realistic AI avatar who creates interior design content on Instagram/TikTok. She builds an audience through aesthetic organization videos, color theory education, and DIY content — then drives conversions by offering personalized room makeover visualizations using AI inpainting.

## Quick Start

```bash
# 1. Clone this repo
git clone <repo-url> && cd sophie-ai-influencer

# 2. Install Python dependencies
pip install Pillow PyYAML requests

# 3. Read the setup guide
cat config/comfyui-setup.md

# 4. Start generating (after ComfyUI is installed)
# Use prompts from prompts/base-prompts.yaml in ComfyUI
```

## MVP Scope

- [x] Visual identity (Brand Bible)
- [x] Image generation pipeline (ComfyUI + Flux Dev)
- [x] LoRA training for face consistency (RunPod)
- [x] Content batch for demo Instagram profile
- [x] Talking head videos (HeyGen + ElevenLabs)
- [x] Room makeover demo (manual inpainting)
- [ ] ~~Automated DM engagement~~ (post-MVP)
- [ ] ~~Automated content posting~~ (post-MVP)
- [ ] ~~Client furniture catalog integration~~ (post-MVP)

## Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| Image Generation | ComfyUI + Flux Dev fp8 | Free (local) |
| Face Consistency | Custom LoRA (trained on RunPod) | ~$5/training |
| Video | HeyGen or D-ID | $24-59/mo |
| Voice | ElevenLabs | $5-22/mo |
| Room Inpainting | ComfyUI + ControlNet | Free (local) |

## Project Structure

See [CLAUDE.md](CLAUDE.md) for full structure and development instructions.

## Utility Commands

```bash
# Validate image/caption pairing and quality checks
python scripts/prepare_dataset.py --dir datasets/sophie_v1

# Add/fix trigger words and generate caption stubs
python scripts/caption_dataset.py --dir datasets/sophie_v1 --trigger sphie --stats

# Rename images sequentially and create paired .txt stubs
python scripts/rename_and_pair.py --dir datasets/sophie_v1 --prefix sophie --dry-run

# Build a checkpoint x strength test manifest for LoRA QA
python scripts/test_lora_strengths.py --checkpoints-dir output/loras --output-dir output/lora_tests --dry-run
```
