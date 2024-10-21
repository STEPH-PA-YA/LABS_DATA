CREATE TABLE `Carreras` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL
);

CREATE TABLE `Roles` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(50) NOT NULL,
  `funciones` TEXT
);

CREATE TABLE `Laboratorios` (
  `codigo` CHAR(10) PRIMARY KEY,
  `nombre` VARCHAR(100) NOT NULL,
  `ubicacion` VARCHAR(50),
  `carrera_id` INT,
  FOREIGN KEY (`carrera_id`) REFERENCES `Carreras` (`id`) ON DELETE SET NULL
);

CREATE TABLE `Equipos` (
  `codigo` CHAR(10) PRIMARY KEY,
  `nombre` VARCHAR(100) NOT NULL,
  `marca` VARCHAR(50),
  `modelo` VARCHAR(50),
  `serie` VARCHAR(50),
  `laboratorio_codigo` CHAR(10),
  FOREIGN KEY (`laboratorio_codigo`) REFERENCES `Laboratorios` (`codigo`) ON DELETE SET NULL
);

CREATE TABLE `Asistentes` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `fullname` VARCHAR(100) NOT NULL,
  `username` VARCHAR(50) UNIQUE NOT NULL,
  `password` CHAR(102) NOT NULL,
  `rol_id` INT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`rol_id`) REFERENCES `Roles` (`id`) ON DELETE SET NULL
);

CREATE TABLE `AsignacionesAsistente` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `asistente_id` INT,
  `laboratorio_codigo` CHAR(10),
  FOREIGN KEY (`asistente_id`) REFERENCES `Asistentes` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`laboratorio_codigo`) REFERENCES `Laboratorios` (`codigo`) ON DELETE CASCADE
);

CREATE TABLE `TiposMantenimiento` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nombre` VARCHAR(50) NOT NULL
);

CREATE TABLE `EquiposTiposMantenimiento` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `equipo_codigo` CHAR(10),
  `tipo_de_mantenimiento_id` INT,
  FOREIGN KEY (`equipo_codigo`) REFERENCES `Equipos` (`codigo`) ON DELETE CASCADE,
  FOREIGN KEY (`tipo_de_mantenimiento_id`) REFERENCES `TiposMantenimiento` (`id`) ON DELETE CASCADE
);

CREATE TABLE `CronogramasMantenimiento` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `equipo_codigo` CHAR(10),
  `mes_ejecucion` TINYINT,
  FOREIGN KEY (`equipo_codigo`) REFERENCES `Equipos` (`codigo`) ON DELETE CASCADE
);
