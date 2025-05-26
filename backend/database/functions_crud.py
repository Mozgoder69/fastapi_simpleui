# backend/database/functions_crud.py

"""Defines CRUD operations for handling database records."""

from typing import Any, Dict, List, Literal, Optional

from config.logging import logger
from database.connection import ConType, DBCon
from database.execution import QueryMode, execute
from database.functions_meta import strip_validate_tab
from database.query_builder import (
    CRUD,
    DataOnly,
    DataOnlyList,
    KeyedData,
    KeyedDataList,
    KeysOnly,
    KeysOnlyList,
    split_record,
)
from fastapi import HTTPException
from pydantic import BaseModel
from utils.serialization import transform_values_types

# Initialize CRUD instance for query caching and generation
crud = CRUD()
"""Instance of the CRUD class for query caching and generation."""


async def gen_many(
    role: str, table: str, data_only_list: DataOnlyList
) -> KeyedDataList:
    """Insert multiple records into a table."""
    if not data_only_list.records:
        raise ValueError("Empty records list")

    # Validate and sanitize table name
    table = await strip_validate_tab(role, table)

    # Retrieve preformatted CRUD queries for the table
    queries = await crud.get_queries(role, table)

    # Extract column names from the first record
    columns = list(data_only_list.records[0].data.keys())

    # Prepare list of values for each record
    records_values = [[r.data[col] for col in columns] for r in data_only_list.records]

    # Flatten the list of lists into a single list of parameters
    params = [val for record in records_values for val in record]

    cols_count = len(columns)

    # Construct SQL fragment for multiple record insertion with parameter placeholders
    records_sql = ", ".join(
        f"({', '.join(f'${i * cols_count + j + 1}' for j in range(cols_count))})"
        for i in range(len(data_only_list.records))
    )

    # Formulate the complete SQL query using the table name, columns, and records
    query = queries["gen_many"].format(
        table=table,
        columns=", ".join(f'"{c}"' for c in columns),
        records=records_sql,
    )

    # Execute the query and fetch the inserted records
    result = await execute(query, role, QueryMode.FETCH_ALL, tuple(params))
    if not result:
        raise HTTPException(status_code=500, detail="Insert failed")

    return KeyedDataList(
        records=[
            KeyedData(keys=keys, data=data)
            for keys, data in (split_record(r, queries["pk_cols"]) for r in result)
        ]
    )


