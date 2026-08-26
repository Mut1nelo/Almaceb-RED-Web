USE almaceb_red;

-- Ejecutar una sola vez en instalaciones que ya tengan la tabla negocios.
-- Si existe un único vendedor, los negocios antiguos se vinculan a esa cuenta.
-- Si existen varios vendedores, asigna cada negocio manualmente antes del
-- ALTER ... NOT NULL para evitar atribuirlos al propietario incorrecto.

ALTER TABLE negocios
    ADD COLUMN usuario_id INT NULL AFTER id;

SET @cantidad_vendedores = (
    SELECT COUNT(*)
    FROM usuarios
    WHERE account_type = 'business'
);

SET @unico_vendedor = (
    SELECT MIN(id)
    FROM usuarios
    WHERE account_type = 'business'
);

UPDATE negocios
SET usuario_id = @unico_vendedor
WHERE usuario_id IS NULL
  AND @cantidad_vendedores = 1;

ALTER TABLE negocios
    MODIFY usuario_id INT NOT NULL,
    ADD INDEX idx_negocios_usuario_id (usuario_id),
    ADD CONSTRAINT fk_negocios_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE;
