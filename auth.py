# auth.py
from datetime import datetime, timedelta
from enum import Enum

from config import db_public, db_super, jwt_exp, jwt_sign
from db_con import con_gen, pools
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer as OAuth2PassBearer
from jose import JWTError, jwt

oauth_schema = OAuth2PassBearer(tokenUrl="token")


class JWTType(Enum):
    AT = "access_token"  # Short-lived token for access control
    ST = "session_token"  # Longer-lived token for maintaining session state
    RT = "refresh_token"  # Token used to renew expired access or session tokens


async def decode_token(
    token: str = Depends(oauth_schema),
    jwt_type: JWTType = JWTType.AT,
):
    """Validate JWT and ensure it is of the correct type."""
    try:
        payload = jwt.decode(token, jwt_sign.key, algorithms=[jwt_sign.alg])
        if payload["type"] != jwt_type.value:
            raise HTTPException(403, f"Invalid JWT type expected {jwt_type.value}")
        return payload
    except JWTError as e:
        raise HTTPException(403, "Could not validate credentials") from e


async def encode_token(uname: str, role: str, jwt_type: JWTType = JWTType.AT):
    """Generate JWT based on user role, type, and predefined expiration."""
    exp_seconds = {
        JWTType.AT: jwt_exp.at_exp,
        JWTType.ST: jwt_exp.st_exp,
        JWTType.RT: jwt_exp.rt_exp,
    }[jwt_type]
    exp = datetime.utcnow() + timedelta(seconds=exp_seconds)
    token_data = {"type": jwt_type.value, "role": role, "uname": uname, "exp": exp}
    return jwt.encode(token_data, jwt_sign.key, algorithm=jwt_sign.alg)


async def authenticate(uname: str, pword: str, guest: bool = False) -> str:
    """Authenticate user and return their role; guest users use public credentials."""
    if guest:
        uname = db_public.uname
        pword = db_public.pword
    async with con_gen(pools, uname, pword) as con:  # Establish DB connection
        if uname in (db_public.uname, db_super.uname):
            return uname  # Return username as role for public/super users
        # Query database for user role using custom authorization function
        role = await con.fetchval("SELECT shared.user_authorize($1, $2)", uname, pword)
        if not role:
            raise HTTPException(401, "Auth Failed")
        return role
