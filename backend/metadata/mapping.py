# backend/metadata/mapping.py

"""Maps database table names and PostgreSQL data types to corresponding application-specific types and icons."""

import datetime

# Maps database table names to corresponding icons.
map_icons = {
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
    "salesorder": "receipt_long",
    "journey": "local_shipping",
    "package": "package_2",
    "product": "shopping_bag",
    "premises": "apartment",
    "scenario_offsite": "home",
    "scenario_onsite": "apparel",
    "texture": "texture",
    "referral": "label_important",
    "problem": "target",
}


def table_to_icon(db_table: str) -> str:
    """Returns the icon associated with a database table name, or a default icon if no match is found."""
    return map_icons.get(db_table, "default-icon")


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


def map_pg_type(pg_type):
    """Maps PostgreSQL data types to Python types"""

    # Define PostgreSQL to Python type mapping
    mapping = {
        "integer": int,
        "text": str,
        "boolean": bool,
        "numeric": float,
        "date": datetime.date,
        "timestamp": datetime.datetime,
        # Прочие типы
    }

    # Return the corresponding type or default to string
    return mapping.get(pg_type, str)
