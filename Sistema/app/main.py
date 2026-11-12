"""API REST principal y servidor web del Sistema Clínica Odontológica Sonrisa Sana."""

import asyncio
import datetime as dt
import os
import sqlite3
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import STATIC_DIR
from app.database import db_session, init_db, log_audit
from app.reminders import process_pending_reminders, schedule_reminder_for_appointment
from app.security import (
    create_access_token,
    decrypt_aes256,
    encrypt_aes256,
    get_current_user,
    hash_password,
    require_roles,
    validate_rut,
    verify_password,
)


class LoginRequest(BaseModel):
    """Credenciales de inicio de sesión."""

    correo: str
    password: str


class RegisterPatientRequest(BaseModel):
    """Datos para registro online de nuevo paciente."""

    rut: str
    nombre: str
    apellido: str
    fecha_nacimiento: str
    telefono: str
    correo: str
    direccion: str = ""
    prevision: str = "Particular"
    password: str = Field(min_length=6)
    consentimiento_datos: bool = True


class CreatePatientRequest(BaseModel):
    """Datos para alta presencial o telefónica de paciente por secretaría."""

    rut: str
    nombre: str
    apellido: str
    fecha_nacimiento: str
    telefono: str
    correo: str
    direccion: str = ""
    prevision: str = "Particular"


class CreateAppointmentRequest(BaseModel):
    """Solicitud de reserva de cita odontológica."""

    id_paciente: int | None = None
    id_odontologo: int
    id_tipo_atencion: int
    fecha: str
    hora_inicio: str
    origen: str = "online"


class RescheduleRequest(BaseModel):
    """Solicitud de modificación/reprogramación de cita por secretaría."""

    fecha: str
    hora_inicio: str
    id_odontologo: int | None = None
    motivo: str = "Reprogramada por secretaría"


class CancelRequest(BaseModel):
    """Solicitud de cancelación de cita."""

    motivo: str = "Cancelada a solicitud"


class ClinicalEvolutionRequest(BaseModel):
    """Registro de evolución médica cifrada en ficha clínica (solo Odontólogo)."""

    id_cita: int | None = None
    pieza_dental: str | None = None
    diagnostico: str = Field(min_length=3)
    tratamiento_realizado: str = Field(min_length=3)
    indicaciones: str | None = None
    antecedentes_medicos: str | None = None
    alergias: str | None = None


class CreateUserRequest(BaseModel):
    """Creación de usuario interno por el administrador."""

    id_rol: int
    rut: str
    nombre: str
    apellido: str
    correo: str
    password: str = Field(min_length=6)
    telefono: str = ""


async def _reminder_loop() -> None:
    """Tarea en segundo plano que procesa recordatorios automáticos cada 60 segundos."""
    while True:
        try:
            process_pending_reminders(force_all=False)
        except Exception:
            pass
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Inicializa la base de datos y arranca el worker de recordatorios al iniciar."""
    init_db()
    task = asyncio.create_task(_reminder_loop())
    yield
    task.cancel()


app = FastAPI(
    title="Clínica Odontológica Sonrisa Sana",
    description="Sistema de Agendamiento Online, Gestión de Secretaría y Ficha Clínica Confidencial",
    version="1.0.0",
    lifespan=lifespan,
)

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _compute_end_time(hora_inicio: str, duracion_min: int) -> str:
    """Calcula la hora de término sumando la duración en minutos."""
    t = dt.datetime.strptime(hora_inicio, "%H:%M") + dt.timedelta(minutes=duracion_min)
    return t.strftime("%H:%M")


@app.get("/", include_in_schema=False)
def serve_index() -> FileResponse:
    """Sirve la interfaz web principal."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.post("/api/auth/login")
