# backend/setup/routers.py

"""Module for setting up application routes."""

from config.logging import logger
from fastapi import FastAPI
from routes.auth_router import auth_router
from routes.bss_ops.activity import activity_router
from routes.bss_ops.ctg_items import ctg_items_router
from routes.bss_ops.ctg_rules import ctg_rules_router
from routes.bss_ops.ext_reg import ext_reg_router
from routes.bss_ops.int_reg import int_reg_router
from routes.bss_ops.mkg_line import mkg_line_router
from routes.bss_ops.org_line import org_line_router
from routes.bss_ops.reports import reports_router
from routes.crud_router import crud_router
from routes.meta_router import meta_router
from routes.spa_router import spa_router


async def setup_routes(app: FastAPI, role: str):
    """Set up application routes including API and GraphQL endpoints."""
    # Include various API routers with the "/api" prefix
    app.include_router(auth_router, prefix="/api")
    app.include_router(meta_router, prefix="/api")
    app.include_router(crud_router, prefix="/api")
    app.include_router(activity_router, prefix="/api")
    app.include_router(ctg_items_router, prefix="/api")
    app.include_router(ctg_rules_router, prefix="/api")
    app.include_router(ext_reg_router, prefix="/api")
    app.include_router(int_reg_router, prefix="/api")
    app.include_router(mkg_line_router, prefix="/api")
    app.include_router(org_line_router, prefix="/api")
    app.include_router(reports_router, prefix="/api")
    # Include the router for the Single Page Application without a prefix
    app.include_router(spa_router)
    logger.info("Routes have been set up successfully.")
