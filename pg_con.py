# pg_con.py

import jwt
import secrets
from asyncpg import Pool, create_pool, PostgresError
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.responses import JSONResponse

KEY = "bf"
SIGN = "HS256"

con_pools = {}


async def allocate_pool(uname, pword):
    if not (uname and pword):
        raise HTTPException(404, 'Please provide a credentials')
    try:
        pool_str = f'postgres://{uname}:{pword}@localhost:1618/cleaners'
        con_pools[uname] = await create_pool(pool_str, min_size=1, max_size=6)
    except Exception as e:
        raise HTTPException(404, f"Error creating pool. Info: {e}")
    return con_pools.get(uname)


async def get_con(uname: str = None, pool: Pool = None):
    if not pool:
        pool = con_pools.get(uname)
        if not pool:
            raise HTTPException(404, 'Please allocate a new pool for user')
    try:
        con = await pool.acquire()
        yield con
    except Exception as e:
        raise HTTPException(404, f'Error getting connection. Info: {e}')


async def test_pool(uname: str = None, pool: Pool = None):
    try:
        async for con in get_con(uname, pool):
            await pool.release(con)
            return True  # Если соединение успешно получено
    except HTTPException:
        return False  # Возвращаем False, если соединение не удалось


async def free_pool(uname):
    if uname:
        pool: Pool = con_pools.get(uname)
        if pool:
            await pool.close()
            del con_pools[uname]


async def set_cookies(role, uname):
    expire = datetime.utcnow() + timedelta(minutes=15)
    jwt_token = jwt.encode({"role": role, "uname": uname, "exp": expire}, KEY, SIGN)
    csrf_token = secrets.token_urlsafe(16)

    content = {"auth_type": "bearer", "token": jwt_token, "role": role, "uid": uname}
    response = JSONResponse(content)

    response.set_cookie(key="jwt", value=jwt_token, secure=True, httponly=True, samesite='Lax')
    response.set_cookie(key="csrf", value=csrf_token, secure=True, httponly=True, samesite='Lax')

    return response


async def auth_user(uname, pword, is_guest=False):
    if is_guest:
        uname = 'customer'
    try:
        await allocate_pool(uname, pword)
        if uname in ('customer', 'postgres'):
            if con_pools.get(uname):
                await free_pool(uname)
                role = uname
            else:
                is_valid = False
        else:
            async for con in get_con(uname):
                is_valid = await con.fetchval("select shared.user_validate($1, $2)", uname, pword)
                if is_valid:
                    role = await con.fetchval("select shared.user_authorize($1, $2)", uname, pword)
    except PostgresError as e:
        raise HTTPException(401, f"Postgres error: {e}")
    except HTTPException as e:
        raise HTTPException(404, f"Token Auth Error: {e}")
    if not role:
        raise HTTPException(407, 'Undefined role. Please try again later')
    return await set_cookies(role, uname)


async def check_token(token): # token : str = Header(None)
    try:
        payload = jwt.decode(token, KEY, [SIGN])
        role = payload.get("role")
        uname = payload.get("uname")
        expire = payload.get("exp")
        if datetime.utcnow() >= datetime.fromtimestamp(expire):
            raise HTTPException(403, 'Token is invalid or expired')
    except jwt.PyJWTError:
        raise HTTPException(403, 'Auth error. Please try again')
    return role, uname