async def list_many(
    role: str,
    table: str,
    conditions: Dict[str, Any] = None,
    columns: List[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> KeyedDataList:
    """Select multiple records from a table with optional filtration and pagination."""

    # Validate and sanitize table name
    table = await strip_validate_tab(role, table)

    # Retrieve preformatted CRUD queries for the table
    queries = await crud.get_queries(role, table)

    # Prepare filter conditions and corresponding parameters
    params = []
    where_clauses = []
    if conditions:
        for k, v in conditions.items():
            if k not in queries["columns"]:
                raise HTTPException(status_code=400, detail=f"Invalid column: {k}")
            param_index = len(params) + 1
            where_clauses.append(f'"{k}" = ${param_index}')
            params.append(v)

    # Construct the WHERE clause with filters and pagination
    where_clause = f"WHERE {' AND '.join(where_clauses)} " if where_clauses else ""
    where_clause += f"LIMIT {limit} OFFSET {offset}"

    # Determine columns to select
    select_columns = "*" if not columns else ", ".join(f'"{c}"' for c in columns)

    # Formulate the complete SQL query
    query = queries["list_many"].format(
        columns=select_columns,
        table=table,
        where_clause=where_clause,
    )

    # Execute the query and fetch the records
    result = await execute(query, role, QueryMode.FETCH_ALL, tuple(params))

    return KeyedDataList(
        records=[
            KeyedData(keys=keys, data=data)
            for keys, data in (split_record(r, queries["pk_cols"]) for r in result)
        ]
    )


async def trim_many(
    role: str, table: str, keys_only_list: KeysOnlyList
) -> KeyedDataList:
    """Delete multiple records from a table."""
    if not keys_only_list.records:
        raise ValueError("Empty keys list")

    # Validate and sanitize table name
    table = await strip_validate_tab(role, table)

    # Retrieve preformatted CRUD queries for the table
    queries = await crud.get_queries(role, table)

    # Prepare primary key values for each record to delete
    pk_count = len(queries["pk_cols"])
    records_values = [
        [k.keys[col] for col in queries["pk_cols"]] for k in keys_only_list.records
    ]

    # Flatten the list of lists into a single list of parameters
    params = [val for record in records_values for val in record]

    # Construct WHERE conditions for each record based on primary keys
    conditions = [
        f"({' AND '.join(f'"{col}" = ${i * pk_count + j + 1}' for j, col in enumerate(queries['pk_cols']))})"
        for i in range(len(keys_only_list.records))
    ]

    # Formulate the complete WHERE clause with OR conditions for multiple records
    query = queries["trim_many"].format(
        table=table, where_clause=f"WHERE {' OR '.join(conditions)}"
    )

    # Execute the delete query and fetch the deleted records
    result = await execute(query, role, QueryMode.FETCH_ALL, tuple(params))
    if not result:
        raise HTTPException(status_code=404, detail="No records deleted")

    return KeyedDataList(
        records=[
            KeyedData(keys=keys, data=data)
            for keys, data in (split_record(r, queries["pk_cols"]) for r in result)
        ]
    )


async def upd_many(
    role: str, table: str, keyed_data_list: KeyedDataList
) -> KeyedDataList:
    """Update multiple records in a table using keyed data records and CTE."""
    if not keyed_data_list.records:
        raise ValueError("Empty records list")

    # Validate and sanitize table name
    table = await strip_validate_tab(role, table)

    # Retrieve preformatted CRUD queries for the table
    queries = await crud.get_queries(role, table)

    # Determine columns to update, excluding primary keys
    update_cols = sorted(
        set().union(*(r.data.keys() for r in keyed_data_list.records))
        - set(queries["pk_cols"])
    )
    if not update_cols:
        raise HTTPException(status_code=400, detail="No columns to update")

    # Retrieve column types for proper type casting in SQL
    column_types = queries["column_types"]

    # Define the complete list of columns: primary keys + columns to update
    columns = queries["pk_cols"] + list(update_cols)

    # Collect parameters in the correct order: primary keys followed by update values
    params = []
    for record in keyed_data_list.records:
        # Add primary key values
        for col in queries["pk_cols"]:
            params.append(record.keys[col])
        # Add update values
        for col in update_cols:
            params.append(record.data[col])

    # Construct WHERE conditions for each record based on primary keys
    conditions = []
    for _ in keyed_data_list.records:
        condition = " AND ".join(
            f'{table}."{col}"::{column_types[col]} = cte."{col}"::{column_types[col]}'
            for col in queries["pk_cols"]
        )
        conditions.append(f"({condition})")

    # Formulate the complete WHERE clause with OR conditions for multiple records
    where_clause = f"WHERE {' OR '.join(conditions)}"

    # Construct SQL fragment for updating multiple records with type casting
    cols_count = len(columns)
    records_sql = ", ".join(
        f"({', '.join(f'${i * cols_count + j + 1}::{column_types[columns[j]]}' for j in range(cols_count))})"
        for i in range(len(keyed_data_list.records))
    )

    # Formulate the complete SQL update query
    query = queries["upd_many"].format(
        table=table,
        columns=", ".join(f'"{c}"' for c in columns),
        records=records_sql,
        set_clause=", ".join(f'"{c}" = cte."{c}"' for c in update_cols),
        where_clause=where_clause,
    )

    # Execute the update query and fetch the updated records
    result = await execute(query, role, QueryMode.FETCH_ALL, tuple(params))
    if not result:
        raise HTTPException(status_code=404, detail="No records updated")

    return KeyedDataList(
        records=[
            KeyedData(keys=keys, data=data)
            for keys, data in (split_record(r, queries["pk_cols"]) for r in result)
        ]
    )


def get_first_record(results: KeyedDataList) -> KeyedData:
    """Fetch the first record from a list of results or raise an HTTPException if none are found."""
    if not results.records:
        raise HTTPException(status_code=404, detail="Record not found")
    logger.debug(f"Returning first record: {results.records[0]}")
    return results.records[0]


async def new_one(role: str, table: str, data_only: DataOnly) -> KeyedData:
    """Use gen_many to insert a single record into a table."""

    results = await gen_many(role, table, DataOnlyList(records=[data_only]))
    return get_first_record(results)


async def read_one(
    role: str, table: str, keys_only: KeysOnly, columns: List[str] = None
) -> KeyedData:
    """Use list_many with keys as a condition to select a single record from a table."""

    results = await list_many(role, table, keys_only.keys, columns, 1)
    return get_first_record(results)


async def del_one(role: str, table: str, keys_only: KeysOnly) -> KeyedData:
    """Use trim_many to delete a single record from a table."""

    results = await trim_many(role, table, KeysOnlyList(records=[keys_only]))
    return get_first_record(results)


async def edit_one(role: str, table: str, keyed_data: KeyedData) -> KeyedData:
    """Use upd_many to update a single record in a table."""

    results = await upd_many(role, table, KeyedDataList(records=[keyed_data]))
    return get_first_record(results)


class WizardStep(BaseModel):
    entity: str
    mode: Literal["insert", "select"]
    data: Dict[str, Any]
    recordId: Optional[Dict[str, Any]]


class WizardResult(BaseModel):
    entity: str
    keys: Dict[str, Any]
    allKeys: Dict[str, Dict[str, Any]]


async def create_wizard_transactional(
    role: str,
    main_entity: str,
    steps: List[WizardStep],
) -> WizardResult:
    # Всё в одной транзакции на одном соединении
    async with DBCon.connect(role, ConType.SESSION) as conn:
        async with conn.transaction():
            pk_map: Dict[str, Dict[str, Any]] = {}
            for step in steps:
                if step.mode == "select":
                    if not step.recordId:
                        raise HTTPException(
                            400, f"No recordId for select on {step.entity}"
                        )
                    pk_map[step.entity] = step.recordId
                else:
                    if not step.data:
                        raise HTTPException(400, f"No data for insert on {step.entity}")
                    # 1) очищаем и валидируем типы
                    clean = await transform_values_types(role, step.entity, step.data)
                    # 2) готовим INSERT ... RETURNING *;
                    queries = await crud.get_queries(role, step.entity)
                    cols = list(clean.keys())
                    placeholders = ", ".join(f"${i + 1}" for i in range(len(cols)))
                    sql = queries["gen_many"].format(
                        table=await strip_validate_tab(role, step.entity),
                        columns=", ".join(f'"{c}"' for c in cols),
                        records=f"({placeholders})",
                    )
                    # 3) выполняем прямо на conn
                    row = await conn.fetchrow(sql, *[clean[c] for c in cols])
                    if not row:
                        raise HTTPException(500, f"Insert failed for {step.entity}")
                    # 4) достаём PK
                    pk_map[step.entity] = {k: row[k] for k in queries["pk_cols"]}

            if main_entity not in pk_map:
                raise HTTPException(400, f"{main_entity} не встретился в шагах")
            return WizardResult(
                entity=main_entity, keys=pk_map[main_entity], allKeys=pk_map
            )
