# db_con.py
import re
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

from asyncpg import Connection, create_pool
from config import db_params, db_public, pool_size
from fastapi import HTTPException
from logs.myrich import logger


def fmt(text):
    """Remove special characters to sanitize inputs."""
    return re.sub(r"[\s\[\](){}<>,;:=+*&%#@?!|/\\\"'`^~-]+", "", text)


def url(uname=None, pword=None, host=None, port=None, base=None):
    """Construct database URL from provided credentials and defaults."""
    uname = uname or db_public.uname
    pword = pword or db_public.pword
    host = host or db_params.host
    port = port or db_params.port
    base = base or db_params.base
    return f"postgresql://{uname}:{pword}@{host}:{port}/{base}"


class DBPool(ABC):
    """Abstract base class to manage database connection pools."""

    def __contains__(self, pool):
        return pool in self.pools

    def __getitem__(self, key):
        return self.pools[key]

    def __init__(self):
        self.pools = {}

    @abstractmethod
    async def init_pool(self, uname: str, pword: str):
        """Initialize a new database connection pool."""
        pass

    @abstractmethod
    async def get_pool(self, uname: str, pword: str):
        """Retrieve an existing connection pool."""
        pass

    @abstractmethod
    async def close_pool(self, uname: str):
        """Close a specific connection pool."""
        pass


class PGPool(DBPool):
    """PostgreSQL connection pool management."""

    async def init_pool(self, uname=None, pword=None):
        """Create a new connection pool for the specified user."""
        if not uname:
            uname = db_public.uname  # use default if no uname
            pword = db_public.pword
        if uname not in self.pools:  # check existing pools for this uname
            if not pword:
                raise HTTPException(400, "Password is required for new pool")
            dsn = url(uname, pword)
            try:
                self.pools[uname] = await create_pool(dsn, **vars(pool_size))
            except Exception as e:
                raise HTTPException(500, f"Failed to create pool: {e}") from e
        return self.pools[uname]

    async def get_pool(self, uname: str, pword: str = None):
        """Retrieve or create a connection pool based on username."""
        if not uname:
            raise HTTPException(400, "Username is required to access a pool")
        try:
            return self.pools[uname]
        except KeyError:
            if not pword:
                raise HTTPException(400, "Password is required to create a pool")
            return await self.init_pool(uname, pword)

    async def close_pool(self, uname: str):
        """Close the specified connection pool if it exists."""
        pool = self.pools.pop(uname, None)
        if pool:
            await pool.close()

    async def close_all_pools(self):
        """Close all connection pools."""
        unames = list(self.pools.keys())
        for uname in unames:
            await self.close_pool(uname)


pools = PGPool()


@asynccontextmanager
async def con_gen(pools: PGPool, uname: str, pword: str = None) -> Connection:
    """Generator for database connections, ensuring proper cleanup."""
    if not uname:
        raise HTTPException(400, "Username required")
    pool = await pools.get_pool(uname, pword)
    con = await pool.acquire()
    try:
        yield con
    except Exception as e:
        err_msg = f"Failed to connect: {str(e)}"
        logger.debug(err_msg)
        raise HTTPException(500, err_msg) from e
    finally:
        await pool.release(con)
