"""App entry point. Run with:  uvicorn app.main:app --reload"""
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import config
from .routes import router

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

app = FastAPI(title="ComicCraft")
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")
app.include_router(router)
