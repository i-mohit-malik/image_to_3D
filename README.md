# Image‑to‑3D Generator (Tripo 3D)

A tiny CLI tool that turns a single input image into a 3D model using the **Tripo 3D API**.

---

## 🚀 Quick start (recommended)

### Windows (PowerShell)
```powershell
.\setup.ps1
```

### macOS / Linux
```bash
./setup.sh
```

Those scripts create a `.venv`, install dependencies, and get you ready to run.

---

## 🧩 Configure your API key

Create `.env` in the repo root and add your Tripo key:

```env
TRIPO_API_KEY=tsk_YOUR_REAL_KEY
```

Here’s an example `.env` showing the supported settings:

```env
TRIPO_API_KEY=tsk_YOUR_REAL_KEY
TRIPO_API_BASE_URL=https://api.tripo3d.ai/v2/openapi
INPUT_IMAGE_PATH=input_images/images.jpg
OUTPUT_DIR=output
```

(Optional) Override where the model is saved (defaults to `output/`):

```env
# OUTPUT_DIR=output
```

> If you don’t have a key yet, create one at: https://platform.tripo3d.ai/api-keys

---

## ▶️ Run it

1. Put an image in `input_images/` (e.g. `input_images/photo.jpg`) and copy path in .env file.
2. Run:

```bash
python src/main.py
```

The script prints where it saved the generated model (absolute path). By default the file is written into:

- `output/<input_basename>.glb`

If you change `OUTPUT_DIR` in `.env`, it will save there instead.

---

## 📁 What’s in this repo

- `src/main.py` — upload → task → poll → download workflow
- `src/config.py` — loads `.env` and sets API settings
- `input_images/` — where you drop source images
- `output/` — where generated models appear

---

## Notes

- `.env` is excluded from Git to avoid leaking secrets.
- If you want different output types, edit `src/main.py`.
