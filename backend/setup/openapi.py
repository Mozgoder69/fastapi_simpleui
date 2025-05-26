# backend/setup/openapi.py

"""Module for setting up OpenAPI schemas."""

from config.logging import logger
from database.functions_meta import get_cached_tables
from fastapi import FastAPI
from routes.meta_router import get_table_schema


async def setup_schemas(app: FastAPI, role: str):
    """Generate and initialize OpenAPI schemas dynamically based on user roles."""
    tables = await get_cached_tables(role)
    schemas = {}
    for tab in tables:
        table = tab.get("table_name")
        try:
            schema = await get_table_schema(role, table)
            schemas[table] = schema
            logger.info(f"Created JSON-Schema '{table}'")
        except Exception as e:
            logger.info(f"Insufficient access was prevented for table '{table}': {e}")
    initialize_openapi(app, schemas)
    app.openapi_schema = None
    app.openapi()
    logger.info("OpenAPI schema has been updated and cached")


def initialize_openapi(app: FastAPI, schemas: dict):
    """Customize OpenAPI schema to include additional table schemas."""

    # Create a clean copy of schemas to add custom tables
    clean_schemas = {table: schema for table, schema in schemas.items()}
    original_openapi = app.openapi

    def new_openapi():
        """Generate a new OpenAPI schema with custom components."""
        if app.openapi_schema:
            return app.openapi_schema
        if original_openapi is None:
            raise RuntimeError("OpenAPI schema is not available")

        # Retrieve original OpenAPI schema
        openapi_schema = original_openapi()

        # Update schema components with new tables
        openapi_schema["components"]["schemas"].update(clean_schemas)

        # Cache the updated schema
        app.openapi_schema = openapi_schema
        logger.info("OpenAPI schema generated successfully")
        return app.openapi_schema

    # Override the OpenAPI schema generation method
    app.openapi = new_openapi
