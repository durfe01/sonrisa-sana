"""Generador de diagramas UML, ER, flujos TO-BE, mockups y tablero Kanban en PNG."""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagramas")
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"

# Colores corporativos Sonrisa Sana (salud dental: azul/turquesa/blanco/naranjo alerta)
C_PRIMARY = "#0F4C81"
C_SEC = "#1E88E5"
C_TEAL = "#00897B"
C_BG = "#F8FAFC"
C_BOX = "#FFFFFF"
C_BORDER = "#334155"
C_ALERT = "#EA580C"
C_ALERT_BG = "#FFF7ED"
C_GREEN = "#16A34A"
C_GREEN_BG = "#DCFCE7"
C_YELLOW = "#CA8A04"
C_YELLOW_BG = "#FEF9C3"
C_RED = "#DC2626"
C_RED_BG = "#FEE2E2"


def draw_actor(ax, x, y, label):
    """Dibuja un actor UML (figura de palotes) con su etiqueta en la posición indicada."""
    # Cabeza
    head = patches.Circle((x, y + 0.32), 0.12, fill=False, edgecolor=C_PRIMARY, lw=2)
    ax.add_patch(head)
    # Cuerpo, brazos, piernas
    ax.plot([x, x], [y + 0.20, y - 0.10], color=C_PRIMARY, lw=2)
    ax.plot([x - 0.16, x + 0.16], [y + 0.10, y + 0.10], color=C_PRIMARY, lw=2)
    ax.plot([x, x - 0.14], [y - 0.10, y - 0.32], color=C_PRIMARY, lw=2)
    ax.plot([x, x + 0.14], [y - 0.10, y - 0.32], color=C_PRIMARY, lw=2)
    ax.text(x, y - 0.45, label, ha="center", va="top", fontsize=9, fontweight="bold", color="#0F172A")


def draw_use_case(ax, x, y, text, w=2.5, h=0.65, color="#E0F2FE"):
    """Dibuja un óvalo de caso de uso UML con texto centrado."""
    el = patches.Ellipse((x, y), w, h, facecolor=color, edgecolor=C_PRIMARY, lw=1.6)
    ax.add_patch(el)
    ax.text(x, y, text, ha="center", va="center", fontsize=8, fontweight="bold", color="#0F172A")


def draw_line(ax, x1, y1, x2, y2, style="-", label="", color="#475569", arrow=False):
    """Traza una línea o flecha entre dos puntos con etiqueta opcional."""
    if arrow:
        arr = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
                              linestyle=style, color=color, lw=1.3)
        ax.add_patch(arr)
    else:
        ax.plot([x1, x2], [y1, y2], linestyle=style, color=color, lw=1.3)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.08, label, ha="center", va="bottom", fontsize=7.2,
                color=color, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))


