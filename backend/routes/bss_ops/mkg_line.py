# routes/bss_ops/mkg_line.py

from auth.jwt_handler import decode_token
from database.execution import QueryMode, execute
from fastapi import APIRouter, Depends, HTTPException, status

mkg_line_router = APIRouter(tags=["BSS_OPS"])


# Sales Order endpoints
@mkg_line_router.put("/salesorder/update/{salesorder_id}/cancel/")
async def cancel_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.cancel_salesorder($1);"
    return await execute(query, payload["role"], 0, salesorder_id)


@mkg_line_router.put("/salesorder/update/{salesorder_id}/accept/")
async def accept_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.accept_salesorder($1);"
    return await execute(query, payload["role"], 0, salesorder_id)


@mkg_line_router.put("/salesorder/update/{salesorder_id}/execute/")
async def execute_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.execute_salesorder($1);"
    return await execute(query, payload["role"], 0, salesorder_id)


@mkg_line_router.put("/salesorder/update/{salesorder_id}/finish/")
async def finish_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.finish_salesorder($1);"
    return await execute(query, payload["role"], 0, salesorder_id)


@mkg_line_router.put("/salesorder/update/{salesorder_id}/return/")
async def return_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.return_salesorder($1);"
    return await execute(query, payload["role"], 0, salesorder_id)
