# routes/bss_ops/archive/ctg_items.py

from auth import decode_token
from fastapi import APIRouter, Depends, HTTPException, status
from routes.db_execute import execute_query

router = APIRouter()


# Factor endpoints
@router.post("/factor/", status_code=status.HTTP_201_CREATED)
async def insert_factor(name: str, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_ctg_items.insert_factor($1);"
    return {
        "factor_id": await execute_query(query, name, fetchval=True, payload=payload)
    }


@router.put("/factor/{factor_id}/")
async def update_factor(
    factor_id: int, name: str, is_active: bool, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_items.update_factor($1, $2, $3);"
    return await execute_query(query, factor_id, name, is_active, payload=payload)


@router.get("/factor/{factor_id}/")
async def select_factor(factor_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_items.select_factor($1);"
    factor = await execute_query(query, factor_id, fetchrow=True, payload=payload)
    if factor:
        return dict(factor)
    raise HTTPException(status_code=404, detail="Factor not found")


# Stage endpoints
@router.post("/stage/", status_code=status.HTTP_201_CREATED)
async def insert_stage(
    name: str,
    priority: int,
    type: str,
    mode: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_ctg_items.insert_stage($1, $2, $3, $4);"
    return {
        "stage_id": await execute_query(
            query, name, priority, type, mode, fetchval=True, payload=payload
        )
    }


@router.put("/stage/{stage_id}/")
async def update_stage(
    stage_id: int,
    name: str,
    priority: int,
    type: str,
    mode: str,
    is_active: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_ctg_items.update_stage($1, $2, $3, $4, $5, $6);"
    return await execute_query(
        query, stage_id, name, priority, type, mode, is_active, payload=payload
    )


@router.get("/stage/{stage_id}/")
async def select_stage(stage_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_items.select_stage($1);"
    stage = await execute_query(query, stage_id, fetchrow=True, payload=payload)
    if stage:
        return dict(stage)
    raise HTTPException(status_code=404, detail="Stage not found")


# Method endpoints
@router.post("/method/", status_code=status.HTTP_201_CREATED)
async def insert_method(
    name: str,
    stage_id: int,
    term_base: int,
    cost_rate: float,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_ctg_items.insert_method($1, $2, $3, $4);"
    return {
        "method_id": await execute_query(
            query, name, stage_id, term_base, cost_rate, fetchval=True, payload=payload
        )
    }


@router.put("/method/{method_id}/")
async def update_method(
    method_id: int,
    name: str,
    stage_id: int,
    term_base: int,
    cost_rate: float,
    is_active: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_ctg_items.update_method($1, $2, $3, $4, $5, $6);"
    return await execute_query(
        query,
        method_id,
        name,
        stage_id,
        term_base,
        cost_rate,
        is_active,
        payload=payload,
    )


@router.get("/method/{method_id}/")
async def select_method(method_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_items.select_method($1);"
    method = await execute_query(query, method_id, fetchrow=True, payload=payload)
    if method:
        return dict(method)
    raise HTTPException(status_code=404, detail="Method not found")


# Scenario endpoints
@router.post("/scenario/", status_code=status.HTTP_201_CREATED)
async def insert_scenario(name: str, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_ctg_items.insert_scenario($1);"
    return {
        "scenario_id": await execute_query(query, name, fetchval=True, payload=payload)
    }


@router.put("/scenario/{scenario_id}/")
async def update_scenario(
    scenario_id: int, name: str, is_active: bool, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_items.update_scenario($1, $2, $3);"
    return await execute_query(query, scenario_id, name, is_active, payload=payload)


@router.get("/scenario/{scenario_id}/")
async def select_scenario(scenario_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_items.select_scenario($1);"
    scenario = await execute_query(query, scenario_id, fetchrow=True, payload=payload)
    if scenario:
        return dict(scenario)
    raise HTTPException(status_code=404, detail="Scenario not found")


# Category endpoints
@router.post("/category/", status_code=status.HTTP_201_CREATED)
async def insert_category(
    name: str,
    purpose: str,
    cost_base: float,
    term_rate: float,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_ctg_items.insert_category($1, $2, $3, $4);"
    return {
        "category_id": await execute_query(
            query, name, purpose, cost_base, term_rate, fetchval=True, payload=payload
        )
    }


@router.put("/category/{category_id}/")
async def update_category(
    category_id: int,
    name: str,
    purpose: str,
    cost_base: float,
    term_rate: float,
    is_active: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_ctg_items.update_category($1, $2, $3, $4, $5, $6);"
    return await execute_query(
        query,
        category_id,
        name,
        purpose,
        cost_base,
        term_rate,
        is_active,
        payload=payload,
    )


@router.get("/category/{category_id}/")
async def select_category(category_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_items.select_category($1);"
    category = await execute_query(query, category_id, fetchrow=True, payload=payload)
    if category:
        return dict(category)
    raise HTTPException(status_code=404, detail="Category not found")


# Material endpoints
@router.post("/material/", status_code=status.HTTP_201_CREATED)
async def insert_material(
    name: str, source: str, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_items.insert_material($1, $2);"
    return {
        "material_id": await execute_query(
            query, name, source, fetchval=True, payload=payload
        )
    }


@router.put("/material/{material_id}/")
async def update_material(
    material_id: int,
    name: str,
    source: str,
    is_active: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_ctg_items.update_material($1, $2, $3, $4);"
    return await execute_query(
        query, material_id, name, source, is_active, payload=payload
    )


@router.get("/material/{material_id}/")
async def select_material(material_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_items.select_material($1);"
    material = await execute_query(query, material_id, fetchrow=True, payload=payload)
    if material:
        return dict(material)
    raise HTTPException(status_code=404, detail="Material not found")


# Pollution endpoints
@router.post("/pollution/", status_code=status.HTTP_201_CREATED)
async def insert_pollution(
    name: str, source: str, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_items.insert_pollution($1, $2);"
    return {
        "pollution_id": await execute_query(
            query, name, source, fetchval=True, payload=payload
        )
    }


@router.put("/pollution/{pollution_id}/")
async def update_pollution(
    pollution_id: int,
    name: str,
    source: str,
    is_active: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_ctg_items.update_pollution($1, $2, $3, $4);"
    return await execute_query(
        query, pollution_id, name, source, is_active, payload=payload
    )


@router.get("/pollution/{pollution_id}/")
async def select_pollution(pollution_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_items.select_pollution($1);"
    pollution = await execute_query(query, pollution_id, fetchrow=True, payload=payload)
    if pollution:
        return dict(pollution)
    raise HTTPException(status_code=404, detail="Pollution not found")


# Symbol endpoints
@router.post("/symbol/", status_code=status.HTTP_201_CREATED)
async def insert_symbol(
    specifics: str, stage_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_items.insert_symbol($1, $2);"
    return {
        "symbol_id": await execute_query(
            query, specifics, stage_id, fetchval=True, payload=payload
        )
    }


@router.put("/symbol/{symbol_id}/")
async def update_symbol(
    symbol_id: int,
    specifics: str,
    stage_id: int,
    is_active: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_ctg_items.update_symbol($1, $2, $3, $4);"
    return await execute_query(
        query, symbol_id, specifics, stage_id, is_active, payload=payload
    )


@router.get("/symbol/{symbol_id}/")
async def select_symbol(symbol_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_items.select_symbol($1);"
    symbol = await execute_query(query, symbol_id, fetchrow=True, payload=payload)
    if symbol:
        return dict(symbol)
    raise HTTPException(status_code=404, detail="Symbol not found")


# Method Chem endpoints
@router.post("/method_chem/", status_code=status.HTTP_201_CREATED)
async def insert_method_chem(
    method_id: int, items_count: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_items.insert_method_chem($1, $2);"
    return await execute_query(query, method_id, items_count, payload=payload)


@router.put("/method_chem/{method_id}/")
async def update_method_chem(
    method_id: int, items_count: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_items.update_method_chem($1, $2);"
    return await execute_query(query, method_id, items_count, payload=payload)


# Method Mech endpoints
@router.post("/method_mech/", status_code=status.HTTP_201_CREATED)
async def insert_method_mech(method_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_ctg_items.insert_method_mech($1);"
    return await execute_query(query, method_id, payload=payload)


@router.put("/method_mech/{method_id}/")
async def update_method_mech(
    method_id: int, is_occupied: bool, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_items.update_method_mech($1, $2);"
    return await execute_query(query, method_id, is_occupied, payload=payload)


# Additional filtering endpoints
@router.get("/check_active_orders/")
async def check_active_orders_before_change(
    item_id: int, item_type: str, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_ctg_items.check_active_orders_before_change($1, $2);"
    return {
        "is_active": await execute_query(
            query, item_id, item_type, fetchval=True, payload=payload
        )
    }


@router.get("/filter/services_by_category/")
async def filter_services_by_category(
    category: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_ctg_items.filter_services_by_category($1);"
    services = await execute_query(query, category, fetch=True, payload=payload)
    return [dict(service) for service in services]


@router.get("/filter/materials_by_source/")
async def filter_materials_by_source(
    source: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_ctg_items.filter_materials_by_source($1);"
    materials = await execute_query(query, source, fetch=True, payload=payload)
    return [dict(material) for material in materials]


@router.get("/filter/pollutions_by_source/")
async def filter_pollutions_by_source(
    source: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_ctg_items.filter_pollutions_by_source($1);"
    pollutions = await execute_query(query, source, fetch=True, payload=payload)
    return [dict(pollution) for pollution in pollutions]


@router.get("/filter/symbols_by_stage/")
async def filter_symbols_by_stage(stage_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_ctg_items.filter_symbols_by_stage($1);"
    symbols = await execute_query(query, stage_id, fetch=True, payload=payload)
    return [dict(symbol) for symbol in symbols]


@router.get("/filter/scenarios_by_purpose/")
async def filter_scenarios_by_purpose(
    purpose: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_ctg_items.filter_scenarios_by_purpose($1);"
    scenarios = await execute_query(query, purpose, fetch=True, payload=payload)
    return [dict(scenario) for scenario in scenarios]
