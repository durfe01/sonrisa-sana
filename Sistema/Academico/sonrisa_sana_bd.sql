-- ============================================================================
-- Sistema de Agendamiento y Gestión Clínica "Sonrisa Sana" (SAG-SonrisaSana)
-- Modelo Físico de Base de Datos (MySQL 8.0+ / Motor InnoDB / utf8mb4)
-- Autores: Fernando A. Durán Leiva, Francisco A. Lara Yévenes, Christopher D. Figueroa Arthur
-- Asignatura: Modelamiento de Soluciones Informáticas (INACAP - Sec. 114-2-F2)
-- ============================================================================

DROP DATABASE IF EXISTS sonrisa_sana_db;
CREATE DATABASE sonrisa_sana_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sonrisa_sana_db;

-- ----------------------------------------------------------------------------
-- 1. SEGURIDAD Y USUARIOS (RF12, RNF01, RNF02)
-- ----------------------------------------------------------------------------
CREATE TABLE rol (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    descripcion VARCHAR(150) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_rol INT NOT NULL,
    rut VARCHAR(12) NOT NULL UNIQUE,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hash bcrypt (RNF01)',
    telefono VARCHAR(20) NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_rol FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 2. ESPECIALIDADES, ODONTÓLOGOS Y HORARIOS (RF04)
-- ----------------------------------------------------------------------------
CREATE TABLE especialidad (
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL UNIQUE,
    duracion_estandar_min SMALLINT NOT NULL DEFAULT 30
) ENGINE=InnoDB;

CREATE TABLE odontologo (
    id_odontologo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    id_especialidad INT NOT NULL,
    registro_superintendencia VARCHAR(30) NOT NULL UNIQUE,
    box_asignado VARCHAR(20) NULL,
    CONSTRAINT fk_odontologo_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    CONSTRAINT fk_odontologo_especialidad FOREIGN KEY (id_especialidad) REFERENCES especialidad(id_especialidad)
) ENGINE=InnoDB;

CREATE TABLE horario_odontologo (
    id_horario INT AUTO_INCREMENT PRIMARY KEY,
    id_odontologo INT NOT NULL,
    dia_semana TINYINT NOT NULL COMMENT '1=Lunes ... 7=Domingo',
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    duracion_bloque_min SMALLINT NOT NULL DEFAULT 30,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_horario_odontologo FOREIGN KEY (id_odontologo) REFERENCES odontologo(id_odontologo),
    CONSTRAINT chk_horario_horas CHECK (hora_fin > hora_inicio),
    CONSTRAINT chk_horario_dia CHECK (dia_semana BETWEEN 1 AND 7)
) ENGINE=InnoDB;

CREATE TABLE bloqueo_horario (
    id_bloqueo INT AUTO_INCREMENT PRIMARY KEY,
    id_odontologo INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    motivo VARCHAR(150) NOT NULL,
    CONSTRAINT fk_bloqueo_odontologo FOREIGN KEY (id_odontologo) REFERENCES odontologo(id_odontologo),
    CONSTRAINT chk_bloqueo_horas CHECK (hora_fin > hora_inicio)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 3. PACIENTES Y TIPOS DE ATENCIÓN (RF01, RF02, RF03)
-- ----------------------------------------------------------------------------
CREATE TABLE paciente (
    id_paciente INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL UNIQUE COMMENT 'NULL si fue registrado presencialmente sin cuenta online aún',
    rut VARCHAR(12) NOT NULL UNIQUE,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE,
    direccion VARCHAR(180) NULL,
    prevision ENUM('Fonasa', 'Isapre', 'Particular') NOT NULL DEFAULT 'Particular',
    consentimiento_datos BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Ley 19.628 / 21.719 (RNF03)',
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_paciente_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
) ENGINE=InnoDB;

CREATE TABLE tipo_atencion (
    id_tipo_atencion INT AUTO_INCREMENT PRIMARY KEY,
    id_especialidad INT NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    duracion_min SMALLINT NOT NULL DEFAULT 30,
    valor_referencia_clp INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_tipo_especialidad FOREIGN KEY (id_especialidad) REFERENCES especialidad(id_especialidad)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 4. AGENDA Y CITAS SIN CHOQUES DE HORARIO (RF03, RF05, RF06, RF07, RNF06)
-- ----------------------------------------------------------------------------
CREATE TABLE cita (
    id_cita INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT NOT NULL,
    id_odontologo INT NOT NULL,
    id_tipo_atencion INT NOT NULL,
    id_usuario_gestion INT NULL COMMENT 'Secretaria o usuario que creó/modificó; NULL si reserva online',
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    origen ENUM('online', 'presencial', 'telefonica') NOT NULL DEFAULT 'online',
    estado ENUM('pendiente', 'confirmada', 'atendida', 'cancelada', 'reprogramada') NOT NULL DEFAULT 'pendiente',
    motivo_cambio_cancelacion VARCHAR(200) NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- Columna generada para garantizar unicidad de bloque activo (evita choques incluso con canceladas)
    bloque_activo VARCHAR(60) GENERATED ALWAYS AS (
        CASE WHEN estado IN ('pendiente', 'confirmada', 'atendida')
             THEN CONCAT(id_odontologo, '_', fecha, '_', hora_inicio)
             ELSE NULL
        END
    ) STORED,
    CONSTRAINT uq_cita_sin_choque UNIQUE (bloque_activo),
    CONSTRAINT fk_cita_paciente FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente),
    CONSTRAINT fk_cita_odontologo FOREIGN KEY (id_odontologo) REFERENCES odontologo(id_odontologo),
    CONSTRAINT fk_cita_tipo FOREIGN KEY (id_tipo_atencion) REFERENCES tipo_atencion(id_tipo_atencion),
    CONSTRAINT fk_cita_usuario FOREIGN KEY (id_usuario_gestion) REFERENCES usuario(id_usuario),
    CONSTRAINT chk_cita_horas CHECK (hora_fin > hora_inicio)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 5. RECORDATORIOS AUTOMÁTICOS (RF08, RF09, RNF07)
-- ----------------------------------------------------------------------------
CREATE TABLE recordatorio (
    id_recordatorio INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    canal ENUM('correo', 'whatsapp', 'sms') NOT NULL DEFAULT 'correo',
    fecha_programada DATETIME NOT NULL,
    fecha_envio DATETIME NULL,
    estado ENUM('pendiente', 'enviado', 'fallido', 'omitido') NOT NULL DEFAULT 'pendiente',
    intentos TINYINT NOT NULL DEFAULT 0,
    token_confirmacion VARCHAR(64) NULL UNIQUE,
    CONSTRAINT fk_recordatorio_cita FOREIGN KEY (id_cita) REFERENCES cita(id_cita)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 6. FICHA CLÍNICA CONFIDENCIAL (RF10, RNF02, RNF03)
-- ----------------------------------------------------------------------------
CREATE TABLE ficha_clinica (
    id_ficha INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT NOT NULL UNIQUE,
    antecedentes_medicos_enc VARBINARY(1024) NULL COMMENT 'Cifrado AES-256 en aplicación/BD (RNF02)',
    alergias_enc VARBINARY(512) NULL COMMENT 'Cifrado AES-256 (RNF02)',
    grupo_sanguineo VARCHAR(5) NULL,
    fecha_apertura DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ficha_paciente FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
) ENGINE=InnoDB;

CREATE TABLE evolucion_clinica (
    id_evolucion INT AUTO_INCREMENT PRIMARY KEY,
    id_ficha INT NOT NULL,
    id_cita INT NULL UNIQUE,
    id_odontologo INT NOT NULL,
    fecha_atencion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pieza_dental VARCHAR(15) NULL,
    diagnostico_enc VARBINARY(1024) NOT NULL COMMENT 'Cifrado AES-256 (RNF02)',
    tratamiento_realizado_enc VARBINARY(1024) NOT NULL COMMENT 'Cifrado AES-256 (RNF02)',
    indicaciones_enc VARBINARY(512) NULL,
    CONSTRAINT fk_evolucion_ficha FOREIGN KEY (id_ficha) REFERENCES ficha_clinica(id_ficha),
    CONSTRAINT fk_evolucion_cita FOREIGN KEY (id_cita) REFERENCES cita(id_cita),
    CONSTRAINT fk_evolucion_odontologo FOREIGN KEY (id_odontologo) REFERENCES odontologo(id_odontologo)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 7. AUDITORÍA Y CONFIGURACIÓN (RF11, RNF02, RNF07)
-- ----------------------------------------------------------------------------
CREATE TABLE auditoria_acceso (
    id_auditoria BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    entidad_afectada VARCHAR(40) NOT NULL,
    id_registro INT NOT NULL,
    accion ENUM('VER_FICHA', 'CREAR', 'MODIFICAR', 'CANCELAR', 'LOGIN', 'DENEGADO') NOT NULL,
    ip_origen VARCHAR(45) NOT NULL,
    detalle VARCHAR(255) NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auditoria_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
) ENGINE=InnoDB;

CREATE TABLE configuracion (
    clave VARCHAR(50) PRIMARY KEY,
    valor VARCHAR(100) NOT NULL,
    descripcion VARCHAR(150) NOT NULL
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 8. ÍNDICES DE RENDIMIENTO (RNF04 < 2 segundos)
-- ----------------------------------------------------------------------------
CREATE INDEX idx_cita_fecha_odontologo ON cita (fecha, id_odontologo, estado);
CREATE INDEX idx_cita_paciente ON cita (id_paciente, fecha);
CREATE INDEX idx_paciente_apellido ON paciente (apellido, nombre);
CREATE INDEX idx_recordatorio_pendiente ON recordatorio (estado, fecha_programada);
CREATE INDEX idx_auditoria_fecha ON auditoria_acceso (fecha_hora, id_usuario);

-- ----------------------------------------------------------------------------
-- 9. VISTAS OPERATIVAS
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_agenda_diaria AS
SELECT
    c.id_cita,
    c.fecha,
    c.hora_inicio,
    c.hora_fin,
    c.estado,
    c.origen,
    CONCAT(p.nombre, ' ', p.apellido) AS paciente,
    p.rut AS rut_paciente,
    p.telefono AS telefono_paciente,
    CONCAT(u.nombre, ' ', u.apellido) AS odontologo,
    e.nombre AS especialidad,
    o.box_asignado,
    ta.nombre AS tipo_atencion
FROM cita c
INNER JOIN paciente p ON c.id_paciente = p.id_paciente
INNER JOIN odontologo o ON c.id_odontologo = o.id_odontologo
INNER JOIN usuario u ON o.id_usuario = u.id_usuario
INNER JOIN especialidad e ON o.id_especialidad = e.id_especialidad
INNER JOIN tipo_atencion ta ON c.id_tipo_atencion = ta.id_tipo_atencion
ORDER BY c.fecha ASC, c.hora_inicio ASC;

CREATE OR REPLACE VIEW v_ocupacion_odontologos AS
SELECT
    o.id_odontologo,
    CONCAT(u.nombre, ' ', u.apellido) AS odontologo,
    DATE_FORMAT(c.fecha, '%Y-%m') AS periodo,
    COUNT(*) AS total_citas,
    SUM(c.estado = 'atendida') AS atendidas,
    SUM(c.estado = 'cancelada') AS canceladas,
    SUM(c.estado IN ('pendiente', 'confirmada')) AS vigentes
FROM cita c
INNER JOIN odontologo o ON c.id_odontologo = o.id_odontologo
INNER JOIN usuario u ON o.id_usuario = u.id_usuario
GROUP BY o.id_odontologo, odontologo, periodo;

-- ----------------------------------------------------------------------------
-- 10. TRIGGERS Y EVENTO AUTOMÁTICO DE RECORDATORIOS
-- ----------------------------------------------------------------------------
DELIMITER $$

-- Al crear una cita pendiente/confirmada, programa automáticamente su recordatorio 24h antes
CREATE TRIGGER trg_cita_ai_recordatorio
AFTER INSERT ON cita
FOR EACH ROW
BEGIN
    DECLARE v_horas_aviso INT DEFAULT 24;
    SELECT CAST(valor AS UNSIGNED) INTO v_horas_aviso
    FROM configuracion WHERE clave = 'horas_aviso_recordatorio';

    IF NEW.estado IN ('pendiente', 'confirmada') THEN
        INSERT INTO recordatorio (id_cita, canal, fecha_programada, estado, token_confirmacion)
        VALUES (
            NEW.id_cita,
            'correo',
            TIMESTAMP(NEW.fecha, NEW.hora_inicio) - INTERVAL v_horas_aviso HOUR,
            'pendiente',
            SHA2(CONCAT(NEW.id_cita, '-', UUID()), 256)
        );
    END IF;
END$$

-- Si una cita se cancela o reprograma, omite recordatorios pendientes anteriores
CREATE TRIGGER trg_cita_au_cancelacion
AFTER UPDATE ON cita
FOR EACH ROW
BEGIN
    IF NEW.estado IN ('cancelada', 'reprogramada') AND OLD.estado <> NEW.estado THEN
        UPDATE recordatorio
        SET estado = 'omitido'
        WHERE id_cita = NEW.id_cita AND estado = 'pendiente';
    END IF;
END$$

-- Al registrar una evolución clínica asociada a cita, marca la cita como atendida
CREATE TRIGGER trg_evolucion_ai_cita
AFTER INSERT ON evolucion_clinica
FOR EACH ROW
BEGIN
    IF NEW.id_cita IS NOT NULL THEN
        UPDATE cita SET estado = 'atendida' WHERE id_cita = NEW.id_cita;
    END IF;
END$$

DELIMITER ;

-- ----------------------------------------------------------------------------
-- 11. DATOS SEMILLA INICIALES
-- ----------------------------------------------------------------------------
INSERT INTO rol (nombre, descripcion) VALUES
('Administrador', 'Gestión de usuarios, roles, configuraciones y reportes de gestión'),
('Odontologo', 'Atención de pacientes y acceso exclusivo a ficha clínica confidencial'),
('Secretaria', 'Gestión de agenda, modificación/cancelación de citas y registro de pacientes'),
('Paciente', 'Reserva de citas online y consulta de sus próximas citas');

INSERT INTO especialidad (nombre, duracion_estandar_min) VALUES
('Odontología General', 30),
('Ortodoncia', 30),
('Endodoncia', 45),
('Odontopediatría', 30);

INSERT INTO configuracion (clave, valor, descripcion) VALUES
('horas_aviso_recordatorio', '24', 'Horas de anticipación para envío automático de recordatorio'),
('max_reprogramaciones_paciente', '2', 'Máximo de reprogramaciones online permitidas por cita');
