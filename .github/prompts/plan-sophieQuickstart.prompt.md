# Sophie MVP — Guía Paso a Paso (Desde Cero)

> Te lleva desde "no tengo nada instalado" hasta "Sophie lista para Instagram".

---

## FASE 0: Preparar tu Máquina

### 0.1 — Verificar tu GPU

Abre PowerShell o CMD y corre:

```bash
nvidia-smi
```

Deberías ver algo como `NVIDIA GeForce RTX 3060` (o similar) y la memoria disponible.
Si no ves nada, instala los drivers NVIDIA: https://www.nvidia.com/drivers

### 0.2 — Instalar Python 3.10+

1. Ve a https://www.python.org/downloads/
2. Descarga Python 3.10 o superior (3.11 recomendado)
3. **IMPORTANTE:** Marca la casilla **"Add Python to PATH"** durante la instalación
4. Verifica:

```bash
python --version
```

### 0.3 — Instalar Git

1. Ve a https://git-scm.com/download/win
2. Instala con opciones por defecto
3. Verifica:

```bash
git --version
```

### 0.4 — Instalar dependencias del proyecto

```bash
cd "C:\Users\betoq\OneDrive\Documentos\GitHub\ai-innovation-project"
pip install Pillow PyYAML requests
```

### 0.5 — Instalar 7-Zip (para descomprimir ComfyUI)

Si no lo tienes: https://www.7-zip.org/download.html

---

## FASE 1: Instalar ComfyUI

### 1.1 — Descargar ComfyUI Portable

