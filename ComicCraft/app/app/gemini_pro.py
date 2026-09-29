"""Gemini Pro: turns the outline into narration + dialogue for every panel."""
import json

from . import config
from .gemini_client import generate_text

PRO_MODELS = [config.PRO_MODEL, "gemini-3.5-flash"]
SYSTEM = "You are a creative comic book writer. You write in plain text only, never markdown."


def generate_story(outline, character_name="Hero", tone="dramatic", prompt="") -> str:
    """Return one text block containing every panel's story."""
    request = f"""Turn this comic outline into a finished comic script.
Story idea: {prompt}
Main character: {character_name}
Tone: {tone}

Outline (JSON):
{json.dumps(outline, indent=2)}

Write EVERY panel in exactly this plain-text format (no markdown, no asterisks):

PANEL 1: <title>
NARRATION: <one or two vivid sentences>
DIALOGUE:
<Speaker>: "<short line>"
<Speaker>: "<short line>"

Rules: one block per panel, in order; 1-3 short dialogue lines per panel; keep the
{tone} tone; finish the story in the last panel."""
    story = generate_text(request, PRO_MODELS, SYSTEM, temperature=0.9)
    return story.replace("*", "").replace("#", "")