def login(body: LoginRequest, request: Request) -> dict:
    """Autentica al usuario verificando hash bcrypt y emite token JWT."""
    with db_session() as conn:
        row = conn.execute(
            """
            SELECT u.*, r.nombre AS rol_nombre,
                   p.id_paciente, o.id_odontologo
            FROM usuario u
            INNER JOIN rol r ON r.id_rol = u.id_rol
            LEFT JOIN paciente p ON p.id_usuario = u.id_usuario
            LEFT JOIN odontologo o ON o.id_usuario = u.id_usuario
            WHERE LOWER(u.correo) = LOWER(?) AND u.activo = 1
            """,
            (body.correo.strip(),),
        ).fetchone()

    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos.")

    user_data = {
        "id_usuario": row["id_usuario"],
        "nombre": f"{row['nombre']} {row['apellido']}",
        "correo": row["correo"],
        "rol": row["rol_nombre"],
        "id_paciente": row["id_paciente"],
        "id_odontologo": row["id_odontologo"],
    }
    token = create_access_token(user_data)
    log_audit(
        row["id_usuario"],
        "usuario",
        row["id_usuario"],
        "LOGIN",
        request.client.host if request.client else "127.0.0.1",
        f"Inicio de sesión rol {row['rol_nombre']}",
    )
    return {"access_token": token, "token_type": "bearer", "user": user_data}


@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register_patient(body: RegisterPatientRequest) -> dict:
    """Registra una cuenta de paciente online validando RUT y consentimiento Ley 19.628."""
    if not body.consentimiento_datos:
        raise HTTPException(status_code=400, detail="Debe aceptar el consentimiento de datos personales.")
    try:
        rut_norm = validate_rut(body.rut)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    pwd_hash = hash_password(body.password)
    with db_session() as conn:
        rol_pac = conn.execute("SELECT id_rol FROM rol WHERE nombre = 'Paciente'").fetchone()
        try:
            cur_u = conn.execute(
                """INSERT INTO usuario (id_rol, rut, nombre, apellido, correo, password_hash, telefono)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (rol_pac["id_rol"], rut_norm, body.nombre.strip(), body.apellido.strip(), body.correo.strip(), pwd_hash, body.telefono.strip()),
            )
            uid = cur_u.lastrowid
            cur_p = conn.execute(
                """INSERT INTO paciente (id_usuario, rut, nombre, apellido, fecha_nacimiento, telefono, correo, direccion, prevision, consentimiento_datos)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                (uid, rut_norm, body.nombre.strip(), body.apellido.strip(), body.fecha_nacimiento, body.telefono.strip(), body.correo.strip(), body.direccion.strip(), body.prevision),
            )
            pid = cur_p.lastrowid
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="El RUT o correo ya se encuentra registrado.") from exc

    user_data = {
        "id_usuario": uid,
        "nombre": f"{body.nombre.strip()} {body.apellido.strip()}",
        "correo": body.correo.strip(),
        "rol": "Paciente",
        "id_paciente": pid,
        "id_odontologo": None,
    }
    return {"access_token": create_access_token(user_data), "token_type": "bearer", "user": user_data}


@app.get("/api/catalogo")
def get_catalog() -> dict:
    """Retorna especialidades, tipos de atención y odontólogos activos para agendamiento."""
    with db_session() as conn:
        especialidades = [dict(r) for r in conn.execute("SELECT * FROM especialidad ORDER BY nombre").fetchall()]
        tipos = [dict(r) for r in conn.execute("SELECT * FROM tipo_atencion ORDER BY nombre").fetchall()]
        odontologos = [
            dict(r)
            for r in conn.execute(
                """
                SELECT o.id_odontologo, o.id_especialidad, o.box_asignado,
                       u.nombre || ' ' || u.apellido AS nombre_completo,
                       e.nombre AS especialidad
                FROM odontologo o
                INNER JOIN usuario u ON u.id_usuario = o.id_usuario
                INNER JOIN especialidad e ON e.id_especialidad = o.id_especialidad
                WHERE u.activo = 1
                ORDER BY u.apellido
                """
            ).fetchall()
        ]
    return {"especialidades": especialidades, "tipos_atencion": tipos, "odontologos": odontologos}


