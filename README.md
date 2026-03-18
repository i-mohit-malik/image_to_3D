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

> If you don’t have a key yet, create one at: https://platform.tripo3d.ai/api-keys

---

## ▶️ Run it

1. Put an image in `input_images/` (e.g. `input_images/photo.jpg`).
2. Run:

```bash
python src/main.py
```

Output is saved to:

- `output/<input_basename>.glb`

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
