"""
Autenticación JWT para panel admin.

Variables de entorno requeridas:
- JWT_SECRET: clave para firmar tokens
- ADMIN_USER: nombre de usuario admin
- ADMIN_PASSWORD: contraseña (hash bcrypt)
"""

import os
import hmac
import hashlib
import time
import bcrypt

from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "predictgool-dev-secret-change-in-production")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")

if not ADMIN_PASSWORD_HASH:
    ADMIN_PASSWORD_HASH = bcrypt.hashpw(
        os.getenv("ADMIN_PASSWORD", "admin123").encode(), bcrypt.gensalt()
    ).decode()

TOKEN_EXPIRY = 8 * 3600


def _base64url_encode(data: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _base64url_decode(data: str) -> bytes:
    import base64
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


def create_token(username: str) -> str:
    header = _base64url_encode(b'{"alg":"HS256","typ":"JWT"}')
    now = int(time.time())
    payload = _base64url_encode(
        f'{{"sub":"{username}","iat":{now},"exp":{now + TOKEN_EXPIRY}}}'.encode()
    )
    signature = hmac.new(
        JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256
    ).digest()
    sig = _base64url_encode(signature)
    return f"{header}.{payload}.{sig}"


def verify_token(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, payload, sig = parts
        expected_sig = _base64url_encode(
            hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(sig, expected_sig):
            return None
        import json
        data = json.loads(_base64url_decode(payload))
        if data.get("exp", 0) < time.time():
            return None
        return data
    except Exception:
        return None


def get_current_user(request: Request) -> dict:
    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(401, "No autenticado")
    user = verify_token(token)
    if not user:
        raise HTTPException(401, "Token inválido o expirado")
    return user


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(req: LoginRequest, response: Response):
    if req.username != ADMIN_USER:
        raise HTTPException(401, "Credenciales inválidas")

    if not bcrypt.checkpw(req.password.encode(), ADMIN_PASSWORD_HASH.encode()):
        raise HTTPException(401, "Credenciales inválidas")

    token = create_token(req.username)
    response.set_cookie(
        "auth_token",
        token,
        httponly=True,
        samesite="strict",
        max_age=TOKEN_EXPIRY,
        secure=False,
    )
    return {"status": "ok", "user": req.username}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("auth_token")
    return {"status": "ok"}


@router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    return {"authenticated": True, "user": user.get("sub")}


@router.get("/check")
def check_auth(request: Request):
    token = request.cookies.get("auth_token")
    if token:
        user = verify_token(token)
        if user:
            return {"authenticated": True, "user": user.get("sub")}
    return {"authenticated": False}
