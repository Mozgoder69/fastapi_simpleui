# routes/bss_ops/archive/reports.py

from auth import decode_token
from fastapi import APIRouter, Depends, Query
from routes.db_execute import execute_query

router = APIRouter()


# Эндпоинт для генерации отчета о выполнении задач сотрудниками
@router.get("/reports/employee-task-performance")
async def generate_employee_task_performance_report(
    start_date: str = Query(..., description="Начальная дата отчета (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Конечная дата отчета (YYYY-MM-DD)"),
    payload: dict = Depends(decode_token),
):
    query = "SELECT * FROM bss_ops_activity.generate_employee_task_performance_report($1, $2);"
    return await execute_query(query, start_date, end_date, fetch=True, payload=payload)


# Эндпоинт для генерации отчета о выполнении заказов сотрудниками
@router.get("/reports/employee-order-performance")
async def generate_employee_order_performance_report(
    start_date: str = Query(..., description="Начальная дата отчета (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Конечная дата отчета (YYYY-MM-DD)"),
    payload: dict = Depends(decode_token),
):
    query = "SELECT * FROM bss_ops_activity.generate_employee_order_performance_report($1, $2);"
    return await execute_query(query, start_date, end_date, fetch=True, payload=payload)


# Эндпоинт для генерации отчета об использовании услуг
@router.get("/reports/service-usage")
async def generate_service_usage_report(
    start_date: str = Query(..., description="Начальная дата отчета (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Конечная дата отчета (YYYY-MM-DD)"),
    payload: dict = Depends(decode_token),
):
    query = "SELECT * FROM bss_ops_activity.generate_service_usage_report($1, $2);"
    return await execute_query(query, start_date, end_date, fetch=True, payload=payload)


# Эндпоинт для генерации отчета об удовлетворенности услугами
@router.get("/reports/service-satisfaction")
async def generate_service_satisfaction_report(
    start_date: str = Query(..., description="Начальная дата отчета (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Конечная дата отчета (YYYY-MM-DD)"),
    payload: dict = Depends(decode_token),
):
    query = (
        "SELECT * FROM bss_ops_activity.generate_service_satisfaction_report($1, $2);"
    )
    return await execute_query(query, start_date, end_date, fetch=True, payload=payload)


# Эндпоинт для генерации отчета об изменениях в каталоге
@router.get("/reports/catalog-change")
async def generate_catalog_change_report(
    start_date: str = Query(..., description="Начальная дата отчета (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Конечная дата отчета (YYYY-MM-DD)"),
    payload: dict = Depends(decode_token),
):
    query = "SELECT * FROM bss_ops_ctg_items.generate_catalog_change_report($1, $2);"
    return await execute_query(query, start_date, end_date, fetch=True, payload=payload)


# Эндпоинт для генерации отчета о сроках выполнения заказов
@router.get("/reports/order-timing")
async def generate_order_timing_report(
    start_date: str = Query(..., description="Начальная дата отчета (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Конечная дата отчета (YYYY-MM-DD)"),
    payload: dict = Depends(decode_token),
):
    query = "SELECT * FROM bss_ops_mkg_line.generate_order_timing_report($1, $2);"
    return await execute_query(query, start_date, end_date, fetch=True, payload=payload)


# Эндпоинт для генерации отчета об использовании каталога
@router.get("/reports/catalog-usage")
async def generate_catalog_usage_report(
    start_date: str = Query(..., description="Начальная дата отчета (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Конечная дата отчета (YYYY-MM-DD)"),
    payload: dict = Depends(decode_token),
):
    query = "SELECT * FROM bss_ops_ctg_items.generate_catalog_usage_report($1, $2);"
    return await execute_query(query, start_date, end_date, fetch=True, payload=payload)