1. Ve a https://github.com/comfyanonymous/ComfyUI/releases
2. Descarga `ComfyUI_windows_portable_nvidia.7z`
3. Extrae a una carpeta con espacio (ej: `D:\ComfyUI\`) — necesitas ~30 GB

### 1.2 — Instalar ComfyUI Manager

```bash
cd D:\ComfyUI\ComfyUI_windows_portable\ComfyUI\custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
```

### 1.3 — Configurar para tu GPU (< 8GB VRAM)

Abre con Notepad:
```
D:\ComfyUI\ComfyUI_windows_portable\run_nvidia_gpu.bat
```

Cambia la línea principal a:
```batch
.\python_embeded\python.exe -s ComfyUI\main.py --lowvram --force-fp16
```

### 1.4 — Descargar los modelos (~17 GB total)

| Archivo | Tamaño | Fuente | Guardar en |
|---------|--------|--------|-----------|
| `flux1-dev-fp8.safetensors` | ~11.9 GB | https://huggingface.co/Comfy-Org/flux1-dev/tree/main | `ComfyUI\models\checkpoints\` |
| `t5xxl_fp8_e4m3fn.safetensors` | ~4.9 GB | https://huggingface.co/comfyanonymous/flux_text_encoders/tree/main | `ComfyUI\models\clip\` |
| `clip_l.safetensors` | ~235 MB | mismo repo | `ComfyUI\models\clip\` |
| `ae.safetensors` | ~335 MB | https://huggingface.co/black-forest-labs/FLUX.1-dev | `ComfyUI\models\vae\` |

### 1.5 — Primer arranque

1. Doble clic en `run_nvidia_gpu.bat`
2. Espera hasta ver: `To see the GUI go to: http://127.0.0.1:8188`
3. Abre esa URL en tu navegador

### 1.6 — Prueba rápida

1. En "Load Checkpoint" → selecciona `flux1-dev-fp8`
2. Prompt: `a cozy living room, warm lighting, interior design magazine`
3. Clic en **"Queue Prompt"**
4. Si genera sin errores: **ComfyUI funciona**

**Si sale "Out of Memory":** cierra Chrome, agrega `--vae-in-cpu` al .bat

---

## FASE 2: Generar el Dataset de Entrenamiento (30-40 imágenes)

> Aquí creas las fotos base de Sophie. Aún NO tienes LoRA, así que no serán 100% consistentes — eso está bien.

### 2.1 — Generar imágenes con los prompts

Abre `prompts/base-prompts.yaml`. Tiene 35 prompts en 4 categorías.

Para CADA prompt:
1. Cópialo al nodo positivo en ComfyUI
2. Reemplaza `{identity_anchor}` con:
   ```
   a 28 year old woman with wavy light brown hair, green eyes, light freckles, warm smile, thin gold chain necklace
   ```
3. Prompt negativo:
   ```
   deformed, ugly, bad anatomy, bad hands, extra fingers, mutated hands, poorly drawn face, mutation, extra limbs, missing arms, blurry, bad quality, watermark, text, logo, cartoon, anime, 3d render, oversaturated
   ```
4. Genera 2-3 variaciones (cambiando seed), elige la mejor
5. Guarda en: `datasets/sophie_v1/`

**Tips:** Selecciona las que se parezcan más entre sí, descarta manos raras o caras distintas.

### 2.2 — Nombrar y emparejar

```bash
cd "C:\Users\betoq\OneDrive\Documentos\GitHub\ai-innovation-project"

# Preview primero (no cambia nada):
python scripts/rename_and_pair.py --dir datasets/sophie_v1 --prefix sophie --dry-run

# Si se ve bien:
python scripts/rename_and_pair.py --dir datasets/sophie_v1 --prefix sophie
```

### 2.3 — Escribir los captions

Cada `.txt` tiene un placeholder. Edítalos para describir la imagen real:

```
sphie, a 28 year old woman with wavy light brown hair and green eyes, thin gold chain necklace, wearing cream oversized knit sweater, standing in bright studio holding fabric samples, soft natural window lighting, editorial photography
```

**Reglas:** Siempre empezar con `sphie`, describir ropa/pose/fondo/luz, mínimo 10 palabras.

Atajo para generar stubs base:
```bash
python scripts/caption_dataset.py --dir datasets/sophie_v1 --trigger sphie --generate-stubs
```

### 2.4 — Validar

```bash
python scripts/prepare_dataset.py --dir datasets/sophie_v1
```

Meta: `VERDICT: ✅ Ready for training!`

---

## FASE 3: Entrenar el LoRA en RunPod

### 3.1 — Crear cuentas

1. **RunPod:** https://www.runpod.io — agrega $10 USD
2. **Hugging Face:** https://huggingface.co — genera token en Settings → Access Tokens
3. **Acepta licencia Flux Dev:** https://huggingface.co/black-forest-labs/FLUX.1-dev

### 3.2 — FluxGym (método recomendado)

1. RunPod Dashboard → Pods → **"+ Deploy"**
2. Busca template: **"Next Diffusion – FluxGym"** → GPU: **RTX 4090**
3. Deploy → espera a que arranque → Connect → **HTTP Service :7860**

### 3.3 — Configurar y entrenar

Sube todos los archivos de `datasets/sophie_v1/` y configura:

| Parámetro | Valor |
|-----------|-------|
| Trigger Word | `sphie` |
| Steps | `1000` |
| Save Every N Steps | `200` |
| Learning Rate | `1e-4` |
| Batch Size | `1` |
| Resolution | `512` |
| LoRA Rank | `16` |

Clic **Start Training** → ~30-60 min

### 3.4 — Descargar y MATAR el pod

Descarga todos los checkpoints (step 200, 400, 600, 800, 1000).
Guárdalos en `output/loras/`.

**⚠️ DETÉN Y ELIMINA EL POD de inmediato. Te cobran por minuto.**

---

## FASE 4: Probar el LoRA

### 4.1 — Copiar a ComfyUI

Copia tu checkpoint (empieza con step 600 u 800) a:
```
D:\ComfyUI\...\ComfyUI\models\loras\sophie_v1.safetensors
```

### 4.2 — Conectar nodo LoRA

En ComfyUI: clic derecho → **Add Node → Loaders → Load LoRA**
- Conecta entre Load Checkpoint y CLIP Text Encode
- Selecciona `sophie_v1`, strength `0.7`

### 4.3 — Test

Prompt:
```
sphie, a 28 year old woman with wavy light brown hair and green eyes, portrait photo, soft natural lighting, Canon EOS R5, 85mm f/1.4, neutral background, warm tones
```

Varía fuerza entre 0.5 y 1.0 para encontrar el sweet spot.

- **Misma pose siempre** = overfitting → usa checkpoint más temprano
- **No se parece a Sophie** = underfitting → usa checkpoint más tardío o sube fuerza

---

## FASE 5: Generar Contenido Demo

### 5.1 — Feed (10 posts)

Con LoRA cargado, usa los prompts de `prompts/feed-prompts.yaml`.
Guarda en `output/feed/feed_01.png` a `feed_10.png`.

(Posts 07 y 08 son Before/After de habitación, NO usan LoRA de Sophie.)

### 5.2 — Stories (5 frames)

Usa `prompts/story-prompts.yaml`. Resolución vertical: `576x1024` o `768x1344`.
Guarda en `output/stories/`.

### 5.3 — Room Makeover (1 before/after)

1. Toma o busca una foto de habitación real (Before)
2. Instala ControlNet Aux desde ComfyUI Manager
3. Usa los estilos de `prompts/inpainting-prompts.yaml` para generar el After

### 5.4 — Videos (3 talking heads, herramientas externas)

1. Elige tu mejor retrato de Sophie (mirada a cámara)
2. HeyGen (https://www.heygen.com) o D-ID para lip-sync
3. ElevenLabs (https://elevenlabs.io) para la voz
4. Guiones en `docs/content-calendar.md`

---

## FASE 6: Verificación Final

### Checklist de entregables

```
output/
├── feed/
│   ├── feed_01.png  ← Sophie + mood board
│   ├── feed_02.png  ← Sophie midiendo pared
│   ├── feed_03.png  ← Sophie con paint swatches
│   ├── feed_04.png  ← Sophie styling bookshelf
│   ├── feed_05.png  ← Sophie en laptop
│   ├── feed_06.png  ← Sophie en flea market
│   ├── feed_07.png  ← Room BEFORE
│   ├── feed_08.png  ← Room AFTER
│   ├── feed_09.png  ← Sophie en fabric showroom
│   └── feed_10.png  ← Sophie sketching en café
├── stories/
│   ├── story_01.png  ← Selfie con café
│   ├── story_02.png  ← POV paint swatches
│   ├── story_03.png  ← BTS desk shot
│   ├── story_04.png  ← Poll A vs B
│   └── story_05.png  ← CTA "mándame tu room"
└── video/
    ├── intro.mp4     ← "Hi, I'm Sophie..."
    ├── tip.mp4       ← "The #1 mistake..."
    └── cta.mp4       ← "Send me a photo..."
```

### Comandos de validación

```bash
# ¿El dataset estaba limpio?
python scripts/prepare_dataset.py --dir datasets/sophie_v1

# ¿Cuántas imágenes generaste?
dir output\feed\*.png | find /c /v ""
dir output\stories\*.png | find /c /v ""
```

---

## Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| `nvidia-smi` no funciona | Instala drivers NVIDIA |
| `python` no se reconoce | Reinstala Python, marca "Add to PATH" |
| ComfyUI "Out of Memory" | Cierra Chrome, agrega `--vae-in-cpu` al .bat |
| LoRA: siempre misma pose | Overfitting → checkpoint más temprano o fuerza 0.5 |
| LoRA: no se parece a Sophie | Underfitting → checkpoint más tardío o fuerza 0.9+ |
| RunPod "Access denied" Flux | Acepta licencia en HuggingFace |

## Costos

| Item | Costo |
|------|-------|
| ComfyUI + Flux Dev | Gratis (local) |
| RunPod LoRA training | ~$0.50 |
| HeyGen starter | $24/mes |
| ElevenLabs starter | $5/mes |
| **Total mínimo MVP** | **~$40 USD** |
