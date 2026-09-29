"""Gemini Flash: fast, structured 5-panel comic outline (JSON)."""
import json
import re

from . import config
from .gemini_client import GeminiError, generate_text

FLASH_MODELS = [config.FLASH_MODEL]
SYSTEM = "You are a comic book story planner. You reply ONLY with valid JSON, nothing else."


def _extract_json(text: str):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(1))


def generate_outline(prompt, character_name="Hero", setting="", tone="dramatic",
                     art_style="comic book", num_panels=5):
    """Return a list of dicts: panel_number, title, scene, image_prompt."""
    request = f"""Create a {num_panels}-panel comic outline.
Story idea: {prompt}
Main character: {character_name}
Setting: {setting or 'your choice'}
Tone: {tone}
Art style: {art_style}

Return a JSON array of exactly {num_panels} objects with these keys:
- "panel_number": integer starting at 1
- "title": short panel title
- "scene": 1-2 sentences describing what happens
- "image_prompt": under 35 words describing the picture for an image generator
  (character, action, setting, camera angle). Describe {character_name}'s look the
  same way in every panel. Do NOT ask for text, captions or speech bubbles.
The story must have a clear beginning, middle and end."""
    problem = "no panels returned"
    for _ in range(2):  # one retry if the JSON is broken
        try:
            raw = generate_text(request, FLASH_MODELS, SYSTEM)
            data = _extract_json(raw)
            items = data.get("panels", []) if isinstance(data, dict) else data
            panels = [
                {
                    "panel_number": i,
                    "title": str(item.get("title", f"Panel {i}")).strip(),
                    "scene": str(item.get("scene", "")).strip(),
                    "image_prompt": str(item.get("image_prompt") or item.get("scene", prompt)).strip(),
                }
                for i, item in enumerate(items[:num_panels], start=1)
            ]
            if panels:
                return panels
        except (ValueError, AttributeError) as exc:  # JSONDecodeError is a ValueError
            problem = str(exc)
    raise GeminiError(f"Could not read the outline from Gemini ({problem}). Please try again.")
