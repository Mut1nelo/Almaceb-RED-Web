USE almaceb_red;

-- Datos editables del perfil de usuario.
ALTER TABLE usuarios
    ADD COLUMN telefono VARCHAR(20) NULL AFTER account_type,
    ADD COLUMN bio VARCHAR(500) NULL AFTER telefono,
    ADD COLUMN foto_perfil VARCHAR(255) NULL AFTER bio;

-- Valoración real almacenada para poder ordenar los negocios destacados.
ALTER TABLE negocios
    ADD COLUMN valoracion DECIMAL(2,1) NOT NULL DEFAULT 0.0 AFTER imagen_perfil;

-- Seguidores queda pendiente hasta que exista una relación real usuario-negocio.
-- No agregar ni consultar una cifra ficticia en esta migración.
