# main.py
# Std libs
from typing import Annotated, Dict, List, Optional

import uvicorn
from app import create_app, setup_openapi, update_openapi

# Local files
from auth import JWTType, authenticate, decode_token, encode_token, oauth_schema
from db_con import pools
from db_fun import funcs
from dynamic import metadata_to_schema, vJSONSchema

# External modules
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt
from logs.myrich import log_cfg, logger

# Instantiate FastAPI app
app = create_app()

# Setup security schema
security = HTTPBearer()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), "static")
templates = Jinja2Templates("templates")


# Initialize and close connection pools on startup/shutdown
@app.on_event("startup")
async def startup():
    await pools.init_pool()


@app.on_event("shutdown")
async def shutdown():
    await pools.close_all_pools()


# Token generation and refreshing endpoints
@app.post("/token")
async def new_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # logger.debug(form_data.password)
    role = await authenticate(form_data.username, form_data.password)
    if not role:
        raise HTTPException(401, "Invalid credentials", {"WWW-Authenticate": "Bearer"})
    at = await encode_token(form_data.username, role, JWTType.AT)
    rt = await encode_token(form_data.username, role, JWTType.RT)
    return {"access_token": at, "refresh_token": rt, "token_type": "Bearer"}


@app.post("/refresh")
async def refresh_old_token(refresh_token: Annotated[str, Depends(oauth_schema)]):
    try:
        payload = await decode_token(refresh_token, JWTType.RT)
        if payload.get("type") == "refresh":
            new_access_token = await encode_token(
                payload["uname"], payload["role"], JWTType.AT
            )
            return {"access_token": new_access_token}
        raise HTTPException(401, "Invalid refresh token type")
    except jwt.JWTError as e:
        raise HTTPException(401, "Invalid token or expired token") from e


@app.post("/identity")
async def identity(access_token: Annotated[str, Depends(oauth_schema)]):
    payload = await decode_token(access_token, JWTType.AT)
    logger.debug(payload)
    if "role" not in payload or "uname" not in payload:
        raise HTTPException(400, "Invalid token")
    return payload


# API endpoint definitions for database interactions
@app.get("/tables")
async def api_tables(access_token: Annotated[dict, Depends(oauth_schema)]):
    try:
        payload = await decode_token(access_token, JWTType.AT)
        return await funcs.get_tables(payload)
    except Exception as e:
        raise HTTPException(500, f"Failed accessing DB: {e}") from e


@app.get("/tables/{table}/schema")
async def table_schema(
    table,
    access_token: Annotated[dict, Depends(oauth_schema)],
    version=vJSONSchema.alpaca,
):
    try:
        payload = await decode_token(access_token, JWTType.AT)
        metadata = await funcs.get_schema(payload, table)
        return metadata_to_schema(table, metadata, version)
    except Exception as e:
        raise HTTPException(500, f"Failed accessing DB: {e}") from e


@app.get("/tables/schemas")
async def tables_schemas(access_token: Annotated[dict, Depends(oauth_schema)]):
    schemas = {}
    tables = await api_tables(access_token)
    for table in tables:
        tabname = table.get("table_name")
        try:
            schema = await table_schema(
                tabname, access_token, version=vJSONSchema.openapi
            )
            schemas[tabname] = schema  # Используйте имя таблицы как ключ
        except Exception as e:
            logger.debug(f"Unsufficient access was prevented. Info: {e}")
    logger.debug(f"Updating OpenAPI with schemas: {schemas}")
    update_openapi(app, schemas)
    return {"schemas": schemas}


""" Маршруты CRUD """


@app.get("/tables/{table}/records/{recordId}")
async def read_one(table: str, oid: int, payload: dict = Depends(decode_token)):
    """Получить из таблицы запись по ID"""
    return JSONResponse(content={"table": table, "oid": oid})


@app.get("/tables/{table}/records/list")
async def list_many(
    table: str, cond: Optional[dict] = None, payload: dict = Depends(decode_token)
):
    """Прочесть из таблицы записи по условию"""
    data = await funcs.get_records(payload, table, pools)
    return JSONResponse(content={"table": table, "rule": cond})


@app.post("/tables/{table}/records/new")
async def new_one(table: str, data: Dict, payload: dict = Depends(decode_token)):
    """Добавить запись с указанными данными в таблицу"""
    return JSONResponse(content={"table": table, "data": data})


@app.post("/tables/{table}/records/bulk")
async def gen_many(table: str, amount: int, payload: dict = Depends(decode_token)):
    """Сгенерировать указанное количество записей в таблице"""
    return JSONResponse(content={"table": table, "amount": amount})


@app.put("/tables/{table}/records/{oid}")
async def edit_one(
    table: str, oid: int, rule: Dict, payload: dict = Depends(decode_token)
):
    """Редактировать в таблице запись по ID"""
    return JSONResponse(content={"table": table, "oid": oid, "rule": rule})


@app.put("/tables/{table}/records/bulk")
async def upd_many(
    table: str, rules: List[Dict], payload: dict = Depends(decode_token)
):
    """Обновить записи в таблице новыми данными"""
    return JSONResponse(content={"table": table, "rules": rules})


@app.delete("/tables/{table}/records/{oid}")
async def del_one(table: str, oid: int, payload: dict = Depends(decode_token)):
    """Удалить записи из таблицы по данному ID"""
    return JSONResponse(content={"table": table, "oid": oid})


@app.delete("/tables/{table}/records/bulk")
async def trim_many(table: str, oids: List[int], payload: dict = Depends(decode_token)):
    """Очистить записи в таблице по данным ID"""
    return JSONResponse(content={"table": table, "oids": oids})


@app.get("/home")
async def index(request: Request):
    # Нет Depends(decode_token) - домой можно ходить и без логина
    title = "Welcome To Cleaners API"
    body_content = "Auth Or Visit /Docs To Explore How To Use API"
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": title, "body_content": body_content}
    )


# Setup OpenAPI configuration
setup_openapi(app)

# Start Uvicorn server if script is run directly
if __name__ == "__main__":
    uvicorn.run(
        app, "127.0.0.1", 8272, log_config=log_cfg, log_level="debug", reload=True
    )
