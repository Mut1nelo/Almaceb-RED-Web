CREATE DATABASE IF NOT EXISTS almaceb_red
CHARACTER SET utf8mb4
COLLATE utf8mb4_spanish_ci;

USE almaceb_red;

-- Crear la tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    account_type ENUM('client', 'business') DEFAULT 'client',

    telefono VARCHAR(20) NULL,
    bio VARCHAR(500) NULL,
    foto_perfil VARCHAR(255) NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reportes (
    id INT AUTO_INCREMENT PRIMARY KEY,

    usuario_id INT NOT NULL,

    tipo_reporte VARCHAR(50) NOT NULL,
    elemento_tipo VARCHAR(50) NOT NULL,
    elemento_id INT NULL,

    motivo VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500) NOT NULL,

    archivo VARCHAR(255) NULL,

    estado ENUM(
        'Pendiente',
        'En revisión',
        'Resuelto',
        'Descartado'
    ) NOT NULL DEFAULT 'Pendiente',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS locales_negocio (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    nombre_local VARCHAR(255) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    lat FLOAT NOT NULL,
    lon FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS negocios (
	id INT PRIMARY KEY AUTO_INCREMENT,
	nombre_negocio VARCHAR(64) NOT NULL UNIQUE,
    business_type ENUM(
        'Almacén',
        'Bazar',
        'Cafetería',
        'Comida rápida',
        'Panadería',
        'Pastelería',
        'Restaurante',
        'Verdulería'
    ) NOT NULL DEFAULT 'Almacén',
    lat FLOAT NOT NULL,
    lon FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

ALTER TABLE usuarios
ADD COLUMN telefono VARCHAR(20) NULL AFTER account_type,
ADD COLUMN bio VARCHAR(500) NULL AFTER telefono,
ADD COLUMN foto_perfil VARCHAR(255) NULL AFTER bio;

ALTER TABLE negocios
    ADD COLUMN direccion VARCHAR(255) NULL AFTER lon,
    ADD COLUMN telefono VARCHAR(20) NULL AFTER direccion,
    ADD COLUMN correo VARCHAR(100) NULL AFTER telefono,
    ADD COLUMN descripcion TEXT NULL AFTER correo,
    ADD COLUMN horario_dia_inicio ENUM('Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo') NULL AFTER descripcion,
    ADD COLUMN horario_dia_fin ENUM('Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo') NULL AFTER horario_dia_inicio,
    ADD COLUMN horario_hora_inicio TIME NULL AFTER horario_dia_fin,
    ADD COLUMN horario_hora_fin TIME NULL AFTER horario_hora_inicio,
    ADD COLUMN imagen_banner VARCHAR(255) NULL AFTER horario_hora_fin,
    ADD COLUMN imagen_perfil VARCHAR(255) NULL AFTER imagen_banner;

CREATE TABLE productos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    negocio_id INT NOT NULL,
    nombre_producto VARCHAR(100) NOT NULL,
    descripcion TEXT NULL,
    precio DECIMAL(10,2) NOT NULL,
    imagen VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (negocio_id) REFERENCES negocios(id) ON DELETE CASCADE
);

CREATE TABLE promociones (
    id INT PRIMARY KEY AUTO_INCREMENT,
    negocio_id INT NOT NULL,
    nombre_promocion VARCHAR(100) NOT NULL,
    precio VARCHAR(50) NULL,
    descripcion TEXT NULL,
    imagen VARCHAR(255) NULL,
    fecha_inicio DATE NULL,
    fecha_fin DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (negocio_id) REFERENCES negocios(id) ON DELETE CASCADE
);
-- Este tmb
-- CREATE TABLE IF NOT EXISTS promociones (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     negocio_id INT NOT NULL,
--     titulo VARCHAR(200) NOT NULL,
--     descripcion TEXT,
--     descuento_porcentaje DECIMAL(5, 2),
--     fecha_inicio DATE,
--     fecha_fin DATE,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     FOREIGN KEY (negocio_id) REFERENCES negocios(id) ON DELETE CASCADE
-- );