"""Generador del informe técnico en Word (.docx) según pauta Evaluación N°1 INACAP."""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIAG_DIR = os.path.join(BASE_DIR, "diagramas")
OUT_DOCX = os.path.join(BASE_DIR, "Fernando_Duran_Sonrisa_Sana.docx")


def set_cell_bg(cell, hex_color):
    """Aplica un color de relleno hexadecimal a una celda de tabla Word."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def add_heading_styled(doc, text, level=1):
    """Agrega un encabezado estilizado con tipografía Calibri y color institucional."""
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = "Calibri"
        run.font.color.rgb = RGBColor(0x0F, 0x4C, 0x81)
    return p


def add_styled_table(doc, headers, rows):
    """Inserta una tabla con encabezado azul corporativo y filas alternadas."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        set_cell_bg(hdr_cells[i], "0F4C81")
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for r_idx, row in enumerate(rows):
        cells = table.rows[r_idx + 1].cells
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            cells[c_idx].text = str(val)
            set_cell_bg(cells[c_idx], bg)
            for p in cells[c_idx].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9)
    doc.add_paragraph()


def add_img(doc, img_name, caption, width_in=6.2):
    """Centra e inserta una imagen PNG junto a su pie de figura en cursiva."""
    path = os.path.join(DIAG_DIR, img_name)
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(path, width=Inches(width_in))
        cap = doc.add_paragraph(caption)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in cap.runs:
            r.italic = True
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(0x47, 0x55, 0x69)


