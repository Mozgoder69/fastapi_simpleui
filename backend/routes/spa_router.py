# backend/routes/spa_router.py

"""Router for serving the Single Page Application (SPA)."""

from os.path import join

from config.logging import logger
from config.settings import settings
from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

spa_router = APIRouter(tags=["SPA"])
"""Router for serving the Single Page Application (SPA)."""


@spa_router.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """Serves the SPA for non-API paths."""
    logger.info(f"Request received for path: {full_path}")
    # Skip serving SPA for API requests
    if full_path.startswith("api/"):
        logger.info(f"API request detected for {full_path}, skipping...")
        raise HTTPException(status_code=404)  # Throw 404, to allow FastAPI search route
    # Serve SPA for all other requests
    logger.info(f"SPA request detected for {full_path}, serving index.html")
    return FileResponse(join(str(settings.front_res_path), "index.html"))
