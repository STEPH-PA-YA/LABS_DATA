-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS BD_UTP;
USE BD_UTP;

-- Tabla de Carreras
CREATE TABLE `Carreras` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL
);

-- Insertar Carreras
INSERT INTO `Carreras` (`nombre`) VALUES
('Ingenieria en Sistemas'),
('Ingenieria Civil');

-- Tabla de Roles
CREATE TABLE `Roles` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(50) NOT NULL,
  `funciones` TEXT
);

-- Insertar Roles
INSERT INTO `Roles` (`nombre`) VALUES
('Administrador'),
('Asistente');

-- Tabla de Laboratorios
CREATE TABLE `Laboratorios` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `ubicacion` VARCHAR(50),
  `carrera_id` INT,
  FOREIGN KEY (`carrera_id`) REFERENCES `Carreras` (`id`) ON DELETE SET NULL
);

-- Tabla de Equipos
CREATE TABLE `Equipos` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `codigo` CHAR(10),
  `nombre` VARCHAR(100) NOT NULL,
  `marca` VARCHAR(50),
  `modelo` VARCHAR(50),
  `serie` VARCHAR(50),
  `laboratorio_id` INT,
  FOREIGN KEY (`laboratorio_id`) REFERENCES `Laboratorios` (`id`) ON DELETE SET NULL
);

-- Tabla de Asistentes
CREATE TABLE `Asistentes` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `fullname` VARCHAR(100) NOT NULL,
  `username` VARCHAR(50) UNIQUE NOT NULL,
  `password` CHAR(102) NOT NULL,
  `rol_id` INT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`rol_id`) REFERENCES `Roles` (`id`) ON DELETE SET NULL
);

-- Tabla de Asignaciones de Asistente
CREATE TABLE `AsignacionesAsistente` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `asistente_id` INT,
  `laboratorio_id` INT,
  FOREIGN KEY (`asistente_id`) REFERENCES `Asistentes` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`laboratorio_id`) REFERENCES `Laboratorios` (`id`) ON DELETE CASCADE
);

-- Tipos de Mantenimiento simplificado
CREATE TABLE `TiposMantenimiento` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `codigo` ENUM('MPI', 'MPE') NOT NULL,
  `nombre` VARCHAR(100) NOT NULL
);

-- Insertar tipos de mantenimiento
INSERT INTO `TiposMantenimiento` (`codigo`, `nombre`) VALUES
('MPI', 'Mantenimiento Preventivo Interno'),
('MPE', 'Mantenimiento Preventivo Externo');

-- Programación de mantenimientos (PLAN ANUAL)
CREATE TABLE `ProgramacionMantenimiento` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `equipo_id` INT,
  `tipo_mantenimiento_id` INT,
  `anio` YEAR NOT NULL,
  `mes` TINYINT NOT NULL COMMENT 'Mes programado (1-12)',
  FOREIGN KEY (`equipo_id`) REFERENCES `Equipos` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`tipo_mantenimiento_id`) REFERENCES `TiposMantenimiento` (`id`) ON DELETE CASCADE,
  UNIQUE KEY `uk_programacion` (`equipo_id`, `tipo_mantenimiento_id`, `mes`, `anio`)
);

-- Registro de mantenimientos (EJECUCIÓN Y SEGUIMIENTO)
CREATE TABLE `RegistroMantenimiento` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `programacion_id` INT,
  `estado` ENUM('PROGRAMADO', 'REALIZADO') DEFAULT 'PROGRAMADO',
  `fecha_realizado` DATE,
  `realizado_por` INT,
  FOREIGN KEY (`programacion_id`) REFERENCES `ProgramacionMantenimiento` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`realizado_por`) REFERENCES `Asistentes` (`id`) ON DELETE SET NULL
);