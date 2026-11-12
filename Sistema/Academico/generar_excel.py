"""Generador del libro Excel completo para el proyecto Clínica Odontológica 'Sonrisa Sana'."""

import os
import datetime as dt
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIAG_DIR = os.path.join(BASE_DIR, "diagramas")
OUT_XLSX = os.path.join(BASE_DIR, "Sonrisa_Sana_Proyecto.xlsx")

# Estilos
FONT_TITLE = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
FONT_SUBTITLE = Font(name="Calibri", size=10, italic=True, color="334155")
FONT_SEC = Font(name="Calibri", size=11, bold=True, color="0F4C81")
FONT_HDR = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
FONT_BODY = Font(name="Calibri", size=10, color="0F172A")
FONT_BOLD = Font(name="Calibri", size=10, bold=True, color="0F172A")
FONT_INPUT = Font(name="Calibri", size=10, color="0000FF")

FILL_PRIMARY = PatternFill("solid", fgColor="0F4C81")
FILL_HDR = PatternFill("solid", fgColor="1E3A8A")
FILL_SEC = PatternFill("solid", fgColor="DBEAFE")
FILL_ZEBRA = PatternFill("solid", fgColor="F8FAFC")
FILL_GANTT = PatternFill("solid", fgColor="00897B")
FILL_HITO = PatternFill("solid", fgColor="EA580C")

THIN = Side(border_style="thin", color="CBD5E1")
BORDER_CELL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

ALIGN_WRAP = Alignment(wrap_text=True, vertical="top", horizontal="left")
ALIGN_CENTER = Alignment(wrap_text=True, vertical="center", horizontal="center")


def style_title(ws, title, subtitle, max_col=6):
    """Aplica título y subtítulo combinados con estilo corporativo a la hoja."""
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_col)
    c1 = ws.cell(1, 1, title)
    c1.font = FONT_TITLE
    c1.fill = FILL_PRIMARY
    c1.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    ws.row_dimensions[1].height = 28

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max_col)
    c2 = ws.cell(2, 1, subtitle)
    c2.font = FONT_SUBTITLE
    c2.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    ws.row_dimensions[2].height = 20


def write_table(ws, start_row, headers, rows, widths=None, input_cols=None):
    """Escribe una tabla formateada con encabezados, zebra striping, bordes y anchos."""
    input_cols = input_cols or set()
    for c_idx, h in enumerate(headers, 1):
        cell = ws.cell(start_row, c_idx, h)
        cell.font = FONT_HDR
        cell.fill = FILL_HDR
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_CELL
    ws.row_dimensions[start_row].height = 24

    for r_offset, row in enumerate(rows, 1):
        r_num = start_row + r_offset
        fill = FILL_ZEBRA if r_offset % 2 == 0 else PatternFill(fill_type=None)
        for c_idx, val in enumerate(row, 1):
            cell = ws.cell(r_num, c_idx, val)
            cell.font = FONT_INPUT if c_idx in input_cols else FONT_BODY
            if fill.fill_type:
                cell.fill = fill
            cell.alignment = ALIGN_WRAP
            cell.border = BORDER_CELL
        ws.row_dimensions[r_num].height = 22

    if widths:
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w
    return start_row + len(rows)


def embed_image(ws, img_name, anchor, width_px=820):
    """Inserta una imagen PNG de la carpeta diagramas/ escalada proporcionalmente."""
    path = os.path.join(DIAG_DIR, img_name)
    if os.path.exists(path):
        img = XLImage(path)
        ratio = width_px / img.width
        img.width = width_px
        img.height = int(img.height * ratio)
        ws.add_image(img, anchor)


