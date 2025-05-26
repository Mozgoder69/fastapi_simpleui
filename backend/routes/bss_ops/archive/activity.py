# routes/bss_ops/archive/activity.py

from auth import decode_token
from fastapi import APIRouter, Depends, HTTPException, status
from routes.db_execute import execute_query  # Импортируем функцию execute_query

router = APIRouter()


# Process endpoints
@router.post("/process/", status_code=status.HTTP_201_CREATED)
async def insert_process(
    opened_by: int, status: str, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_activity.insert_process($1, $2);"
    return {
        "process_id": await execute_query(
            query, opened_by, status, fetchval=True, payload=payload
        )
    }


@router.put("/process/{process_id}/")
async def update_process(
    process_id: int, status: str, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_activity.update_process($1, $2);"
    return await execute_query(query, process_id, status, payload=payload)


@router.get("/process/{process_id}/")
async def select_process(process_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_activity.select_process($1);"
    process = await execute_query(query, process_id, fetchrow=True, payload=payload)
    if process:
        return dict(process)
    raise HTTPException(status_code=404, detail="Process not found")


# Workflow endpoints
@router.post("/workflow/", status_code=status.HTTP_201_CREATED)
async def insert_workflow(
    process_id: int,
    employee_id: int,
    result_status: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_activity.insert_workflow($1, $2, $3);"
    return await execute_query(
        query, process_id, employee_id, result_status, payload=payload
    )


@router.get("/workflow/{process_id}/")
async def select_workflow(process_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_activity.select_workflow($1);"
    workflow = await execute_query(query, process_id, fetch=True, payload=payload)
    return [dict(record) for record in workflow]


# Request endpoints
@router.post("/request/", status_code=status.HTTP_201_CREATED)
async def insert_request(
    process_id: int, action: str, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_activity.insert_request($1, $2);"
    return {
        "request_id": await execute_query(
            query, process_id, action, fetchval=True, payload=payload
        )
    }


@router.post("/request/{request_id}/accept/")
async def accept_request(request_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_activity.accept_request($1);"
    return await execute_query(query, request_id, payload=payload)


@router.post("/request/{request_id}/reject/")
async def reject_request(request_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_activity.reject_request($1);"
    return await execute_query(query, request_id, payload=payload)


@router.get("/request/{request_id}/")
async def select_request(request_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_activity.select_request($1);"
    request = await execute_query(query, request_id, fetchrow=True, payload=payload)
    if request:
        return dict(request)
    raise HTTPException(status_code=404, detail="Request not found")
