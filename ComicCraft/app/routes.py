"""All web routes: the form pages and the JSON API."""
import logging
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from . import config
from .exporters import save_pdf
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .schemas import PromptRequest

log = logging.getLogger("comiccraft")
router = APIRouter()
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))


def run_pipeline(data: PromptRequest):
    """outline -> story -> images -> layout -> PDF."""
    outline = generate_outline(data.prompt, data.character_name, data.setting,
                               data.tone, data.art_style, data.num_panels)
    story = generate_story(outline, data.character_name, data.tone, data.prompt)
    images = [generate_image(p["image_prompt"], data.art_style, p["panel_number"]) for p in outline]
    layout = build_comic_layout(outline, story, images)
    pdf_path = save_pdf(layout, title=data.prompt[:80])
    return layout, pdf_path


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate", response_class=HTMLResponse)
def generate(request: Request,
             prompt: str = Form(...),
             character_name: str = Form("Hero"),
             setting: str = Form(""),
             tone: str = Form("dramatic"),
             art_style: str = Form("comic book"),
             num_panels: int = Form(5)):
    form = {"prompt": prompt, "character_name": character_name, "setting": setting,
            "tone": tone, "art_style": art_style, "num_panels": num_panels}
    try:
        data = PromptRequest(**{**form, "character_name": character_name or "Hero"})
        layout, pdf_path = run_pipeline(data)
    except Exception as exc:
        log.exception("Comic generation failed")
        return templates.TemplateResponse(request=request, name="index.html",
                                          context={"error": str(exc), "form": form}, status_code=500)
    return templates.TemplateResponse(request=request, name="comic_preview.html", context={
        "panels": layout, "title": data.prompt, "pdf_filename": Path(pdf_path).name})


@router.post("/generate-comic/json")
def generate_comic_json(data: PromptRequest):
    try:
        layout, pdf_path = run_pipeline(data)
    except Exception as exc:
        log.exception("Comic generation failed")
        raise HTTPException(status_code=500, detail=str(exc))
    return {"panels": layout, "pdf_path": pdf_path, "pdf_url": f"/static/exports/{Path(pdf_path).name}"}


@router.get("/export-success", response_class=HTMLResponse)
def export_success(request: Request, file: str):
    name = Path(file).name  # blocks path tricks like ../../
    if not (config.EXPORTS_DIR / name).is_file():
        raise HTTPException(status_code=404, detail="PDF not found")
    return templates.TemplateResponse(request=request, name="export_success.html",
                                      context={"pdf_filename": name})


@router.get("/test-image")
def test_image(prompt: str = "a brave fox exploring an enchanted forest", art_style: str = "comic book"):
    try:
        path = generate_image(prompt, art_style, 0)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"image_path": path, "image_url": f"/static/panels/{Path(path).name}"}