def build_workbook():
    """Construye y guarda el libro Excel completo con sus 17 hojas, fórmulas y diagramas."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # 1. ÍNDICE
    ws = wb.create_sheet("Índice")
    style_title(ws, 'Caso Aplicado: Clínica Odontológica "Sonrisa Sana"',
                "Modelamiento de Soluciones Informáticas · INACAP · Sección 114-2-F2 · Docente: Yaleni Gómez Peña", 4)
    ws.cell(4, 1, "Problemática").font = FONT_SEC
    ws.merge_cells("A5:D5")
    ws.cell(5, 1, ('La Clínica Odontológica "Sonrisa Sana" utiliza actualmente un cuaderno físico para agendar horas, '
                   'lo que genera choques de horarios, pérdida de tiempo y errores de registro. Se requiere un sistema web '
                   'para que los pacientes reserven horas online y reciban recordatorios automáticos, las secretarias puedan '
                   'cancelar o modificar citas fácilmente, con tiempos de respuesta muy rápidos y estricta confidencialidad '
                   'de los datos médicos.')).alignment = ALIGN_WRAP
    ws.row_dimensions[5].height = 48

    idx_rows = [
        ["Acta Proyecto", "Acta de Definición del Proyecto: identificación, objetivos, alcance, restricciones, riesgos e hitos.", "1.1.1 · 1.1.6", "Acta de Definición"],
        ["Roles SCRUM", "Stakeholders, roles del equipo (Fernando Durán, Francisco Lara, Christopher Figueroa), eventos y RACI.", "1.1.6", "Roles y matriz RACI"],
        ["Req Funcionales", "16 requerimientos funcionales (13 trazados a HU + 3 Won't fuera de alcance), priorizados con MoSCoW.", "1.1.1 · 1.1.2", "Levantamiento RF"],
        ["Req No Funcionales", "13 requerimientos no funcionales (ISO/IEC 25010) con métrica verificable (rendimiento y confidencialidad).", "1.1.1 · 1.1.2", "Levantamiento RNF"],
        ["Resumen MoSCoW", "Conteo y porcentaje automático por prioridad mediante fórmulas COUNTIF.", "1.1.2", "Análisis MoSCoW"],
        ["Historias Usuario", "13 historias de usuario priorizadas en formato Rol / Característica / Razón / Condiciones.", "1.1.2", "Product Backlog"],
        ["Product Backlog", "Backlog priorizado por MoSCoW y dependencias, asignado a 2 sprints de ejecución.", "1.1.2 · 1.1.6", "Product Backlog"],
        ["Tareas", "Tareas del proyecto (19-10-2026 al 17-11-2026) con esfuerzo, dependencias y fechas hábiles.", "1.1.6", "Planificación"],
        ["Carta Gantt", "Carta Gantt semanal (5 semanas hasta el 17-11-2026) vinculada a la hoja Tareas.", "1.1.6", "Carta Gantt"],
        ["Espacio Colaborativo", "Tablero Kanban con límites WIP, Trello/Jira, Drive y GitHub.", "1.1.6", "Tablero Kanban"],
        ["Casos de Uso", "Catálogo de 14 casos de uso trazados a RF/HU y Diagrama de Casos de Uso General.", "1.1.3", "Diagrama CU"],
        ["Especificación CU", "Especificación detallada de los 6 casos de uso principales (flujo básico y alternativo).", "1.1.3", "Especificación CU"],
        ["Modelo BD", "Modelo Lógico, Relacional y Físico (12 tablas 3FN), reglas de negocio y Diagrama ER.", "1.1.4", "Modelo BD"],
        ["Diccionario Datos", "Diccionario de datos completo de las 12 tablas (tipo, nulo, PK/FK/UQ, descripción).", "1.1.4", "Diccionario Datos"],
        ["Diagramas Flujo", "3 diagramas de flujo TO-BE: reserva online, gestión secretaría, atención confidencial y recordatorios.", "1.1.5", "Diagramas Flujo"],
        ["Mockups UI", "Wireframes y mockups de interfaz de usuario alineados a los casos de uso.", "1.1.3", "Mockups UI"],
    ]
    write_table(ws, 7, ["Hoja", "Contenido", "Criterio Evaluación", "Entregable"], idx_rows, [22, 65, 20, 24])

    # 2. ACTA PROYECTO
    ws = wb.create_sheet("Acta Proyecto")
    style_title(ws, "Acta de Definición del Proyecto — SAG Sonrisa Sana",
                "Documento formal de inicio, alcance, condiciones, riesgos e hitos hasta la entrega (17-11-2026)", 2)
    acta_rows = [
        ["Nombre del proyecto", 'Sistema de Agendamiento y Gestión Clínica "Sonrisa Sana" (SAG-SonrisaSana)'],
        ["Cliente / Patrocinador", 'Dirección Médica y Administración — Clínica Odontológica "Sonrisa Sana"'],
        ["Scrum Master / Líder BD", "Fernando A. Durán Leiva"],
        ["Analista Funcional / UX", "Francisco A. Lara Yévenes"],
        ["Desarrollador Full-Stack / QA", "Christopher D. Figueroa Arthur"],
        ["Docente guía", "Yaleni Gómez Peña (INACAP — Asignatura Modelamiento de Soluciones Informáticas, Sec. 114-2-F2)"],
        ["Período del proyecto", "19-10-2026 al 17-11-2026 (5 semanas hasta fecha de entrega oficial)"],
        ["Metodología", "SCRUM + Tablero Kanban (Sprint 0 de análisis/modelado + 2 Sprints + Cierre)"],
        ["Situación actual", "Agendamiento manual en cuaderno físico: choques horarios, pérdida de tiempo y nula trazabilidad."],
        ["Objetivo general", "Desarrollar un sistema web rápido, seguro y confidencial que permita a los pacientes reservar horas online con recordatorios automáticos y a las secretarias gestionar/modificar/cancelar citas sin conflictos."],
        ["Objetivos específicos", "OE1: Eliminar choques horarios mediante validación automática y restricción única en BD.\nOE2: Habilitar reserva online en ≤ 3 pasos para pacientes.\nOE3: Facilitar modificación y cancelación de citas por secretaría en ≤ 2 clics.\nOE4: Automatizar envío de recordatorios (correo/WhatsApp) 24h antes.\nOE5: Proteger confidencialidad médica con RBAC estricto y cifrado AES-256."],
        ["Dentro del alcance", "Gestión de usuarios/roles, pacientes, reserva online, agenda secretaría (modificar/cancelar), horarios odontólogos, recordatorios automáticos, ficha clínica cifrada exclusiva para odontólogos y auditoría."],
        ["Fuera del alcance", "Facturación electrónica SII/Fonasa/Isapre, odontograma 3D avanzado, aplicación móvil nativa."],
        ["Restricciones", "Entrega final: 17-11-2026. Cumplimiento Ley 19.628, Ley 21.719 (Datos Personales) y Ley 20.584 (Derechos del Paciente)."],
        ["Hitos clave", "H1 (23-10-2026): Levantamiento RF/RNF e Historias de Usuario.\nH2 (30-10-2026): Casos de uso, Modelo BD, Diagramas de flujo y Mockups.\nH3 (06-11-2026): Incremento 1 (Usuarios, Pacientes, Reserva Online).\nH4 (13-11-2026): Incremento 2 (Secretaría, Recordatorios, Ficha Confidencial).\nH5 (17-11-2026): Entrega final del Informe UML, Excel y prototipo validado."],
    ]
    write_table(ws, 4, ["Sección / Campo", "Detalle"], acta_rows, [28, 95])

    # 3. ROLES SCRUM
    ws = wb.create_sheet("Roles SCRUM")
    style_title(ws, "Roles, Funciones e Involucrados del Proyecto",
                "Equipo de proyecto, stakeholders externos, eventos SCRUM y matriz RACI", 6)
    roles_rows = [
        ["Product Owner (PO)", "Dirección Clínica Sonrisa Sana", "Define visión, prioriza Product Backlog (MoSCoW) y valida entregables.", "Planning, Review", "Product Backlog", "2 h/sem"],
        ["Scrum Master / Líder BD", "Fernando A. Durán Leiva", "Facilita SCRUM/Kanban, diseña Modelo BD (Lógico/Relacional/Físico) y script SQL, controla plazos.", "Todos los eventos", "Carta Gantt, Kanban, BD", "10 h/sem"],
        ["Analista Funcional / UX", "Francisco A. Lara Yévenes", "Levantamiento RF/RNF, Historias de Usuario, Casos de Uso, Diagramas de Flujo y Mockups.", "Planning, Daily, Review", "RF/RNF, HU, UML, Mockups", "10 h/sem"],
        ["Dev Full-Stack / QA", "Christopher D. Figueroa Arthur", "Implementación de seguridad RBAC/cifrado, pruebas funcionales/rendimiento y documentación.", "Planning, Daily, Review", "Pruebas QA, Informe Final", "10 h/sem"],
        ["Usuarios Clave", "Secretarias / Odontólogos / Pacientes", "Validan usabilidad de reserva online, agenda rápida y confidencialidad clínica.", "Entrevistas, UAT", "Actas de validación", "Según cita"],
        ["Sponsor Académico", "Docente Yaleni Gómez Peña", "Evalúa informe de requerimiento y modelado UML según pauta (60 pts).", "Entrega 17-11-2026", "Evaluación Sumativa", "Hito final"],
    ]
    write_table(ws, 4, ["Rol", "Asignado a", "Funciones / Responsabilidades", "Eventos", "Artefactos a cargo", "Dedicación"], roles_rows, [24, 28, 48, 20, 24, 14])

    # 4. REQ FUNCIONALES
    ws = wb.create_sheet("Req Funcionales")
    style_title(ws, "Requerimientos Funcionales (RF) — Priorizados con MoSCoW",
                "Levantamiento trazado a Historias de Usuario (HU) para Clínica Odontológica Sonrisa Sana", 6)
    rf_rows = [
        ["RF01", "Pacientes / Acceso", "Registro y autenticación de pacientes para reserva online (RUT/correo único, clave cifrada).", "Must", "Habilita el autoservicio de reserva online.", "HU01"],
        ["RF02", "Pacientes / Recepción", "Gestión de pacientes por secretaría: alta presencial, búsqueda por RUT/nombre y actualización.", "Must", "Soporta pacientes que llaman o acuden presencialmente.", "HU02"],
        ["RF03", "Reserva Online", "Reserva de hora online por especialidad/odontólogo/fecha, validando que no existan choques.", "Must", "Resuelve el problema central del cuaderno físico.", "HU03"],
        ["RF04", "Agenda Médica", "Configuración de horarios de atención y bloqueos excepcionales por odontólogo.", "Must", "Define la oferta de bloques disponibles.", "HU04"],
        ["RF05", "Agenda Clínica", "Visualización de agenda diaria/semanal filtrable por odontólogo y estado con colores.", "Must", "Reemplaza la vista del cuaderno diario.", "HU05"],
        ["RF06", "Gestión Secretaría", "Modificación/reprogramación fácil de citas por secretaría validando disponibilidad.", "Must", "Requisito explícito del cliente para secretarias.", "HU06"],
        ["RF07", "Gestión Secretaría", "Cancelación fácil de citas (por secretaría o paciente) liberando inmediatamente el bloque.", "Must", "Evita horas perdidas y permite reasignar bloques.", "HU07"],
        ["RF08", "Recordatorios", "Envío automático de recordatorios de cita (correo/WhatsApp) 24h antes sin duplicados.", "Must", "Requisito explícito para reducir inasistencias.", "HU08"],
        ["RF09", "Recordatorios", "Confirmación o anulación directa de cita mediante enlace único en el recordatorio.", "Should", "Agiliza la confirmación sin intervención de secretaría.", "HU09"],
        ["RF10", "Ficha Clínica", "Consulta y registro de ficha clínica (antecedentes, alergias, evolución) solo para Odontólogo.", "Must", "Protege estrictamente la confidencialidad médica.", "HU10"],
        ["RF11", "Seguridad", "Registro de auditoría de accesos a fichas médicas y cambios críticos en citas.", "Should", "Trazabilidad ante accesos indebidos.", "HU11"],
        ["RF12", "Administración", "Gestión de usuarios y asignación de roles (Admin, Odontólogo, Secretaria, Paciente).", "Must", "Base del control de acceso RBAC.", "HU12"],
        ["RF13", "Reportes", "Reporte de ocupación de agenda, asistencia y cancelaciones por rango de fechas.", "Could", "Apoya decisiones de gestión clínica.", "HU13"],
        ["RF14", "Fuera de alcance", "Integración de facturación electrónica SII, Fonasa e Isapre.", "Won't", "Complejidad y costo fuera del alcance v1.", "—"],
        ["RF15", "Fuera de alcance", "Odontograma gráfico 3D avanzado.", "Won't", "No requerido en esta primera etapa.", "—"],
        ["RF16", "Fuera de alcance", "Aplicación móvil nativa (Android / iOS).", "Won't", "Cubierto por diseño web responsive.", "—"],
    ]
    write_table(ws, 4, ["ID", "Módulo", "Requerimiento Funcional", "Prioridad MoSCoW", "Justificación", "HU"], rf_rows, [10, 20, 56, 16, 40, 10])

    # 5. REQ NO FUNCIONALES
    ws = wb.create_sheet("Req No Funcionales")
    style_title(ws, "Requerimientos No Funcionales (RNF) — ISO/IEC 25010",
                "Enfoque en tiempos de respuesta muy rápidos y estricta confidencialidad de datos médicos", 6)
    rnf_rows = [
        ["RNF01", "Seguridad", "Contraseñas cifradas con bcrypt (cost >= 12) y tráfico bajo HTTPS (TLS 1.3).", "Revisión de BD sin texto plano y certificado SSL válido.", "Must", "Protege credenciales de acceso."],
        ["RNF02", "Confidencialidad", "RBAC estricto y cifrado AES-256 para antecedentes, alergias y diagnósticos médicos.", "Secretaria/Admin reciben HTTP 403 al intentar ver ficha.", "Must", "Exigencia crítica de confidencialidad médica."],
        ["RNF03", "Legal / Privacidad", "Cumplimiento Ley N° 19.628, Ley N° 21.719 y Ley N° 20.584 de derechos del paciente.", "Registro explícito de consentimiento al crear cuenta.", "Must", "Marco legal vigente en Chile."],
        ["RNF04", "Eficiencia", "Tiempo de respuesta P95 < 1.5s en consulta de bloques y < 2s al reservar/modificar.", "Prueba de carga con 50 usuarios concurrentes.", "Must", "Exigencia de tiempos de respuesta muy rápidos."],
        ["RNF05", "Usabilidad", "Reserva online en máximo 3 pasos; modificación/cancelación por secretaría en ≤ 2 clics.", "Prueba cronometrada con usuarios reales.", "Must", "Adopción rápida frente al cuaderno."],
        ["RNF06", "Integridad", "Prevención absoluta de doble reserva mediante restricción UNIQUE (bloque_activo) y transacciones.", "Prueba de concurrencia simultánea sobre mismo bloque.", "Must", "Elimina choques de horario."],
        ["RNF07", "Fiabilidad", "Proceso automático de recordatorios ejecutado cada 15 min sin intervención manual.", "Logs de ejecución continua del scheduler.", "Must", "Garantiza recordatorios oportunos."],
        ["RNF08", "Fiabilidad", "Respaldo automático diario cifrado de la BD con retención de 30 días.", "Prueba mensual de restauración exitosa.", "Must", "Evita pérdida de agenda e historial."],
        ["RNF09", "Disponibilidad", "Disponibilidad 99.5% en horario clínico y 99% para reservas online 24/7.", "Monitoreo de uptime mensual.", "Should", "Continuidad operativa."],
        ["RNF10", "Compatibilidad", "Web responsive compatible con Chrome, Edge, Firefox y Safari (PC, tablet, móvil).", "Pruebas en 3 navegadores y 3 resoluciones.", "Must", "Uso de pacientes desde celular."],
        ["RNF11", "Mantenibilidad", "Arquitectura en capas (MVC/REST) y control de versiones en Git (main/develop).", "Repositorio documentado con README.", "Should", "Facilita evolución futura."],
        ["RNF12", "Localización", "Español de Chile, fechas dd-mm-aaaa, validación RUT módulo 11, zona America/Santiago.", "Revisión de formularios y alertas.", "Must", "Contexto nacional."],
        ["RNF13", "Fiabilidad", "Operación offline sin conexión a internet.", "—", "Won't", "La clínica dispone de internet estable."],
    ]
    write_table(ws, 4, ["ID", "Categoría ISO 25010", "Requerimiento No Funcional", "Métrica / Criterio de Verificación", "Prioridad MoSCoW", "Justificación"], rnf_rows, [10, 20, 50, 40, 16, 32])

    # 6. RESUMEN MOSCOW (con fórmulas dinámicas)
    ws = wb.create_sheet("Resumen MoSCoW")
    style_title(ws, "Resumen de Priorización MoSCoW (Calculado con Fórmulas)",
                "Conteo automático desde Req Funcionales y Req No Funcionales", 6)
    moscow_headers = ["Prioridad", "RF (cantidad)", "RNF (cantidad)", "Total", "% del total", "Significado"]
    for c_idx, h in enumerate(moscow_headers, 1):
        cell = ws.cell(4, c_idx, h)
        cell.font = FONT_HDR
        cell.fill = FILL_HDR
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_CELL
    prioridades = [
        ("Must", "Imprescindible para salir a producción (MVP)."),
        ("Should", "Importante, se incluye dentro del alcance si el plazo lo permite."),
        ("Could", "Deseable, aporta valor de gestión pero no bloquea la operación."),
        ("Won't", "Fuera de esta versión (acordado con la clínica)."),
    ]
    for i, (prio, desc) in enumerate(prioridades, 5):
        ws.cell(i, 1, prio).font = FONT_BOLD
        ws.cell(i, 2, f'=COUNTIF(\'Req Funcionales\'!$D$5:$D$20, A{i})')
        ws.cell(i, 3, f'=COUNTIF(\'Req No Funcionales\'!$E$5:$E$17, A{i})')
        ws.cell(i, 4, f'=B{i}+C{i}')
        ws.cell(i, 5, f'=D{i}/$D$9')
        ws.cell(i, 5).number_format = "0.0%"
        ws.cell(i, 6, desc)
        for c in range(1, 7):
            ws.cell(i, c).border = BORDER_CELL
            ws.cell(i, c).alignment = ALIGN_CENTER if c in (2, 3, 4, 5) else ALIGN_WRAP
    ws.cell(9, 1, "Total").font = FONT_BOLD
    ws.cell(9, 2, "=SUM(B5:B8)").font = FONT_BOLD
    ws.cell(9, 3, "=SUM(C5:C8)").font = FONT_BOLD
    ws.cell(9, 4, "=SUM(D5:D8)").font = FONT_BOLD
    ws.cell(9, 5, "=SUM(E5:E8)").font = FONT_BOLD
    ws.cell(9, 5).number_format = "0.0%"
    ws.cell(9, 6, "Total de requerimientos levantados (RF + RNF)")
    for c in range(1, 7):
        ws.cell(9, c).border = BORDER_CELL
        ws.cell(9, c).fill = FILL_SEC
    for idx, w in enumerate([16, 16, 16, 14, 14, 52], 1):
        ws.column_dimensions[get_column_letter(idx)].width = w

    # 7. HISTORIAS USUARIO
    ws = wb.create_sheet("Historias Usuario")
    style_title(ws, 'Historias de Usuario Priorizadas — Clínica Odontológica "Sonrisa Sana"',
                "Formato: Rol / Característica / Razón / Condiciones de aceptación + Story Points (Fibonacci)", 9)
    hu_rows = [
        ["HU01", "Como paciente", "Necesito registrarme e iniciar sesión con RUT y correo", "Para reservar horas online de forma segura", "• Validar RUT módulo 11 y correo único.\n• Contraseña cifrada con bcrypt.\n• Consentimiento de datos (Ley 19.628).", "RF01", "Must", 3, "E1 Acceso y Pacientes"],
        ["HU02", "Como secretaria", "Necesito registrar y buscar pacientes por RUT o nombre", "Para atender solicitudes telefónicas o presenciales", "• Alta rápida con RUT, nombre, teléfono y previsión.\n• Búsqueda instantánea (< 1s).", "RF02", "Must", 3, "E1 Acceso y Pacientes"],
        ["HU03", "Como paciente", "Necesito reservar una hora odontológica online", "Para agendar sin llamar ni esperar respuesta", "• Máximo 3 pasos.\n• Solo muestra bloques libres.\n• Impide choques horarios en BD.", "RF03", "Must", 8, "E2 Reserva y Agenda"],
        ["HU04", "Como administrador", "Necesito configurar horarios y bloqueos de odontólogos", "Para reflejar disponibilidad real en la web", "• Definir días, hora inicio/fin y duración.\n• Bloqueos por permisos o feriados.", "RF04", "Must", 5, "E2 Reserva y Agenda"],
        ["HU05", "Como secretaria", "Necesito ver la agenda diaria/semanal con estados por color", "Para controlar el flujo de atención sin cuaderno", "• Filtrar por odontólogo y fecha.\n• Colores distintos por estado.", "RF05", "Must", 5, "E2 Reserva y Agenda"],
        ["HU06", "Como secretaria", "Necesito modificar o reprogramar una cita fácilmente", "Para reubicar al paciente ante cambios de horario", "• Operación en ≤ 2 clics.\n• Valida disponibilidad del nuevo bloque.\n• Notifica al paciente.", "RF06", "Must", 5, "E2 Reserva y Agenda"],
        ["HU07", "Como secretaria", "Necesito cancelar una cita y liberar su bloque horario", "Para que otro paciente pueda tomar esa hora", "• Registra motivo de cancelación.\n• Libera bloque inmediatamente.\n• Omite recordatorios pendientes.", "RF07", "Must", 3, "E2 Reserva y Agenda"],
        ["HU08", "Como paciente", "Necesito recibir recordatorios automáticos antes de mi cita", "Para no olvidar mi hora odontológica", "• Envío automático 24h antes.\n• Canal correo/WhatsApp.\n• Sin duplicar envíos.", "RF08", "Must", 5, "E3 Recordatorios"],
        ["HU09", "Como paciente", "Necesito confirmar o anular mi cita desde el recordatorio", "Para avisar asistencia en un clic", "• Enlace con token único seguro.\n• Actualiza estado a confirmada o cancelada.", "RF09", "Should", 3, "E3 Recordatorios"],
        ["HU10", "Como odontólogo", "Necesito consultar y registrar la ficha clínica confidencial", "Para llevar el historial médico protegido del paciente", "• Acceso exclusivo rol Odontólogo (HTTP 403 a otros).\n• Datos médicos cifrados AES-256.\n• Cierra cita como atendida.", "RF10", "Must", 8, "E4 Ficha Confidencial"],
        ["HU11", "Como administrador", "Necesito auditar accesos a fichas médicas y cambios de citas", "Para garantizar trazabilidad y confidencialidad", "• Registra usuario, IP, acción y fecha/hora.\n• Incluye intentos denegados.", "RF11", "Should", 3, "E4 Ficha Confidencial"],
        ["HU12", "Como administrador", "Necesito gestionar usuarios y roles del sistema", "Para controlar quién accede a cada módulo", "• Roles: Admin, Odontólogo, Secretaria, Paciente.\n• Activar/desactivar cuentas.", "RF12", "Must", 5, "E1 Acceso y Pacientes"],
        ["HU13", "Como administrador", "Necesito ver reportes de ocupación y cancelaciones", "Para evaluar demanda y eficiencia de la clínica", "• Filtro por rango de fechas y odontólogo.\n• Solo rol Administrador.", "RF13", "Could", 5, "E5 Reportes"],
    ]
    write_table(ws, 4, ["ID", "Rol", "Característica / Funcionalidad", "Razón / Resultado", "Condiciones de Aceptación", "RF", "MoSCoW", "SP", "Épica"], hu_rows, [8, 18, 36, 30, 44, 8, 10, 6, 22])

    # 8. PRODUCT BACKLOG
    ws = wb.create_sheet("Product Backlog")
    style_title(ws, "Product Backlog Priorizado",
                "Ordenado por prioridad MoSCoW y dependencias técnicas (2 Sprints de ejecución hasta 17-11-2026)", 9)
    pb_rows = [
        [1, "TEC01", "Arquitectura base, repositorio Git y entorno HTTPS", "E0 Técnica", "Must", 3, "Sprint 1", "Terminado", "—"],
        [2, "TEC02", "Modelo físico BD (12 tablas, UNIQUE bloque_activo, cifrado)", "E0 Técnica", "Must", 5, "Sprint 1", "Terminado", "TEC01"],
        [3, "HU12", "Gestionar usuarios y roles (RBAC)", "E1 Acceso y Pacientes", "Must", 5, "Sprint 1", "Terminado", "TEC02"],
        [4, "HU01", "Registro y login de pacientes (RUT/bcrypt)", "E1 Acceso y Pacientes", "Must", 3, "Sprint 1", "Terminado", "HU12"],
        [5, "HU02", "Gestión de pacientes por secretaría", "E1 Acceso y Pacientes", "Must", 3, "Sprint 1", "Terminado", "HU12"],
        [6, "HU04", "Horarios y bloqueos de odontólogos", "E2 Reserva y Agenda", "Must", 5, "Sprint 1", "Terminado", "HU12"],
        [7, "HU03", "Reserva de hora online sin choques (<1.5s)", "E2 Reserva y Agenda", "Must", 8, "Sprint 2", "En Revisión", "HU01, HU04"],
        [8, "HU05", "Agenda diaria/semanal con estados por color", "E2 Reserva y Agenda", "Must", 5, "Sprint 2", "En Revisión", "HU03"],
        [9, "HU06", "Modificar/reprogramar citas fácilmente", "E2 Reserva y Agenda", "Must", 5, "Sprint 2", "En Progreso", "HU05"],
        [10, "HU07", "Cancelar citas y liberar bloque horario", "E2 Reserva y Agenda", "Must", 3, "Sprint 2", "En Progreso", "HU05"],
        [11, "HU08", "Recordatorios automáticos 24h antes", "E3 Recordatorios", "Must", 5, "Sprint 2", "Por Hacer", "HU03"],
        [12, "HU10", "Ficha clínica confidencial cifrada (solo Odontólogo)", "E4 Ficha Confidencial", "Must", 8, "Sprint 2", "Por Hacer", "HU02, HU12"],
        [13, "HU09", "Confirmar/anular desde enlace de recordatorio", "E3 Recordatorios", "Should", 3, "Backlog", "Pendiente", "HU08"],
        [14, "HU11", "Auditoría de accesos y modificaciones", "E4 Ficha Confidencial", "Should", 3, "Backlog", "Pendiente", "HU10"],
        [15, "HU13", "Reportes de ocupación y cancelaciones", "E5 Reportes", "Could", 5, "Backlog", "Pendiente", "HU05"],
    ]
    end_pb = write_table(ws, 4, ["Orden", "ID", "Ítem del Backlog", "Épica", "MoSCoW", "Story Points", "Sprint", "Estado", "Dependencia"], pb_rows, [8, 10, 44, 22, 10, 13, 12, 14, 16])

    cap_r = end_pb + 2
    ws.cell(cap_r, 1, "Capacidad por Sprint (Fórmulas)").font = FONT_SEC
    cap_headers = ["Sprint", "Story Points", "Capacidad", "Uso %", "Objetivo del Sprint"]
    for c_idx, h in enumerate(cap_headers, 1):
        c = ws.cell(cap_r + 1, c_idx, h)
        c.font, c.fill, c.alignment, c.border = FONT_HDR, FILL_HDR, ALIGN_CENTER, BORDER_CELL
    sprints_cap = [
        ("Sprint 1", 24, "Base técnica, BD 3FN, RBAC, pacientes y horarios de odontólogos."),
        ("Sprint 2", 34, "Reserva online, agenda secretaría (modificar/cancelar), recordatorios y ficha confidencial."),
        ("Backlog", 11, "Mejoras Should/Could para fase de cierre o evolución."),
    ]
    for idx, (sp_name, cap, obj) in enumerate(sprints_cap, cap_r + 2):
        ws.cell(idx, 1, sp_name).font = FONT_BOLD
        ws.cell(idx, 2, f'=SUMIF($G$5:$G${end_pb}, A{idx}, $F$5:$F${end_pb})')
        ws.cell(idx, 3, cap).font = FONT_INPUT
        ws.cell(idx, 4, f'=B{idx}/C{idx}')
        ws.cell(idx, 4).number_format = "0.0%"
        ws.cell(idx, 5, obj)
        for c in range(1, 6):
            ws.cell(idx, c).border = BORDER_CELL

    # 9. TAREAS
    ws = wb.create_sheet("Tareas")
    style_title(ws, "Tareas del Proyecto (19-10-2026 al 17-11-2026)",
                "Ordenadas por fase y dependencias. Texto azul = editable; Esfuerzo y Fin calculados con fórmulas.", 13)
    t_rows = [
        [1, "T01", "Inicio", "Reunión kick-off y levantamiento inicial Clínica Sonrisa Sana", "Fernando Durán + Equipo", "—", "Baja", 1, 3, "=I5*H5", dt.date(2026, 10, 19), 1, "=WORKDAY(K5,L5-1)"],
        [2, "T02", "Inicio", "Definir Acta de Proyecto, Roles SCRUM y Tablero Kanban", "Fernando Durán", "T01", "Baja", 1, 4, "=I6*H6", dt.date(2026, 10, 20), 1, "=WORKDAY(K6,L6-1)"],
        [3, "T03", "Análisis", "Levantamiento y análisis crítico RF/RNF + Matriz MoSCoW", "Francisco Lara", "T01", "Alta", 3, 8, "=I7*H7", dt.date(2026, 10, 21), 2, "=WORKDAY(K7,L7-1)"],
        [4, "T04", "Análisis", "Redacción de 13 Historias de Usuario y Product Backlog", "Francisco Lara", "T03", "Alta", 3, 8, "=I8*H8", dt.date(2026, 10, 23), 2, "=WORKDAY(K8,L8-1)"],
        [5, "T05", "Modelado", "Diagramas de Casos de Uso y Especificación detallada", "Francisco Lara", "T04", "Alta", 3, 10, "=I9*H9", dt.date(2026, 10, 26), 2, "=WORKDAY(K9,L9-1)"],
        [6, "T06", "Modelado", "Modelo BD (Lógico, Relacional, Físico SQL) y Diccionario", "Fernando Durán", "T04", "Alta", 3, 10, "=I10*H10", dt.date(2026, 10, 26), 3, "=WORKDAY(K10,L10-1)"],
        [7, "T07", "Modelado", "Diagramas de Flujo TO-BE y Wireframes / Mockups UI", "Francisco Lara", "T05", "Media", 2, 8, "=I11*H11", dt.date(2026, 10, 28), 3, "=WORKDAY(K11,L11-1)"],
        [8, "T08", "Sprint 1", "Arquitectura base, RBAC, usuarios, pacientes y horarios", "Fernando + Christopher", "T06", "Alta", 3, 24, "=I12*H12", dt.date(2026, 11, 2), 4, "=WORKDAY(K12,L12-1)"],
        [9, "T09", "Sprint 1", "Pruebas funcionales Sprint 1 (QA) y validación", "Christopher Figueroa", "T08", "Media", 2, 6, "=I13*H13", dt.date(2026, 11, 5), 2, "=WORKDAY(K13,L13-1)"],
        [10, "T10", "Sprint 2", "Reserva online, agenda secretaría, recordatorios y ficha AES-256", "Fernando + Christopher", "T09", "Alta", 3, 28, "=I14*H14", dt.date(2026, 11, 9), 4, "=WORKDAY(K14,L14-1)"],
        [11, "T11", "Sprint 2", "Pruebas de seguridad RBAC, rendimiento (<2s) y QA", "Christopher Figueroa", "T10", "Alta", 3, 8, "=I15*H15", dt.date(2026, 11, 12), 2, "=WORKDAY(K15,L15-1)"],
        [12, "T12", "Cierre", "Consolidación de Informe UML, Excel y revisión de pauta (60 pts)", "Todo el equipo", "T11", "Media", 2, 8, "=I16*H16", dt.date(2026, 11, 16), 1, "=WORKDAY(K16,L16-1)"],
        [13, "T13", "Cierre", "Entrega formal en Ambiente de Aprendizaje INACAP (Hito H5)", "Todo el equipo", "T12", "Baja", 1, 2, "=I17*H17", dt.date(2026, 11, 17), 1, "=WORKDAY(K17,L17-1)"],
    ]
    end_t = write_table(ws, 4, ["N°", "ID", "Fase", "Tarea", "Responsable", "Dep.", "Dificultad", "Factor", "Horas", "Esfuerzo", "Inicio", "Duración (d)", "Fin"], t_rows,
                        [5, 7, 12, 46, 22, 7, 11, 8, 8, 10, 12, 12, 12], input_cols={8, 9, 11, 12})
    for r in range(5, end_t + 1):
        ws.cell(r, 11).number_format = "yyyy-mm-dd"
        ws.cell(r, 13).number_format = "yyyy-mm-dd"
    ws.cell(end_t + 1, 4, "TOTALES").font = FONT_BOLD
    ws.cell(end_t + 1, 9, f"=SUM(I5:I{end_t})").font = FONT_BOLD
    ws.cell(end_t + 1, 10, f"=SUM(J5:J{end_t})").font = FONT_BOLD
    ws.cell(end_t + 1, 12, f"=SUM(L5:L{end_t})").font = FONT_BOLD

    # 10. CARTA GANTT
    ws = wb.create_sheet("Carta Gantt")
    style_title(ws, "Carta Gantt Semanal — Proyecto Sonrisa Sana (19-10-2026 al 17-11-2026)",
                "Vinculada dinámicamente a la hoja Tareas. Semanas S1 a S5 hasta la fecha de entrega (17-11-2026).", 11)
    g_headers = ["ID", "Fase", "Tarea", "Responsable", "Inicio", "Fin", "S1\n19-10", "S2\n26-10", "S3\n02-11", "S4\n09-11", "S5\n16-11"]
    for c_idx, h in enumerate(g_headers, 1):
        c = ws.cell(4, c_idx, h)
        c.font, c.fill, c.alignment, c.border = FONT_HDR, FILL_HDR, ALIGN_CENTER, BORDER_CELL
    ws.row_dimensions[4].height = 28
    week_starts = [dt.date(2026, 10, 19), dt.date(2026, 10, 26), dt.date(2026, 11, 2), dt.date(2026, 11, 9), dt.date(2026, 11, 16)]
    for idx, t in enumerate(t_rows, 5):
        ws.cell(idx, 1, f"=Tareas!B{idx}").alignment = ALIGN_CENTER
        ws.cell(idx, 2, f"=Tareas!C{idx}")
        ws.cell(idx, 3, f"=Tareas!D{idx}")
        ws.cell(idx, 4, f"=Tareas!E{idx}")
        ws.cell(idx, 5, f"=Tareas!K{idx}").number_format = "dd-mm-yyyy"
        ws.cell(idx, 6, f"=Tareas!M{idx}").number_format = "dd-mm-yyyy"
        t_ini = t[10]
        t_fin = t_ini + dt.timedelta(days=t[11] - 1)
        for w_i, ws_date in enumerate(week_starts, 7):
            we_date = ws_date + dt.timedelta(days=4)
            cell = ws.cell(idx, w_i, "")
            if t_ini <= we_date and t_fin >= ws_date:
                if t[1] in ("T04", "T07", "T09", "T11", "T13"):
                    cell.value = "◆"
                    cell.fill = FILL_HITO
                    cell.font = FONT_HDR
                else:
                    cell.value = "■"
                    cell.fill = FILL_GANTT
                    cell.font = FONT_HDR
                cell.alignment = ALIGN_CENTER
        for c in range(1, 12):
            ws.cell(idx, c).border = BORDER_CELL
    for idx, w in enumerate([7, 12, 44, 22, 12, 12, 10, 10, 10, 10, 10], 1):
        ws.column_dimensions[get_column_letter(idx)].width = w

    # 11. ESPACIO COLABORATIVO (TABLERO KANBAN)
    ws = wb.create_sheet("Espacio Colaborativo")
    style_title(ws, "Espacio de Trabajo Colaborativo y Tablero Kanban",
                "Organización del tablero Kanban (Trello/Jira), límites WIP, Google Drive y GitHub", 4)
    k_rows = [
        ["📥 Product Backlog", "Todas las HU pendientes ordenadas por prioridad MoSCoW.", "Solo PO/SM reordena.", "Sin límite"],
        ["📋 Por Hacer (Sprint)", "HU comprometidas para el Sprint activo con subtareas técnicas.", "Se carga al inicio del Sprint.", "~19–25 SP"],
        ["🔨 En Progreso", "Tarjetas en desarrollo activo con responsable asignado.", "Máximo 2 tarjetas simultáneas por integrante.", "2 / persona"],
        ["🔍 En Revisión / QA", "Pull request abierto, pruebas de seguridad RBAC y tiempos (<2s).", "QA verifica condiciones de aceptación.", "3 tarjetas"],
        ["✅ Terminado", "Cumple Definición de Terminado (DoD) y validado.", "Solo tras Sprint Review.", "Sin límite"],
        ["🚧 Impedimentos", "Bloqueos técnicos o de negocio detectados en Daily.", "SM resuelve en ≤ 24 h.", "Sin límite"],
    ]
    end_k = write_table(ws, 4, ["Columna Kanban", "Contenido", "Regla de Movimiento", "Límite WIP"], k_rows, [24, 52, 40, 16])
    embed_image(ws, "09_tablero_kanban.png", f"A{end_k + 2}", 900)

    # 12. CASOS DE USO
    ws = wb.create_sheet("Casos de Uso")
    style_title(ws, "Modelo de Casos de Uso — Catálogo y Diagrama General",
                "14 Casos de Uso trazados a RF y HU con relaciones <<include>> y <<extend>>", 7)
    cu_rows = [
        ["CU01", "Registrarse / Iniciar sesión", "Paciente / Usuario", "—", "—", "RF01, RF12", "HU01, HU12"],
        ["CU02", "Gestionar pacientes", "Secretaria", "—", "<<include>> Validar RUT", "RF02", "HU02"],
        ["CU03", "Reservar hora online", "Paciente", "—", "<<include>> CU04", "RF03", "HU03"],
        ["CU04", "Validar disponibilidad horaria", "(incluido)", "—", "Incluido por CU03 y CU06", "RF03, RF06", "HU03, HU06"],
        ["CU05", "Ver agenda diaria / semanal", "Secretaria", "Odontólogo", "—", "RF05", "HU05"],
        ["CU06", "Modificar / reprogramar cita", "Secretaria", "—", "<<include>> CU04", "RF06", "HU06"],
        ["CU07", "Cancelar cita y liberar bloque", "Secretaria / Paciente", "—", "Omite recordatorio", "RF07", "HU07"],
        ["CU08", "Configurar horarios y bloqueos", "Administrador", "Odontólogo", "—", "RF04", "HU04"],
        ["CU09", "Enviar recordatorio automático", "Reloj del sistema", "Mensajería / Paciente", "<<extend>> Confirmar por link", "RF08, RF09", "HU08, HU09"],
        ["CU10", "Consultar ficha clínica confidencial", "Odontólogo", "—", "<<extend>> CU11", "RF10", "HU10"],
        ["CU11", "Registrar evolución, diagnóstico y tratamiento", "Odontólogo", "—", "Extiende CU10", "RF10", "HU10"],
        ["CU12", "Gestionar usuarios y roles (RBAC)", "Administrador", "—", "—", "RF12", "HU12"],
        ["CU13", "Consultar auditoría de accesos", "Administrador", "—", "—", "RF11", "HU11"],
        ["CU14", "Generar reporte de ocupación", "Administrador", "—", "—", "RF13", "HU13"],
    ]
    end_cu = write_table(ws, 4, ["ID", "Caso de Uso", "Actor Principal", "Actor Secundario", "Relaciones", "RF", "HU"], cu_rows, [8, 36, 22, 22, 28, 14, 14])
    embed_image(ws, "01_casos_de_uso_general.png", f"A{end_cu + 2}", 880)

    # 13. ESPECIFICACIÓN CU
    ws = wb.create_sheet("Especificación CU")
    style_title(ws, "Especificación Detallada de Casos de Uso Principales",
                "Flujo básico, flujos alternativos, precondiciones, postcondiciones y reglas de negocio", 2)
    ecu_rows = [
        ["CU03 — Reservar hora online", "Actor: Paciente | Trazabilidad: RF03, HU03, RNF04, RNF06.\nPrecondición: Paciente autenticado; odontólogo con horario configurado.\nFlujo básico: 1) Elige especialidad, odontólogo y fecha. 2) Sistema consulta bloques libres (<1.5s). 3) Paciente elige bloque y confirma. 4) Sistema inserta cita (UNIQUE bloque_activo) y programa recordatorio 24h antes.\nAlternativo: 3a) Choque simultáneo → rechaza y sugiere bloques cercanos."],
        ["CU06 — Modificar / reprogramar cita", "Actor: Secretaria | Trazabilidad: RF06, HU06, RNF05.\nPrecondición: Cita en estado pendiente o confirmada.\nFlujo básico: 1) Secretaria selecciona cita en agenda y pulsa Reprogramar. 2) Elige nuevo bloque disponible (CU04). 3) Sistema actualiza cita, omite recordatorio previo, programa uno nuevo y notifica al paciente.\nRegla: Operación completa en ≤ 2 clics desde la agenda."],
        ["CU07 — Cancelar cita y liberar bloque", "Actor: Secretaria o Paciente | Trazabilidad: RF07, HU07.\nFlujo básico: 1) Selecciona cita y pulsa Cancelar. 2) Ingresa motivo. 3) Sistema cambia estado a «cancelada», libera columna generada bloque_activo y omite recordatorios pendientes."],
        ["CU09 — Enviar recordatorio automático", "Actor: Reloj del sistema | Trazabilidad: RF08, RF09, RNF07.\nFlujo básico: 1) Cada 15 min consulta recordatorios pendientes con fecha_programada <= NOW(). 2) Verifica que la cita siga vigente. 3) Envía correo/WhatsApp con token único de confirmación y marca «enviado»."],
        ["CU10 / CU11 — Ficha clínica confidencial", "Actor: Odontólogo | Trazabilidad: RF10, HU10, RNF02, RNF03.\nPrecondición: Usuario autenticado con rol estricto «Odontólogo».\nFlujo básico: 1) Odontólogo abre ficha del paciente. 2) Sistema descifra antecedentes/alergias (AES-256) y registra acceso en auditoria_acceso. 3) Odontólogo registra evolución/diagnóstico; trigger marca cita como «atendida».\nAlternativo: 1a) Rol Secretaria o Admin intenta acceder → HTTP 403 + registro en auditoría."],
    ]
    write_table(ws, 4, ["Caso de Uso", "Especificación Completa"], ecu_rows, [32, 98])

    # 14. MODELO BD
    ws = wb.create_sheet("Modelo BD")
    style_title(ws, "Modelo de Base de Datos (Lógico, Relacional 3FN y Físico)",
                "12 tablas en MySQL 8.0 InnoDB (script en sonrisa_sana_bd.sql). Incluye cifrado AES-256 y prevención de choques.", 5)
    bd_rows = [
        ["rol", "1 : N", "usuario", "asigna", "Roles: Administrador, Odontologo, Secretaria, Paciente (RF12)."],
        ["usuario", "1 : 0..1", "odontologo", "es", "Extiende datos profesionales (registro Superintendencia, box)."],
        ["especialidad", "1 : N", "odontologo", "pertenece", "Odontología General, Ortodoncia, Endodoncia, Odontopediatría."],
        ["odontologo", "1 : N", "horario_odontologo", "define", "Jornada semanal y duración de bloque (RF04)."],
        ["odontologo", "1 : N", "bloqueo_horario", "registra", "Bloqueos excepcionales sin atención."],
        ["paciente", "1 : N", "cita", "reserva", "Citas online o presenciales; restricción UNIQUE bloque_activo (RNF06)."],
        ["cita", "1 : N", "recordatorio", "programa", "Trigger crea recordatorio automático 24h antes (RF08)."],
        ["paciente", "1 : 1", "ficha_clinica", "posee", "Antecedentes y alergias cifrados AES-256 (RNF02)."],
        ["ficha_clinica", "1 : N", "evolucion_clinica", "registra", "Diagnóstico y tratamiento cifrados, solo Odontólogo (RF10)."],
        ["usuario", "1 : N", "auditoria_acceso", "genera", "Trazabilidad de lecturas a ficha y cambios en citas (RF11)."],
    ]
    end_bd = write_table(ws, 4, ["Entidad A", "Card.", "Entidad B", "Verbo", "Regla de Negocio"], bd_rows, [22, 10, 22, 14, 64])
    embed_image(ws, "02_modelo_bd_er.png", f"A{end_bd + 2}", 900)

    # 15. DICCIONARIO DATOS
    ws = wb.create_sheet("Diccionario Datos")
    style_title(ws, "Diccionario de Datos — Sistema Sonrisa Sana",
                "Motor InnoDB · Codificación utf8mb4_unicode_ci · Script físico: sonrisa_sana_bd.sql", 6)
    dd_rows = [
        ["rol", "id_rol", "INT (AI)", "NO", "PK", "Identificador único del rol"],
        ["rol", "nombre", "VARCHAR(30)", "NO", "UQ", "Administrador, Odontologo, Secretaria, Paciente"],
        ["usuario", "id_usuario", "INT (AI)", "NO", "PK", "Identificador del usuario"],
        ["usuario", "id_rol", "INT", "NO", "FK -> rol", "Rol asignado"],
        ["usuario", "rut", "VARCHAR(12)", "NO", "UQ", "RUT chileno validado"],
        ["usuario", "correo", "VARCHAR(120)", "NO", "UQ", "Correo de acceso"],
        ["usuario", "password_hash", "VARCHAR(255)", "NO", "—", "Hash bcrypt (RNF01)"],
        ["odontologo", "id_odontologo", "INT (AI)", "NO", "PK", "Identificador del odontólogo"],
        ["odontologo", "id_usuario", "INT", "NO", "FK, UQ", "Usuario asociado"],
        ["odontologo", "id_especialidad", "INT", "NO", "FK", "Especialidad principal"],
        ["paciente", "id_paciente", "INT (AI)", "NO", "PK", "Identificador del paciente"],
        ["paciente", "rut", "VARCHAR(12)", "NO", "UQ", "RUT único del paciente"],
        ["paciente", "consentimiento_datos", "BOOLEAN", "NO", "—", "Aceptación Ley 19.628 / 21.719"],
        ["cita", "id_cita", "INT (AI)", "NO", "PK", "Identificador de la cita"],
        ["cita", "id_paciente", "INT", "NO", "FK -> paciente", "Paciente que asiste"],
        ["cita", "id_odontologo", "INT", "NO", "FK -> odontologo", "Odontólogo asignado"],
        ["cita", "fecha / hora_inicio / fin", "DATE / TIME", "NO", "—", "Fecha y bloque horario"],
        ["cita", "estado", "ENUM", "NO", "—", "pendiente, confirmada, atendida, cancelada, reprogramada"],
        ["cita", "bloque_activo", "VARCHAR(60) STORED", "SÍ", "UQ", "Evita doble reserva simultánea en BD (RNF06)"],
        ["recordatorio", "id_recordatorio", "INT (AI)", "NO", "PK", "Identificador del recordatorio"],
        ["recordatorio", "canal / estado", "ENUM", "NO", "—", "correo/whatsapp/sms | pendiente/enviado/fallido/omitido"],
        ["ficha_clinica", "id_ficha", "INT (AI)", "NO", "PK", "Identificador de ficha médica"],
        ["ficha_clinica", "antecedentes_medicos_enc", "VARBINARY(1024)", "SÍ", "—", "Cifrado AES-256 (RNF02)"],
        ["evolucion_clinica", "diagnostico_enc", "VARBINARY(1024)", "NO", "—", "Diagnóstico cifrado AES-256 (RNF02)"],
        ["auditoria_acceso", "accion", "ENUM", "NO", "—", "VER_FICHA, CREAR, MODIFICAR, CANCELAR, LOGIN, DENEGADO"],
    ]
    write_table(ws, 4, ["Tabla", "Columna", "Tipo de Dato", "¿Nulo?", "Clave", "Descripción / Restricción"], dd_rows, [20, 26, 20, 8, 14, 52])

    # 16. DIAGRAMAS FLUJO
    ws = wb.create_sheet("Diagramas Flujo")
    style_title(ws, "Diagramas de Flujo TO-BE de Procesos Principales",
                "Óvalo = inicio/fin · Rectángulo = proceso · Rombo = decisión · Paralelogramo = entrada · Naranjo = excepción/alerta", 4)
    embed_image(ws, "03_flujo_reserva_online.png", "A4", 680)
    embed_image(ws, "04_flujo_gestion_secretaria.png", "A44", 680)
    embed_image(ws, "05_flujo_atencion_y_recordatorios.png", "A84", 720)

    # 17. MOCKUPS UI
    ws = wb.create_sheet("Mockups UI")
    style_title(ws, "Wireframes y Mockups de la Interfaz de Usuario",
                "Alineados a los casos de uso CU03 (Reserva Online), CU05-CU07 (Secretaría) y CU10-CU11 (Ficha Confidencial)", 4)
    embed_image(ws, "06_mockup_reserva_online.png", "A4", 760)
    embed_image(ws, "07_mockup_agenda_secretaria.png", "A34", 760)
    embed_image(ws, "08_mockup_ficha_clinica.png", "A64", 760)

    wb.save(OUT_XLSX)
    print("Excel generado exitosamente en:", OUT_XLSX)


if __name__ == "__main__":
    build_workbook()
