# pg_fun.py

import string
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from pg_con import gen_con

async def get_selectable_tables(role):
    async for con in gen_con(role):
        query = f"select * from shared.extract_selectable_tables($1)"
        return await con.fetch(query, role)

async def strip_validate_tab(table_name):
    table_name = table_name.translate(str.maketrans("", "", string.whitespace))
    available_tables = [record['table_name'] for record in await get_selectable_tables('postgres')]

    if table_name not in available_tables:
        raise ValueError(f"Invalid table name: {table_name}. Check your input.")
    
    return table_name

async def get_table_columns(table_name):
    table_name = await strip_validate_tab(table_name)
    async for con in gen_con("postgres"):
        query = "SELECT * FROM shared.extract_table_columns($1)"
        return await con.fetch(query, table_name)

async def get_table_records(table_name):
    table_name = await strip_validate_tab(table_name)
    async for con in gen_con("postgres"):
        await con.execute('SET search_path TO pi')
        query = f'SELECT * FROM "{table_name}"'
        return await con.fetch(query)

# async def get_enum_values(enum_name):
#     enum_name = await