def gen_use_case_diagram():
    """Genera el diagrama general de casos de uso UML (01_casos_de_uso_general.png)."""
    fig, ax = plt.subplots(figsize=(14, 9.5), dpi=180)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(7, 9.65, "Diagrama de Casos de Uso General — Sistema Clínica Odontológica «Sonrisa Sana»",
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_PRIMARY)

    # Frontera del sistema
    sys_box = FancyBboxPatch((2.6, 0.5), 8.8, 8.7, boxstyle="round,pad=0.1",
                             facecolor="#F8FAFC", edgecolor=C_PRIMARY, lw=2)
    ax.add_patch(sys_box)
    ax.text(7.0, 9.0, "Sistema de Agendamiento y Gestión Clínica «Sonrisa Sana»",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color=C_PRIMARY)

    # Actores izquierda
    draw_actor(ax, 1.1, 7.6, "Paciente")
    draw_actor(ax, 1.1, 5.2, "Secretaria")
    draw_actor(ax, 1.1, 2.7, "Odontólogo")
    draw_actor(ax, 1.1, 1.0, "Administrador")

    # Actores derecha
    draw_actor(ax, 12.8, 6.8, "Reloj del\nSistema")
    draw_actor(ax, 12.8, 4.2, "Servicio de\nMensajería")

    # Casos de uso
    draw_use_case(ax, 4.5, 8.1, "CU01: Registrarse /\nIniciar Sesión", 2.4, 0.65)
    draw_use_case(ax, 4.5, 7.1, "CU03: Reservar Hora\nOnline", 2.4, 0.65)
    draw_use_case(ax, 8.6, 7.5, "CU04: Validar\nDisponibilidad", 2.4, 0.62, "#FEF3C7")
    draw_use_case(ax, 8.6, 6.4, "CU09: Enviar Recordatorio\nAutomático", 2.6, 0.65, "#DCFCE7")

    draw_use_case(ax, 4.5, 5.9, "CU02: Gestionar\nPacientes", 2.4, 0.62)
    draw_use_case(ax, 4.5, 5.0, "CU05: Ver Agenda\nDiaria / Semanal", 2.4, 0.62)
    draw_use_case(ax, 8.6, 5.2, "CU06: Modificar /\nReprogramar Cita", 2.5, 0.62)
    draw_use_case(ax, 8.6, 4.2, "CU07: Cancelar Cita\ny Liberar Bloque", 2.5, 0.62)

    draw_use_case(ax, 4.5, 3.3, "CU10: Consultar Ficha\nClínica Confidencial", 2.6, 0.65, "#FCE7F3")
    draw_use_case(ax, 8.6, 3.1, "CU11: Registrar Evolución,\nDiagnóstico y Tratamiento", 2.8, 0.65, "#FCE7F3")
    draw_use_case(ax, 4.5, 2.2, "CU08: Configurar Horarios\ny Bloqueos", 2.6, 0.62)

    draw_use_case(ax, 4.5, 1.1, "CU12: Gestionar Usuarios\ny Roles (RBAC)", 2.6, 0.62, "#EDE9FE")
    draw_use_case(ax, 8.6, 1.8, "CU13: Consultar Auditoría\nde Accesos", 2.5, 0.62, "#EDE9FE")
    draw_use_case(ax, 8.6, 0.95, "CU14: Generar Reporte\nde Ocupación", 2.5, 0.62, "#EDE9FE")

    # Asociaciones Paciente
    draw_line(ax, 1.4, 7.7, 3.3, 8.1)
    draw_line(ax, 1.4, 7.5, 3.3, 7.1)
    draw_line(ax, 1.4, 7.3, 7.35, 4.2)  # Cancelar propia cita

    # Asociaciones Secretaria
    draw_line(ax, 1.4, 5.4, 3.3, 5.9)
    draw_line(ax, 1.4, 5.2, 3.3, 5.0)
    draw_line(ax, 1.4, 5.1, 7.35, 5.2)
    draw_line(ax, 1.4, 4.9, 7.35, 4.2)

    # Asociaciones Odontólogo
    draw_line(ax, 1.4, 2.9, 3.2, 3.3)
    draw_line(ax, 1.4, 2.7, 7.2, 3.1)
    draw_line(ax, 1.4, 2.5, 3.2, 2.2)
    draw_line(ax, 1.4, 2.8, 3.3, 5.0)

    # Asociaciones Administrador
    draw_line(ax, 1.4, 1.0, 3.2, 1.1)
    draw_line(ax, 1.4, 1.1, 7.35, 1.8)
    draw_line(ax, 1.4, 0.9, 7.35, 0.95)

    # Actores sistema derecha
    draw_line(ax, 12.4, 6.8, 9.9, 6.45)
    draw_line(ax, 12.4, 4.2, 9.9, 6.35)

    # Include / Extend
    draw_line(ax, 5.7, 7.1, 7.4, 7.45, style="--", label="<<include>>", color=C_TEAL, arrow=True)
    draw_line(ax, 7.35, 5.2, 7.4, 7.25, style="--", label="<<include>>", color=C_TEAL, arrow=True)
    draw_line(ax, 5.8, 3.3, 7.2, 3.15, style="--", label="<<extend>>", color=C_ALERT, arrow=True)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "01_casos_de_uso_general.png"), dpi=180)
    plt.close()


def draw_entity(ax, x, y, title, cols, w=2.5, header_color=C_PRIMARY):
    """Dibuja una entidad del diagrama ER con su cabecera y lista de atributos."""
    line_h = 0.22
    h = 0.34 + len(cols) * line_h
    box = FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0.03",
                         facecolor="white", edgecolor=header_color, lw=1.5)
    ax.add_patch(box)
    hdr = FancyBboxPatch((x, y - 0.34), w, 0.34, boxstyle="round,pad=0.03",
                         facecolor=header_color, edgecolor=header_color, lw=1)
    ax.add_patch(hdr)
    ax.text(x + w / 2, y - 0.17, title, ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="white")
    for idx, col in enumerate(cols):
        cy = y - 0.34 - (idx + 0.55) * line_h
        ax.text(x + 0.08, cy, col, ha="left", va="center", fontsize=7.0, color="#1E293B")
    return (x, y - h / 2, x + w, y - h / 2, x + w / 2, y, x + w / 2, y - h)


