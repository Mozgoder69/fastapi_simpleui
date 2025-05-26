# routes/bss_ops/ctg_rules.py

from auth.jwt_handler import decode_token
from database.execution import QueryMode, execute
from fastapi import APIRouter, Depends, status

ctg_rules_router = APIRouter(tags=["BSS_OPS"])
