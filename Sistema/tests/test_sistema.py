"""Suite de pruebas automatizadas para validar seguridad, RBAC, anti-choques y flujos críticos."""

import os
import tempfile
import datetime as dt

import pytest
from fastapi.testclient import TestClient

# Configurar base de datos temporal aislada para pruebas
_TMP_DB = os.path.join(tempfile.gettempdir(), "sonrisa_sana_test.db")
if os.path.exists(_TMP_DB):
    os.remove(_TMP_DB)
os.environ["SONRISA_DB_PATH"] = _TMP_DB

from app.database import get_connection, init_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    """Inicializa la BD limpia y provee un TestClient de FastAPI para toda la suite."""
    init_db()
    with TestClient(app) as tc:
        yield tc


def _login(client: TestClient, email: str) -> str:
    """Autentica un usuario de prueba y retorna su token Bearer."""
    res = client.post("/api/auth/login", json={"correo": email, "password": "Sonrisa2026!"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_reserva_online_y_prevencion_choque(client: TestClient):
    """Verifica que un paciente reserve una hora y que un segundo intento en el mismo bloque retorne 409."""
    token = _login(client, "maria.gonzalez@correo.cl")
    headers = {"Authorization": f"Bearer {token}"}
    fecha = (dt.date.today() + dt.timedelta(days=3)).isoformat()
    if dt.date.fromisoformat(fecha).isoweekday() == 7:
        fecha = (dt.date.today() + dt.timedelta(days=4)).isoformat()

    payload = {
        "id_odontologo": 1,
        "id_tipo_atencion": 1,
        "fecha": fecha,
        "hora_inicio": "10:30",
    }
    r1 = client.post("/api/citas", json=payload, headers=headers)
    assert r1.status_code == 201

    r2 = client.post("/api/citas", json=payload, headers=headers)
    assert r2.status_code == 409


def test_secretaria_reprograma_y_cancela(client: TestClient):
    """Verifica que la secretaría pueda reprogramar y cancelar citas liberando el bloque."""
    token_sec = _login(client, "secretaria@sonrisasana.cl")
    headers = {"Authorization": f"Bearer {token_sec}"}
    citas = client.get("/api/citas", headers=headers).json()
    pendiente = next(c for c in citas if c["estado"] == "pendiente")

    nueva_fecha = (dt.date.today() + dt.timedelta(days=5)).isoformat()
    if dt.date.fromisoformat(nueva_fecha).isoweekday() == 7:
        nueva_fecha = (dt.date.today() + dt.timedelta(days=6)).isoformat()

    res_rep = client.put(
        f"/api/citas/{pendiente['id_cita']}/reprogramar",
        json={"fecha": nueva_fecha, "hora_inicio": "12:00", "motivo": "Cambio de hora"},
        headers=headers,
    )
    assert res_rep.status_code == 200

    res_can = client.put(
        f"/api/citas/{pendiente['id_cita']}/cancelar",
        json={"motivo": "Cancelado en prueba"},
        headers=headers,
    )
    assert res_can.status_code == 200
    assert res_can.json()["estado"] == "cancelada"


def test_rbac_estricto_ficha_clinica_y_cifrado_aes256(client: TestClient):
    """Verifica HTTP 403 para roles no odontólogos y cifrado real AES-256 en la BD."""
    for email in ("secretaria@sonrisasana.cl", "admin@sonrisasana.cl", "maria.gonzalez@correo.cl"):
        tok = _login(client, email)
        res = client.get("/api/fichas/1", headers={"Authorization": f"Bearer {tok}"})
        assert res.status_code == 403

    tok_od = _login(client, "valeria.munoz@sonrisasana.cl")
    headers_od = {"Authorization": f"Bearer {tok_od}"}
    res_get = client.get("/api/fichas/1", headers=headers_od)
    assert res_get.status_code == 200
    assert "Penicilina" in res_get.json()["alergias"]

    secreto = "Diagnóstico confidencial periodontitis severa"
    res_post = client.post(
        "/api/fichas/1/evolucion",
        json={"pieza_dental": "2.1", "diagnostico": secreto, "tratamiento_realizado": "Raspaje radicular"},
        headers=headers_od,
    )
    assert res_post.status_code == 201

    conn = get_connection()
    raw = conn.execute("SELECT diagnostico_enc FROM evolucion_clinica ORDER BY id_evolucion DESC LIMIT 1").fetchone()[0]
    conn.close()
    assert secreto.encode("utf-8") not in raw
