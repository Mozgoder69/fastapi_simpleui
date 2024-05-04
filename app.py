# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi


def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:8272"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization"],
    )
    return app


def setup_openapi(app):
    if app.openapi_schema is None:
        openapi_schema = get_openapi(
            title="Schemas",
            version="2.5.5",
            description="Initial OpenAPI config",
            routes=app.routes,
        )
        openapi_schema["components"] = {
            "securitySchemes": {
                "OAuth2PasswordBearer": {
                    "type": "oauth2",
                    "flows": {
                        "password": {
                            "tokenUrl": "/token",
                            "scopes": {},
                        }
                    },
                }
            }
        }
        app.openapi_schema = openapi_schema
    app.openapi = lambda: app.openapi_schema


def update_openapi(app, models):
    if not app.openapi_schema:
        setup_openapi(app)
    # Убедимся, что у нас есть ключ 'components' и внутри него 'schemas'
    if "components" not in app.openapi_schema:
        app.openapi_schema["components"] = {"schemas": {}}
    if "schemas" not in app.openapi_schema["components"]:
        app.openapi_schema["components"]["schemas"] = {}

    # Обновляем schemas с новыми моделями
    app.openapi_schema["components"]["schemas"].update(models)

    # Пересоздаем схему OpenAPI, чтобы она включала последние изменения
    # app.openapi_schema = get_openapi(
    #     title="Schemas",
    #     version="2.5.6",
    #     description="Updated OpenAPI config",
    #     routes=app.routes,
    #     components=app.openapi_schema["components"],
    # )
