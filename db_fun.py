# db_fun.py
from abc import ABC, abstractmethod

from db_con import PGPool, con_gen, fmt, pools


class DBFunc(ABC):
    """Abstract base class defining the database functionality interface."""

    @abstractmethod
    async def get_tables(self, payload: dict):
        """Retrieve a list of tables accessible based on the user's role."""
        pass

    @abstractmethod
    async def get_records(self, payload: dict, table: str):
        """Fetch records from a specific table according to user access level."""
        pass

    @abstractmethod
    async def get_schema(self, payload: dict, table: str):
        """Get the schema of a specific table detailing columns and data types."""
        pass


class PGFunc(DBFunc):
    """PostgreSQL implementation of DBFunc providing specific methods to interact with the database."""

    def __init__(self, pools: PGPool):
        self.pools = pools  # Database connection pool

    async def get_tables(self, payload: dict):
        """Fetch and return tables that the user has permission to access."""
        async with con_gen(pools, payload.get("uname")) as con:
            query = "SELECT * FROM shared.extract_selectable_tables($1)"
            return await con.fetch(query, payload.get("role"))

    async def strip_validate_tab(self, payload: dict, table: str):
        """Validate and sanitize table name from user input against allowed tables."""
        table = fmt(table)  # Remove unwanted characters from table name
        visible = [rec["table_name"] for rec in await self.get_tables(payload)]
        if table not in visible:
            raise ValueError(f"Invalid table name: {fmt(table)}. Check your input.")
        return table

    async def get_records(self, payload: dict, table: str):
        """Retrieve all records from a validated table name."""
        table = await self.strip_validate_tab(payload, table)
        async with con_gen(pools, payload.get("uname")) as con:
            await con.execute("SET search_path TO pi")
            return await con.fetch(f'SELECT * FROM "{fmt(table)}"')

    async def get_schema(self, payload: dict, table: str):
        """Obtain the schema of a specific table including column details and types."""
        table = await self.strip_validate_tab(payload, table)
        async with con_gen(pools, payload.get("uname")) as con:
            query = "SELECT * FROM shared.extract_table_metadata('pi', $1)"
            return await con.fetch(query, fmt(table))


funcs = PGFunc(pools)  # Instance of the PostgreSQL functions