def gen_er_diagram():
    """Genera el diagrama Entidad-Relación 3FN (02_modelo_bd_er.png)."""
    fig, ax = plt.subplots(figsize=(15, 10), dpi=180)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(7.5, 9.7, "Modelo Entidad-Relación (Lógico / Relacional 3FN) — «Sonrisa Sana»",
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_PRIMARY)

    # Fila superior: Seguridad y Personal
    draw_entity(ax, 0.4, 9.2, "ROL", ["PK id_rol", "UQ nombre", "   descripcion"], 2.1, "#475569")
    draw_entity(ax, 3.1, 9.2, "USUARIO", ["PK id_usuario", "FK id_rol", "UQ rut", "UQ correo", "   password_hash", "   activo"], 2.3, "#475569")
    draw_entity(ax, 6.2, 9.2, "ODONTOLOGO", ["PK id_odontologo", "FK id_usuario", "FK id_especialidad", "UQ reg_superint", "   box_asignado"], 2.4, C_PRIMARY)
    draw_entity(ax, 9.3, 9.2, "ESPECIALIDAD", ["PK id_especialidad", "UQ nombre", "   duracion_est_min"], 2.2, C_PRIMARY)
    draw_entity(ax, 12.1, 9.2, "HORARIO_ODONT", ["PK id_horario", "FK id_odontologo", "   dia_semana", "   hora_inicio / fin", "   duracion_bloque"], 2.4, C_TEAL)

    # Fila media: Pacientes, Citas, Tipos, Bloqueos
    draw_entity(ax, 0.4, 6.4, "PACIENTE", ["PK id_paciente", "FK id_usuario (NULL)", "UQ rut", "UQ correo", "   nombre / apellido", "   telefono / prevision", "   consentimiento_datos"], 2.5, C_SEC)
    draw_entity(ax, 3.8, 6.4, "CITA", ["PK id_cita", "FK id_paciente", "FK id_odontologo", "FK id_tipo_atencion", "FK id_usuario_gestion", "   fecha / hora_inicio", "   estado / origen", "UQ bloque_activo"], 2.7, C_PRIMARY)
    draw_entity(ax, 7.4, 6.4, "TIPO_ATENCION", ["PK id_tipo_atencion", "FK id_especialidad", "   nombre", "   duracion_min", "   valor_ref_clp"], 2.3, C_TEAL)
    draw_entity(ax, 10.5, 6.4, "RECORDATORIO", ["PK id_recordatorio", "FK id_cita", "   canal (correo/wa)", "   fecha_programada", "   estado / intentos", "UQ token_confirm"], 2.4, C_GREEN)
    draw_entity(ax, 13.3, 6.4, "BLOQUEO", ["PK id_bloqueo", "FK id_odontologo", "   fecha", "   hora_ini / fin", "   motivo"], 1.5, C_ALERT)

    # Fila inferior: Ficha Clínica Confidencial y Auditoría
    draw_entity(ax, 0.4, 3.0, "FICHA_CLINICA", ["PK id_ficha", "FK id_paciente (UQ)", "   antecedentes_enc", "   alergias_enc", "   grupo_sanguineo"], 2.6, "#9D174D")
    draw_entity(ax, 3.8, 3.0, "EVOLUCION_CLINICA", ["PK id_evolucion", "FK id_ficha", "FK id_cita (UQ)", "FK id_odontologo", "   pieza_dental", "   diagnostico_enc", "   tratamiento_enc"], 2.7, "#9D174D")
    draw_entity(ax, 7.4, 3.0, "AUDITORIA_ACCESO", ["PK id_auditoria", "FK id_usuario", "   entidad_afectada", "   accion / ip_origen", "   fecha_hora"], 2.5, "#6D28D9")
    draw_entity(ax, 10.6, 3.0, "CONFIGURACION", ["PK clave", "   valor", "   descripcion"], 2.2, "#475569")

    # Relaciones con etiquetas de cardinalidad
    draw_line(ax, 2.5, 8.7, 3.1, 8.7, label="1 : N")
    draw_line(ax, 5.4, 8.7, 6.2, 8.7, label="1 : 0..1")
    draw_line(ax, 8.6, 8.7, 9.3, 8.7, label="N : 1")
    draw_line(ax, 8.6, 8.2, 12.1, 8.2, label="1 : N")

    draw_line(ax, 3.6, 7.6, 1.6, 6.4, label="0..1 : 1")
    draw_line(ax, 2.9, 5.5, 3.8, 5.5, label="1 : N")
    draw_line(ax, 6.5, 5.5, 7.4, 5.5, label="N : 1")
    draw_line(ax, 6.5, 5.1, 10.5, 5.1, label="1 : N")
    draw_line(ax, 7.4, 7.5, 5.2, 6.4, label="1 : N")
    draw_line(ax, 12.1, 7.5, 13.8, 6.4, label="1 : N")

    draw_line(ax, 1.6, 4.3, 1.6, 3.0, label="1 : 0..1")
    draw_line(ax, 3.0, 2.2, 3.8, 2.2, label="1 : N")
    draw_line(ax, 5.1, 3.9, 5.1, 3.0, label="0..1 : 0..1")
    draw_line(ax, 4.3, 7.5, 8.6, 3.0, label="1 : N")

    ax.text(7.5, 0.4, "Nota: Tablas en magenta (FICHA_CLINICA, EVOLUCION_CLINICA) almacenan datos médicos cifrados con AES-256 y acceso exclusivo para rol Odontólogo (RNF02).",
            ha="center", va="center", fontsize=8.5, style="italic", color="#9D174D",
            bbox=dict(boxstyle="round,pad=0.3", fc="#FDF2F8", ec="#9D174D"))

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "02_modelo_bd_er.png"), dpi=180)
    plt.close()


def draw_flow_node(ax, x, y, text, kind="process", w=2.8, h=0.65):
    """Dibuja un nodo de diagrama de flujo (inicio/fin, proceso, decisión, E/S o alerta)."""
    if kind == "start":
        el = patches.Ellipse((x, y), w * 0.8, h * 0.85, facecolor="#DBEAFE", edgecolor=C_PRIMARY, lw=1.8)
        ax.add_patch(el)
    elif kind == "end":
        el = patches.Ellipse((x, y), w * 0.8, h * 0.85, facecolor=C_GREEN_BG, edgecolor=C_GREEN, lw=1.8)
        ax.add_patch(el)
    elif kind == "alert":
        box = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05",
                             facecolor=C_ALERT_BG, edgecolor=C_ALERT, lw=1.8)
        ax.add_patch(box)
    elif kind == "decision":
        pts = [(x, y + h * 0.65), (x + w * 0.52, y), (x, y - h * 0.65), (x - w * 0.52, y)]
        poly = patches.Polygon(pts, closed=True, facecolor=C_YELLOW_BG, edgecolor=C_YELLOW, lw=1.7)
        ax.add_patch(poly)
    elif kind == "io":
        pts = [(x - w * 0.45, y - h * 0.45), (x + w * 0.52, y - h * 0.45),
               (x + w * 0.45, y + h * 0.45), (x - w * 0.52, y + h * 0.45)]
        poly = patches.Polygon(pts, closed=True, facecolor="#E0F2FE", edgecolor=C_SEC, lw=1.6)
        ax.add_patch(poly)
    else:
        box = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05",
                             facecolor="white", edgecolor=C_BORDER, lw=1.5)
        ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0F172A")