@app.get("/api/disponibilidad")
def get_availability(
    id_odontologo: int = Query(...),
    fecha: str = Query(..., description="YYYY-MM-DD"),
) -> dict:
    """Calcula bloques horarios disponibles de un odontólogo para una fecha dada (<1.5s)."""
    try:
        fecha_dt = dt.date.fromisoformat(fecha)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido (use YYYY-MM-DD).") from exc

    dia_semana = fecha_dt.isoweekday()
    with db_session() as conn:
        horarios = conn.execute(
            """
            SELECT hora_inicio, hora_fin, duracion_bloque_min
            FROM horario_odontologo
            WHERE id_odontologo = ? AND dia_semana = ? AND activo = 1
            ORDER BY hora_inicio
            """,
            (id_odontologo, dia_semana),
        ).fetchall()

        ocupadas = {
            r["hora_inicio"]
            for r in conn.execute(
                """
                SELECT hora_inicio FROM cita
                WHERE id_odontologo = ? AND fecha = ? AND estado IN ('pendiente', 'confirmada', 'atendida')
                """,
                (id_odontologo, fecha),
            ).fetchall()
        }

        bloqueos = conn.execute(
            "SELECT hora_inicio, hora_fin FROM bloqueo_horario WHERE id_odontologo = ? AND fecha = ?",
            (id_odontologo, fecha),
        ).fetchall()

    slots = []
    for h in horarios:
        cur = dt.datetime.strptime(h["hora_inicio"], "%H:%M")
        fin = dt.datetime.strptime(h["hora_fin"], "%H:%M")
        step = dt.timedelta(minutes=h["duracion_bloque_min"])
        while cur + step <= fin:
            hi_str = cur.strftime("%H:%M")
            bloqueado = any(b["hora_inicio"] <= hi_str < b["hora_fin"] for b in bloqueos)
            slots.append({"hora_inicio": hi_str, "disponible": (hi_str not in ocupadas) and not bloqueado})
            cur += step

    return {"id_odontologo": id_odontologo, "fecha": fecha, "bloques": slots}


@app.get("/api/citas")
def list_appointments(
    fecha: str | None = None,
    id_odontologo: int | None = None,
    user: dict = Depends(get_current_user),
) -> list[dict]:
    """Lista citas según el rol: Paciente ve solo las suyas; equipo clínico ve agenda filtrable."""
    sql = """
        SELECT c.*, p.nombre || ' ' || p.apellido AS paciente_nombre, p.rut AS paciente_rut,
               p.telefono AS paciente_telefono,
               u.nombre || ' ' || u.apellido AS odontologo_nombre, o.box_asignado,
               e.nombre AS especialidad, ta.nombre AS tipo_atencion
        FROM cita c
        INNER JOIN paciente p ON p.id_paciente = c.id_paciente
        INNER JOIN odontologo o ON o.id_odontologo = c.id_odontologo
        INNER JOIN usuario u ON u.id_usuario = o.id_usuario
        INNER JOIN especialidad e ON e.id_especialidad = o.id_especialidad
        INNER JOIN tipo_atencion ta ON ta.id_tipo_atencion = c.id_tipo_atencion
        WHERE 1=1
    """
    params: list = []
    if user["rol"] == "Paciente":
        sql += " AND c.id_paciente = ?"
        params.append(user["id_paciente"])
    elif user["rol"] == "Odontologo" and user.get("id_odontologo"):
        sql += " AND c.id_odontologo = ?"
        params.append(user["id_odontologo"])

    if fecha:
        sql += " AND c.fecha = ?"
        params.append(fecha)
    if id_odontologo:
        sql += " AND c.id_odontologo = ?"
        params.append(id_odontologo)

    sql += " ORDER BY c.fecha ASC, c.hora_inicio ASC"
    with db_session() as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
    return [dict(r) for r in rows]


