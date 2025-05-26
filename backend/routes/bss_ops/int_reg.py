# routes/bss_ops/int_reg.py

from auth.jwt_handler import decode_token
from database.execution import QueryMode, execute
from fastapi import APIRouter, Depends, HTTPException, status

int_reg_router = APIRouter(tags=["BSS_OPS"])


# Password reset endpoint
@int_reg_router.put("/employee/{employee_id}/reset_password/")
async def reset_password(
    employee_id: int, password: str, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_reg_int.reset_password($1, $2);"
    return await execute(query, payload["role"], 0, employee_id, password)
