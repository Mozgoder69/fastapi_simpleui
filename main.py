# Стандартные библиотеки
from http import HTTPStatus
from typing import Optional

# Сторонние библиотеки
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
import uvicorn

# Локальные модули
from pg_con import get_con, auth_user
from pg_fun import get_selectable_tables, get_table_columns, get_table_records
import views
import domain

# Создайте основное приложение FastAPI
app = FastAPI()
views = Jinja2Templates(directory="views")
static = StaticFiles(directory="views/static")
app.mount("/static", static, name="static")

@app.post("/auth")
async def auth(form_data: OAuth2PasswordRequestForm = Depends(), is_guest=False):
    # try:
    #     jwt_token = await auth_user(form_data.username, form_data.password, is_guest)
    # except Exception as e:
    #     raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=f"Incorrect username or password: {e}")

    response = await auth_user(form_data.username, form_data.password, False)

    return response

@app.get("/api/fields/{table_name}")
async def api_fields(request: Request, table_name):
    columns_data = await get_columns(table_name)
    columns = [dict(record) for record in columns_data["table_columns"]]  # Преобразование каждой записи в словарь

    for column in columns:
        column["html_input_type"] = db_type_to_input(column["ctype"])

    icon_name = db_table_to_icon(table_name)

    # Рендерим HTML-форму с использованием Jinja2
    return views.TemplateResponse("form_template.html", {"request": request, "icon_name": icon_name, "table_name": table_name, "columns": columns})


@app.get("/api/tables")
async def api_tables():
    return await get_tables()

@app.get("/api/columns/{table_name}")
async def api_columns(table_name):
    return await get_columns(table_name)

@app.get("/api/records/{table_name}")
async def api_records(table_name):
    return await get_records(table_name)


#


@app.get('/table={table_name}/select_one/id={obj_id}', response_class=HTMLResponse)
def select_one(table_name: str, obj_id: int):
    return views.TemplateResponse("obj_view.html", {"table": table_name, "obj_id": obj_id})

@app.get('/table={table_name}/select_many', response_class=HTMLResponse)
def select_many(table_name: str, options: Optional[dict] = None):
    return views.TemplateResponse("list_view.html", {"table": table_name, "filter": options})



@app.post('/table={table_name}/insert_one', response_class=HTMLResponse)
def insert_one(table_name: str, values: dict):
    return views.TemplateResponse("new_form.html", {"table": table_name, "values": values})

@app.post('/table={table_name}/insert_many', response_class=HTMLResponse)
def insert_many(table_name: str, amount: int):
    return views.TemplateResponse("gen_form.html", {"table": table_name, "amount": amount})



@app.put('/table={table_name}/update_one/id={obj_id}', response_class=HTMLResponse)
def update_one(table_name: str, obj_id: int, values: dict):
    return views.TemplateResponse("edit_form.html", {"table": table_name, "obj_id": obj_id, "values":values})

@app.put('/table={table_name}/update_many', response_class=HTMLResponse)
def update_many(table_name: str, options: Optional[dict], values: dict):
    return views.TemplateResponse("mod_form.html", {"table": table_name, "options": options, "values": values})



@app.get("/table/{table_name}/create")
async def get_insert_form(table_name: str):
    columns = await get_columns(table_name)
    return views.TemplateResponse("create_form.html", {"table": table_name, "columns": columns})


@app.post("/table/{table_name}/create")
async def post_insert_data(request: Request, table_name: str, columns: list):
    data = await request.form()
    try:
        await insert_one(table_name, data)
        # Redirect to success page or list view
    except ValidationError as e:
        # Display errors in the form
        return views.TemplateResponse("create_form.html", {"table": table_name, "columns": columns, "errors": e.errors()})
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus(500), detail=str(e))





@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return views.TemplateResponse("index.html", {"request": request, "title": "Hello", "body_content": "Hello"})






if __name__ == "__main__":
    # def_pool = open_pool("postgres")
    uvicorn.run("main:app", host='127.0.0.1', port=8272, reload=True)