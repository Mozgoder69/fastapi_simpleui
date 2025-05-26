# backend/auth/jwt_handler.py

"""Handles JWT operations including encoding, decoding, and authentication."""

from datetime import datetime, timedelta, timezone
from enum import Enum

from config.logging import logger
from config.settings import settings
from database.connection import ConType, DBCon, SessionData, pools, session_vars
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

oauth_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


class JWTType(Enum):
    """Enumeration for JWT token types."""

    AT = "access_token"  # Short-lived token for direct access
    RT = "refresh_token"  # Long-lived token for renew expired access


def validate_jwt_type(payload: dict, jwt_type: JWTType):
    """Validate that the JWT payload matches the expected type."""
    required_claims = {"type", "exp", "uname", "role"}
    if not required_claims.issubset(payload.keys()):
        missing = required_claims - payload.keys()
        raise HTTPException(401, f"Missing claims: {', '.join(missing)}")
    if payload.get("type") != jwt_type.value:
        raise HTTPException(401, f"Invalid JWT type, expected {jwt_type.value}")


# В decode_token и encode_token параметр алгоритма передаётся в виде строки,
# поскольку в нашем случае jwt.decode и jwt.encode корректно работают с одиночной строкой.


# Параметры функции decode_token: token извлекается через Depends, а jwt_type имеет значение по умолчанию (AT).
async def decode_token(token=Depends(oauth_scheme), jwt_type: JWTType = JWTType.AT):
    try:
        payload = jwt.decode(token, settings.jwt.key, algorithms=f"{settings.jwt.alg}")
        validate_jwt_type(payload, jwt_type)

        # Обновляем сессионные переменные
        session_vars.set(
            {
                "customer_id": payload.get("customer_id"),
                "employee_id": payload.get("employee_id"),
                "branch_id": payload.get("branch_id"),
            }
        )

        return payload

    except ExpiredSignatureError:
        raise HTTPException(401, "Token has expired")
    except JWTError:
        logger.error("JWT error occurred")
        raise HTTPException(401, "Invalid token")


async def encode_token(
    uname: str, role: str, jwt_type: JWTType, session_data: SessionData = None
):
    exp_seconds = settings.jwt.at_exp if jwt_type == JWTType.AT else settings.jwt.rt_exp
    exp = int((datetime.now(timezone.utc) + timedelta(seconds=exp_seconds)).timestamp())

    token_data = {"type": jwt_type.value, "exp": exp, "uname": uname, "role": role}

    if session_data:
        # Если session_data является экземпляром с методом to_dict(), то используем его,
        # иначе (например, если это словарь) объединяем напрямую.
        if hasattr(session_data, "to_dict"):
            token_data.update(session_data.to_dict())
        elif isinstance(session_data, dict):
            token_data.update(session_data)

    return jwt.encode(token_data, settings.jwt.key, algorithm=f"{settings.jwt.alg}")


async def authenticate(uname: str, pword: str, guest=False):
    try:
        # Для гостей и технических ролей
        if guest or uname in settings.database.default_roles:
            return {"position": f"{uname}"}

        # Для бизнес-пользователей и работников
        async with DBCon.connect(
            settings.database.get_role(), ConType.SIMPLE, uname, pword
        ) as conn:
            session_data = await conn.fetchrow(
                "SELECT * FROM shared.account_authorize($1, $2)", uname, pword
            )

            if session_data is None:
                raise HTTPException(403, "Authentication Failed")

            await pools.get_pool(session_data["position"], uname, pword)

            return session_data

    except Exception as e:
        logger.error(f"Authentication failed for user: {uname}, error: {e}")
        raise HTTPException(403, "Authentication Failed")
