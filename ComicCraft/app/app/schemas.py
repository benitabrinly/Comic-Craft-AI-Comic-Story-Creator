"""Pydantic model that validates the JSON API input."""
from pydantic import BaseModel, ConfigDict, Field


class PromptRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    prompt: str = Field(min_length=3, max_length=500)
    character_name: str = Field(default="Hero", max_length=60)
    setting: str = Field(default="", max_length=120)
    tone: str = Field(default="dramatic", max_length=40)
    art_style: str = Field(default="comic book", max_length=40)
    num_panels: int = Field(default=5, ge=1, le=8)
