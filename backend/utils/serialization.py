# backend/utils/serialization.py

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from config.logging import logger
from database.functions_meta import get_cached_schema
from fastapi import HTTPException


async def validate_column_names(
    role: str, table: str, col_names: List[str], keys_only: bool = False
) -> None:
    schema = await get_cached_schema(role, table)
    if not schema:
        raise HTTPException(status_code=404, detail=f"No schema for table {table}")

    valid_cols = []
    if keys_only:
        # Ищем только первичные ключи, безопасно проверяя const_type
        for col in schema:
            const_type_val = col.get("const_type")  # Получаем значение, может быть None
            # ---> ИСПРАВЛЕНИЕ: Проверяем, что значение - строка, перед вызовом upper() <---
            if (
                isinstance(const_type_val, str)
                and "PRIMARY KEY" in const_type_val.upper()
            ):
                valid_cols.append(col["column_name"])
            # ---> КОНЕЦ ИСПРАВЛЕНИЯ <---
    else:
        # Для не-keys_only просто собираем все имена колонок
        valid_cols = [
            col["column_name"] for col in schema if col.get("column_name")
        ]  # Добавим проверку на наличие имени

    # Проверяем, являются ли ПЕРЕДАННЫЕ col_names допустимыми
    invalid = [c for c in col_names if c not in valid_cols]
    if invalid:
        # Формируем строку только из не-None значений
        invalid_str = ", ".join([str(i) for i in invalid if i is not None])
        # Если строка все еще пуста (например, все invalid были None), покажем общую ошибку
        detail_msg = (
            f"Invalid columns: {invalid_str}"
            if invalid_str
            else "Invalid columns provided"
        )
        raise HTTPException(status_code=400, detail=detail_msg)


async def parse_and_validate_columns(
    role: str, table: str, param: Optional[str], keys_only: bool = False
) -> List[str]:
    if not param or param.strip() in ("[]", "{}", ""):
        return []

    try:
        parsed = json.loads(param)
        if not isinstance(parsed, list):
            raise ValueError('columns must be a JSON array (["col1", "col2"])')
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid columns format: {str(e)}")

    # вызываем универсальную функцию
    await validate_column_names(role, table, parsed, keys_only=keys_only)

    return parsed


async def parse_and_validate_filters(
    role: str,
    table: str,
    param: Optional[str],
    keys_only: bool = False,
) -> Dict[str, Any]:
    if not param or param.strip() in ("[]", "{}", ""):
        return {}

    try:
        parsed = json.loads(param)
        if not isinstance(parsed, dict):
            raise ValueError("Filters must be a JSON object")
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid filters format: {str(e)}")

    # Вызываем ту же универсальную функцию,
    # но передаем list(parsed.keys())
    await validate_column_names(role, table, list(parsed.keys()), keys_only=keys_only)

    return parsed


async def transform_values_types(
    role: str, table: str, parsed: Dict[str, Any]
) -> Dict[str, Any]:
    """Transform string values to appropriate types based on column types."""
    schema = await get_cached_schema(role, table)
    column_types = {col["column_name"]: col["data_type"] for col in schema}

    transformed = parsed.copy()

    date_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]

    for key, value in transformed.items():
        if key not in column_types:
            continue

        col_type = column_types[key].lower()

        if isinstance(value, str):
            if col_type in (
                "date",
                "timestamp",
                "timestamptz",
                "timestamp with time zone",
                "timestamp without time zone",
            ):
                for date_format in date_formats:
                    try:
                        dt = datetime.strptime(value, date_format)
                        if col_type == "date":
                            transformed[key] = dt.date()
                        else:
                            transformed[key] = dt
                        logger.info(
                            f"Transformed {key} from {value} to {transformed[key]} (type: {col_type})"
                        )
                        break
                    except ValueError:
                        continue
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid date format for {key}: {value}. Expected one of {date_formats} (e.g., '2015-01-01T10:00:00' or '2015-01-01')",
                    )
            elif col_type in ("integer", "int", "int4"):
                try:
                    transformed[key] = int(value)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid integer format for {key}: {value}. Expected an integer.",
                    )
            elif col_type in ("numeric", "decimal"):
                try:
                    transformed[key] = float(value)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid numeric format for {key}: {value}. Expected a number.",
                    )
            elif col_type == "boolean":
                if value.lower() in ("true", "false"):
                    transformed[key] = value.lower() == "true"
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid boolean format for {key}: {value}. Expected 'true' or 'false'.",
                    )
            elif col_type in ("json", "jsonb"):
                try:
                    transformed[key] = json.loads(value)
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid JSON format for {key}: {value}. Expected valid JSON.",
                    )

    return transformed
