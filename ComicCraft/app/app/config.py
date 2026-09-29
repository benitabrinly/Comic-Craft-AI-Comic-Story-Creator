"""Central settings: folders, API key and model names (read from .env)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"
TEMPLATES_DIR = BASE_DIR / "templates"
for _folder in (PANELS_DIR, EXPORTS_DIR):
    _folder.mkdir(parents=True, exist_ok=True)


def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


GEMINI_API_KEY = _get("GEMINI_API_KEY") or _get("GOOGLE_API_KEY")
FLASH_MODEL = _get("GEMINI_FLASH_MODEL", "gemini-2.5-flash")
PRO_MODEL = _get("GEMINI_PRO_MODEL", "gemini-2.5-pro")
IMAGE_MODEL = _get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
IMAGE_BACKEND = _get("IMAGE_BACKEND", "auto").lower()
SD_MODEL_ID = _get("SD_MODEL_ID", "stable-diffusion-v1-5/stable-diffusion-v1-5")
SD_STEPS = int(_get("SD_STEPS", "0") or 0)  # 0 = automatic (25 on GPU, 15 on CPU)
