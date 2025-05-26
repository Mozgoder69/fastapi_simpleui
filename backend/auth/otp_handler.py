# backend/auth/otp_handler.py
from auth.jwt_handler import JWTType, encode_token
from database.connection import SessionData  # добавляем импорт
from database.execution import QueryMode, execute
from fastapi import HTTPException


async def generate_otp(contact: str, role: str) -> dict:
    search_query = "SELECT shared.find_customer_by_contact($1);"
    customer_id = await execute(search_query, role, QueryMode.FETCH_ONE, (contact,))
    if not customer_id:
        raise HTTPException(404, "Customer not found")
    await execute(
        "SELECT shared.generate_message($1);", role, QueryMode.EXECUTE, (customer_id,)
    )
    return {"customer_id": customer_id, "message": "OTP generated successfully"}


async def validate_otp(contact: str, subject: str, uname: str, role: str) -> dict:
    search_query = "SELECT shared.find_customer_by_contact($1);"
    customer_id = await execute(search_query, role, QueryMode.FETCH_ONE, (contact,))
    validation_query = "SELECT shared.validate_message($1, $2);"
    is_valid = await execute(
        validation_query, role, QueryMode.FETCH_ONE, (customer_id, subject)
    )
    if not is_valid:
        raise HTTPException(400, "Invalid OTP")
    # Оборачиваем customer_id в объект SessionData
    session_data = SessionData(customer_id=customer_id)
    return {
        "access_token": await encode_token(uname, role, JWTType.AT, session_data),
        "refresh_token": await encode_token(uname, role, JWTType.RT, session_data),
    }
