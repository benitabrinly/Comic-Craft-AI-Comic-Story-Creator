"""Shared Gemini helper: one client, and automatic fallback to other models."""
import logging
from functools import lru_cache

from google import genai
from google.genai import types

from . import config

log = logging.getLogger("comiccraft")


class GeminiError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    if not config.GEMINI_API_KEY:
        raise GeminiError("GEMINI_API_KEY is missing. Add it to the .env file and restart the server.")
    return genai.Client(api_key=config.GEMINI_API_KEY)


def generate_text(prompt, models, system_instruction=None, json_mode=False, temperature=0.9) -> str:
    """Try each model name in order until one returns text."""
    client = get_client()
    cfg = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
        response_mime_type=None,
    )
    errors = []
    for model in dict.fromkeys(models):  # removes duplicates, keeps order
        try:
            response = client.models.generate_content(model=model, contents=prompt, config=cfg)
            if response.text and response.text.strip():
                return response.text.strip()
            errors.append(f"{model}: empty response")
        except Exception as exc:
            log.warning("Gemini model %s failed: %s", model, exc)
            errors.append(f"{model}: {str(exc)[:160]}")
    raise GeminiError("All Gemini models failed. " + " | ".join(errors))
