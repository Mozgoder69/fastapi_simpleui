# routes/bss_ops/archive/int_reg.py

from auth import decode_token
from fastapi import APIRouter, Depends, HTTPException, status
from routes.db_execute import execute_query

router = APIRouter()


# Branch endpoints
@router.post("/branch/", status_code=status.HTTP_201_CREATED)
async def insert_branch(
    address_id: int,
    name: str,
    opened_at: str,
    closed_at: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_int.insert_branch($1, $2, $3, $4);"
    return await execute_query(
        query, address_id, name, opened_at, closed_at, payload=payload
    )


@router.put("/branch/{branch_id}/")
async def update_branch(
    branch_id: int,
    name: str,
    opened_at: str,
    closed_at: str,
    is_active: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_int.update_branch($1, $2, $3, $4, $5);"
    return await execute_query(
        query, branch_id, name, opened_at, closed_at, is_active, payload=payload
    )


@router.get("/branch/{branch_id}/")
async def select_branch(branch_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_reg_int.select_branch($1);"
    branch = await execute_query(query, branch_id, fetchrow=True, payload=payload)
    if branch:
        return dict(branch)
    raise HTTPException(status_code=404, detail="Branch not found")


# Employee endpoints
@router.post("/employee/", status_code=status.HTTP_201_CREATED)
async def insert_employee(
    first_name: str,
    last_name: str,
    position: str,
    signup_date: str,
    branch_id: int,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_int.insert_employee($1, $2, $3, $4, $5);"
    return {
        "employee_id": await execute_query(
            query,
            first_name,
            last_name,
            position,
            signup_date,
            branch_id,
            fetchval=True,
            payload=payload,
        )
    }


@router.put("/employee/{employee_id}/")
async def update_employee(
    employee_id: int,
    first_name: str,
    last_name: str,
    position: str,
    branch_id: int,
    is_active: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_int.update_employee($1, $2, $3, $4, $5, $6);"
    return await execute_query(
        query,
        employee_id,
        first_name,
        last_name,
        position,
        branch_id,
        is_active,
        payload=payload,
    )


@router.get("/employee/{employee_id}/")
async def select_employee(employee_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_reg_int.select_employee($1);"
    employee = await execute_query(query, employee_id, fetchrow=True, payload=payload)
    if employee:
        return dict(employee)
    raise HTTPException(status_code=404, detail="Employee not found")


# Password reset endpoint
@router.post("/employee/{employee_id}/reset_password/")
async def reset_password(
    employee_id: int, password: str, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_reg_int.reset_password($1, $2);"
    return await execute_query(query, employee_id, password, payload=payload)
