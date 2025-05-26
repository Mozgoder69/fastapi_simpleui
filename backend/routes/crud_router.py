# backend/routes/crud_router.py

"""Router for CRUD-related database operations."""

from typing import List, Optional

from auth.jwt_handler import decode_token
from database.functions_crud import (
    WizardStep,
    create_wizard_transactional,
    del_one,
    edit_one,
    gen_many,
    list_many,
    new_one,
    read_one,
    trim_many,
    upd_many,
)
from database.query_builder import (
    DataOnly,
    DataOnlyList,
    KeyedData,
    KeyedDataList,
    KeysOnly,
    KeysOnlyList,
)
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from utils.serialization import (
    parse_and_validate_columns,
    parse_and_validate_filters,
    transform_values_types,
)

# Initialize CRUD router with the tag "CRUD"
crud_router = APIRouter(tags=["CRUD"])
"""Router for CRUD-related database operations."""


def get_role(payload: dict = Depends(decode_token)) -> str:
    """Extracts the user role from the decoded token payload."""
    return payload["role"]


@crud_router.post("/tables/{table}/data/bulk", response_model=KeyedDataList)
async def gen_data(
    table: str, data_only_list: DataOnlyList, role: str = Depends(get_role)
):
    """Insert multiple records into a table."""
    if not data_only_list.records:
        raise HTTPException(status_code=400, detail="Data list cannot be empty.")

    transformed_records = []
    for record in data_only_list.records:
        transformed_data = await transform_values_types(role, table, record.data)
        transformed_records.append(DataOnly(data=transformed_data))

    transformed_data_only_list = DataOnlyList(records=transformed_records)
    return await gen_many(role, table, transformed_data_only_list)


@crud_router.get("/tables/{table}/data/bulk", response_model=KeyedDataList)
async def list_data(
    table: str,
    filters: Optional[str] = Query(None),  # Фильтры как JSON-строка
    columns: Optional[str] = Query(None),  # Колонки как JSON-строка
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    role: str = Depends(get_role),
):
    """Select multiple records from a table with optional filtration and pagination."""

    filters = await parse_and_validate_filters(role, table, filters, False)
    columns = await parse_and_validate_columns(role, table, columns, False)

    filters = await transform_values_types(role, table, filters)

    return await list_many(role, table, filters, columns, limit, offset)


@crud_router.delete("/tables/{table}/data/bulk", response_model=KeyedDataList)
async def trim_data(
    table: str, keys_only_list: KeysOnlyList, role: str = Depends(get_role)
):
    """Delete multiple records from a table."""
    if not keys_only_list.records:
        raise HTTPException(status_code=400, detail="Records list cannot be empty.")

    return await trim_many(role, table, keys_only_list)


@crud_router.put("/tables/{table}/data/bulk", response_model=KeyedDataList)
async def upd_data(
    table: str, keyed_data_list: KeyedDataList, role: str = Depends(get_role)
):
    """Update multiple records in a table using keyed data records and CTE."""
    if not keyed_data_list.records:
        raise HTTPException(status_code=400, detail="Records list cannot be empty.")

    transformed_records = []
    for record in keyed_data_list.records:
        transformed_keys = await transform_values_types(role, table, record.keys)
        transformed_data = await transform_values_types(role, table, record.data)
        transformed_records.append(
            KeyedData(keys=transformed_keys, data=transformed_data)
        )

    transformed_keyed_data_list = KeyedDataList(records=transformed_records)
    return await upd_many(role, table, transformed_keyed_data_list)


@crud_router.post("/tables/{table}/data", response_model=KeyedData)
async def new_data(table: str, data_only: DataOnly, role: str = Depends(get_role)):
    """Use gen_data to insert a single new record into a table."""

    transformed_data = await transform_values_types(role, table, data_only.data)
    return await new_one(role, table, DataOnly(data=transformed_data))


@crud_router.get("/tables/{table}/data", response_model=KeyedData)
async def read_data(
    table: str,
    filters: Optional[str] = Query(None),  # Фильтры как JSON-строка
    columns: Optional[str] = Query(None),  # Колонки как JSON-строка
    role: str = Depends(get_role),
):
    """Use list_many with keys as a condition to select a single record from a table."""

    filters = await parse_and_validate_filters(role, table, filters, True)
    columns = await parse_and_validate_columns(role, table, columns, False)

    if not filters:
        raise HTTPException(status_code=400, detail="Filters cannot be empty.")

    filters = await transform_values_types(role, table, filters)

    return await read_one(role, table, KeysOnly(keys=filters), columns)


@crud_router.delete("/tables/{table}/data", response_model=KeyedData)
async def del_data(
    table: str, keys_only: KeysOnly = Body(...), role: str = Depends(get_role)
):
    """Use trim_data to delete a single record in a table."""
    return await del_one(role, table, keys_only)


@crud_router.put("/tables/{table}/data", response_model=KeyedData)
async def edit_data(
    table: str, keyed_data: KeyedData = Body(...), role: str = Depends(get_role)
):
    """Use upd_data to update a single record in a table."""
    transformed_keys = await transform_values_types(role, table, keyed_data.keys)
    transformed_data = await transform_values_types(role, table, keyed_data.data)
    return await edit_one(
        role, table, KeyedData(keys=transformed_keys, data=transformed_data)
    )


@crud_router.post("/tables/{table}/data/wizard")
async def create_wizard(
    table: str, steps: List[WizardStep], role: str = Depends(get_role)
):
    # 1) по-надёжному трансформируем и валидируем входящие JSON-данные
    for step in steps:
        if step.mode == "insert":
            step.data = await transform_values_types(role, step.entity, step.data)
    # 2) вызываем уже готовую централизованную функцию
    return await create_wizard_transactional(role, table, steps)
