# routes/bss_ops/archive/mkg_line.py

from auth import decode_token
from fastapi import APIRouter, Depends, HTTPException, status
from routes.db_execute import execute_query

router = APIRouter()


# Sales Order endpoints
@router.post("/salesorder/", status_code=status.HTTP_201_CREATED)
async def insert_salesorder(
    customer_id: int,
    purpose: str,
    paymethod: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_mkg_line.insert_salesorder($1, $2, $3);"
    return {
        "salesorder_id": await execute_query(
            query, customer_id, purpose, paymethod, fetchval=True, payload=payload
        )
    }


@router.put("/salesorder/{salesorder_id}/")
async def update_salesorder(
    salesorder_id: int,
    purpose: str,
    paymethod: str,
    status: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_mkg_line.update_salesorder($1, $2, $3, $4);"
    return await execute_query(
        query, salesorder_id, purpose, paymethod, status, payload=payload
    )


@router.get("/salesorder/{salesorder_id}/")
async def select_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_mkg_line.select_salesorder($1);"
    salesorder = await execute_query(
        query, salesorder_id, fetchrow=True, payload=payload
    )
    if salesorder:
        return dict(salesorder)
    raise HTTPException(status_code=404, detail="Sales order not found")


@router.post("/salesorder/{salesorder_id}/cancel/")
async def cancel_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.cancel_salesorder($1);"
    return await execute_query(query, salesorder_id, payload=payload)


@router.post("/salesorder/{salesorder_id}/accept/")
async def accept_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.accept_salesorder($1);"
    return await execute_query(query, salesorder_id, payload=payload)


@router.post("/salesorder/{salesorder_id}/execute/")
async def execute_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.execute_salesorder($1);"
    return await execute_query(query, salesorder_id, payload=payload)


@router.post("/salesorder/{salesorder_id}/finish/")
async def finish_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.finish_salesorder($1);"
    return await execute_query(query, salesorder_id, payload=payload)


@router.post("/salesorder/{salesorder_id}/return/")
async def return_salesorder(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.return_salesorder($1);"
    return await execute_query(query, salesorder_id, payload=payload)


# Product endpoints
@router.post("/product/", status_code=status.HTTP_201_CREATED)
async def insert_product(
    category_id: int,
    agreed_price: float,
    color: str,
    size: str,
    condition: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_mkg_line.insert_product($1, $2, $3, $4, $5);"
    return {
        "product_id": await execute_query(
            query,
            category_id,
            agreed_price,
            color,
            size,
            condition,
            fetchval=True,
            payload=payload,
        )
    }


@router.put("/product/{product_id}/")
async def update_product(
    product_id: int,
    category_id: int,
    agreed_price: float,
    color: str,
    size: str,
    condition: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_mkg_line.update_product($1, $2, $3, $4, $5, $6);"
    return await execute_query(
        query,
        product_id,
        category_id,
        agreed_price,
        color,
        size,
        condition,
        payload=payload,
    )


@router.get("/product/{product_id}/")
async def select_product(product_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_mkg_line.select_product($1);"
    product = await execute_query(query, product_id, fetchrow=True, payload=payload)
    if product:
        return dict(product)
    raise HTTPException(status_code=404, detail="Product not found")


# Package endpoints
@router.post("/package/", status_code=status.HTTP_201_CREATED)
async def insert_package(
    salesorder_id: int,
    product_id: int,
    items_count: int,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_mkg_line.insert_package($1, $2, $3);"
    return {
        "package_id": await execute_query(
            query,
            salesorder_id,
            product_id,
            items_count,
            fetchval=True,
            payload=payload,
        )
    }


@router.get("/package/{salesorder_id}/")
async def select_package(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_mkg_line.select_package($1);"
    package = await execute_query(query, salesorder_id, fetch=True, payload=payload)
    return [dict(record) for record in package]


# Premises endpoints
@router.post("/premises/", status_code=status.HTTP_201_CREATED)
async def insert_premises(
    category_id: int,
    agreed_price: float,
    color: str,
    size: str,
    condition: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_mkg_line.insert_premises($1, $2, $3, $4, $5);"
    return {
        "premises_id": await execute_query(
            query,
            category_id,
            agreed_price,
            color,
            size,
            condition,
            fetchval=True,
            payload=payload,
        )
    }


@router.put("/premises/{premises_id}/")
async def update_premises(premises_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_mkg_line.update_premises($1);"
    return await execute_query(query, premises_id, payload=payload)


@router.get("/premises/{address_id}/")
async def select_premises(address_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_mkg_line.select_premises($1);"
    premises = await execute_query(query, address_id, fetch=True, payload=payload)
    return [dict(record) for record in premises]


# Journey endpoints
@router.post("/journey/", status_code=status.HTTP_201_CREATED)
async def insert_journey(
    salesorder_id: int, address_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT bss_ops_mkg_line.insert_journey($1, $2);"
    return {
        "journey_id": await execute_query(
            query, salesorder_id, address_id, fetchval=True, payload=payload
        )
    }


@router.get("/journey/{salesorder_id}/")
async def select_journey(salesorder_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_mkg_line.select_journey($1);"
    journey = await execute_query(query, salesorder_id, fetch=True, payload=payload)
    return [dict(record) for record in journey]


# Filter Sales Orders endpoints
@router.get("/salesorders/customer/{customer_id}/")
async def filter_salesorders_by_customer(
    customer_id: int, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_mkg_line.filter_salesorders_by_customer($1);"
    salesorders = await execute_query(query, customer_id, fetch=True, payload=payload)
    return [dict(record) for record in salesorders]


@router.get("/salesorders/purpose/{purpose}/")
async def filter_salesorders_by_purpose(
    purpose: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_mkg_line.filter_salesorders_by_purpose($1);"
    salesorders = await execute_query(query, purpose, fetch=True, payload=payload)
    return [dict(record) for record in salesorders]


@router.get("/salesorders/status/{status}/")
async def filter_salesorders_by_status(
    status: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_mkg_line.filter_salesorders_by_status($1);"
    salesorders = await execute_query(query, status, fetch=True, payload=payload)
    return [dict(record) for record in salesorders]
