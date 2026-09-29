"""Matches each panel's image with its story text."""
import re
from pathlib import Path

_HEADER = re.compile(r"^\W*PANEL\s*(\d+)\b[^\n]*$", re.IGNORECASE | re.MULTILINE)


def split_story(story: str) -> dict:
    """{1: 'NARRATION...', 2: '...'} from the 'PANEL n:' blocks."""
    found = list(_HEADER.finditer(story))
    parts = {}
    for i, match in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(story)
        parts[int(match.group(1))] = story[match.end():end].strip()
    return parts


def build_comic_layout(outline, story, image_paths):
    """List of dicts: panel_number, title, image_path, image_url, text."""
    parts = split_story(story)
    layout = []
    for panel, image_path in zip(outline, image_paths):
        number = panel["panel_number"]
        layout.append({
            "panel_number": number,
            "title": panel["title"],
            "image_path": str(image_path),
            "image_url": f"/static/panels/{Path(image_path).name}",
            "text": parts.get(number) or panel["scene"],  # fall back to the outline scene
        })
    return layout
