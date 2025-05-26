# routes/bss_ops/ext_reg.py
from typing import Optional

from auth.jwt_handler import JWTType, decode_token, encode_token
from auth.otp_handler import generate_otp, validate_otp
from database.execution import QueryMode, execute
from fastapi import APIRouter, Depends, HTTPException

ext_reg_router = APIRouter(tags=["BSS_OPS"])


@ext_reg_router.get("/contact/validate")
async def validate_unique_contact(contact: str, payload: dict = Depends(decode_token)):
    """Checks if contact is unique (not associated with any existing customer)."""
    role = payload["role"]
    query = "SELECT bss_ops_reg_ext.validate_unique_contact($1);"
    is_unique = await execute(query, role, QueryMode.FETCHVAL, (contact,))
    return {"is_unique": is_unique}
