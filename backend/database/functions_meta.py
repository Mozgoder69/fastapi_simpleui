# backend/database/functions_meta.py

"""Provides metadata utilities for database interactions."""

from enum import Enum
from typing import List
from aiocache import cached, Cache
from config.logging import logger
from database.connection import sanitize
from database.execution import QueryMode, execute
from fastapi import HTTPException


class QueryType(Enum):
    """Enumeration for query types."""

    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


async def get_enum_types(role: str):
    """Retrieve all enum types in the database."""
    query = "SELECT * FROM meta.get_enum_types()"
    return await execute(query, role, QueryMode.FETCH_ALL)


async def get_enum_labels(role: str, enum_name: str):
    """Fetch labels for a specific enum."""
    query = "SELECT * FROM meta.get_enum_labels($1)"
    params = (sanitize(enum_name),)
    return await execute(query, role, QueryMode.FETCH_ALL, params)


async def get_tables(role: str, qType: QueryType = QueryType.SELECT):
    """Fetch tables the user has permissions for."""
    query = "SELECT * FROM meta.get_available_tables($1, $2)"
    logger.info(query)
    params = (role, qType.value)
    return await execute(query, role, QueryMode.FETCH_ALL, params)


@cached(ttl=30, cache=Cache.MEMORY)
async def get_cached_tables(role: str, qType: QueryType = QueryType.SELECT):
    """Fetch and cache table metadata."""
    try:
        return await get_tables(role, qType)
    except Exception as e:
        logger.error(f"Cache error: {e}")
        raise HTTPException(500, "Cache failure")


async def strip_validate_tab(role: str, table: str):
    """Validate and sanitize a table name against allowed tables."""
    fmt_table = sanitize(table)  # Remove unwanted characters from table name
    visible = [rec["table_name"] for rec in await get_cached_tables(role)]
    if fmt_table not in visible:
        raise HTTPException(400, f"Invalid table: {fmt_table}. Check your input.")
    return fmt_table


async def get_schema(role: str, table: str):
    """Retrieve schema details for a specific table."""
    fmt_table = await strip_validate_tab(role, table)
    query = "SELECT * FROM meta.get_relation_metadata($1)"
    params = (fmt_table,)
    return await execute(query, role, QueryMode.FETCH_ALL, params)


@cached(ttl=30, cache=Cache.MEMORY)
async def get_cached_schema(role: str, table: str):
    """Fetch and cache schema details."""
    try:
        return await get_schema(role, table)
    except Exception as e:
        logger.error(f"Cache error: {e}")
        raise HTTPException(500, "Cache failure")


async def get_pk_columns(role: str, table: str) -> List[str]:
    """Fetch primary key columns for a specific table."""
    schema = await get_cached_schema(role, table)
    pk_columns = [
        col["column_name"]
        for col in schema
        if "primary key" in (col.get("const_type") or "").lower()
    ]
    if not pk_columns:
        raise ValueError(f"No primary key columns found for table {table}")
    return pk_columns
