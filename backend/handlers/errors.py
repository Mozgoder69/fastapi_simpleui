# backend/handlers/errors.py

"""Handles various types of exceptions and returns appropriate HTTP responses."""

from config.logging import logger
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from jose import JWTError


async def http_error_handler(request: Request, exc: HTTPException):
    """Handles HTTP exceptions and returns a JSON response."""
    logger.warning(f"HTTPException: {exc.detail} - Status code: {exc.status_code}")
    return JSONResponse({"message": exc.detail}, exc.status_code)


async def jwt_error_handler(request: Request, exc: JWTError):
    """Handles JWT-related errors and returns a 401 response."""
    logger.error(f"JWTError: {str(exc)}")
    return JSONResponse({"message": "Invalid or expired token"}, 401)


async def general_error_handler(request: Request, exc: Exception):
    """Handles general exceptions and returns a 500 response."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse({"message": f"{exc}"}, 500)
