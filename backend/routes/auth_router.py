# backend/routes/auth_router.py

"""Router for authentication-related endpoints."""

from auth.jwt_handler import JWTType, authenticate, decode_token, encode_token
from auth.otp_handler import generate_otp, validate_otp
from config.logging import logger
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

auth_router = APIRouter(tags=["Auth"])
"""Router for authentication-related endpoints."""


async def manual_token(uname: str, pword: str):
    """Manually generates a token using username and password."""
    return await access_token(OAuth2PasswordRequestForm(username=uname, password=pword))


@auth_router.post("/token")
async def access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Generates access and refresh tokens for valid user credentials."""
    uname = form_data.username
    pword = form_data.password
    session_data = dict(await authenticate(uname, pword))
    role = session_data.pop("position")
    if not role:
        raise HTTPException(401, "Invalid credentials", {"WWW-Authenticate": "Bearer"})
    at = await encode_token(uname, role, JWTType.AT, session_data)
    rt = await encode_token(uname, role, JWTType.RT, session_data)
    logger.info(f"Tokens for user {uname} are generated")
    return {"access_token": at, "refresh_token": rt, "token_type": "Bearer"}


@auth_router.post("/token/refresh")
async def refresh_token(refresh_token: str = Form(...)):
    """Refreshes access and refresh tokens using a valid refresh token."""
    try:
        payload = await decode_token(refresh_token, JWTType.RT)
        uname = payload["uname"]
        role = payload["role"]
        new_at = await encode_token(uname, role, JWTType.AT, payload)
        new_rt = await encode_token(uname, role, JWTType.RT, payload)
        return {"access_token": new_at, "refresh_token": new_rt, "token_type": "Bearer"}
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(status_code=400, detail="Could not refresh token")


@auth_router.post("/token/introspect")
async def introspect_token(payload: dict = Depends(decode_token)):
    """Returns user information extracted from a decoded token."""
    return payload


@auth_router.post("/token/validate")
async def validate_token(payload: dict = Depends(decode_token)):
    """Validates the provided token and checks its claims."""
    try:
        return {"validity": True, "message": "Token is valid", "payload": payload}
    except jwt.JWTError as e:
        return {"validity": False, "message": str(e)}


@auth_router.post("/token/revoke")
async def revoke_token(payload: dict = Depends(decode_token)):
    """Handles token revocation logic."""
    # TODO: Implement token revocation logic
    logger.info(f"Revoking token for user: {payload['uname']}")
    return {"message": "To Be Done"}


@auth_router.post("/message/generate")
async def generate_message(contact: str, payload: dict = Depends(decode_token)):
    """Generate OTP for authentication."""
    return await generate_otp(contact, payload["role"])


@auth_router.post("/message/validate")
async def validate_message(
    contact: str, subject: str, payload: dict = Depends(decode_token)
):
    """Validate OTP and return tokens."""
    return await validate_otp(contact, subject, payload["uname"], payload["role"])