@app.post("/api/citas", status_code=status.HTTP_201_CREATED)
def create_appointment(
    body: CreateAppointmentRequest,
    request: Request,
    user: dict = Depends(get_current_user),
) -> dict:
    """Reserva una nueva cita validando integridad anti-choques y programando recordatorio."""
    id_paciente = user["id_paciente"] if user["rol"] == "Paciente" else body.id_paciente
    if not id_paciente:
        raise HTTPException(status_code=400, detail="Debe especificar un paciente válido.")

    with db_session() as conn:
        tipo = conn.execute("SELECT duracion_min FROM tipo_atencion WHERE id_tipo_atencion = ?", (body.id_tipo_atencion,)).fetchone()
        duracion = tipo["duracion_min"] if tipo else 30
        hora_fin = _compute_end_time(body.hora_inicio, duracion)
        try:
            cur = conn.execute(
                """
                INSERT INTO cita (id_paciente, id_odontologo, id_tipo_atencion, id_usuario_gestion, fecha, hora_inicio, hora_fin, origen, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendiente')
                """,
                (
                    id_paciente,
                    body.id_odontologo,
                    body.id_tipo_atencion,
                    None if user["rol"] == "Paciente" else user["id_usuario"],
                    body.fecha,
                    body.hora_inicio,
                    hora_fin,
                    body.origen if user["rol"] != "Paciente" else "online",
                ),
            )
            cita_id = cur.lastrowid
            schedule_reminder_for_appointment(conn, cita_id, body.fecha, body.hora_inicio)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(
                status_code=409,
                detail="Choque de horario: ese bloque ya fue reservado. Por favor elija otro horario disponible.",
            ) from exc

    log_audit(
        user["id_usuario"],
        "cita",
        cita_id,
        "CREAR",
        request.client.host if request.client else "127.0.0.1",
        f"Cita {body.fecha} {body.hora_inicio}",
    )
    return {"id_cita": cita_id, "estado": "pendiente", "mensaje": "Cita reservada con recordatorio programado."}


@app.put("/api/citas/{id_cita}/reprogramar")
def reschedule_appointment(
    id_cita: int,
    body: RescheduleRequest,
    request: Request,
    user: dict = Depends(require_roles("Secretaria", "Administrador")),
) -> dict:
    """Reprograma una cita existente (<= 2 clics) validando que el nuevo bloque esté libre."""
    with db_session() as conn:
        cita = conn.execute("SELECT * FROM cita WHERE id_cita = ?", (id_cita,)).fetchone()
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada.")
        if cita["estado"] in ("cancelada", "atendida"):
            raise HTTPException(status_code=400, detail="No se puede reprogramar una cita cancelada o ya atendida.")

        nuevo_od = body.id_odontologo or cita["id_odontologo"]
        tipo = conn.execute("SELECT duracion_min FROM tipo_atencion WHERE id_tipo_atencion = ?", (cita["id_tipo_atencion"],)).fetchone()
        hora_fin = _compute_end_time(body.hora_inicio, tipo["duracion_min"] if tipo else 30)

        try:
            conn.execute(
                """
                UPDATE cita
                SET id_odontologo = ?, fecha = ?, hora_inicio = ?, hora_fin = ?,
                    estado = 'pendiente', motivo_cambio_cancelacion = ?,
                    id_usuario_gestion = ?, fecha_actualizacion = datetime('now', 'localtime')
                WHERE id_cita = ?
                """,
                (nuevo_od, body.fecha, body.hora_inicio, hora_fin, body.motivo, user["id_usuario"], id_cita),
            )
            conn.execute("UPDATE recordatorio SET estado = 'omitido' WHERE id_cita = ? AND estado = 'pendiente'", (id_cita,))
            schedule_reminder_for_appointment(conn, id_cita, body.fecha, body.hora_inicio)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="El nuevo horario seleccionado ya está ocupado.") from exc

    log_audit(
        user["id_usuario"],
        "cita",
        id_cita,
        "MODIFICAR",
        request.client.host if request.client else "127.0.0.1",
        f"Reprogramada a {body.fecha} {body.hora_inicio}",
    )
    return {"id_cita": id_cita, "mensaje": "Cita reprogramada exitosamente."}


