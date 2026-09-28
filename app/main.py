from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router


BASE_DIR = Path(__file__).resolve().parent.parent

# Create required folders
(BASE_DIR / "static" / "panels").mkdir(
    parents=True,
    exist_ok=True
)

(BASE_DIR / "static" / "exports").mkdir(
    parents=True,
    exist_ok=True
)


app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="AI-powered comic story creator using Gemini and Stable Diffusion.",
    version="1.0.0"
)


# Serve CSS, generated images and exported PDFs
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)


# Register application routes
app.include_router(router)