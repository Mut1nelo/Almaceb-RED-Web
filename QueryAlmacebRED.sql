-- =========================================================
-- 1. CREACIÓN DE LA BASE DE DATOS
-- =========================================================
CREATE DATABASE IF NOT EXISTS almacen_red
CHARACTER SET utf8mb4
COLLATE utf8mb4_spanish_ci;

USE almacen_red;

-- =========================================================
-- 2. TABLA DE ROLES
-- =========================================================
CREATE TABLE roles (
    id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(45) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- =========================================================
-- 3. TABLA DE USUARIOS
-- Todos los tipos de cuenta se autentican desde esta tabla.
-- =========================================================
CREATE TABLE usuarios (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    foto_perfil LONGBLOB,
    rol_id TINYINT UNSIGNED NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_usuarios_roles
        FOREIGN KEY (rol_id)
        REFERENCES roles(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- 4. TABLA DE VENDEDORES
-- Guarda solo los datos comerciales adicionales.
-- =========================================================
CREATE TABLE vendedores (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT UNSIGNED NOT NULL UNIQUE,
    rut VARCHAR(12) NOT NULL UNIQUE,
    nombre_negocio VARCHAR(100) NOT NULL,
    direccion_negocio VARCHAR(255),
    descripcion TEXT,
    foto_negocio LONGBLOB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_vendedores_usuarios
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- 5. TABLA DE PRODUCTOS
-- Cada producto pertenece a un vendedor.
-- =========================================================
CREATE TABLE productos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    vendedor_id INT UNSIGNED NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(12,2) NOT NULL,
    stock INT UNSIGNED NOT NULL DEFAULT 0,
    foto_producto LONGBLOB,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_productos_precio
        CHECK (precio >= 0),

    CONSTRAINT fk_productos_vendedores
        FOREIGN KEY (vendedor_id)
        REFERENCES vendedores(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_productos_vendedor (vendedor_id),
    INDEX idx_productos_nombre (nombre),
    INDEX idx_productos_activo (activo)
) ENGINE=InnoDB;

-- =========================================================
-- 6. PRODUCTOS FAVORITOS
-- Relación muchos a muchos entre usuarios y productos.
-- =========================================================
CREATE TABLE productos_favoritos (
    usuario_id INT UNSIGNED NOT NULL,
    producto_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (usuario_id, producto_id),

    CONSTRAINT fk_productos_favoritos_usuarios
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_productos_favoritos_productos
        FOREIGN KEY (producto_id)
        REFERENCES productos(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_productos_favoritos_producto (producto_id)
) ENGINE=InnoDB;

-- =========================================================
-- 7. LIKES
-- Un usuario puede dar solo un like a cada producto.
-- =========================================================
CREATE TABLE likes (
    usuario_id INT UNSIGNED NOT NULL,
    producto_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (usuario_id, producto_id),

    CONSTRAINT fk_likes_usuarios
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_likes_productos
        FOREIGN KEY (producto_id)
        REFERENCES productos(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_likes_producto (producto_id)
) ENGINE=InnoDB;

-- =========================================================
-- 8. COMENTARIOS
-- =========================================================
CREATE TABLE comentarios (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT UNSIGNED NOT NULL,
    producto_id INT UNSIGNED NOT NULL,
    comentario TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_comentarios_usuarios
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_comentarios_productos
        FOREIGN KEY (producto_id)
        REFERENCES productos(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_comentarios_usuario (usuario_id),
    INDEX idx_comentarios_producto (producto_id),
    INDEX idx_comentarios_fecha (created_at)
) ENGINE=InnoDB;

-- =========================================================
-- 9. VENDEDORES FAVORITOS
-- =========================================================
CREATE TABLE vendedores_favoritos (
    usuario_id INT UNSIGNED NOT NULL,
    vendedor_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (usuario_id, vendedor_id),

    CONSTRAINT fk_vendedores_favoritos_usuarios
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_vendedores_favoritos_vendedores
        FOREIGN KEY (vendedor_id)
        REFERENCES vendedores(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_vendedores_favoritos_vendedor (vendedor_id)
) ENGINE=InnoDB;

-- =========================================================
-- 10. SEGUIDORES
-- Se conserva como concepto distinto a vendedor favorito.
-- =========================================================
CREATE TABLE seguidores (
    usuario_id INT UNSIGNED NOT NULL,
    vendedor_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (usuario_id, vendedor_id),

    CONSTRAINT fk_seguidores_usuarios
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_seguidores_vendedores
        FOREIGN KEY (vendedor_id)
        REFERENCES vendedores(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_seguidores_vendedor (vendedor_id)
) ENGINE=InnoDB;

-- =========================================================
-- 11. DATOS INICIALES SUGERIDOS
-- =========================================================
INSERT INTO roles (nombre)
VALUES ('administrador'), ('vendedor'), ('cliente');