@app.put("/api/citas/{id_cita}/cancelar")
def cancel_appointment(
    id_cita: int,
    body: CancelRequest,
    request: Request,
    user: dict = Depends(get_current_user),
) -> dict:
    """Cancela una cita liberando de inmediato el bloque horario y omitiendo recordatorios."""
    with db_session() as conn:
        cita = conn.execute("SELECT * FROM cita WHERE id_cita = ?", (id_cita,)).fetchone()
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada.")
        if user["rol"] == "Paciente" and cita["id_paciente"] != user["id_paciente"]:
            raise HTTPException(status_code=403, detail="Solo puede cancelar sus propias citas.")
        if cita["estado"] == "atendida":
            raise HTTPException(status_code=400, detail="No es posible cancelar una cita ya atendida.")

        conn.execute(
            """
            UPDATE cita
            SET estado = 'cancelada', motivo_cambio_cancelacion = ?,
                id_usuario_gestion = ?, fecha_actualizacion = datetime('now', 'localtime')
            WHERE id_cita = ?
            """,
            (body.motivo, user["id_usuario"], id_cita),
        )
        conn.execute("UPDATE recordatorio SET estado = 'omitido' WHERE id_cita = ? AND estado = 'pendiente'", (id_cita,))

    log_audit(
        user["id_usuario"],
        "cita",
        id_cita,
        "CANCELAR",
        request.client.host if request.client else "127.0.0.1",
        body.motivo,
    )
    return {"id_cita": id_cita, "estado": "cancelada", "mensaje": "Cita cancelada y bloque horario liberado."}


@app.get("/api/pacientes")
def list_patients(
    q: str = "",
    _user: dict = Depends(require_roles("Secretaria", "Odontologo", "Administrador")),
) -> list[dict]:
    """Busca pacientes por RUT, nombre o apellido."""
    like = f"%{q.strip()}%"
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT id_paciente, rut, nombre, apellido, fecha_nacimiento, telefono, correo, prevision
            FROM paciente
            WHERE rut LIKE ? OR nombre LIKE ? OR apellido LIKE ?
            ORDER BY apellido ASC, nombre ASC
            """,
            (like, like, like),
        ).fetchall()
    return [dict(r) for r in rows]


@app.post("/api/pacientes", status_code=status.HTTP_201_CREATED)
def create_patient(
    body: CreatePatientRequest,
    _user: dict = Depends(require_roles("Secretaria", "Administrador")),
) -> dict:
    """Da de alta un paciente desde recepción o atención telefónica."""
    try:
        rut_norm = validate_rut(body.rut)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    with db_session() as conn:
        try:
            cur = conn.execute(
                """
                INSERT INTO paciente (rut, nombre, apellido, fecha_nacimiento, telefono, correo, direccion, prevision, consentimiento_datos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (rut_norm, body.nombre.strip(), body.apellido.strip(), body.fecha_nacimiento, body.telefono.strip(), body.correo.strip(), body.direccion.strip(), body.prevision),
            )
            return {"id_paciente": cur.lastrowid, "rut": rut_norm}
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="El RUT o correo del paciente ya existe.") from exc


