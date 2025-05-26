# backend/database/execution.py

"""Executes database queries and handles related errors."""

from enum import Enum
from typing import Any, Optional, Tuple

from asyncpg.exceptions import (
    CheckViolationError,
    ForeignKeyViolationError,
    NotNullViolationError,
    UniqueViolationError,
)
from config.logging import logger
from database.connection import DBCon
from fastapi import HTTPException


class QueryMode(Enum):
    """Enumeration of query execution modes."""

    EXECUTE = 0
    FETCH_ALL = 1
    FETCH_ROW = 2
    FETCH_ONE = 3


# Mapping of specific database exceptions to HTTP exceptions
DB_ERROR_MAP = {
    CheckViolationError: (400, "Check constraint violation"),
    ForeignKeyViolationError: (409, "Foreign key violation"),
    NotNullViolationError: (400, "Required field missing"),
    UniqueViolationError: (409, "Duplicate record"),
}


def handle_db_error(e: Exception) -> None:
    """Convert database exceptions to HTTP exceptions."""
    for exc_type, (status_code, detail) in DB_ERROR_MAP.items():
        if isinstance(e, exc_type):
            # Convert known database errors into corresponding HTTP exceptions
            raise HTTPException(status_code=status_code, detail=detail) from e
    # If exception is not in the mapping, re-raise it
    raise e


async def execute(
    query: str, role: str, qMode: QueryMode, params: Optional[Tuple[Any, ...]] = None
):
    """Execute a database query with the specified mode and parameters."""
    logger.info(f"Role: [yellow]{role}[/yellow], Params: {params} \nQuery: {query};")
    try:
        params = params or ()

        async with DBCon.connect(role) as con:
            if qMode == QueryMode.FETCH_ONE:
                # Execute query and return a single value
                return await con.fetchval(query, *params)
            elif qMode == QueryMode.FETCH_ROW:
                # Execute query and return a single row as a dictionary
                if record := await con.fetchrow(query, *params):
                    return dict(record)
                raise HTTPException(status_code=404, detail="Item not found")
            elif qMode == QueryMode.FETCH_ALL:
                # Execute query and return all rows as a list of dictionaries
                records = await con.fetch(query, *params)
                return [dict(record) for record in records] if records else []
            elif qMode == QueryMode.EXECUTE:
                # Execute query without returning data
                await con.execute(query, *params)
                return {"detail": "Operation completed successfully"}

    except Exception as e:
        try:
            # Handle known database errors
            handle_db_error(e)
        except Exception as e:
            logger.error(f"Failed To Execute Operation: {e}")
            raise HTTPException(status_code=500, detail="Operation Failed") from e
