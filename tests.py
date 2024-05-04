# tests.py
import pytest
from deepdiff import DeepDiff
from dynamic import metadata_to_schema


@pytest.fixture
def mock_metadata():
    """Provides mock metadata representing a database table schema, which includes
    various column configurations such as data types, nullability, defaults, and enum options."""
    return {
        "person": [
            {
                "col_name": "document_id",
                "data_type": "int4",
                "is_null": "NO",
                "const_type": "FOREIGN KEY",
                "ref_schema": "public",
                "ref_table": "document",
                "ref_column": "document_id",
            },
            {
                "col_name": "full_name",
                "data_type": "text",
                "is_null": "NO",
                "col_default": "",
            },
            {"col_name": "last_login", "data_type": "timestamptz", "is_null": "YES"},
            {"col_name": "birth_date", "data_type": "date", "is_null": "YES"},
            {
                "col_name": "discount",
                "data_type": "numeric",
                "is_null": "YES",
                "col_default": "0.0",
            },
            {
                "col_name": "position",
                "data_type": "e_position_type",
                "is_null": "NO",
                "col_default": "sales_operator",
                "enum_options": [
                    "service_master",
                    "sales_operator",
                    "resources_admin",
                    "project_leader",
                ],
            },
            {
                "col_name": "is_active",
                "data_type": "bool",
                "is_null": "NO",
                "col_default": "false",
            },
        ]
    }


def test_enum_types(mock_metadata):
    """Tests if enum fields in the schema correctly declare enum values."""
    schema = metadata_to_schema("person", mock_metadata["person"])
    for field in mock_metadata["person"]:
        if field["data_type"].startswith("e_"):
            field_schema = schema["properties"][field["col_name"]]
            assert "enum" in field_schema, f"Enum field missing for {field['col_name']}"
            assert (
                field_schema["enum"] == field["enum_options"]
            ), f"Enum values mismatch for {field['col_name']}"


def test_metadata_to_schema(mock_metadata):
    """Compares the output schema from metadata_to_schema function to the expected schema,
    ensuring that the conversion process adheres to the expected format and properties."""
    actual_schema = metadata_to_schema("person", mock_metadata["person"])
    expected_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "document_id": {
                "type": "integer",
                "foreign_key": {
                    "ref_schema": "public",
                    "ref_table": "document",
                    "ref_column": "document_id",
                },
            },
            "full_name": {"type": "string", "default": ""},
            "last_login": {"type": "string", "format": "date-time"},
            "birth_date": {"type": "string", "format": "date"},
            "discount": {"type": "number", "default": "0.0"},
            "position": {
                "type": "string",
                "default": "sales_operator",
                "enum": [
                    "service_master",
                    "sales_operator",
                    "resources_admin",
                    "project_leader",
                ],
                "format": "e_position_type",
            },
            "is_active": {"type": "boolean", "default": "false"},
        },
        "required": ["document_id", "full_name", "position", "is_active"],
        "additionalProperties": False,
    }
    differences = DeepDiff(actual_schema, expected_schema, ignore_order=True)
    assert differences == {}, f"Differences found: {differences}"


if __name__ == "__main__":
    pytest.main()