def build_report():
    """Genera y guarda el informe técnico completo en formato Word (.docx)."""
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    # PORTADA
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_inst.add_run("INSTITUTO PROFESIONAL INACAP\nÁREA TECNOLOGÍAS DE INFORMACIÓN Y CIBERSEGURIDAD\nIngeniería en Informática – Analista Programador")
    r.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0x0F, 0x4C, 0x81)

    doc.add_paragraph("\n\n")
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rt = p_title.add_run('INFORME DE REQUERIMIENTOS Y MODELADO UML\nSistema de Agendamiento y Gestión Clínica\n«Clínica Odontológica Sonrisa Sana»')
    rt.bold = True
    rt.font.size = Pt(20)
    rt.font.color.rgb = RGBColor(0x0F, 0x4C, 0x81)

    doc.add_paragraph("\n")
    meta = [
        ["Asignatura", "Modelamiento de Soluciones Informáticas (Sección 114-2-F2)"],
        ["Evaluación", "Prueba N° I — Unidad 1: Informe de Requerimiento y Modelado UML (20%)"],
        ["Docente", "Yaleni Gómez Peña"],
        ["Integrantes", "Fernando A. Durán Leiva\nFrancisco A. Lara Yévenes\nChristopher D. Figueroa Arthur"],
        ["Fecha de Entrega", "17 de noviembre de 2026"],
    ]
    add_styled_table(doc, ["Campo", "Detalle"], meta)
    doc.add_page_break()

    # 1. INTRODUCCIÓN Y ANÁLISIS CRÍTICO (Criterio 1.1.1 y 1.1.2)
    add_heading_styled(doc, "1. Introducción, Problemática y Análisis Crítico", 1)
    doc.add_paragraph(
        'La Clínica Odontológica "Sonrisa Sana" gestiona actualmente su agenda de pacientes mediante un cuaderno físico. '
        'Esta práctica artesanal provoca choques de horarios, pérdida de tiempo operativo para las secretarias, imposibilidad de '
        'reservar fuera del horario de atención y una alta tasa de inasistencias por ausencia de recordatorios. Adicionalmente, '
        'el manejo de datos médicos sensibles exige estrictos controles de confidencialidad y tiempos de respuesta muy rápidos.'
    )
    add_heading_styled(doc, "1.1 Desafíos y Especificaciones Técnicas (Criterio 1.1.1)", 2)
    add_styled_table(doc, ["Desafío Detectado", "Especificación Técnica de Solución"], [
        ["Choques horarios por registro en cuaderno", "Restricción UNIQUE sobre columna generada `bloque_activo` en MySQL InnoDB + transacciones ACID."],
        ["Reservas online 24/7 sin fricción", "Portal web responsive en 3 pasos (< 90 s) con consulta de disponibilidad P95 < 1.5 segundos."],
        ["Modificación/cancelación rápida por secretaría", "Agenda diaria con filtros por odontólogo/estado y acciones en ≤ 2 clics con liberación inmediata del bloque."],
        ["Inasistencias de pacientes", "Scheduler automático cada 15 min + Trigger SQL que programa recordatorios por correo/WhatsApp 24 h antes."],
        ["Confidencialidad estricta de datos médicos", "Control de acceso RBAC estricto (HTTP 403 a no odontólogos), cifrado AES-256 en reposo, bcrypt y TLS 1.3 (Ley 19.628 / 21.719 / 20.584)."],
    ])

    # 2. REQUERIMIENTOS (Criterio 1.1.1 y 1.1.2)
    add_heading_styled(doc, "2. Levantamiento de Requerimientos y Priorización MoSCoW", 1)
    doc.add_paragraph(
        "Se levantaron 16 Requerimientos Funcionales (13 dentro del alcance y 3 Won't) y 13 Requerimientos No Funcionales "
        "bajo la norma ISO/IEC 25010, aplicando la técnica de priorización MoSCoW para asegurar la entrega del MVP dentro del plazo."
    )
    add_heading_styled(doc, "2.1 Requerimientos Funcionales (Extracto Principal)", 2)
    add_styled_table(doc, ["ID", "Módulo", "Descripción", "MoSCoW", "HU"], [
        ["RF01", "Acceso", "Registro y autenticación de pacientes para reserva online.", "Must", "HU01"],
        ["RF02", "Recepción", "Gestión de pacientes por secretaría (alta, búsqueda por RUT).", "Must", "HU02"],
        ["RF03", "Reserva", "Reserva de hora online validando disponibilidad sin choques.", "Must", "HU03"],
        ["RF04", "Agenda", "Configuración de horarios y bloqueos por odontólogo.", "Must", "HU04"],
        ["RF05", "Agenda", "Visualización de agenda diaria/semanal con estados por color.", "Must", "HU05"],
        ["RF06", "Secretaría", "Modificación/reprogramación fácil de citas validando bloques.", "Must", "HU06"],
        ["RF07", "Secretaría", "Cancelación fácil de citas liberando el bloque de inmediato.", "Must", "HU07"],
        ["RF08", "Recordatorios", "Envío automático de recordatorios 24h antes (correo/WhatsApp).", "Must", "HU08"],
        ["RF09", "Recordatorios", "Confirmación o anulación directa desde enlace en recordatorio.", "Should", "HU09"],
        ["RF10", "Ficha Clínica", "Consulta/registro de ficha clínica cifrada solo para Odontólogo.", "Must", "HU10"],
        ["RF11", "Seguridad", "Auditoría de accesos a fichas y cambios en citas.", "Should", "HU11"],
        ["RF12", "Admin", "Gestión de usuarios y roles (RBAC).", "Must", "HU12"],
        ["RF13", "Reportes", "Reporte de ocupación y cancelaciones por período.", "Could", "HU13"],
    ])

    add_heading_styled(doc, "2.2 Requerimientos No Funcionales Críticos", 2)
    add_styled_table(doc, ["ID", "Categoría", "Requerimiento y Métrica Verificable", "MoSCoW"], [
        ["RNF01", "Seguridad", "Hash bcrypt (cost >= 12) y HTTPS TLS 1.3 obligatorio.", "Must"],
        ["RNF02", "Confidencialidad", "RBAC estricto + cifrado AES-256 en antecedentes, alergias y diagnósticos.", "Must"],
        ["RNF03", "Legal", "Cumplimiento Ley N° 19.628, Ley N° 21.719 y Ley N° 20.584.", "Must"],
        ["RNF04", "Eficiencia", "P95 < 1.5 s en consulta de bloques y < 2 s al reservar/modificar (50 concurrentes).", "Must"],
        ["RNF05", "Usabilidad", "Reserva online en ≤ 3 pasos; modificación/cancelación en ≤ 2 clics.", "Must"],
        ["RNF06", "Integridad", "Restricción UNIQUE `bloque_activo` para impedir doble reserva.", "Must"],
    ])

    # 3. HISTORIAS DE USUARIO
    add_heading_styled(doc, "3. Historias de Usuario Priorizadas", 1)
    add_styled_table(doc, ["ID", "Rol", "Funcionalidad y Razón", "Condiciones Clave", "MoSCoW", "SP"], [
        ["HU03", "Paciente", "Reservar hora online sin llamar ni esperar", "≤ 3 pasos, solo bloques libres, sin choques.", "Must", "8"],
        ["HU06", "Secretaria", "Modificar/reprogramar cita fácilmente", "≤ 2 clics, valida disponibilidad, notifica.", "Must", "5"],
        ["HU07", "Secretaria", "Cancelar cita y liberar bloque horario", "Registra motivo, libera bloque, omite recordatorio.", "Must", "3"],
        ["HU08", "Paciente", "Recibir recordatorios automáticos 24h antes", "Envío automático correo/WhatsApp sin duplicar.", "Must", "5"],
        ["HU10", "Odontólogo", "Consultar y registrar ficha clínica confidencial", "Exclusivo Odontólogo (403 a otros), cifrado AES-256.", "Must", "8"],
    ])

    # 4. CASOS DE USO (Criterio 1.1.3)
    add_heading_styled(doc, "4. Modelado de Casos de Uso (UML)", 1)
    doc.add_paragraph(
        "El diagrama general modela los 14 casos de uso del sistema, sus actores humanos (Paciente, Secretaria, Odontólogo, "
        "Administrador) y actores de sistema (Reloj del Sistema y Servicio de Mensajería), detallando relaciones <<include>> y <<extend>>."
    )
    add_img(doc, "01_casos_de_uso_general.png", "Figura 1: Diagrama de Casos de Uso General — Clínica Odontológica Sonrisa Sana.")

    # 5. WIREFRAMES Y MOCKUPS (Criterio 1.1.3)
    add_heading_styled(doc, "5. Wireframes y Mockups de Interfaz de Usuario", 1)
    doc.add_paragraph("Alineados directamente con los casos de uso CU03 (Reserva Online), CU05–CU07 (Panel Secretaría) y CU10–CU11 (Ficha Confidencial).")
    add_img(doc, "06_mockup_reserva_online.png", "Figura 2: Mockup Portal de Reserva de Hora Online (Paciente — máx. 3 pasos).")
    add_img(doc, "07_mockup_agenda_secretaria.png", "Figura 3: Mockup Panel de Agenda Diaria (Secretaría — Reprogramar/Cancelar en ≤ 2 clics).")
    add_img(doc, "08_mockup_ficha_clinica.png", "Figura 4: Mockup Ficha Clínica Confidencial (Acceso exclusivo Odontólogo, cifrado AES-256).")

    # 6. BASE DE DATOS (Criterio 1.1.4)
    add_heading_styled(doc, "6. Diseño de Base de Datos (Lógico, Relacional y Físico)", 1)
    doc.add_paragraph(
        "El modelo de datos cumple con la Tercera Forma Normal (3FN) en 12 tablas bajo MySQL 8.0 (InnoDB, utf8mb4). "
        "El script físico completo se entrega en `sonrisa_sana_bd.sql` e incluye índices compuestos para cumplir P95 < 1.5s, "
        "triggers automáticos para recordatorios y cierre de citas, y la columna generada `bloque_activo` con restricción UNIQUE."
    )
    add_img(doc, "02_modelo_bd_er.png", "Figura 5: Modelo Entidad-Relación (Lógico / Relacional 3FN) — 12 Tablas.")

    # 7. DIAGRAMAS DE FLUJO (Criterio 1.1.5)
    add_heading_styled(doc, "7. Diagramas de Flujo de Procesos Principales (TO-BE)", 1)
    add_img(doc, "03_flujo_reserva_online.png", "Figura 6: Diagrama de Flujo TO-BE — Reserva de Hora Online (RF03 / HU03).", 5.5)
    add_img(doc, "04_flujo_gestion_secretaria.png", "Figura 7: Diagrama de Flujo TO-BE — Modificación y Cancelación por Secretaría (RF05–RF07).", 5.5)
    add_img(doc, "05_flujo_atencion_y_recordatorios.png", "Figura 8: Diagrama de Flujo TO-BE — Atención Confidencial y Recordatorios Automáticos.", 5.8)

    # 8. PLANIFICACIÓN KANBAN Y GANTT (Criterio 1.1.6)
    add_heading_styled(doc, "8. Planificación del Proyecto: Tablero Kanban y Carta Gantt", 1)
    doc.add_paragraph(
        "El proyecto se planificó del 19-10-2026 al 17-11-2026 (5 semanas hasta la fecha de entrega oficial), "
        "combinando iteraciones SCRUM con gestión visual mediante Tablero Kanban y límites de trabajo en curso (WIP)."
    )
    add_img(doc, "09_tablero_kanban.png", "Figura 9: Tablero Kanban del Proyecto «Sonrisa Sana» con límites WIP y etiquetas MoSCoW.")

    # 9. CONCLUSIONES
    add_heading_styled(doc, "9. Conclusiones y Recomendaciones", 1)
    doc.add_paragraph(
        'La propuesta de modelamiento para la Clínica Odontológica "Sonrisa Sana" resuelve integralmente las problemáticas '
        'del agendamiento manual en cuaderno. La trazabilidad completa desde el levantamiento RF/RNF hasta los casos de uso, '
        'mockups, modelo de base de datos 3FN (con prevención física de choques y cifrado AES-256), diagramas de flujo y '
        'tablero Kanban garantiza una solución rápida, segura, confidencial y viable dentro del plazo establecido.'
    )

    doc.save(OUT_DOCX)
    print("Informe Word generado exitosamente en:", OUT_DOCX)


if __name__ == "__main__":
    build_report()
