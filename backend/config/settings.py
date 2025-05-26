# backend/config/settings.py

"""Configuration settings for the FastAPI application."""

import os
from pathlib import Path
from secrets import token_hex
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings


class Role(BaseModel):
    """Represents a user role with scope, username, and password."""

    scope: str
    uname: str
    pword: str


class DBSettings(BaseSettings):
    """Database settings and configuration."""

    pool_min_size: int = 1
    pool_max_size: int = 15
    db_host: str = "localhost"
    db_port: int = 1618
    db_base: str = "cleaners"
    db_postgres_password: str = Field(..., description="Database password")
    db_endpoint_password: str = Field(..., description="Backend password")
    db_customer_password: str = Field(..., description="Frontend password")
    default_roles: Dict[str, Role] = {}

    class Config:
        env_file = ".env"
        env_prefix = "DB_"

    def get_role(self, role_name: Optional[str] = None) -> Optional[Role]:
        """Retrieve the Role object for a given role name."""
        return self.default_roles.get(role_name or "customer")

    @model_validator(mode="after")
    def set_default_roles(cls, values):
        """Set default roles after model initialization."""
        values.default_roles = {
            "postgres": Role(
                scope="DATABASE", uname="postgres", pword=values.db_postgres_password
            ),
            "endpoint": Role(
                scope="BACKEND", uname="endpoint", pword=values.db_endpoint_password
            ),
            "customer": Role(
                scope="FRONTEND", uname="customer", pword=values.db_customer_password
            ),
        }
        return values


class CORSSettings(BaseSettings):
    """Settings related to Cross-Origin Resource Sharing (CORS)."""

    allow_headers: List[str] = ["Authorization", "Content-Type", "X-API-Version"]
    allow_methods: List[str] = ["OPTIONS", "GET", "POST", "PATCH", "PUT", "DELETE"]
    allow_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    class Config:
        env_prefix = "CORS_"


class ServerSettings(BaseSettings):
    """Server configuration settings."""

    host: str = "127.0.0.1"
    port: int = 8173

    class Config:
        env_prefix = "SERVER_"


class JWTSettings(BaseSettings):
    """Settings for JSON Web Tokens (JWT)."""

    alg: str = "HS256"
    key: str = Field(default_factory=lambda: token_hex(32))
    at_exp: int = 1800  # Access token expiration time in seconds
    rt_exp: int = 180000  # Refresh token expiration time in seconds

    class Config:
        env_prefix = "JWT_"


class LoggingSettings(BaseSettings):
    """Configuration for application logging."""

    # Log formats
    logfmt_default: str = "[bold red]%(funcName)s[/bold red]: %(message)s"
    logfmt_details: str = (
        "[%(asctime)s][%(levelname)s][%(name)s] at ('%(pathname)s \\ %(filename)s' "
        "#%(lineno)d) in %(module)s %(funcName)s: { ```%(message)s``` }"
    )
    log_datefmt: str = "[%H:%M:%S]"
    # Logging configurations
    dev_terminal_level: str = "INFO"
    dev_terminal_class: str = "rich.logging.RichHandler"
    dev_terminal_formatter: str = "default"
    dev_terminal_rich_tracebacks: bool = True
    dev_terminal_markup: bool = True
    logs_history_level: str = "WARNING"
    logs_history_class: str = "logging.FileHandler"
    logs_history_formatter: str = "details"
    logs_history_filename: str = "history.log"
    prod_console_level: str = "ERROR"
    prod_console_class: str = "logging.StreamHandler"
    prod_console_formatter: str = "default"
    prod_console_stream: str = "ext://sys.stdout"

    class Config:
        env_prefix = "LOG_"


class Settings(BaseSettings):
    """Main application settings."""

    APP_TITLE: str = Field("My FastAPI App", env="APP_TITLE")
    APP_DESCRIPTION: str = Field("Description of my FastAPI app", env="APP_DESCRIPTION")
    APP_VERSION: str = Field("1.0.0", env="APP_VERSION")
    # Paths to application directories
    app_path: Optional[Path] = Field(
        default_factory=lambda: Path(__file__).resolve().parents[2], env="APP_PATH"
    )
    back_path: Optional[Path] = Field(None, env="BACK_PATH")
    front_path: Optional[Path] = Field(None, env="FRONT_PATH")
    front_src_path: Optional[Path] = Field(None, env="FRONT_SRC_PATH")
    front_res_path: Optional[Path] = Field(None, env="FRONT_RES_PATH")
    # Include all settings
    cors: CORSSettings = CORSSettings()
    server: ServerSettings = ServerSettings()
    database: DBSettings = DBSettings()
    jwt: JWTSettings = JWTSettings()
    logging: LoggingSettings = LoggingSettings()

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")

    @model_validator(mode="after")
    def set_default_paths(cls, values):
        """Set default paths after model initialization."""
        if not values.back_path:
            values.back_path = values.app_path / "backend"
        if not values.front_path:
            values.front_path = values.app_path / "frontend"
        if not values.front_src_path:
            values.front_src_path = values.front_path / "src"
        if not values.front_res_path:
            values.front_res_path = values.front_path / "dist"
        return values


# Initialize settings
settings = Settings()
