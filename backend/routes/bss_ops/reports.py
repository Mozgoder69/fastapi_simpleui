# routes/bss_ops/reports.py

from auth.jwt_handler import decode_token
from database.execution import QueryMode, execute
from fastapi import APIRouter, Depends, Query

reports_router = APIRouter(tags=["BSS_OPS"])


# Эндпоинт для генерации отчета о выполнении задач сотрудниками
@reports_router.get("/reports/employee-task-performance")
async def generate_employee_task_performance_report(
    start_date: str, end_date: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_activity.generate_employee_task_performance_report($1, $2);"
    return await execute(query, payload["role"], QueryMode.FETCH, start_date, end_date)


# Эндпоинт для генерации отчета о выполнении заказов сотрудниками
@reports_router.get("/reports/employee-order-performance")
async def generate_employee_order_performance_report(
    start_date: str, end_date: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_activity.generate_employee_order_performance_report($1, $2);"
    return await execute(query, payload["role"], QueryMode.FETCH, start_date, end_date)


# Эндпоинт для генерации отчета об использовании услуг
@reports_router.get("/reports/service-usage")
async def generate_service_usage_report(
    start_date: str, end_date: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_activity.generate_service_usage_report($1, $2);"
    return await execute(query, payload["role"], QueryMode.FETCH, start_date, end_date)


# Эндпоинт для генерации отчета об удовлетворенности услугами
@reports_router.get("/reports/service-satisfaction")
async def generate_service_satisfaction_report(
    start_date: str, end_date: str, payload: dict = Depends(decode_token)
):
    query = (
        "SELECT * FROM bss_ops_activity.generate_service_satisfaction_report($1, $2);"
    )
    return await execute(query, payload["role"], QueryMode.FETCH, start_date, end_date)


# Эндпоинт для генерации отчета об изменениях в каталоге
@reports_router.get("/reports/catalog-change")
async def generate_catalog_change_report(
    start_date: str, end_date: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_ctg_items.generate_catalog_change_report($1, $2);"
    return await execute(query, payload["role"], QueryMode.FETCH, start_date, end_date)


# Эндпоинт для генерации отчета о сроках выполнения заказов
@reports_router.get("/reports/order-timing")
async def generate_order_timing_report(
    start_date: str, end_date: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_mkg_line.generate_order_timing_report($1, $2);"
    return await execute(query, payload["role"], QueryMode.FETCH, start_date, end_date)


# Эндпоинт для генерации отчета об использовании каталога
@reports_router.get("/reports/catalog-usage")
async def generate_catalog_usage_report(
    start_date: str, end_date: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_ctg_items.generate_catalog_usage_report($1, $2);"
    return await execute(query, payload["role"], QueryMode.FETCH, start_date, end_date)
