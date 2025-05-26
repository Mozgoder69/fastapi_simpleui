# backend/metadata/schema.py

from enum import Enum
from typing import Any, Dict, List, Set

from metadata.mapping import map_types


class ConstType(Enum):
    UK = "UNIQUE"
    FK = "FOREIGN KEY"
    PK = "PRIMARY KEY"


def is_field_mandatory(col_src: Dict[str, Any]) -> bool:
    """Determines if a column is mandatory based on its metadata."""
    is_not_null = col_src.get("is_nullable") == "NO"
    const_type = col_src.get("const_type") or ""

    info_consts = ("UNIQUE", "FOREIGN KEY")
    has_non_pk_const = any(const in const_type for const in info_consts)

    # Include types like time and date as criteria for field mandatory

    return is_not_null and (col_src.get("enum_options") is not None or has_non_pk_const)


def merge_json_data(col_src: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compiles all relevant JSON data from aggregated column metadata
    into a single dictionary.
    Ожидает на вход словарь с агрегированными данными для одного столбца.
    """
    json_data = {}

    # Base type and label
    data_type = col_src.get("data_type", "").lower()
    json_data.update(map_types.get(data_type, {"type": "string"}))
    json_data["label"] = col_src.get("column_name", "").replace("_", " ").title()

    # Enum data
    if col_src.get("enum_options"):
        json_data["enum"] = col_src["enum_options"]
        json_data["format"] = "select"  # Можно вынести в map_types для enum

    # Constraints and keys - теперь работаем с агрегированными данными
    constraint_types: Set[str] = col_src.get("constraint_types", set())
    foreign_keys: List[Dict[str, str]] = col_src.get("foreign_keys", [])

    json_data["primary_key"] = "PRIMARY KEY" in constraint_types

    # Используем множественное число и ожидаем список словарей
    if foreign_keys:
        json_data["foreign_keys"] = foreign_keys  # Список деталей FK

    # Default value
    default_value = col_src.get("column_default")
    if default_value is not None:
        # Простая очистка кавычек может быть недостаточной для всех типов по умолчанию
        if isinstance(default_value, str):
            # Удаляем кавычки и возможное указание типа (::text)
            if "::" in default_value:
                default_value = default_value.split("::")[0]
            json_data["default"] = default_value.strip("'")
        else:
            json_data["default"] = default_value

    # Required status
    # json_data["required"] = is_field_mandatory(col_src)

    return json_data