@app.get("/api/fichas/{id_paciente}")
def get_clinical_record(
    id_paciente: int,
    request: Request,
    user: dict = Depends(require_roles("Odontologo")),
) -> dict:
    """Retorna la ficha clínica descifrada (AES-256). Acceso exclusivo para rol Odontólogo."""
    with db_session() as conn:
        pac = conn.execute("SELECT id_paciente, rut, nombre, apellido, fecha_nacimiento, prevision FROM paciente WHERE id_paciente = ?", (id_paciente,)).fetchone()
        if not pac:
            raise HTTPException(status_code=404, detail="Paciente no encontrado.")
        ficha = conn.execute("SELECT * FROM ficha_clinica WHERE id_paciente = ?", (id_paciente,)).fetchone()
        evoluciones = []
        if ficha:
            evs = conn.execute(
                """
                SELECT ev.*, u.nombre || ' ' || u.apellido AS odontologo_nombre
                FROM evolucion_clinica ev
                INNER JOIN odontologo o ON o.id_odontologo = ev.id_odontologo
                INNER JOIN usuario u ON u.id_usuario = o.id_usuario
                WHERE ev.id_ficha = ?
                ORDER BY ev.fecha_atencion DESC
                """,
                (ficha["id_ficha"],),
            ).fetchall()
            for ev in evs:
                evoluciones.append(
                    {
                        "id_evolucion": ev["id_evolucion"],
                        "fecha_atencion": ev["fecha_atencion"],
                        "odontologo": ev["odontologo_nombre"],
                        "pieza_dental": ev["pieza_dental"],
                        "diagnostico": decrypt_aes256(ev["diagnostico_enc"]),
                        "tratamiento_realizado": decrypt_aes256(ev["tratamiento_realizado_enc"]),
                        "indicaciones": decrypt_aes256(ev["indicaciones_enc"]),
                    }
                )

    log_audit(
        user["id_usuario"],
        "ficha_clinica",
        id_paciente,
        "VER_FICHA",
        request.client.host if request.client else "127.0.0.1",
        f"Consulta de ficha clínica paciente {id_paciente}",
    )
    return {
        "paciente": dict(pac),
        "antecedentes_medicos": decrypt_aes256(ficha["antecedentes_medicos_enc"]) if ficha else "",
        "alergias": decrypt_aes256(ficha["alergias_enc"]) if ficha else "",
        "grupo_sanguineo": ficha["grupo_sanguineo"] if ficha else "",
        "evoluciones": evoluciones,
    }


@app.post("/api/fichas/{id_paciente}/evolucion", status_code=status.HTTP_201_CREATED)
def add_clinical_evolution(
    id_paciente: int,
    body: ClinicalEvolutionRequest,
    request: Request,
    user: dict = Depends(require_roles("Odontologo")),
) -> dict:
    """Registra una evolución clínica cifrada con AES-256 y marca la cita asociada como atendida."""
    with db_session() as conn:
        ficha = conn.execute("SELECT id_ficha FROM ficha_clinica WHERE id_paciente = ?", (id_paciente,)).fetchone()
        if not ficha:
            cur_f = conn.execute(
                "INSERT INTO ficha_clinica (id_paciente, antecedentes_medicos_enc, alergias_enc) VALUES (?, ?, ?)",
                (id_paciente, encrypt_aes256(body.antecedentes_medicos), encrypt_aes256(body.alergias)),
            )
            id_ficha = cur_f.lastrowid
        else:
            id_ficha = ficha["id_ficha"]
            if body.antecedentes_medicos is not None or body.alergias is not None:
                conn.execute(
                    """
                    UPDATE ficha_clinica
                    SET antecedentes_medicos_enc = COALESCE(?, antecedentes_medicos_enc),
                        alergias_enc = COALESCE(?, alergias_enc)
                    WHERE id_ficha = ?
                    """,
                    (encrypt_aes256(body.antecedentes_medicos), encrypt_aes256(body.alergias), id_ficha),
                )

        cur_ev = conn.execute(
            """
            INSERT INTO evolucion_clinica (id_ficha, id_cita, id_odontologo, pieza_dental, diagnostico_enc, tratamiento_realizado_enc, indicaciones_enc)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id_ficha,
                body.id_cita,
                user["id_odontologo"],
                body.pieza_dental,
                encrypt_aes256(body.diagnostico),
                encrypt_aes256(body.tratamiento_realizado),
                encrypt_aes256(body.indicaciones),
            ),
        )
        if body.id_cita:
            conn.execute("UPDATE cita SET estado = 'atendida' WHERE id_cita = ?", (body.id_cita,))

    log_audit(
        user["id_usuario"],
        "evolucion_clinica",
        cur_ev.lastrowid,
        "CREAR",
        request.client.host if request.client else "127.0.0.1",
        f"Evolución cifrada AES-256 para paciente {id_paciente}",
    )
    return {"id_evolucion": cur_ev.lastrowid, "mensaje": "Evolución clínica guardada y cifrada (AES-256)."}


@app.get("/api/recordatorios")
def list_reminders(_user: dict = Depends(require_roles("Secretaria", "Administrador"))) -> list[dict]:
    """Lista la cola de recordatorios automáticos con estado y paciente asociado."""
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT r.*, c.fecha, c.hora_inicio, c.estado AS estado_cita,
                   p.nombre || ' ' || p.apellido AS paciente, p.correo
            FROM recordatorio r
            INNER JOIN cita c ON c.id_cita = r.id_cita
            INNER JOIN paciente p ON p.id_paciente = c.id_paciente
            ORDER BY r.id_recordatorio DESC
            LIMIT 50
            """
        ).fetchall()
    return [dict(r) for r in rows]


