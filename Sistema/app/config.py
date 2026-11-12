"""Configuración centralizada de rutas, seguridad y parámetros del sistema."""

import os
import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("SONRISA_DB_PATH", os.path.join(BASE_DIR, "sonrisa_sana.db"))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Clave JWT persistente en sesión o variable de entorno
JWT_SECRET = os.environ.get("SONRISA_JWT_SECRET", "sonrisa-sana-dev-jwt-secret-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 480

# Clave AES-256 (32 bytes) para cifrado de ficha clínica en reposo (RNF02)
_DEFAULT_AES_HEX = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
AES_KEY_BYTES = bytes.fromhex(os.environ.get("SONRISA_AES_KEY_HEX", _DEFAULT_AES_HEX))
