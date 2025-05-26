# routes/bss_ops/archive/ext_reg.py

from auth import decode_token
from fastapi import APIRouter, Depends, HTTPException, status
from routes.db_execute import execute_query

router = APIRouter()


# Address endpoints
@router.post("/address/", status_code=status.HTTP_201_CREATED)
async def insert_address(
    region: str,
    locality: str,
    district: str,
    street: str,
    house: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_ext.insert_address($1, $2, $3, $4, $5);"
    return {
        "address_id": await execute_query(
            query,
            region,
            locality,
            district,
            street,
            house,
            fetchval=True,
            payload=payload,
        )
    }


@router.put("/address/{address_id}/")
async def update_address(
    address_id: int,
    region: str,
    locality: str,
    district: str,
    street: str,
    house: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_ext.update_address($1, $2, $3, $4, $5, $6);"
    return await execute_query(
        query, address_id, region, locality, district, street, house, payload=payload
    )


@router.get("/address/{_address_id}/")
async def select_address(_address_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_reg_ext.select_address($1);"
    address = await execute_query(query, _address_id, fetchrow=True, payload=payload)
    if address:
        return dict(address)
    raise HTTPException(status_code=404, detail="Address not found")


# Customer endpoints
@router.post("/customer/", status_code=status.HTTP_201_CREATED)
async def insert_customer(
    first_name: str,
    last_name: str,
    birth_date: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_ext.insert_customer($1, $2, $3);"
    return {
        "customer_id": await execute_query(
            query, first_name, last_name, birth_date, fetchval=True, payload=payload
        )
    }


@router.put("/customer/{customer_id}/")
async def update_customer(
    customer_id: int,
    first_name: str,
    last_name: str,
    birth_date: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_ext.update_customer($1, $2, $3, $4);"
    return await execute_query(
        query, customer_id, first_name, last_name, birth_date, payload=payload
    )


@router.get("/customer/{customer_id}/")
async def select_customer(customer_id: int, payload: dict = Depends(decode_token)):
    query = "SELECT * FROM bss_ops_reg_ext.select_customer($1);"
    customer = await execute_query(query, customer_id, fetchrow=True, payload=payload)
    if customer:
        return dict(customer)
    raise HTTPException(status_code=404, detail="Customer not found")


# Customer Contact endpoints
@router.post("/customer/contact/", status_code=status.HTTP_201_CREATED)
async def insert_customer_contact(
    customer_id: int,
    contact: str,
    contact_type: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_ext.insert_customer_contact($1, $2, $3);"
    return await execute_query(
        query, customer_id, contact, contact_type, payload=payload
    )


@router.put("/customer/contact/{customer_id}/")
async def update_customer_contact(
    customer_id: int,
    contact: str,
    is_active: bool,
    contact_type: str,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_ext.update_customer_contact($1, $2, $3, $4);"
    return await execute_query(
        query, customer_id, contact, is_active, contact_type, payload=payload
    )


@router.get("/customer/contact/{customer_id}/{contact_type}/")
async def select_customer_contact(
    customer_id: int, contact_type: str, payload: dict = Depends(decode_token)
):
    query = "SELECT * FROM bss_ops_reg_ext.select_customer_contact($1, $2);"
    contact = await execute_query(
        query, customer_id, contact_type, fetchrow=True, payload=payload
    )
    if contact:
        return dict(contact)
    raise HTTPException(status_code=404, detail="Contact not found")


# Message endpoints
@router.post("/message/", status_code=status.HTTP_201_CREATED)
async def generate_message(
    customer_id: int,
    subject: str,
    is_password: bool,
    payload: dict = Depends(decode_token),
):
    query = "SELECT bss_ops_reg_ext.generate_message($1, $2, $3);"
    return await execute_query(
        query, customer_id, subject, is_password, payload=payload
    )


@router.post("/message/validate/")
async def validate_message(text: str, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_reg_ext.validate_message($1);"
    is_valid = await execute_query(query, text, fetchval=True, payload=payload)
    return {"is_valid": is_valid}


# Contact Validation endpoint
@router.get("/contact/validate/")
async def validate_unique_contact(contact: str, payload: dict = Depends(decode_token)):
    query = "SELECT bss_ops_reg_ext.validate_unique_contact($1);"
    is_unique = await execute_query(query, contact, fetchval=True, payload=payload)
    return {"is_unique": is_unique}
