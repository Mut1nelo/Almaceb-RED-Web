USE almaceb_red;

-- Conserva el límite de cuatro negocios por vendedor: usa una cuenta de negocio
-- con espacio suficiente y reutiliza el mismo propietario si se ejecuta otra vez.
SET @ranking_owner_id := COALESCE(
    (
        SELECT usuario_id
        FROM negocios
        WHERE nombre_negocio = 'Café Aurora'
        LIMIT 1
    ),
    (
        SELECT u.id
        FROM usuarios u
        LEFT JOIN negocios n ON n.usuario_id = u.id
        WHERE u.account_type = 'business'
        GROUP BY u.id
        HAVING COUNT(n.id) <= 1
        ORDER BY COUNT(n.id), u.id
        LIMIT 1
    )
);

INSERT INTO negocios (
    usuario_id, nombre_negocio, business_type, lat, lon, direccion,
    telefono, correo, descripcion,
    horario_dia_inicio, horario_dia_fin, horario_hora_inicio, horario_hora_fin,
    imagen_banner, imagen_perfil, valoracion
)
SELECT
    @ranking_owner_id, 'Café Aurora', 'Cafetería', -33.5418, -70.6442,
    'San Ramón, Santiago', NULL, NULL,
    'Cafetería de barrio con preparaciones para compartir.',
    'Lunes', 'Sábado', '08:00:00', '20:00:00',
    'imgs/products/5.jpg', 'imgs/default-business.png', 0.0
WHERE @ranking_owner_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM negocios WHERE nombre_negocio = 'Café Aurora');

INSERT INTO negocios (
    usuario_id, nombre_negocio, business_type, lat, lon, direccion,
    telefono, correo, descripcion,
    horario_dia_inicio, horario_dia_fin, horario_hora_inicio, horario_hora_fin,
    imagen_banner, imagen_perfil, valoracion
)
SELECT
    @ranking_owner_id, 'Pastelería Dulce Barrio', 'Pastelería', -33.5389, -70.6481,
    'San Ramón, Santiago', NULL, NULL,
    'Pastelería local con productos preparados durante el día.',
    'Martes', 'Domingo', '09:00:00', '19:30:00',
    'imgs/products/8.jpg', 'imgs/default-business.png', 0.0
WHERE @ranking_owner_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM negocios WHERE nombre_negocio = 'Pastelería Dulce Barrio');

INSERT INTO negocios (
    usuario_id, nombre_negocio, business_type, lat, lon, direccion,
    telefono, correo, descripcion,
    horario_dia_inicio, horario_dia_fin, horario_hora_inicio, horario_hora_fin,
    imagen_banner, imagen_perfil, valoracion
)
SELECT
    @ranking_owner_id, 'Verdulería El Encuentro', 'Verdulería', -33.5451, -70.6407,
    'San Ramón, Santiago', NULL, NULL,
    'Frutas y verduras para las compras cotidianas del barrio.',
    'Lunes', 'Domingo', '08:30:00', '20:30:00',
    'imgs/default-business.png', 'imgs/icons/vegetables-salad-svgrepo-com.svg', 0.0
WHERE @ranking_owner_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM negocios WHERE nombre_negocio = 'Verdulería El Encuentro');
