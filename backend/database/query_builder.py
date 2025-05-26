# backend/database/query_builder.py

"""Provides utilities for building dynamic SQL queries and managing schema-based record definitions."""

from typing import Any, Dict, Generic, List, Tuple, TypeVar

from database.functions_meta import get_cached_schema, get_pk_columns
from pydantic import BaseModel, model_validator
from cachetools import TTLCache


class DictModel(BaseModel):
    """Base class for models with validation for non-empty fields."""

    @model_validator(mode="after")
    def check_non_empty(cls, values):
        """Ensure that all fields are not None."""
        for field_name, value in values.dict().items():
            if value is None:
                raise ValueError(f"{field_name} must not be None")
        return values


T = TypeVar("T")


class Records(BaseModel, Generic[T]):
    records: List[T]


class DataOnly(DictModel):
    """Model for representing data-only payloads."""

    data: Dict[str, Any]


class KeysOnly(DictModel):
    """Model for representing primary key-only payloads."""

    keys: Dict[str, Any]


class KeyedData(DictModel):
    """Model for representing payloads with primary keys and data."""

    keys: Dict[str, Any]
    data: Dict[str, Any]


DataOnlyList = Records[DataOnly]
"""Model for a list of data-only records."""
KeysOnlyList = Records[KeysOnly]
"""Model for a list of primary key-only records."""
KeyedDataList = Records[KeyedData]
"""Model for a list of records with primary keys and data."""


def split_record(
    record: Dict[str, Any], pk_cols: List[str]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Split a record into keys (primary keys) and data (non-primary keys)."""
    return {k: record[k] for k in pk_cols}, {
        k: v for k, v in record.items() if k not in pk_cols
    }


class CRUDQueries:
    """SQL templates for common CRUD operations."""

    INSERT = "INSERT INTO pi.{table} ({columns}) VALUES {records} RETURNING *;"
    SELECT = "SELECT {columns} FROM pi.{table} {where_clause};"
    DELETE = "DELETE FROM pi.{table} {where_clause} RETURNING *;"
    UPDATE = "WITH cte ({columns}) AS (VALUES {records}) UPDATE pi.{table} SET {set_clause} FROM cte {where_clause} RETURNING *;"


class CRUD:
    """Cache and generate SQL queries dynamically based on table schema."""

    def __init__(self):
        """Initialize the CRUD class with an empty query cache."""
        self.query_cache = TTLCache(maxsize=128, ttl=30)

    async def get_queries(self, role: str, table: str) -> Dict[str, Any]:
        """Retrieve or generate cached queries for a specific table."""
        if table not in self.query_cache:
            # Retrieve table schema from cache
            schema = await get_cached_schema(role, table)
            if not schema:
                raise ValueError(f"No schema for table {table}")

            # Retrieve primary key columns
            columns = [col["column_name"] for col in schema]
            pk_cols = await get_pk_columns(role, table)
            if not pk_cols:
                raise ValueError(f"No primary key for table {table}")

            # Define columns to update (excluding primary keys)
            set_cols = [col for col in columns if col not in pk_cols]

            # Extract column types
            column_types = {col["column_name"]: col["data_type"] for col in schema}

            # Cache SQL templates
            self.query_cache[table] = {
                "gen_many": CRUDQueries.INSERT,
                "list_many": CRUDQueries.SELECT,
                "trim_many": CRUDQueries.DELETE,
                "upd_many": CRUDQueries.UPDATE,
                "columns": columns,
                "pk_cols": pk_cols,
                "set_cols": set_cols,
                "column_types": column_types,
            }
        return self.query_cache[table]
