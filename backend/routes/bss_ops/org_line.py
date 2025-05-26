# routes/bss_ops/org_line.py

from auth.jwt_handler import decode_token
from database.execution import QueryMode, execute
from fastapi import APIRouter, Depends, HTTPException, status

org_line_router = APIRouter(tags=["BSS_OPS"])


# Scenarios endpoints
@org_line_router.put("/scenario_offsite/update/{address_id}/{scenario_id}/")
async def update_scenario_offsite_rooms(
    address_id: int,
    scenario_id: int,
    rooms_left: int,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_org_line.update_scenario_offsite_rooms($1, $2, $3);"
    return await execute(query, payload["role"], 0, address_id, scenario_id, rooms_left)


@org_line_router.put("/scenario_onsite/update/{product_id}/{scenario_id}/")
async def update_scenario_onsite_stage(
    product_id: int,
    scenario_id: int,
    current_stage: int,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_org_line.update_scenario_onsite_stage($1, $2, $3);"
    return await execute(
        query, payload["role"], 0, product_id, scenario_id, current_stage
    )