def gen_flow_diagrams():
    """Genera los tres diagramas de flujo TO-BE de procesos principales (03 a 05)."""
    # 1. Flujo Reserva Online
    fig, ax = plt.subplots(figsize=(10, 9.5), dpi=180)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(5, 9.65, "Diagrama de Flujo 1 (TO-BE): Reserva de Hora Online (RF03 / HU03)",
            ha="center", va="center", fontsize=12, fontweight="bold", color=C_PRIMARY)

    draw_flow_node(ax, 4.2, 8.9, "Inicio: Paciente ingresa al portal", "start", 3.4, 0.6)
    draw_flow_node(ax, 4.2, 7.9, "Autenticación / Registro (RUT y correo)", "io", 3.4, 0.65)
    draw_flow_node(ax, 4.2, 6.8, "Seleccionar Especialidad,\nOdontólogo y Fecha", "io", 3.4, 0.68)
    draw_flow_node(ax, 4.2, 5.6, "Consultar bloques disponibles (<1.5s)", "process", 3.4, 0.6)
    draw_flow_node(ax, 4.2, 4.4, "¿Bloque horario\ndisponible?", "decision", 3.0, 0.85)
    draw_flow_node(ax, 8.0, 4.4, "Mostrar alerta de choque\ny sugerir horarios cercanos", "alert", 2.9, 0.75)
    draw_flow_node(ax, 4.2, 3.0, "Registrar Cita (UNIQUE bloque_activo)\nEstado: «pendiente»", "process", 3.6, 0.68)
    draw_flow_node(ax, 4.2, 1.9, "Trigger: Programar recordatorio\nautomático 24h antes + Comprobante", "process", 3.6, 0.68)
    draw_flow_node(ax, 4.2, 0.8, "Fin: Hora reservada sin choques", "end", 3.4, 0.6)

    draw_line(ax, 4.2, 8.6, 4.2, 8.25, arrow=True)
    draw_line(ax, 4.2, 7.55, 4.2, 7.15, arrow=True)
    draw_line(ax, 4.2, 6.45, 4.2, 5.9, arrow=True)
    draw_line(ax, 4.2, 5.3, 4.2, 4.95, arrow=True)
    draw_line(ax, 5.75, 4.4, 6.5, 4.4, label="No", color=C_ALERT, arrow=True)
    draw_line(ax, 8.0, 4.8, 8.0, 6.8, color=C_ALERT)
    draw_line(ax, 8.0, 6.8, 5.95, 6.8, color=C_ALERT, arrow=True)
    draw_line(ax, 4.2, 3.85, 4.2, 3.35, label="Sí", color=C_GREEN, arrow=True)
    draw_line(ax, 4.2, 2.65, 4.2, 2.25, arrow=True)
    draw_line(ax, 4.2, 1.55, 4.2, 1.1, arrow=True)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "03_flujo_reserva_online.png"), dpi=180)
    plt.close()

    # 2. Flujo Secretaría Modificar/Cancelar
    fig, ax = plt.subplots(figsize=(10.5, 9), dpi=180)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 9.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(5.25, 9.15, "Diagrama de Flujo 2 (TO-BE): Modificación / Cancelación por Secretaría (RF05–RF07)",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color=C_PRIMARY)

    draw_flow_node(ax, 5.2, 8.4, "Inicio: Secretaria abre Agenda del Día", "start", 3.8, 0.6)
    draw_flow_node(ax, 5.2, 7.4, "Buscar cita por Paciente (RUT) u Odontólogo", "io", 3.8, 0.62)
    draw_flow_node(ax, 5.2, 6.2, "¿Acción a realizar?", "decision", 3.0, 0.8)
    draw_flow_node(ax, 2.4, 4.7, "Seleccionar nuevo\nfecha/hora disponible", "io", 3.0, 0.65)
    draw_flow_node(ax, 2.4, 3.5, "Validar sin choque\ny actualizar Cita", "process", 3.0, 0.62)
    draw_flow_node(ax, 8.0, 4.7, "Registrar motivo de\ncancelación", "io", 3.0, 0.65)
    draw_flow_node(ax, 8.0, 3.5, "Cambiar estado a «cancelada»\n(Libera bloque horario)", "alert", 3.2, 0.65)
    draw_flow_node(ax, 5.2, 2.1, "Omitir recordatorio previo y notificar\nal Paciente + Registrar Auditoría", "process", 4.6, 0.68)
    draw_flow_node(ax, 5.2, 0.9, "Fin: Agenda actualizada en tiempo real", "end", 3.8, 0.6)

    draw_line(ax, 5.2, 8.1, 5.2, 7.72, arrow=True)
    draw_line(ax, 5.2, 7.08, 5.2, 6.72, arrow=True)
    draw_line(ax, 3.7, 6.2, 2.4, 5.05, label="Modificar", color=C_SEC, arrow=True)
    draw_line(ax, 6.7, 6.2, 8.0, 5.05, label="Cancelar", color=C_ALERT, arrow=True)
    draw_line(ax, 2.4, 4.35, 2.4, 3.82, arrow=True)
    draw_line(ax, 8.0, 4.35, 8.0, 3.85, arrow=True)
    draw_line(ax, 2.4, 3.18, 4.2, 2.45, arrow=True)
    draw_line(ax, 8.0, 3.15, 6.2, 2.45, arrow=True)
    draw_line(ax, 5.2, 1.75, 5.2, 1.2, arrow=True)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "04_flujo_gestion_secretaria.png"), dpi=180)
    plt.close()

    # 3. Flujo Atención Clínica Confidencial y Recordatorios
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=180)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 9)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(5.5, 8.65, "Diagrama de Flujo 3 (TO-BE): Atención Confidencial (RNF02) y Recordatorios (RF08)",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color=C_PRIMARY)

    # Subproceso A: Ficha Clínica
    ax.text(2.7, 8.05, "A. Acceso a Ficha Clínica", ha="center", fontsize=10, fontweight="bold", color="#9D174D")
    draw_flow_node(ax, 2.7, 7.4, "Usuario solicita Ficha", "start", 2.8, 0.55)
    draw_flow_node(ax, 2.7, 6.2, "¿Rol == Odontólogo?", "decision", 2.6, 0.78)
    draw_flow_node(ax, 0.9, 4.6, "DENEGAR (403)\n+ Log Auditoría", "alert", 1.7, 0.65)
    draw_flow_node(ax, 3.7, 4.6, "Descifrar AES-256\ny mostrar historial", "process", 2.4, 0.62)
    draw_flow_node(ax, 3.7, 3.3, "Guardar evolución\n(Cita -> atendida)", "process", 2.4, 0.62)
    draw_flow_node(ax, 3.7, 2.0, "Fin Atención", "end", 2.2, 0.55)

    draw_line(ax, 2.7, 7.12, 2.7, 6.72, arrow=True)
    draw_line(ax, 1.4, 6.2, 0.9, 4.95, label="No", color=C_ALERT, arrow=True)
    draw_line(ax, 3.5, 5.7, 3.7, 4.95, label="Sí", color=C_GREEN, arrow=True)
    draw_line(ax, 3.7, 4.28, 3.7, 3.62, arrow=True)
    draw_line(ax, 3.7, 2.98, 3.7, 2.28, arrow=True)

    # Divisor
    ax.plot([5.6, 5.6], [1.2, 8.2], linestyle=":", color="#CBD5E1", lw=1.5)

    # Subproceso B: Recordatorios Automáticos
    ax.text(8.3, 8.05, "B. Proceso Automático de Recordatorios", ha="center", fontsize=10, fontweight="bold", color=C_TEAL)
    draw_flow_node(ax, 8.3, 7.4, "Reloj del Sistema (cada 15 min)", "start", 3.3, 0.55)
    draw_flow_node(ax, 8.3, 6.3, "Consultar recordatorios\npendientes <= NOW()", "process", 3.2, 0.62)
    draw_flow_node(ax, 8.3, 5.0, "¿Cita sigue\nvigente?", "decision", 2.5, 0.78)
    draw_flow_node(ax, 6.7, 3.5, "Marcar «omitido»", "alert", 1.9, 0.55)
    draw_flow_node(ax, 9.5, 3.5, "Enviar Correo / WA\ncon link confirmar", "process", 2.4, 0.62)
    draw_flow_node(ax, 9.5, 2.0, "Marcar «enviado»\n(Fin ciclo)", "end", 2.3, 0.55)

    draw_line(ax, 8.3, 7.12, 8.3, 6.62, arrow=True)
    draw_line(ax, 8.3, 5.98, 8.3, 5.52, arrow=True)
    draw_line(ax, 7.05, 5.0, 6.7, 3.8, label="No", color=C_ALERT, arrow=True)
    draw_line(ax, 9.2, 4.5, 9.5, 3.82, label="Sí", color=C_GREEN, arrow=True)
    draw_line(ax, 9.5, 3.18, 9.5, 2.28, arrow=True)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "05_flujo_atencion_y_recordatorios.png"), dpi=180)
    plt.close()


