# backend/routes/meta_router.py

"""Router for metadata-related operations."""

from auth.jwt_handler import decode_token
from config.logging import logger
from database.connection import sanitize  # Допустим, sanitize нужен
from database.execution import QueryMode, execute  # Допустим, execute нужен
from database.functions_meta import (
    get_cached_schema,
    get_cached_tables,
    get_enum_labels,
    get_enum_types,
)
from fastapi import APIRouter, Depends
from metadata.views import SchemaBuilder, SchemaView

meta_router = APIRouter(tags=["Meta"])
"""Router for metadata-related operations."""


@meta_router.get("/enums")
async def list_enum_types(payload: dict = Depends(decode_token)):
    """Lists all available enum types for the user's role."""
    return await get_enum_types(payload["role"])


@meta_router.get("/enums/{enum_type}")
async def list_enum_labels(enum_type: str, payload: dict = Depends(decode_token)):
    """Lists all labels for a specific enum type."""
    return await get_enum_labels(payload["role"], enum_type)


@meta_router.get("/tables")
async def list_tables(payload: dict = Depends(decode_token)):
    """Lists all database tables accessible to the user's role."""
    return await get_cached_tables(payload["role"])


async def get_table_schema(role: str, table: str):
    """Retrieves the schema definition for a specific table."""
    schema = await get_cached_schema(role, table)
    metagen = SchemaBuilder(schema)
    return metagen.build_base_schema(schema)


@meta_router.get("/tables/{table}/schema")
async def table_schema(table: str, payload: dict = Depends(decode_token)):
    """Fetches the schema of the specified table."""
    return await get_table_schema(payload["role"], table)


@meta_router.get("/tables/{table}/schema/WizardView")
async def table_wizard_schema(table: str, payload: dict = Depends(decode_token)):
    """Fetches the schema of the table in WizardView format."""
    schema = await get_cached_schema(payload["role"], table)
    metagen = SchemaBuilder(schema)
    return await metagen.build_wizard_view_schema(payload)


@meta_router.get("/tables/{table}/schema/{viewType}")
async def table_view_schema(
    table: str, viewType: SchemaView, payload: dict = Depends(decode_token)
):
    """Fetches the schema of the table for a specific view type."""
    logger.info(viewType.value)
    schema = await get_cached_schema(payload["role"], table)
    metagen = SchemaBuilder(schema)
    return metagen.build_view_schema(viewType)


@meta_router.get("/tables/schemas")
async def tables_schemas(payload: dict = Depends(decode_token)):
    """Fetches schemas for all tables accessible to the user's role."""
    schemas = {}
    tables = await get_cached_tables(payload["role"])
    for tab in tables:
        table = tab.get("table_name")
        schema = await table_schema(table, payload)
        schemas[table] = schema
    return schemas


@meta_router.get("/tables/{table}/refs")
async def get_back_refs(table: str, payload: dict = Depends(decode_token)):
    """Fetches information about tables referencing the given table."""
    fmt_table = sanitize(table)
    # await strip_validate_tab(payload["role"], fmt_table)
    query = "SELECT * FROM meta.get_back_refs($1)"
    params = (fmt_table,)
    back_refs = await execute(query, payload["role"], QueryMode.FETCH_ALL, params)
    return back_refs
