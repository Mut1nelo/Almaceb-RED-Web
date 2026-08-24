CREATE DATABASE IF NOT EXISTS almaceb_red
CHARACTER SET utf8mb4
COLLATE utf8mb4_spanish_ci;

USE almaceb_red;

-- Create the usuarios table
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    account_type ENUM('client', 'business') DEFAULT 'client',
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

CREATE TABLE negocios (
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