def gen_mockups():
    """Genera los wireframes/mockups de reserva online, secretaría y ficha clínica (06 a 08)."""
    # Mockup 1: Reserva Online Paciente
    fig, ax = plt.subplots(figsize=(11, 6.8), dpi=180)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis("off")
    fig.patch.set_facecolor("#F1F5F9")

    # Marco navegador
    ax.add_patch(FancyBboxPatch((0.3, 0.3), 10.4, 6.4, boxstyle="round,pad=0.05", fc="white", ec="#94A3B8", lw=1.5))
    ax.add_patch(FancyBboxPatch((0.3, 6.1), 10.4, 0.6, boxstyle="round,pad=0.02", fc=C_PRIMARY, ec=C_PRIMARY))
    ax.text(0.7, 6.4, "Clínica Odontológica «Sonrisa Sana» — Reserva de Hora Online", color="white", fontsize=11, fontweight="bold", va="center")
    ax.text(10.3, 6.4, "Paciente: María González | Cerrar sesión", color="#BAE6FD", fontsize=8.5, ha="right", va="center")

    # Barra pasos
    steps = ["1. Especialidad y Odontólogo", "2. Fecha y Bloque", "3. Confirmación"]
    for i, s in enumerate(steps):
        col = C_TEAL if i == 1 else ("#CBD5E1" if i == 2 else C_SEC)
        ax.add_patch(FancyBboxPatch((0.7 + i * 3.3, 5.35), 3.0, 0.45, boxstyle="round,pad=0.04", fc=col, ec="none"))
        ax.text(2.2 + i * 3.3, 5.57, s, color="white" if i < 2 else "#334155", fontsize=8.5, fontweight="bold", ha="center", va="center")

    # Panel izquierdo: selección
    ax.add_patch(FancyBboxPatch((0.7, 0.8), 4.4, 4.2, boxstyle="round,pad=0.06", fc="#F8FAFC", ec="#CBD5E1"))
    ax.text(0.95, 4.7, "Selección de Atención", fontsize=10, fontweight="bold", color=C_PRIMARY)
    fields = [("Especialidad:", "Odontología General"), ("Odontólogo:", "Dra. Valeria Muñoz (Box 2)"),
              ("Tipo de atención:", "Control / Limpieza (30 min)"), ("Fecha:", "18-11-2026")]
    for idx, (k, v) in enumerate(fields):
        fy = 4.15 - idx * 0.8
        ax.text(0.95, fy, k, fontsize=8.5, fontweight="bold", color="#334155")
        ax.add_patch(FancyBboxPatch((0.95, fy - 0.42), 3.9, 0.34, boxstyle="round,pad=0.03", fc="white", ec="#94A3B8"))
        ax.text(1.1, fy - 0.25, v, fontsize=8.5, color="#0F172A", va="center")

    # Panel derecho: bloques horarios
    ax.add_patch(FancyBboxPatch((5.4, 0.8), 4.9, 4.2, boxstyle="round,pad=0.06", fc="#F8FAFC", ec="#CBD5E1"))
    ax.text(5.65, 4.7, "Horarios Disponibles — 18-11-2026", fontsize=10, fontweight="bold", color=C_PRIMARY)
    slots = [("09:00", "libre"), ("09:30", "ocupado"), ("10:00", "seleccionado"), ("10:30", "libre"),
             ("11:00", "libre"), ("11:30", "ocupado"), ("12:00", "libre"), ("12:30", "libre")]
    for idx, (hora, st) in enumerate(slots):
        r, c = divmod(idx, 2)
        sx, sy = 5.65 + c * 2.25, 3.95 - r * 0.65
        fc = C_TEAL if st == "seleccionado" else ("#E2E8F0" if st == "ocupado" else "white")
        tc = "white" if st == "seleccionado" else ("#94A3B8" if st == "ocupado" else C_PRIMARY)
        ax.add_patch(FancyBboxPatch((sx, sy), 2.0, 0.45, boxstyle="round,pad=0.04", fc=fc, ec=tc))
        lbl = f"{hora} ({'Ocupado' if st=='ocupado' else 'Disponible' if st=='libre' else 'Elegido'})"
        ax.text(sx + 1.0, sy + 0.22, lbl, fontsize=8, fontweight="bold", color=tc, ha="center", va="center")

    ax.add_patch(FancyBboxPatch((7.3, 1.0), 2.7, 0.5, boxstyle="round,pad=0.04", fc=C_PRIMARY, ec="none"))
    ax.text(8.65, 1.25, "Confirmar Reserva ->", color="white", fontsize=9, fontweight="bold", ha="center", va="center")

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "06_mockup_reserva_online.png"), dpi=180)
    plt.close()

    # Mockup 2: Agenda Secretaría (Modificar / Cancelar)
    fig, ax = plt.subplots(figsize=(11, 6.8), dpi=180)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis("off")
    fig.patch.set_facecolor("#F1F5F9")

    ax.add_patch(FancyBboxPatch((0.3, 0.3), 10.4, 6.4, boxstyle="round,pad=0.05", fc="white", ec="#94A3B8", lw=1.5))
    ax.add_patch(FancyBboxPatch((0.3, 6.1), 10.4, 0.6, boxstyle="round,pad=0.02", fc=C_PRIMARY, ec=C_PRIMARY))
    ax.text(0.7, 6.4, "Panel de Secretaría — Agenda Diaria y Gestión de Citas", color="white", fontsize=11, fontweight="bold", va="center")

    # Filtros
    ax.add_patch(FancyBboxPatch((0.6, 5.25), 2.5, 0.45, boxstyle="round,pad=0.03", fc="#F8FAFC", ec="#94A3B8"))
    ax.text(0.75, 5.47, "Fecha: 18-11-2026", fontsize=8.5, va="center")
    ax.add_patch(FancyBboxPatch((3.3, 5.25), 3.1, 0.45, boxstyle="round,pad=0.03", fc="#F8FAFC", ec="#94A3B8"))
    ax.text(3.45, 5.47, "Odontólogo: Todos", fontsize=8.5, va="center")
    ax.add_patch(FancyBboxPatch((6.6, 5.25), 2.1, 0.45, boxstyle="round,pad=0.03", fc="#F8FAFC", ec="#94A3B8"))
    ax.text(6.75, 5.47, "Buscar RUT...", fontsize=8.5, color="#64748B", va="center")
    ax.add_patch(FancyBboxPatch((8.9, 5.25), 1.5, 0.45, boxstyle="round,pad=0.03", fc=C_TEAL, ec="none"))
    ax.text(9.65, 5.47, "+ Nueva Cita", fontsize=8.5, fontweight="bold", color="white", ha="center", va="center")

    # Tabla agenda
    headers = ["Hora", "Paciente (RUT)", "Odontólogo", "Estado", "Acciones Rápidas"]
    xs = [0.6, 1.5, 4.1, 6.3, 7.9]
    ax.add_patch(FancyBboxPatch((0.6, 4.55), 9.8, 0.45, boxstyle="round,pad=0.02", fc="#E2E8F0", ec="none"))
    for x, h in zip(xs, headers):
        ax.text(x + 0.1, 4.77, h, fontsize=8.5, fontweight="bold", color="#1E293B", va="center")

    rows = [
        ("09:00", "Juan Pérez (15.432.110-4)", "Dra. V. Muñoz", "Confirmada", C_GREEN_BG, C_GREEN),
        ("09:30", "Ana Soto (18.221.903-K)", "Dr. R. Torres", "Pendiente", C_YELLOW_BG, C_YELLOW),
        ("10:00", "María González (19.876.543-2)", "Dra. V. Muñoz", "Pendiente", C_YELLOW_BG, C_YELLOW),
        ("10:30", "Carlos Díaz (12.345.678-9)", "Dra. V. Muñoz", "Cancelada", C_RED_BG, C_RED),
        ("11:00", "Lucía Vera (20.112.334-5)", "Dr. R. Torres", "Atendida", "#DBEAFE", C_PRIMARY),
    ]
    for idx, (hr, pac, od, est, ebg, efg) in enumerate(rows):
        ry = 3.85 - idx * 0.68
        ax.add_patch(FancyBboxPatch((0.6, ry), 9.8, 0.55, boxstyle="round,pad=0.02", fc="white", ec="#E2E8F0"))
        ax.text(0.7, ry + 0.27, hr, fontsize=8.5, fontweight="bold", va="center")
        ax.text(1.6, ry + 0.27, pac, fontsize=8.3, va="center")
        ax.text(4.2, ry + 0.27, od, fontsize=8.3, va="center")
        ax.add_patch(FancyBboxPatch((6.35, ry + 0.1), 1.3, 0.34, boxstyle="round,pad=0.02", fc=ebg, ec=efg))
        ax.text(7.0, ry + 0.27, est, fontsize=7.8, fontweight="bold", color=efg, ha="center", va="center")
        if est not in ("Cancelada", "Atendida"):
            ax.add_patch(FancyBboxPatch((7.95, ry + 0.1), 1.15, 0.34, boxstyle="round,pad=0.02", fc=C_SEC, ec="none"))
            ax.text(8.52, ry + 0.27, "Reprogramar", fontsize=7.5, fontweight="bold", color="white", ha="center", va="center")
            ax.add_patch(FancyBboxPatch((9.2, ry + 0.1), 1.0, 0.34, boxstyle="round,pad=0.02", fc=C_RED, ec="none"))
            ax.text(9.7, ry + 0.27, "Cancelar", fontsize=7.5, fontweight="bold", color="white", ha="center", va="center")

    ax.text(0.6, 0.55, "Nota de seguridad (RNF02): La secretaria visualiza únicamente datos de agendamiento; la ficha clínica está oculta.",
            fontsize=8, style="italic", color="#475569")

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "07_mockup_agenda_secretaria.png"), dpi=180)
    plt.close()

    # Mockup 3: Ficha Clínica Confidencial (Solo Odontólogo)
    fig, ax = plt.subplots(figsize=(11, 6.8), dpi=180)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis("off")
    fig.patch.set_facecolor("#F1F5F9")

    ax.add_patch(FancyBboxPatch((0.3, 0.3), 10.4, 6.4, boxstyle="round,pad=0.05", fc="white", ec="#9D174D", lw=1.5))
    ax.add_patch(FancyBboxPatch((0.3, 6.1), 10.4, 0.6, boxstyle="round,pad=0.02", fc="#831843", ec="#831843"))
    ax.text(0.7, 6.4, "Ficha Clínica Odontológica Confidencial — Acceso Exclusivo Odontólogo", color="white", fontsize=11, fontweight="bold", va="center")
    ax.text(10.3, 6.4, "AES-256 | Auditado", color="#FBCFE8", fontsize=8.5, ha="right", va="center")

    ax.add_patch(FancyBboxPatch((0.6, 5.25), 9.8, 0.55, boxstyle="round,pad=0.03", fc="#FDF2F8", ec="#F9A8D4"))
    ax.text(0.8, 5.52, "Paciente: Juan Pérez (15.432.110-4) | Edad: 34 años | Previsión: Fonasa | Alergias: Penicilina",
            fontsize=9, fontweight="bold", color="#831843", va="center")

    ax.add_patch(FancyBboxPatch((0.6, 1.0), 4.6, 4.0, boxstyle="round,pad=0.05", fc="#F8FAFC", ec="#CBD5E1"))
    ax.text(0.85, 4.7, "Historial de Evoluciones", fontsize=9.5, fontweight="bold", color=C_PRIMARY)
    ax.text(0.85, 4.15, "• 10-09-2026 | Pieza 1.6 | Caries oclusal -> Resina compuesta", fontsize=8, color="#1E293B")
    ax.text(0.85, 3.65, "• 15-05-2026 | General   | Destartraje supragingival", fontsize=8, color="#1E293B")

    ax.add_patch(FancyBboxPatch((5.5, 1.0), 4.9, 4.0, boxstyle="round,pad=0.05", fc="#F8FAFC", ec="#CBD5E1"))
    ax.text(5.75, 4.7, "Nueva Evolución (Cita 18-11-2026)", fontsize=9.5, fontweight="bold", color=C_PRIMARY)
    for idx, (lbl, val) in enumerate([("Pieza dental:", "2.4"), ("Diagnóstico (cifrado):", "Pulpitis reversible"),
                                      ("Tratamiento:", "Protección pulpar + restauración")]):
        yy = 4.15 - idx * 0.85
        ax.text(5.75, yy, lbl, fontsize=8, fontweight="bold", color="#334155")
        ax.add_patch(FancyBboxPatch((5.75, yy - 0.42), 4.4, 0.34, boxstyle="round,pad=0.03", fc="white", ec="#94A3B8"))
        ax.text(5.9, yy - 0.25, val, fontsize=8, va="center")

    ax.add_patch(FancyBboxPatch((7.6, 1.15), 2.5, 0.45, boxstyle="round,pad=0.04", fc="#831843", ec="none"))
    ax.text(8.85, 1.37, "Guardar y Cerrar Cita", color="white", fontsize=8.5, fontweight="bold", ha="center", va="center")

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "08_mockup_ficha_clinica.png"), dpi=180)
    plt.close()


