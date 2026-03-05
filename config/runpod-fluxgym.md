# RunPod — LoRA Training for Sophie

## Pre-Flight Checklist

Before renting GPU time, have these ready locally:

- [ ] `datasets/sophie_v1/` folder with 30-40 images + .txt captions
- [ ] Run `python scripts/prepare_dataset.py --dir datasets/sophie_v1` — all green
- [ ] RunPod account created: https://www.runpod.io
- [ ] $10 USD added to RunPod balance
- [ ] Hugging Face account + token: https://huggingface.co/settings/tokens
- [ ] Accepted Flux Dev license on HuggingFace: https://huggingface.co/black-forest-labs/FLUX.1-dev

## Option A: FluxGym (Easiest — GUI Based)

### 1. Deploy Pod

1. Go to RunPod Dashboard → Pods → "+ Deploy"
2. Search for template: **"Next Diffusion – FluxGym"**
   - If not found: use any PyTorch template + RTX 4090
3. Select GPU: **RTX 4090** (Community Cloud, ~$0.44/hr)
4. Click **"Deploy On-Demand"**
5. Wait for pod to start (1-2 min)

### 2. Connect

1. Click **Connect** on your pod
2. Select **HTTP Service → :7860**
3. FluxGym UI opens in your browser

### 3. Upload Dataset

1. In FluxGym, find the dataset upload area
2. Upload all images + .txt files from `datasets/sophie_v1/`
3. Set trigger word: `sphie`

### 4. Configure Training

```
Trigger Word:        sphie
Training Steps:      1000
Save Every N Steps:  200
Learning Rate:       1e-4
Batch Size:          1
Resolution:          512
LoRA Rank:           16
```

### 5. Start Training

- Click "Start Training"
- Takes ~30-60 min depending on dataset size
- Monitor the loss curve — it should decrease and stabilize

### 6. Download Results

- Navigate to the output folder in FluxGym
- Download ALL checkpoint files (step 200, 400, 600, 800, 1000)
- Each is a `.safetensors` file (~50-200 MB)

### 7. STOP THE POD

**⚠️ IMMEDIATELY stop and delete the pod after downloading. You're charged per minute.**

## Option B: SimpleTuner (More Control)

### 1. Deploy Pod

Same as Option A — RTX 4090, any PyTorch template.

### 2. Open Terminal

Click Connect → Jupyter Lab (port 8888) → Terminal

### 3. Install SimpleTuner

```bash
cd /workspace
git clone --branch=release https://github.com/bghira/SimpleTuner.git
cd SimpleTuner
python -m venv .venv
source .venv/bin/activate
pip install -U poetry pip
poetry install --no-root
pip install optimum-quanto
```

### 4. Login to HuggingFace

```bash
huggingface-cli login
# Paste your token when prompted
# Press 'n' when asked about Git credential
```

### 5. Upload Dataset

Via Jupyter Lab file browser, upload your dataset to:
```
/workspace/sophie_dataset/
```

### 6. Configure

Edit `config.env`:
- Find every instance of `m0del` and replace with `sphie`
- Set paths to point to `/workspace/sophie_dataset/`
- Adjust training steps, LR, etc. per `config/training-params.yaml`

### 7. Train

```bash
bash train.sh
# If prompted about wandb: select option 3 (disable)
# Training takes ~30-60 min
# Optimal checkpoint is usually around step 1600 of 2000
```

### 8. Download

- Navigate to `SimpleTuner/outputs/models/`
- Download checkpoint folders — each contains `pytorch_lora_weights.safetensors`
- Right-click → Download

### 9. STOP THE POD

**⚠️ DELETE THE POD. Every minute costs money.**

## After Training: Local Setup

1. Rename your best checkpoint to `sophie_v1.safetensors`
2. Copy to: `ComfyUI/models/loras/sophie_v1.safetensors`
3. Restart ComfyUI
4. In your workflow, add a "Load LoRA" node between Checkpoint and CLIP
5. Select `sophie_v1`, set strength to `0.7`
6. Test with the prompt from `config/training-params.yaml` → `test_prompt`

## Troubleshooting

**"Out of memory" during training:**
- Reduce batch size to 1
- Reduce resolution to 512
- Enable gradient checkpointing

**LoRA produces same face/angle regardless of prompt (overfitting):**
- Use an earlier checkpoint (e.g., step 600 instead of 1000)
- Lower the LoRA strength to 0.5-0.6
- Next training: use more diverse dataset, lower learning rate

**LoRA doesn't look like Sophie at all:**
- Check that captions all start with trigger word `sphie`
- Check that dataset images are consistent (same person)
- Try a later checkpoint or higher LoRA strength (0.9-1.0)
- Next training: use higher rank (32), more steps

**FluxGym won't start:**
- Check if antivirus is blocking RunPod API
- Try a different browser
- Check terminal for error messages
