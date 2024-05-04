# dynamic.py

import re
from decimal import Decimal, InvalidOperation
from enum import Enum

from logs.myrich import logger


class vJSONSchema(Enum):
    alpaca = "http://json-schema.org/draft-07/schema#"
    openapi = "https://json-schema.org/draft/2020-12/schema"


# Maps PostgreSQL data types to JSON Schema types and formats.
map_types = {
    **dict.fromkeys(["bool", "boolean"], {"type": "boolean"}),
    **dict.fromkeys(["int", "int4", "integer"], {"type": "integer"}),
    **dict.fromkeys(["money", "numeric", "decimal"], {"type": "number"}),
    **dict.fromkeys(
        ["text", "char", "varchar", "character", "character varying"],
        {"type": "string"},
    ),
    **dict.fromkeys(["date"], {"type": "string", "format": "date"}),
    **dict.fromkeys(
        ["time", "timetz", "time with time zone", "time without time zone"],
        {"type": "string", "format": "time"},
    ),
    **dict.fromkeys(
        ["datetime", "date-time"], {"type": "string", "format": "date-time"}
    ),
    **dict.fromkeys(
        [
            "timestamp",
            "timestamptz",
            "timestamp with time zone",
            "timestamp without time zone",
        ],
        {"type": "string", "format": "date-time"},
    ),
}


def fetch_default(info):
    """Generates a 'default' schema attribute if applicable, ignoring defaults for certain data types or constraints."""
    if not (
        info.get("col_default") is None
        or info.get("const_type") in {"FOREIGN KEY", "PRIMARY KEY"}
        or info.get("data_type")
        in {"date", "timestamp", "timestamptz", "time", "timetz"}
    ):
        default = str(info["col_default"]).split("::")[0].strip("'")
        return {"default": str(default)}
    return {}


def fetch_enum(info):
    """Extracts enum options for fields with enumerated types and logs the operation."""
    json_data = {}
    if "enum_options" in info:
        json_data["enum"] = info["enum_options"]
        json_data["format"] = info["data_type"].split(".")[-1]
        logger.debug(f"Enum data added: {json_data}")
    return json_data


def fetch_fkey(info):
    """Extracts foreign key information from the field metadata if available and logs the addition."""
    json_data = {}
    if all(info.get(k) for k in ("ref_schema", "ref_table", "ref_column")):
        json_data["foreign_key"] = {
            "ref_schema": info["ref_schema"],
            "ref_table": info["ref_table"],
            "ref_column": info["ref_column"],
        }
        logger.debug(f"Foreign key data added: {json_data}")
    return json_data


def get_json_data(info):
    """Compiles all relevant JSON data from a column's metadata into a single dictionary."""
    json_data = {}

    # Determine base type from PostgreSQL data type.
    data_type = info.get("data_type").lower()
    base_type = map_types.get(data_type, {"type": "string"})
    json_data.update(base_type)

    # Include enum data if present.
    if str(info["data_type"]).split(".")[-1].startswith("e_"):
        enum_data = fetch_enum(info)
        json_data.update(enum_data)

    # Add foreign key data if present.
    if info.get("const_type") == "FOREIGN KEY":
        fkey_data = fetch_fkey(info)
        json_data.update(fkey_data)

    # Add default value if present.
    default_data = fetch_default(info)
    json_data.update(default_data)

    # Check for non-null constraint.
    return json_data, info.get("is_null") == "NO"


def metadata_to_schema(table_name, table_metadata, version=vJSONSchema.alpaca):
    """Converts table metadata into a JSON schema object using the specified schema version."""
    json_schema = {
        "$schema": version.value,
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }
    required_columns = set()

    for record in table_metadata:
        try:
            record = dict(record.items()) if hasattr(record, "items") else record
            col_name = record.get("col_name")
            if not col_name:
                logger.warning("Nameless column found")
                continue  # Skip columns without names.

            json_field, is_required = get_json_data(record)
            json_schema["properties"][col_name] = json_field
            if is_required:
                required_columns.add(col_name)
        except Exception as e:
            logger.error(f"Error processing record {record}: {e}")
            continue  # Proceed to the next record.

    json_schema["required"] = list(required_columns)
    return json_schema


# mapping.py

icon_mapping = {
    "address": "location_on",
    "customer": "person",
    "customer_email": "contact_mail",
    "customer_phone": "contact_phone",
    "branch": "hub",
    "employee": "badge",
    "account": "passkey",
    "message": "chat_info",
    "process": "manufacturing",
    "workflow": "manage_history",
    "request": "business_messages",
    "stage": "flag",
    "factor": "vital_signs",
    "method": "cleaning_services",
    "scenario": "strategy",
    "category": "category",
    "material": "layers",
    "symbol": "rule_folder",
    "pollution": "barefoot",
    "catalyst": "electric_bolt",
    "harmful_factor": "release_alert",
    "helpful_factor": "new_releases",
    "method_chem": "household_supplies",
    "method_mech": "electrical_services",
    "solution": "emoji_objects",
    "order": "receipt_long",
    "journey": "local_shipping",
    "package": "package_2",
    "product": "shopping_bag",
    "premises": "apartment",
    "offsite_service": "home",
    "onsite_service": "apparel",
    "texture": "texture",
    "referral": "label_important",
    "problem": "target",
}


def table_to_icon(db_table: str) -> str:
    """Returns the icon associated with a database table name, or a default icon if no match is found."""
    return icon_mapping.get(db_table, "default-icon")
