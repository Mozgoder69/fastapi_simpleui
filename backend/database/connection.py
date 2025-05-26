# backend/database/connection.py

"""Handles database connections and manages PostgreSQL connection pools."""

import asyncio
import contextvars
import re
from abc import ABC
from contextlib import asynccontextmanager
from enum import Enum

import asyncpg
from asyncpg import Connection, create_pool
from config.logging import logger
from config.settings import settings
from fastapi import HTTPException
from pydantic import BaseModel


class SessionData(BaseModel):
    customer_id: int | None = None
    employee_id: int | None = None
    branch_id: int | None = None

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)


session_vars = contextvars.ContextVar("session_vars", default={})


def sanitize(text: str) -> str:
    """Remove special characters to sanitize inputs."""
    return re.sub(r"[\s\[\](){}<>,;:=+*&%#@?!|/\\\"'`^~-]+", "", text)


def url(uname=None, pword=None, host=None, port=None, base=None):
    """Construct a PostgreSQL database URL."""
    default_role = settings.database.get_role()
    if default_role is None:
        raise HTTPException(500, "Default customer role is not configured")
    uname = uname or default_role.uname
    pword = pword or default_role.pword
    host = host or settings.database.db_host
    port = port or settings.database.db_port
    base = base or settings.database.db_base
    return f"postgresql://{uname}:{pword}@{host}:{port}/{base}"


class PGPool(ABC):
    """Manages PostgreSQL connection pools."""

    def __contains__(self, pool):
        return pool in self.pools

    def __getitem__(self, key):
        return self.pools[key]

    def __init__(self):
        self.pools = {}
        self._lock = asyncio.Lock()

    async def init_pool(self, role: str, uname: str = None, pword: str = None):
        if role in self.pools:
            return self.pools[role]
        async with self._lock:
            if role not in self.pools:
                role_creds = settings.database.get_role(role)
                if role_creds:
                    uname = uname or role_creds.uname
                    pword = pword or role_creds.pword
                else:
                    if not uname or not pword:
                        raise HTTPException(
                            400, "Username and password are required for new pool"
                        )
                dsn = url(uname, pword)
                try:
                    self.pools[role] = await create_pool(
                        dsn,
                        min_size=settings.database.pool_min_size,
                        max_size=settings.database.pool_max_size,
                        timeout=30,
                    )
                    logger.info(f"Created pool for role {role}")
                except Exception as e:
                    logger.error(f"Failed to create pool for role {role}: {e}")
                    raise HTTPException(500, f"Failed to create pool: {e}") from e
            return self.pools[role]

    async def get_pool(self, role: str, uname: str = None, pword: str = None):
        if not role:
            raise ValueError("Role is required")
        try:
            return self.pools[role]
        except KeyError:
            return await self.init_pool(role, uname, pword)

    async def close_pool(self, role: str):
        pool = self.pools.pop(role, None)
        if pool:
            await pool.close()
            logger.info(f"Closed pool for role {role}")

    async def close_all_pools(self):
        for role in list(self.pools.keys()):
            try:
                await self.close_pool(role)
            except Exception as e:
                logger.error(f"Error closing pool: {e}")


pools = PGPool()


class ConType(Enum):
    """Types of database connections."""

    SIMPLE = "simple"  # Simple connection for authentication
    POOLED = "pooled"  # Connection from pool
    SESSION = "session"  # Connection with session context


class DBCon:
    """Manages different types of database connections."""

    @staticmethod
    async def _setup_session(conn: Connection, role: str):
        """Setup session context."""
        vars = session_vars.get()
        # logger.info(
        #     f"role: {role}, cid: {vars['customer_id']}, eid: {vars['employee_id']}, bid: {vars['branch_id']}"
        # )
        await conn.execute(
            """CREATE TEMP TABLE IF NOT EXISTS app_session (
                position TEXT PRIMARY KEY, customer_id INT, employee_id INT, branch_id INT
            ) ON COMMIT PRESERVE ROWS"""
        )

        # Вставляем запись или обновляем её, если она уже есть
        await conn.execute(
            """INSERT INTO app_session (position, customer_id, employee_id, branch_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (position) DO UPDATE
            SET customer_id = EXCLUDED.customer_id,
                employee_id = EXCLUDED.employee_id,
                branch_id = EXCLUDED.branch_id""",
            role,
            vars.get("customer_id"),
            vars.get("employee_id"),
            vars.get("branch_id"),
        )

    @staticmethod
    async def _cleanup_session(conn: Connection):
        """Cleanup session context."""
        await conn.execute("DROP TABLE IF EXISTS app_session")

    @staticmethod
    @asynccontextmanager
    async def connect(
        role: str,
        conn_type: ConType = ConType.SESSION,
        uname: str = None,
        pword: str = None,
    ):
        """Universal connection context manager."""
        if not role:
            raise ValueError("Role is required")

        if conn_type == ConType.SIMPLE:
            if not uname:
                raise ValueError("Credentials required for simple connection")
            conn = await asyncpg.connect(dsn=url(uname, pword))
            try:
                yield conn
            finally:
                await conn.close()
        else:
            # Для пулов используем либо переданные credentials, либо из сессии
            pool = await pools.get_pool(role, uname, pword)
            conn = await pool.acquire()
            try:
                if conn_type == ConType.SESSION:
                    await DBCon._setup_session(conn, role)
                yield conn
                if conn_type == ConType.SESSION:
                    await DBCon._cleanup_session(conn)
            except Exception as e:
                err_msg = f"Database connection failed: {str(e)}"
                logger.error(err_msg)
                raise HTTPException(status_code=500, detail=err_msg) from e
            finally:
                await pool.release(conn)
