# routes/bss_ops/activity.py

from auth.jwt_handler import decode_token
from database.execution import QueryMode, execute
from fastapi import APIRouter, Depends, HTTPException, status

activity_router = APIRouter(tags=["BSS_OPS"])


# Request endpoints
@activity_router.put("/request/{request_id}/accept/")
async def accept_request(request_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_activity.accept_request($1);"
    return await execute(query, payload["role"], 0, request_id)


@activity_router.put("/request/{request_id}/reject/")
async def reject_request(request_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_activity.reject_request($1);"
    return await execute(query, payload["role"], 0, request_id)