def gen_kanban_board():
    """Genera la vista visual del tablero Kanban con límites WIP (09_tablero_kanban.png)."""
    fig, ax = plt.subplots(figsize=(15, 7.5), dpi=180)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 7.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(7.5, 7.15, "Tablero Kanban — Proyecto «Sonrisa Sana» (Período 19-10-2026 al 17-11-2026)",
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_PRIMARY)

    cols = [
        ("Product Backlog", "Sin límite WIP", "#E2E8F0", [
            ("HU13: Reporte ocupación", "Could | 5 SP | F. Durán", C_GREEN_BG, C_GREEN),
            ("HU09: Confirmar por link", "Should | 3 SP | C. Figueroa", C_YELLOW_BG, C_YELLOW),
        ]),
        ("Por Hacer (Sprint)", "Límite: ~19 SP", "#DBEAFE", [
            ("HU08: Recordatorios auto", "Must | 5 SP | C. Figueroa", C_RED_BG, C_RED),
            ("HU10: Ficha confidencial", "Must | 8 SP | F. Durán", C_RED_BG, C_RED),
            ("HU11: Auditoría accesos", "Should | 3 SP | F. Lara", C_YELLOW_BG, C_YELLOW),
        ]),
        ("En Progreso", "WIP Máx: 2 / persona", "#FEF3C7", [
            ("HU06: Modificar citas", "Must | 5 SP | C. Figueroa", C_RED_BG, C_RED),
            ("HU07: Cancelar citas", "Must | 3 SP | F. Lara", C_RED_BG, C_RED),
            ("T12: Modelo BD + SQL", "Alta | F. Durán", C_RED_BG, C_RED),
        ]),
        ("En Revisión / QA", "WIP Máx: 3 tarjetas", "#EDE9FE", [
            ("HU03: Reserva online", "Must | 8 SP | C. Figueroa", C_RED_BG, C_RED),
            ("HU05: Agenda diaria", "Must | 5 SP | F. Lara", C_RED_BG, C_RED),
        ]),
        ("Terminado", "Aceptado por PO", "#DCFCE7", [
            ("TEC01: Arquitectura base", "Must | 3 SP | F. Durán", C_RED_BG, C_RED),
            ("HU01/02: Pacientes", "Must | 6 SP | F. Lara", C_RED_BG, C_RED),
            ("HU04/12: Roles y Horarios", "Must | 8 SP | F. Durán", C_RED_BG, C_RED),
        ]),
    ]

    for idx, (title, wip, bg, cards) in enumerate(cols):
        cx = 0.3 + idx * 2.92
        ax.add_patch(FancyBboxPatch((cx, 0.4), 2.72, 6.3, boxstyle="round,pad=0.05", fc=bg, ec="#94A3B8", lw=1.2))
        ax.text(cx + 1.36, 6.42, title, ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0F172A")
        ax.text(cx + 1.36, 6.12, wip, ha="center", va="center", fontsize=7.5, style="italic", color="#475569")
        for cidx, (ctitle, cmeta, cbg, cedge) in enumerate(cards):
            cy = 5.0 - cidx * 1.35
            ax.add_patch(FancyBboxPatch((cx + 0.12, cy), 2.48, 1.1, boxstyle="round,pad=0.04", fc="white", ec=cedge, lw=1.5))
            ax.add_patch(FancyBboxPatch((cx + 0.18, cy + 0.72), 0.9, 0.25, boxstyle="round,pad=0.02", fc=cbg, ec="none"))
            ax.text(cx + 0.63, cy + 0.84, cmeta.split("|")[0].strip(), ha="center", va="center", fontsize=7, fontweight="bold", color=cedge)
            ax.text(cx + 0.2, cy + 0.45, ctitle, ha="left", va="center", fontsize=8, fontweight="bold", color="#0F172A")
            ax.text(cx + 0.2, cy + 0.18, "|".join(cmeta.split("|")[1:]).strip(), ha="left", va="center", fontsize=7.2, color="#475569")

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "09_tablero_kanban.png"), dpi=180)
    plt.close()


if __name__ == "__main__":
    gen_use_case_diagram()
    gen_er_diagram()
    gen_flow_diagrams()
    gen_mockups()
    gen_kanban_board()
    print("Diagramas generados exitosamente en:", OUT_DIR)
