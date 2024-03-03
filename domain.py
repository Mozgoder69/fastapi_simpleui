from unicodedata import decimal
from pydantic import BaseModel, create_model, Field
from enum import Enum
from typing import Any, Tuple, Type, Union

def db_type_to_py_type(db_type: str) -> type:
    """Преобразует тип данных из базы данных в тип данных Python."""
    return {
        "text": str,
        "int4": int,
        "numeric": decimal,
        "bool": bool,
        "e_order_payment": str,  # предполагаем, что это пользовательский перечисляемый тип, используем строку
        # Добавьте другие соответствия типов данных по мере необходимости
    }.get(db_type, str)

# def create_pydantic_model_from_db(table_columns: list[Dict[str, Any]]) -> type:
#     """Динамически создает Pydantic модель на основе метаданных столбцов таблицы."""
#     fields = {col['cname']: (db_type_to_python_type(col['ctype']), ...) for col in table_columns}
#     return create_model('DynamicModel', **fields)

def db_type_to_input_type(db_type: str) -> str:
    type_mapping = {
        "text": "text",
        "int4": "number",
        "numeric": "number",
        "date": "date",
        "timestamptz": "datetime-local",
        # другие типы данных
    }
    return type_mapping.get(db_type, "text")  # По умолчанию text

def gen_input_html(ctype: str, cname: str, cval: str = "", checked: bool = False) -> str:
    input_type = db_type_to_input_type(ctype)
    if ctype == "bool": 
        input_html = f'''<label>
                        <input type="checkbox" class="filled-in" name="{cname}" value="{cval}" {'checked="checked"' if checked else ""} />
                        <span>{cname}</span>
                    </label>'''
    elif ctype.startswith("e_"):
        input_html = f'''
            asd
        '''
    else:
        input_html = ""
        

    return html_mapping.get(input_type, f'<input type="{ctype}" name="{cname}" value="{cval}">')  # По умолчанию text

def db_table_to_icon(db_table: str) -> str:
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
    return icon_mapping.get(db_table, "default-icon")
