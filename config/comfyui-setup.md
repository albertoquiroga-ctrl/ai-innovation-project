# ComfyUI Local Setup — Windows + NVIDIA < 8GB VRAM

## Installation

### Step 1: Download ComfyUI Portable

1. Go to: https://github.com/comfyanonymous/ComfyUI/releases
2. Download: `ComfyUI_windows_portable_nvidia.7z`
3. Extract to: `D:\ComfyUI\` (or wherever you have space — needs ~30 GB total)

### Step 2: Install Git (if needed)

- Download: https://git-scm.com/download/win
- Default settings are fine

### Step 3: Install ComfyUI Manager

```bash
cd D:\ComfyUI\ComfyUI_windows_portable\ComfyUI\custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
```

### Step 4: Configure for Low VRAM

Edit `D:\ComfyUI\ComfyUI_windows_portable\run_nvidia_gpu.bat`:

Change the line to:
```batch
.\python_embeded\python.exe -s ComfyUI\main.py --lowvram --force-fp16
```

### Step 5: Download Models

Place these files in the correct folders:

```
ComfyUI\models\checkpoints\
  └── flux1-dev-fp8.safetensors          (~11.9 GB)
      Source: https://huggingface.co/Comfy-Org/flux1-dev/tree/main

ComfyUI\models\clip\
  ├── t5xxl_fp8_e4m3fn.safetensors       (~4.9 GB)
  │   Source: https://huggingface.co/comfyanonymous/flux_text_encoders/tree/main
  └── clip_l.safetensors                  (~235 MB)
      Source: same repo as above

ComfyUI\models\vae\
  └── ae.safetensors                      (~335 MB)
      Source: https://huggingface.co/black-forest-labs/FLUX.1-dev

ComfyUI\models\loras\
  └── sophie_v1.safetensors              (after training — ~50-200 MB)
```

**Total download: ~17 GB**

### Step 6: First Run

1. Double-click `run_nvidia_gpu.bat`
2. Wait for terminal to show "To see the GUI go to: http://127.0.0.1:8188"
3. Open that URL in your browser
4. You should see the ComfyUI node editor

### Step 7: Test Basic Generation

1. Load default workflow (should auto-load)
2. In "Load Checkpoint" node → select `flux1-dev-fp8`
3. In positive prompt → type: `a cozy living room, warm lighting, interior design magazine`
4. Click "Queue Prompt"
5. If it generates without errors → you're good!

**If you get OOM (Out of Memory):**
- Close other GPU-using apps (Chrome with hardware acceleration, games, etc.)
- Try adding `--cpu` flag for the VAE: `--lowvram --force-fp16 --vae-in-cpu`
- As last resort: use RunPod cloud for generation too (~$0.44/hr)

## Post-LoRA Workflow

After training and downloading your LoRA:

1. Copy `sophie_v1.safetensors` to `ComfyUI\models\loras\`
2. In ComfyUI, right-click canvas → Add Node → Loaders → Load LoRA
3. Connect: Load Checkpoint → **Load LoRA** → CLIP Text Encode
4. In Load LoRA node:
   - Select: `sophie_v1`
   - Strength Model: `0.7`
   - Strength CLIP: `0.7`
5. In your prompt, always start with trigger word: `sphie, ...`

## Useful Custom Nodes to Install (via Manager)

- **ComfyUI-Manager** (already installed)
- **rgthree's ComfyUI Nodes** — quality of life improvements
- **ComfyUI ControlNet Aux** — needed for room inpainting later
- **ComfyUI Impact Pack** — useful utilities
