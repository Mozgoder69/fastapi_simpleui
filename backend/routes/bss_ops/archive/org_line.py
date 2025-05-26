# routes/bss_ops/archive/org_line.py

from auth import decode_token
from fastapi import APIRouter, Depends, HTTPException, status
from routes.db_execute import execute_query

router = APIRouter()


# Product Material endpoints
@router.post("/product_material/", status_code=status.HTTP_201_CREATED)
async def insert_product_material(
    product_id: int,
    material_id: int,
    density: str,
    is_mix: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_org_line.insert_product_material($1, $2, $3, $4);"
    return await execute_query(
        query, product_id, material_id, density, is_mix, payload=payload
    )


@router.delete("/product_material/{product_id}/{material_id}/")
async def delete_product_material(
    product_id: int, material_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_org_line.delete_product_material($1, $2);"
    return await execute_query(query, product_id, material_id, payload=payload)


@router.get("/product_material/{product_id}/")
async def select_product_material(
    product_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_org_line.select_product_material($1);"
    materials = await execute_query(query, product_id, fetch=True, payload=payload)
    return [dict(record) for record in materials]


# Product Pollution endpoints
@router.post("/product_pollution/", status_code=status.HTTP_201_CREATED)
async def insert_product_pollution(
    product_id: int,
    pollution_id: int,
    is_old: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_org_line.insert_product_pollution($1, $2, $3);"
    return await execute_query(query, product_id, pollution_id, is_old, payload=payload)


@router.put("/product_pollution/{product_id}/{pollution_id}/")
async def update_product_pollution(
    product_id: int,
    pollution_id: int,
    is_removed: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_org_line.update_product_pollution($1, $2, $3);"
    return await execute_query(
        query, product_id, pollution_id, is_removed, payload=payload
    )


@router.delete("/product_pollution/{product_id}/{pollution_id}/")
async def delete_product_pollution(
    product_id: int, pollution_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_org_line.delete_product_pollution($1, $2);"
    return await execute_query(query, product_id, pollution_id, payload=payload)


@router.get("/product_pollution/{product_id}/")
async def select_product_pollution(
    product_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_org_line.select_product_pollution($1);"
    pollutions = await execute_query(query, product_id, fetch=True, payload=payload)
    return [dict(record) for record in pollutions]


# Product Symbol endpoints
@router.post("/product_symbol/", status_code=status.HTTP_201_CREATED)
async def insert_product_symbol(
    product_id: int,
    symbol_id: int,
    is_underlined: bool,
    is_crossedout: bool,
    temperature: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_org_line.insert_product_symbol($1, $2, $3, $4, $5);"
    return await execute_query(
        query,
        product_id,
        symbol_id,
        is_underlined,
        is_crossedout,
        temperature,
        payload=payload,
    )


@router.delete("/product_symbol/{product_id}/{symbol_id}/")
async def delete_product_symbol(
    product_id: int, symbol_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_org_line.delete_product_symbol($1, $2);"
    return await execute_query(query, product_id, symbol_id, payload=payload)


@router.get("/product_symbol/{product_id}/")
async def select_product_symbol(product_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_org_line.select_product_symbol($1);"
    symbols = await execute_query(query, product_id, fetch=True, payload=payload)
    return [dict(record) for record in symbols]


# Scenario Onsite endpoints
@router.post("/scenario_onsite/", status_code=status.HTTP_201_CREATED)
async def insert_scenario_onsite(
    product_id: int,
    scenario_id: int,
    current_stage: int,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_org_line.insert_scenario_onsite($1, $2, $3);"
    return {
        "scenario_onsite_id": await execute_query(
            query,
            product_id,
            scenario_id,
            current_stage,
            fetchval=True,
            payload=payload,
        )
    }


@router.put("/scenario_onsite/{product_id}/{scenario_id}/")
async def update_scenario_onsite_stage(
    product_id: int,
    scenario_id: int,
    current_stage: int,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_org_line.update_scenario_onsite_stage($1, $2, $3);"
    return await execute_query(
        query, product_id, scenario_id, current_stage, payload=payload
    )


@router.delete("/scenario_onsite/{product_id}/{scenario_id}/")
async def delete_scenario_onsite(
    product_id: int, scenario_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_org_line.delete_scenario_onsite($1, $2);"
    return await execute_query(query, product_id, scenario_id, payload=payload)


@router.get("/scenario_onsite/{product_id}/{scenario_id}/")
async def select_scenario_onsite(
    product_id: int, scenario_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_org_line.select_scenario_onsite($1, $2);"
    scenario_onsite = await execute_query(
        query, product_id, scenario_id, fetchrow=True, payload=payload
    )
    if scenario_onsite:
        return dict(scenario_onsite)
    raise HTTPException(status_code=404, detail="Scenario onsite not found")


# Scenario Offsite endpoints
@router.post("/scenario_offsite/", status_code=status.HTTP_201_CREATED)
async def insert_scenario_offsite(
    address_id: int,
    scenario_id: int,
    rooms_left: int,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_org_line.insert_scenario_offsite($1, $2, $3);"
    return {
        "scenario_offsite_id": await execute_query(
            query, address_id, scenario_id, rooms_left, fetchval=True, payload=payload
        )
    }


@router.put("/scenario_offsite/{address_id}/{scenario_id}/")
async def update_scenario_offsite_rooms(
    address_id: int,
    scenario_id: int,
    rooms_left: int,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_org_line.update_scenario_offsite_rooms($1, $2, $3);"
    return await execute_query(
        query, address_id, scenario_id, rooms_left, payload=payload
    )


@router.delete("/scenario_offsite/{address_id}/{scenario_id}/")
async def delete_scenario_offsite(
    address_id: int, scenario_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_org_line.delete_scenario_offsite($1, $2);"
    return await execute_query(query, address_id, scenario_id, payload=payload)


@router.get("/scenario_offsite/{address_id}/{scenario_id}/")
async def select_scenario_offsite(
    address_id: int, scenario_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_org_line.select_scenario_offsite($1, $2);"
    scenario_offsite = await execute_query(
        query, address_id, scenario_id, fetchrow=True, payload=payload
    )
    if scenario_offsite:
        return dict(scenario_offsite)
    raise HTTPException(status_code=404, detail="Scenario offsite not found")
