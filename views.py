from fastapi import Request, HTTPException
from pg_fun import *
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging  # Добавьте импорт для работы с логгером

views = Jinja2Templates(directory="views")


async def get_tables():
    try:
        table_names = await get_selectable_tables()
        return {"tables": table_names}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error accessing database: {str(e)}"
        )


async def get_columns(table_name):
    try:
        table_columns = await get_table_columns(table_name)
        return {"table_columns": table_columns}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error accessing database: {str(e)}"
        )


async def get_records(table_name):
    try:
        table_records = await get_table_records(table_name)
        return {"table_records": table_records}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error accessing database: {str(e)}"
        )



def get_fields_data(columns_data):
    type_mapping = {
        "int4": "int",
        "e_order_payment": "str",
        # Добавьте другие соответствия типов данных по мере необходимости
    }

    fields = []
    for column in columns_data.get("table_columns", []):
        cname = column.get("cname", "")
        ctype = column.get("ctype", "")

        # Преобразование типов данных с использованием type_mapping
        ctype_mapped = type_mapping.get(ctype, ctype)

        field = {"name": cname, "type": ctype_mapped}
        fields.append(field)

    return fields


# def get_fields_html(fields_data):
#     html_code = "<form>"
#     for field in fields_data:
#         cname = field["name"]
#         ctype = field["type"]

#         # Определение типа поля ввода в зависимости от целевого типа данных PostgreSQL
#         input_type = None
#         if (
#             ctype == "int4"
#             or ctype == "int"
#             or ctype == "serial"
#             or ctype == "float"
#             or ctype == "number"
#         ):
#             input_type = "number"
#         elif ctype == "bool":
#             input_type = "checkbox"
#         elif ctype == "date":
#             input_type = "date"
#         elif ctype == "datetime":
#             input_type = "datetime-local"
#         elif ctype == "color":
#             input_type = "color"
#         elif ctype == "range":
#             input_type = "range"
#         elif ctype == "search":
#             input_type = "search"
#         elif ctype == "url":
#             input_type = "url"
#         elif ctype == "text":
#             input_type = "text"
#         # Добавьте другие условия для других типов данных по мере необходимости

#         # Создаем соответствующий HTML-код для поля ввода
#         html_code += f'<label for="{cname}">{cname}:</label>'
#         html_code += f'<input type="{input_type}" id="{cname}" name="{cname}" value="" required><br>'
#     html_code += '<input type="submit" value="Submit"></form>'
#     return html_code


# async def create_fields(Request: Request, table_name: str = "your_table_name"):
#     logging.basicConfig(level=logging.INFO)  # Инициализация логгера

#     try:
#         with open("views/form_template.html", "r") as template_file:
#             template_content = template_file.read()
#     except FileNotFoundError:
#         raise HTTPException(status_code=500, detail="Template file not found")

#     columns_data = await get_columns(table_name)

#     # Получаем теоретический результат
#     fields_data = get_fields_data(columns_data)
#     logging.info(f"Теоретический результат: {fields_data}")

#     # Получаем и выводим практический результат с полями ввода
#     fields_html = get_fields_html(fields_data)
#     logging.info(f"Практический результат (HTML код с полями ввода): {fields_html}")

#     final_html_code = template_content.format(html_code=fields_html)

#     with open("views/final_form.html", "w") as final_file:
#         final_file.write(final_html_code)

#     return views.TemplateResponse(
#         "views/final_form.html",
#         {"request": request, "title": "Hello", "body_content": "Hello"},
#     )
