# backend/main.py
"""Main entry point for the FastAPI backend application."""

import uvicorn
from auth.jwt_handler import decode_token
from config.logging import log_cfg, logger
from config.settings import settings
from database.connection import pools
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from handlers.errors import general_error_handler, http_error_handler, jwt_error_handler
from jose import JWTError
from routes.auth_router import manual_token
from setup.openapi import setup_schemas
from setup.routers import setup_routes


async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the FastAPI application."""
    setup_user = settings.database.get_role("endpoint")
    # Get access token for the configured user
    token = await manual_token(setup_user.uname, setup_user.pword)
    # Decode token and store payload in app state
    app.state.payload = await decode_token(token["access_token"])
    role = app.state.payload.get("role", "customer")
    # Setup application routes
    await setup_routes(app, role)
    # Setup OpenAPI schemas based on user roles
    await setup_schemas(app, role)
    app.state.payload = None
    yield
    # Close all connection pools on shutdown
    await pools.close_all_pools()


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.cors.allow_origins,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)

if not settings.front_res_path.exists():
    logger.error(f"Frontend path {settings.front_res_path} not found")
    raise RuntimeError("Frontend directory missing")
app.mount("/static", StaticFiles(directory=str(settings.front_res_path)), name="static")

app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(JWTError, jwt_error_handler)
app.add_exception_handler(Exception, general_error_handler)

lh = settings.server.host
lp = settings.server.port


# Start Uvicorn server if script is run directly
if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=lh, port=lp, reload=True, log_config=log_cfg, log_level="info"
    )
