"""Servicio automático de recordatorios de citas (RF08, RF09, RNF07)."""

import datetime as dt
import secrets
from app.database import db_session


def schedule_reminder_for_appointment(conn, id_cita: int, fecha: str, hora_inicio: str) -> None:
    """Programa un recordatorio automático 24 horas antes de la cita."""
    token = secrets.token_urlsafe(24)
    dt_cita = dt.datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M")
    dt_prog = dt_cita - dt.timedelta(hours=24)
    conn.execute(
        """
        INSERT INTO recordatorio (id_cita, canal, fecha_programada, estado, token_confirmacion)
        VALUES (?, 'correo', ?, 'pendiente', ?)
        """,
        (id_cita, dt_prog.strftime("%Y-%m-%d %H:%M:%S"), token),
    )


def process_pending_reminders(force_all: bool = False) -> dict:
    """Procesa recordatorios pendientes y omite los de citas canceladas o reprogramadas."""
    now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    enviados = 0
    omitidos = 0

    with db_session() as conn:
        query = """
            SELECT r.id_recordatorio, r.id_cita, r.canal, r.fecha_programada,
                   c.estado AS estado_cita, c.fecha, c.hora_inicio,
                   p.nombre || ' ' || p.apellido AS paciente, p.correo
            FROM recordatorio r
            INNER JOIN cita c ON c.id_cita = r.id_cita
            INNER JOIN paciente p ON p.id_paciente = c.id_paciente
            WHERE r.estado = 'pendiente'
        """
        params: tuple = ()
        if not force_all:
            query += " AND r.fecha_programada <= ?"
            params = (now_str,)

        rows = conn.execute(query, params).fetchall()
        for row in rows:
            if row["estado_cita"] in ("cancelada", "reprogramada", "atendida"):
                conn.execute(
                    "UPDATE recordatorio SET estado = 'omitido' WHERE id_recordatorio = ?",
                    (row["id_recordatorio"],),
                )
                omitidos += 1
            else:
                conn.execute(
                    """
                    UPDATE recordatorio
                    SET estado = 'enviado', fecha_envio = ?, intentos = intentos + 1
                    WHERE id_recordatorio = ?
                    """,
                    (now_str, row["id_recordatorio"]),
                )
                enviados += 1

    return {"procesados": enviados + omitidos, "enviados": enviados, "omitidos": omitidos, "timestamp": now_str}
