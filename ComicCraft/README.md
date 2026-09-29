# ComicCraft - AI Comic Story Creator

Type a story idea and ComicCraft writes a panel-by-panel comic with Google Gemini, draws each panel,
shows a preview in the browser and exports a PDF. Built with FastAPI, Gemini, Stable Diffusion and FPDF.

## How it works
1. `gemini_flash.py` - Gemini Flash makes a JSON outline (title, scene, image prompt per panel).
2. `gemini_pro.py` - Gemini Pro writes narration and dialogue.
3. `image_generator.py` - draws each panel (Stable Diffusion on a GPU, else Gemini image, else a placeholder).
4. `layout_builder.py` - matches every image with its text.
5. `exporters.py` - saves the comic as a PDF in `static/exports/`.
6. `routes.py` / `main.py` - FastAPI pages and API.

## Setup (Windows)
```
python -m venv comiccraft-env
comiccraft-env\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Open `.env` and paste your key from https://aistudio.google.com/apikey as `GEMINI_API_KEY`.

## Run
```
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 (API docs at /docs).

## Image options (`IMAGE_BACKEND` in .env)
- `auto` (default): Stable Diffusion if an NVIDIA GPU is found, otherwise Gemini image, otherwise placeholder.
- `diffusers`: force Stable Diffusion. Run `pip install -r requirements-sd.txt` first (slow without a GPU).
- `gemini`: use the Gemini image model. `placeholder`: plain yellow panels, for testing.

## Routes
| Route | What it does |
|---|---|
| `GET /` | Input form |
| `POST /generate` | Form submit, generates the comic, shows the preview |
| `POST /generate-comic/json` | Same, JSON in and JSON out |
| `GET /export-success` | Confirmation page and PDF download |
| `GET /test-image` | Tests image generation only |

## Push to GitHub
```
git init
git add .
git commit -m "ComicCraft project"
git branch -M main
git remote add origin https://github.com/<your-username>/comiccraft.git
git push -u origin main
```
`.env` is in `.gitignore`, so your API key is not uploaded.
