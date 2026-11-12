"""Capa de acceso a datos SQLite, esquema 3FN anti-choques y datos iniciales."""

import datetime as dt
import sqlite3
from contextlib import contextmanager

from app.config import DB_PATH
from app.security import encrypt_aes256, hash_password


def get_connection() -> sqlite3.Connection:
    """Abre una conexión SQLite con Row factory y llaves foreáneas habilitadas."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


@contextmanager
def db_session():
    """Provee un contexto transaccional seguro con commit/rollback automático."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def log_audit(
    id_usuario: int,
    entidad_afectada: str,
    id_registro: int,
    accion: str,
    ip_origen: str = "127.0.0.1",
    detalle: str | None = None,
) -> None:
    """Registra un evento en la tabla auditoria_acceso sin interrumpir el flujo principal."""
    with db_session() as conn:
        if id_usuario:
            conn.execute(
                """
                INSERT INTO auditoria_acceso (id_usuario, entidad_afectada, id_registro, accion, ip_origen, detalle)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (id_usuario, entidad_afectada, id_registro, accion, ip_origen, detalle),
            )


def init_db() -> None:
    """Crea las 12 tablas del modelo 3FN, índices de rendimiento y carga datos semilla si está vacía."""
    schema_sql = """
    CREATE TABLE IF NOT EXISTS rol (
        id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        descripcion TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS usuario (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        id_rol INTEGER NOT NULL REFERENCES rol(id_rol),
        rut TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        telefono TEXT,
        activo INTEGER NOT NULL DEFAULT 1,
        fecha_creacion TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS especialidad (
        id_especialidad INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        duracion_estandar_min INTEGER NOT NULL DEFAULT 30
    );

    CREATE TABLE IF NOT EXISTS odontologo (
        id_odontologo INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL UNIQUE REFERENCES usuario(id_usuario),
        id_especialidad INTEGER NOT NULL REFERENCES especialidad(id_especialidad),
        registro_superintendencia TEXT NOT NULL UNIQUE,
        box_asignado TEXT
    );

    CREATE TABLE IF NOT EXISTS horario_odontologo (
        id_horario INTEGER PRIMARY KEY AUTOINCREMENT,
        id_odontologo INTEGER NOT NULL REFERENCES odontologo(id_odontologo),
        dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL,
        duracion_bloque_min INTEGER NOT NULL DEFAULT 30,
        activo INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS bloqueo_horario (
        id_bloqueo INTEGER PRIMARY KEY AUTOINCREMENT,
        id_odontologo INTEGER NOT NULL REFERENCES odontologo(id_odontologo),
        fecha TEXT NOT NULL,
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL,
        motivo TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS paciente (
        id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER UNIQUE REFERENCES usuario(id_usuario),
        rut TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        fecha_nacimiento TEXT NOT NULL,
        telefono TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE,
        direccion TEXT,
        prevision TEXT NOT NULL DEFAULT 'Particular',
        consentimiento_datos INTEGER NOT NULL DEFAULT 1,
        fecha_registro TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS tipo_atencion (
        id_tipo_atencion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_especialidad INTEGER NOT NULL REFERENCES especialidad(id_especialidad),
        nombre TEXT NOT NULL,
        duracion_min INTEGER NOT NULL DEFAULT 30,
        valor_referencia_clp INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS cita (
        id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
        id_paciente INTEGER NOT NULL REFERENCES paciente(id_paciente),
        id_odontologo INTEGER NOT NULL REFERENCES odontologo(id_odontologo),
        id_tipo_atencion INTEGER NOT NULL REFERENCES tipo_atencion(id_tipo_atencion),
        id_usuario_gestion INTEGER REFERENCES usuario(id_usuario),
        fecha TEXT NOT NULL,
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL,
        origen TEXT NOT NULL DEFAULT 'online',
        estado TEXT NOT NULL DEFAULT 'pendiente'
            CHECK (estado IN ('pendiente', 'confirmada', 'atendida', 'cancelada', 'reprogramada')),
        motivo_cambio_cancelacion TEXT,
        fecha_creacion TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        fecha_actualizacion TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
    );

    -- Índice único parcial: garantiza 0 choques horarios para citas activas (RNF06)
    CREATE UNIQUE INDEX IF NOT EXISTS uq_cita_bloque_activo
        ON cita (id_odontologo, fecha, hora_inicio)
        WHERE estado IN ('pendiente', 'confirmada', 'atendida');

    CREATE INDEX IF NOT EXISTS idx_cita_fecha ON cita (fecha, id_odontologo, estado);
    CREATE INDEX IF NOT EXISTS idx_cita_paciente ON cita (id_paciente, fecha);

    CREATE TABLE IF NOT EXISTS recordatorio (
        id_recordatorio INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cita INTEGER NOT NULL REFERENCES cita(id_cita),
        canal TEXT NOT NULL DEFAULT 'correo' CHECK (canal IN ('correo', 'whatsapp', 'sms')),
        fecha_programada TEXT NOT NULL,
        fecha_envio TEXT,
        estado TEXT NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'enviado', 'fallido', 'omitido')),
        intentos INTEGER NOT NULL DEFAULT 0,
        token_confirmacion TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS ficha_clinica (
        id_ficha INTEGER PRIMARY KEY AUTOINCREMENT,
        id_paciente INTEGER NOT NULL UNIQUE REFERENCES paciente(id_paciente),
        antecedentes_medicos_enc BLOB,
        alergias_enc BLOB,
        grupo_sanguineo TEXT,
        fecha_apertura TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS evolucion_clinica (
        id_evolucion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ficha INTEGER NOT NULL REFERENCES ficha_clinica(id_ficha),
        id_cita INTEGER UNIQUE REFERENCES cita(id_cita),
        id_odontologo INTEGER NOT NULL REFERENCES odontologo(id_odontologo),
        fecha_atencion TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
        pieza_dental TEXT,
        diagnostico_enc BLOB NOT NULL,
        tratamiento_realizado_enc BLOB NOT NULL,
        indicaciones_enc BLOB
    );

    CREATE TABLE IF NOT EXISTS auditoria_acceso (
        id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL REFERENCES usuario(id_usuario),
        entidad_afectada TEXT NOT NULL,
        id_registro INTEGER NOT NULL,
        accion TEXT NOT NULL,
        ip_origen TEXT NOT NULL,
        detalle TEXT,
        fecha_hora TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS configuracion (
        clave TEXT PRIMARY KEY,
        valor TEXT NOT NULL,
        descripcion TEXT NOT NULL
    );
    """

    with db_session() as conn:
        conn.executescript(schema_sql)

        count_roles = conn.execute("SELECT COUNT(*) FROM rol").fetchone()[0]
        if count_roles > 0:
            return

        # Seed de roles
        conn.executemany(
            "INSERT INTO rol (nombre, descripcion) VALUES (?, ?)",
            [
                ("Administrador", "Gestión de usuarios, roles, horarios y reportes"),
                ("Odontologo", "Atención clínica y acceso exclusivo a ficha médica cifrada"),
                ("Secretaria", "Gestión de agenda diaria, modificación y cancelación de citas"),
                ("Paciente", "Reserva de horas online y consulta de sus citas"),
            ],
        )

        # Seed de especialidades y tipos de atención
        conn.executemany(
            "INSERT INTO especialidad (nombre, duracion_estandar_min) VALUES (?, ?)",
            [
                ("Odontología General", 30),
                ("Ortodoncia", 30),
                ("Endodoncia", 45),
                ("Odontopediatría", 30),
            ],
        )
        conn.executemany(
            "INSERT INTO tipo_atencion (id_especialidad, nombre, duracion_min, valor_referencia_clp) VALUES (?, ?, ?, ?)",
            [
                (1, "Evaluación y Diagnóstico", 30, 15000),
                (1, "Limpieza / Destartraje", 30, 35000),
                (1, "Restauración / Tapadura", 30, 45000),
                (2, "Control de Ortodoncia", 30, 30000),
                (3, "Tratamiento de Conducto", 45, 120000),
                (4, "Control Odontopediátrico", 30, 25000),
            ],
        )

        # Seed de usuarios demo (clave común: Sonrisa2026!)
        pwd = hash_password("Sonrisa2026!")
        usuarios = [
            (1, "11111111-1", "Fernando", "Durán", "admin@sonrisasana.cl", pwd, "+56981001100"),
            (2, "12345678-5", "Valeria", "Muñoz", "valeria.munoz@sonrisasana.cl", pwd, "+56982002200"),
            (2, "13456789-0", "Rodrigo", "Torres", "rodrigo.torres@sonrisasana.cl", pwd, "+56983003300"),
            (3, "14567890-9", "Camila", "Rojas", "secretaria@sonrisasana.cl", pwd, "+56984004400"),
            (4, "19876543-3", "María", "González", "maria.gonzalez@correo.cl", pwd, "+56991234567"),
            (4, "18221903-1", "Juan", "Pérez", "juan.perez@correo.cl", pwd, "+56997654321"),
        ]
        conn.executemany(
            "INSERT INTO usuario (id_rol, rut, nombre, apellido, correo, password_hash, telefono) VALUES (?, ?, ?, ?, ?, ?, ?)",
            usuarios,
        )

        # Seed odontólogos y sus horarios semanales (lun-sáb)
        conn.executemany(
            "INSERT INTO odontologo (id_usuario, id_especialidad, registro_superintendencia, box_asignado) VALUES (?, ?, ?, ?)",
            [
                (2, 1, "SUP-OD-44512", "Box 1"),
                (3, 2, "SUP-OD-51908", "Box 2"),
            ],
        )
        for od_id in (1, 2):
            for dia in range(1, 7):
                conn.execute(
                    "INSERT INTO horario_odontologo (id_odontologo, dia_semana, hora_inicio, hora_fin, duracion_bloque_min) VALUES (?, ?, ?, ?, ?)",
                    (od_id, dia, "09:00", "13:00", 30),
                )
                if dia <= 5:
                    conn.execute(
                        "INSERT INTO horario_odontologo (id_odontologo, dia_semana, hora_inicio, hora_fin, duracion_bloque_min) VALUES (?, ?, ?, ?, ?)",
                        (od_id, dia, "14:30", "18:30", 30),
                    )

        # Seed pacientes
        conn.executemany(
            """INSERT INTO paciente (id_usuario, rut, nombre, apellido, fecha_nacimiento, telefono, correo, direccion, prevision)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (5, "19876543-3", "María", "González", "1994-05-14", "+56991234567", "maria.gonzalez@correo.cl", "Av. Concha y Toro 1240, Puente Alto", "Fonasa"),
                (6, "18221903-1", "Juan", "Pérez", "1990-11-02", "+56997654321", "juan.perez@correo.cl", "Los Olmos 450, La Florida", "Isapre"),
                (None, "15432110-7", "Ana", "Soto", "1985-03-22", "+56988776655", "ana.soto@correo.cl", "Pasaje Sur 88, Puente Alto", "Particular"),
            ],
        )

        # Seed citas de ejemplo para hoy y mañana
        hoy = dt.date.today().isoformat()
        manana = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        citas_seed = [
            (1, 1, 1, 4, hoy, "09:00", "09:30", "online", "confirmada"),
            (2, 1, 2, 4, hoy, "10:00", "10:30", "telefonica", "pendiente"),
            (3, 2, 4, 4, hoy, "11:00", "11:30", "presencial", "pendiente"),
            (1, 1, 3, None, manana, "09:30", "10:00", "online", "pendiente"),
        ]
        for pac, od, tipo, ug, fec, hi, hf, orig, est in citas_seed:
            cur = conn.execute(
                """INSERT INTO cita (id_paciente, id_odontologo, id_tipo_atencion, id_usuario_gestion, fecha, hora_inicio, hora_fin, origen, estado)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (pac, od, tipo, ug, fec, hi, hf, orig, est),
            )
            cita_id = cur.lastrowid
            prog = f"{fec} {hi}:00"
            conn.execute(
                "INSERT INTO recordatorio (id_cita, canal, fecha_programada, estado, token_confirmacion) VALUES (?, 'correo', datetime(?, '-24 hours'), 'pendiente', ?)",
                (cita_id, prog, f"tok-seed-{cita_id}"),
            )

        # Seed ficha clínica cifrada AES-256
        cur_ficha = conn.execute(
            "INSERT INTO ficha_clinica (id_paciente, antecedentes_medicos_enc, alergias_enc, grupo_sanguineo) VALUES (?, ?, ?, ?)",
            (1, encrypt_aes256("Hipertensión controlada"), encrypt_aes256("Penicilina"), "O+"),
        )
        ficha_id = cur_ficha.lastrowid
        conn.execute(
            """INSERT INTO evolucion_clinica (id_ficha, id_cita, id_odontologo, pieza_dental, diagnostico_enc, tratamiento_realizado_enc, indicaciones_enc)
               VALUES (?, NULL, 1, ?, ?, ?, ?)""",
            (
                ficha_id,
                "1.6",
                encrypt_aes256("Caries oclusal incipiente en pieza 1.6"),
                encrypt_aes256("Restauración con resina compuesta fotocurada"),
                encrypt_aes256("Control en 6 meses y técnica de cepillado"),
            ),
        )

        conn.executemany(
            "INSERT INTO configuracion (clave, valor, descripcion) VALUES (?, ?, ?)",
            [
                ("horas_aviso_recordatorio", "24", "Horas de anticipación para envío automático de recordatorio"),
                ("clinica_nombre", "Clínica Odontológica Sonrisa Sana", "Nombre comercial de la clínica"),
            ],
        )
