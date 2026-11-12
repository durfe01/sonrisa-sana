"""Módulo de seguridad: bcrypt, cifrado AES-256-GCM, validación RUT, JWT y RBAC."""

import datetime as dt
import os
import re
from typing import Callable, Iterable

import bcrypt
import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import AES_KEY_BYTES, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET

_bearer = HTTPBearer(auto_error=False)


def hash_password(plain_password: str) -> str:
    """Genera un hash bcrypt seguro (cost=12) para la contraseña en texto plano."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash bcrypt."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def encrypt_aes256(plain_text: str | None) -> bytes | None:
    """Cifra un texto médico sensible usando AES-256-GCM con nonce aleatorio de 12 bytes."""
    if plain_text is None or plain_text == "":
        return None
    aesgcm = AESGCM(AES_KEY_BYTES)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
    return nonce + ciphertext


def decrypt_aes256(blob: bytes | None) -> str:
    """Descifra un blob AES-256-GCM (nonce + ciphertext) almacenado en la base de datos."""
    if not blob:
        return ""
    aesgcm = AESGCM(AES_KEY_BYTES)
    nonce, ciphertext = blob[:12], blob[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")


def validate_rut(rut: str) -> str:
    """Normaliza y valida un RUT chileno mediante algoritmo módulo 11."""
    clean = re.sub(r"[^0-9kK]", "", rut or "").upper()
    if len(clean) < 2:
        raise ValueError("RUT inválido: longitud insuficiente.")
    body, dv = clean[:-1], clean[-1]
    if not body.isdigit():
        raise ValueError("RUT inválido: cuerpo no numérico.")
    total = 0
    factor = 2
    for ch in reversed(body):
        total += int(ch) * factor
        factor = 2 if factor == 7 else factor + 1
    rem = 11 - (total % 11)
    expected = "0" if rem == 11 else ("K" if rem == 10 else str(rem))
    if dv != expected:
        raise ValueError("RUT inválido: dígito verificador incorrecto.")
    return f"{int(body)}-{dv}"


def create_access_token(payload: dict) -> str:
    """Crea un token JWT firmado con expiración configurada."""
    data = payload.copy()
    exp = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=JWT_EXPIRE_MINUTES)
    data["exp"] = exp
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decodifica y valida un token JWT; lanza HTTPException 401 si es inválido."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada o token inválido.",
        ) from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """Obtiene el usuario autenticado a partir del header Authorization Bearer."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida.",
        )
    return decode_access_token(credentials.credentials)


def require_roles(*allowed_roles: str) -> Callable:
    """Genera una dependencia FastAPI que restringe el acceso a los roles permitidos (RBAC)."""

    def _checker(request: Request, user: dict = Depends(get_current_user)) -> dict:
        if user.get("rol") not in allowed_roles:
            from app.database import log_audit

            log_audit(
                id_usuario=user.get("id_usuario", 0),
                entidad_afectada=request.url.path,
                id_registro=0,
                accion="DENEGADO",
                ip_origen=request.client.host if request.client else "127.0.0.1",
                detalle=f"Rol '{user.get('rol')}' intentó acceder a recurso restringido a {allowed_roles}",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: privilegios insuficientes para este recurso.",
            )
        return user

    return _checker
