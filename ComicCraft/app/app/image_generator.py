"""Panel illustrations. Tries Stable Diffusion (GPU), then Gemini image, then a placeholder."""
import logging
import re
import textwrap
import threading
import uuid
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from . import config
from .gemini_client import get_client

log = logging.getLogger("comiccraft")
SIZE = 640
_sd_lock = threading.Lock()
_sd_pipe = None


def _slug(text: str) -> str:
    """Safe filename part."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:40] or "panel"


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def _stable_diffusion(prompt: str) -> Image.Image:
    global _sd_pipe
    import torch
    from diffusers import StableDiffusionPipeline

    with _sd_lock:  # one image at a time
        cuda = torch.cuda.is_available()
        if _sd_pipe is None:
            log.info("Loading Stable Diffusion (first time downloads ~4 GB)...")
            pipe = StableDiffusionPipeline.from_pretrained(
                config.SD_MODEL_ID, torch_dtype=torch.float16 if cuda else torch.float32)
            pipe = pipe.to("cuda" if cuda else "cpu")
            pipe.enable_attention_slicing()
            _sd_pipe = pipe
        steps = config.SD_STEPS or (25 if cuda else 15)
        return _sd_pipe(prompt, negative_prompt="text, watermark, blurry, deformed, extra limbs",
                        num_inference_steps=steps, guidance_scale=7.5,
                        height=512, width=512).images[0]


def _gemini_image(prompt: str) -> Image.Image:
    response = get_client().models.generate_content(model=config.IMAGE_MODEL, contents=prompt)
    for candidate in response.candidates or []:
        parts = (candidate.content.parts if candidate.content else None) or []
        for part in parts:
            if getattr(part, "inline_data", None) and part.inline_data.data:
                return Image.open(BytesIO(part.inline_data.data))
    raise RuntimeError("Gemini returned no image")


def _placeholder(prompt: str, panel_number: int) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), (255, 210, 63))
    draw = ImageDraw.Draw(img)
    draw.rectangle([12, 12, SIZE - 12, SIZE - 12], outline=(21, 21, 31), width=6)
    try:
        font = ImageFont.load_default(size=26)
    except TypeError:  # very old Pillow
        font = ImageFont.load_default()
    draw.text((40, 40), f"Panel {panel_number} (placeholder image)", fill=(21, 21, 31), font=font)
    wrapped = "\n".join(textwrap.wrap(prompt, 34)[:12])
    draw.multiline_text((40, 100), wrapped, fill=(21, 21, 31), font=font, spacing=8)
    return img


def _finish(img: Image.Image) -> Image.Image:
    """Centre-crop to a square so every panel has the same shape."""
    img = img.convert("RGB")
    w, h = img.size
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    return img.crop((left, top, left + s, top + s)).resize((SIZE, SIZE))


def _backend_order() -> list:
    choice = config.IMAGE_BACKEND
    if choice == "auto":
        return (["diffusers"] if _cuda_available() else []) + ["gemini", "placeholder"]
    if choice in ("diffusers", "gemini"):
        return [choice, "placeholder"]
    return ["placeholder"]


def generate_image(prompt: str, art_style: str = "comic book", panel_number: int = 1) -> str:
    """Create one panel image, save it in static/panels and return its file path."""
    full_prompt = (f"{art_style} style comic panel illustration, {prompt}, "
                   "vibrant colors, bold ink outlines, no text, no speech bubbles")
    image = None
    for backend in _backend_order():
        try:
            if backend == "diffusers":
                image = _stable_diffusion(full_prompt)
            elif backend == "gemini":
                image = _gemini_image(full_prompt)
            else:
                image = _placeholder(prompt, panel_number)
            log.info("Panel %s made with %s", panel_number, backend)
            break
        except Exception as exc:
            log.warning("Image backend %s failed: %s", backend, exc)
    path = config.PANELS_DIR / f"panel_{panel_number}_{_slug(prompt)}_{uuid.uuid4().hex[:6]}.png"
    _finish(image).save(path)
    return str(path)
