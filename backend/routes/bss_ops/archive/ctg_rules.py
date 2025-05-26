# routes/bss_ops/archive/ctg_rules.py

from auth import decode_token
from fastapi import APIRouter, Depends, status
from routes.db_execute import execute_query

router = APIRouter()


# Catalyst endpoints
@router.post("/catalyst/", status_code=status.HTTP_201_CREATED)
async def insert_catalyst(
    stage_id: int, factor_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_rules.insert_catalyst($1, $2);"
    return await execute_query(query, stage_id, factor_id, payload=payload)


@router.delete("/catalyst/", status_code=status.HTTP_200_OK)
async def delete_catalyst(
    stage_id: int, factor_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_rules.delete_catalyst($1, $2);"
    return await execute_query(query, stage_id, factor_id, payload=payload)


@router.get("/catalyst/{stage_id}/")
async def select_catalyst(stage_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_rules.select_catalyst($1);"
    catalyst = await execute_query(query, stage_id, fetch=True, payload=payload)
    return [dict(record) for record in catalyst]


# Harmful Factor endpoints
@router.post("/harmful_factor/", status_code=status.HTTP_201_CREATED)
async def insert_harmful_factor(
    material_id: int, factor_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_rules.insert_harmful_factor($1, $2);"
    return await execute_query(query, material_id, factor_id, payload=payload)


@router.delete("/harmful_factor/", status_code=status.HTTP_200_OK)
async def delete_harmful_factor(
    material_id: int, factor_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_rules.delete_harmful_factor($1, $2);"
    return await execute_query(query, material_id, factor_id, payload=payload)


@router.get("/harmful_factor/{material_id}/")
async def select_harmful_factor(
    material_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_ctg_rules.select_harmful_factor($1);"
    harmful_factors = await execute_query(
        query, material_id, fetch=True, payload=payload
    )
    return [dict(record) for record in harmful_factors]


# Helpful Factor endpoints
@router.post("/helpful_factor/", status_code=status.HTTP_201_CREATED)
async def insert_helpful_factor(
    pollution_id: int, factor_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_rules.insert_helpful_factor($1, $2);"
    return await execute_query(query, pollution_id, factor_id, payload=payload)


@router.delete("/helpful_factor/", status_code=status.HTTP_200_OK)
async def delete_helpful_factor(
    pollution_id: int, factor_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_rules.delete_helpful_factor($1, $2);"
    return await execute_query(query, pollution_id, factor_id, payload=payload)


@router.get("/helpful_factor/{pollution_id}/")
async def select_helpful_factor(
    pollution_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_ctg_rules.select_helpful_factor($1);"
    helpful_factors = await execute_query(
        query, pollution_id, fetch=True, payload=payload
    )
    return [dict(record) for record in helpful_factors]


# Solution endpoints
@router.post("/solution/", status_code=status.HTTP_201_CREATED)
async def insert_solution(
    scenario_id: int, method_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_rules.insert_solution($1, $2);"
    return await execute_query(query, scenario_id, method_id, payload=payload)


@router.delete("/solution/", status_code=status.HTTP_200_OK)
async def delete_solution(
    scenario_id: int, method_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_rules.delete_solution($1, $2);"
    return await execute_query(query, scenario_id, method_id, payload=payload)


@router.get("/solution/{scenario_id}/")
async def select_solution(scenario_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_rules.select_solution($1);"
    solutions = await execute_query(query, scenario_id, fetch=True, payload=payload)
    return [dict(record) for record in solutions]
