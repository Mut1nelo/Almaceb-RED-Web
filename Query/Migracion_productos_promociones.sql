USE almaceb_red;

CREATE TABLE IF NOT EXISTS productos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    negocio_id INT NOT NULL,
    nombre_producto VARCHAR(100) NOT NULL,
    descripcion TEXT NULL,
    precio DECIMAL(10,2) NOT NULL,
    imagen VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_productos_negocio_id (negocio_id),
    FOREIGN KEY (negocio_id) REFERENCES negocios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS promociones (
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
    INDEX idx_promociones_negocio_id (negocio_id),
    INDEX idx_promociones_fechas (fecha_inicio, fecha_fin),
    FOREIGN KEY (negocio_id) REFERENCES negocios(id) ON DELETE CASCADE
);