@app.post("/api/recordatorios/procesar")
def trigger_reminders(_user: dict = Depends(require_roles("Secretaria", "Administrador"))) -> dict:
    """Ejecuta manualmente el procesamiento de recordatorios pendientes."""
    return process_pending_reminders(force_all=True)


@app.get("/api/admin/dashboard")
def admin_dashboard(_user: dict = Depends(require_roles("Administrador", "Secretaria"))) -> dict:
    """Entrega métricas de ocupación de agenda, estados de citas y últimos eventos de auditoría."""
    with db_session() as conn:
        resumen_estados = [
            dict(r)
            for r in conn.execute("SELECT estado, COUNT(*) AS cantidad FROM cita GROUP BY estado").fetchall()
        ]
        auditoria = [
            dict(r)
            for r in conn.execute(
                """
                SELECT a.*, u.nombre || ' ' || u.apellido AS usuario
                FROM auditoria_acceso a
                LEFT JOIN usuario u ON u.id_usuario = a.id_usuario
                ORDER BY a.id_auditoria DESC
                LIMIT 20
                """
            ).fetchall()
        ]
        usuarios = [
            dict(r)
            for r in conn.execute(
                """
                SELECT u.id_usuario, u.rut, u.nombre, u.apellido, u.correo, u.activo, r.nombre AS rol
                FROM usuario u INNER JOIN rol r ON r.id_rol = u.id_rol
                ORDER BY u.id_usuario
                """
            ).fetchall()
        ]
    return {"resumen_estados": resumen_estados, "auditoria": auditoria, "usuarios": usuarios}


@app.post("/api/admin/usuarios", status_code=status.HTTP_201_CREATED)
def admin_create_user(
    body: CreateUserRequest,
    _user: dict = Depends(require_roles("Administrador")),
) -> dict:
    """Permite al administrador crear usuarios con contraseña bcrypt y rol asignado."""
    try:
        rut_norm = validate_rut(body.rut)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    with db_session() as conn:
        try:
            cur = conn.execute(
                """
                INSERT INTO usuario (id_rol, rut, nombre, apellido, correo, password_hash, telefono)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (body.id_rol, rut_norm, body.nombre.strip(), body.apellido.strip(), body.correo.strip(), hash_password(body.password), body.telefono.strip()),
            )
            return {"id_usuario": cur.lastrowid}
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="El RUT o correo ya existe.") from exc
