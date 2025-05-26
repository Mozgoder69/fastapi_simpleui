# backend/metadata/views.py

"""Builds JSON schemas for different view types based on table metadata."""

from copy import deepcopy
from enum import Enum
from functools import cached_property
from typing import Any, Dict, List, Set

from config.logging import logger
from database.functions_meta import get_cached_schema
from metadata.mapping import table_to_icon
from metadata.schema import merge_json_data


class SchemaView(Enum):
    """Enumeration of possible schema view types."""

    FORM_VIEW = "FormView"
    TABLE_VIEW = "TableView"
    CARD_VIEW = "CardView"


class EntityType(Enum):
    SEPARATE_FORM = "Standalone Form Entity"
    FOREIGN_STEP = "Wizard Step for Foreign Entity"
    PRIMARY_STEP = "Wizard Step for Primary Entity"


MODE_TITLES = {
    "insert": "Create a new",
    "select": "Find an existing",
    "update": "Edit an existing",
}


class SchemaBuilder:
    """Class for building JSON schemas based on table metadata."""

    def __init__(self, source=None):
        """Initializes the schema builder with optional source metadata."""
        # self.base_schema = self.build_base_schema(source)
        self.source = source

    def view_schema(self, view_type: str = None):
        result = {"$schema": "https://json-schema.org/draft/2020-12/schema"}
        if view_type:
            result.update({"view": view_type})
        return result

    def entity_schema(self, entity: str, title: str = None, icon: str = None):
        return {
            "entity": entity,
            "title": title or entity.replace("_", " ").title(),
            "icon": icon or table_to_icon(entity),
        }

    @cached_property
    def base_schema(self):
        """Builds and caches the base JSON schema from the source metadata."""
        if not self.source:
            raise ValueError("No schema metadata provided (source is None).")
        return self.build_base_schema(self.source)

    def build_base_schema(self, tab_src: List[Dict[str, Any]]):
        """
        Converts table metadata (potentially multiple rows per column)
        into a JSON schema object by grouping and aggregating.
        """
        if not tab_src:
            raise ValueError("No schema metadata provided (tab_src is empty).")

        # --- Начало Группировки и Агрегации ---
        grouped_cols: Dict[str, List[Dict[str, Any]]] = {}
        for row_obj in tab_src:
            # Преобразуем row_obj в dict, если это не так (например, psycopg Record)
            row = dict(row_obj) if hasattr(row_obj, "items") else row_obj
            col_name = row.get("column_name")
            if not col_name:
                logger.warning(f"Row without column_name skipped: {row}")
                continue
            if col_name not in grouped_cols:
                grouped_cols[col_name] = []
            grouped_cols[col_name].append(row)
        # --- Конец Группировки ---

        # Определяем имя таблицы из первой строки первой группы
        first_group = next(iter(grouped_cols.values()), [])
        if not first_group:
            raise ValueError("Metadata processing resulted in no valid columns.")
        table_name = first_group[0].get("table_name")
        if not table_name:
            raise ValueError("Table name not found in schema metadata.")

        base_schema = {
            **self.view_schema(),
            **self.entity_schema(table_name),
            "properties": {},
            "uiHints": {},  # Можно будет заполнять позже
            "additionalProperties": False,
        }

        # --- Начало Обработки Групп ---
        processed_properties = {}
        for col_name, rows in grouped_cols.items():
            if not rows:
                continue  # Пропускаем пустые группы (не должно быть)

            first_row = rows[0]  # Берем общие данные из первой строки
            aggregated_data: Dict[str, Any] = {
                "table_schema": first_row.get("table_schema"),
                "table_name": first_row.get("table_name"),
                "column_name": col_name,
                "data_type": first_row.get("data_type"),
                "is_nullable": first_row.get("is_nullable"),
                "column_default": first_row.get("column_default"),
                "enum_options": first_row.get("enum_options"),
                "incoming_references": first_row.get(
                    "incoming_references"
                ),  # Добавляем back refs
                "constraint_types": set(),  # Множество для уникальных типов
                "foreign_keys": [],  # Список для деталей FK
            }

            # Агрегируем ограничения из всех строк для этого столбца
            for row in rows:
                const_type = row.get("const_type")
                if const_type:
                    aggregated_data["constraint_types"].add(const_type)
                    if const_type == "FOREIGN KEY":
                        # Собираем детали FK, только если они есть
                        ref_table = row.get("ref_table")
                        if ref_table:  # Убедимся, что это действительно данные FK
                            fk_detail = {
                                "ref_schema": row.get("ref_schema"),
                                "ref_table": ref_table,
                                "ref_column": row.get("ref_column"),
                                # Можно добавить имя ограничения, если оно нужно и доступно
                            }
                            # Избегаем дубликатов FK деталей (на случай странных данных)
                            if fk_detail not in aggregated_data["foreign_keys"]:
                                aggregated_data["foreign_keys"].append(fk_detail)

            # Преобразуем set в list для JSON-совместимости
            aggregated_data["constraint_types"] = sorted(
                list(aggregated_data["constraint_types"])
            )

            try:
                # Вызываем merge_json_data с агрегированными данными
                processed_properties[col_name] = merge_json_data(aggregated_data)
            except KeyError as e:
                logger.error(
                    f"Missing key {e} processing aggregated data for column {col_name}: {aggregated_data}"
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error processing aggregated data for column {col_name} {aggregated_data}: {e}"
                )
                continue

        base_schema["properties"] = processed_properties
        # --- Конец Обработки Групп ---

        return base_schema

    def get_is_enabled(self, details, mode):
        is_pk = details.get("primary_key", False)
        is_fk = "foreign_keys" in details
        is_autopk = is_pk and not is_fk
        return (
            mode == "update"
            or (mode == "select" and is_pk)
            or (mode == "insert" and not is_autopk)
        )

    def check_properties(self, properties, mode):
        """Cached computation of enabled properties."""
        return {
            field_name: {
                **details,
                "is_enabled": self.get_is_enabled(details, mode),
            }
            for field_name, details in properties.items()
        }

    def build_form_schema(
        self, title, properties, entity_type=EntityType.SEPARATE_FORM
    ):
        """Generates schema for form modes or a single mode."""
        modes_map = {
            EntityType.SEPARATE_FORM: ["insert", "select", "update"],
            EntityType.FOREIGN_STEP: ["insert", "select"],
            EntityType.PRIMARY_STEP: ["insert"],
        }
        modes = modes_map.get(entity_type, ["insert"])

        return [
            {
                "mode": mode,
                "title": f"{MODE_TITLES.get(mode, 'Perform action on')} {title}",
                "properties": self.check_properties(properties, mode),
            }
            for mode in modes
        ]

    def build_form_view_schema(self):
        """Generates an enhanced FormView schema with multiple modes."""
        return {
            **self.view_schema("FormView"),
            **self.entity_schema(self.base_schema["entity"]),
            "modes": self.build_form_schema(
                self.base_schema["title"],
                self.base_schema["properties"],
                EntityType.SEPARATE_FORM,
            ),
        }

    async def build_wizard_view_schema(self, payload: dict):
        """Generates a wizard schema with nested forms for related tables."""
        wizard_schema = {
            **self.view_schema("WizardView"),
            **self.entity_schema(self.base_schema["entity"]),
            "steps": [],
        }

        # Скопируем уже готовые свойства основной схемы (с правильным primary_key)
        main_properties = deepcopy(self.base_schema["properties"])
        ref_schemas: Dict[str, Dict[str, Any]] = {}

        # Собираем список внешних таблиц по foreign_keys
        for prop_details in main_properties.values():
            for fk in prop_details.get("foreign_keys", []):
                ref_table = fk.get("ref_table")
                if ref_table and ref_table not in ref_schemas:
                    try:
                        schema_data = await get_cached_schema(
                            payload["role"], ref_table
                        )
                        if not schema_data:
                            logger.warning(
                                f"No schema data for related table: {ref_table}"
                            )
                            continue

                        # Построим для неё базовую схему так же, как для главной
                        related_base = self.build_base_schema(schema_data)
                        ref_schemas[ref_table] = {
                            "title": f"{ref_table.replace('_', ' ').title()} Details",
                            "icon": table_to_icon(ref_table),
                            "properties": deepcopy(related_base["properties"]),
                        }
                    except Exception as e:
                        logger.error(f"Failed to load schema for {ref_table}: {e}")

        # Убираем из main_properties все поля, которые влезли в отдельные шаги
        for ref_table in ref_schemas:
            main_properties = {
                name: details
                for name, details in main_properties.items()
                if not any(
                    fk.get("ref_table") == ref_table
                    for fk in details.get("foreign_keys", [])
                )
            }

        step = 1
        # Шаги для связанных сущностей
        for ref_table, ref_data in ref_schemas.items():
            wizard_schema["steps"].append(
                {
                    "step": step,
                    **self.entity_schema(
                        ref_table, ref_data["title"], ref_data["icon"]
                    ),
                    "modes": self.build_form_schema(
                        ref_data["title"],
                        ref_data["properties"],
                        EntityType.FOREIGN_STEP,
                    ),
                }
            )
            step += 1

        # Последний шаг для основной сущности
        if main_properties:
            wizard_schema["steps"].append(
                {
                    "step": step,
                    **self.entity_schema(self.base_schema["entity"]),
                    "modes": self.build_form_schema(
                        self.base_schema["title"],
                        main_properties,
                        EntityType.PRIMARY_STEP,
                    ),
                }
            )

        # Если ни один шаг не собрался, можно здесь залогировать предупреждение

        return wizard_schema

    def build_view_schema(self, view_type: SchemaView):
        """Generates a schema for the specified view type by applying modifications."""

        if view_type == SchemaView.FORM_VIEW:
            return self.build_form_view_schema()

        return {
            **self.view_schema(view_type.value),
            **self.entity_schema(self.base_schema["entity"]),
            "properties": {
                col_name: deepcopy(details)
                for col_name, details in self.base_schema["properties"].items()
            },
        }
