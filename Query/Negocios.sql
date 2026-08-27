USE almaceb_red;

-- ============================================================
-- ALMACEB RED - DATOS DE DEMOSTRACIÓN PARA LA FERIA TP 2026
-- ============================================================
--
-- Crea:
--   4 negocios
--   16 productos
--   8 promociones
--
-- Las promociones están vigentes durante la feria.
--
-- IMPORTANTE:
-- Intenta escoger automáticamente una cuenta VENDEDOR
-- que tenga espacio para los cuatro negocios.
-- ============================================================


-- ------------------------------------------------------------
-- 1. BUSCAR PROPIETARIO
-- ------------------------------------------------------------

SET @usuario_demo := (
    SELECT u.id
    FROM usuarios u
    LEFT JOIN negocios n
        ON n.usuario_id = u.id
    WHERE u.account_type = 'business'
    GROUP BY u.id
    HAVING COUNT(n.id) = 0
    ORDER BY u.id
    LIMIT 1
);

-- Ver qué usuario fue seleccionado.
SELECT
    @usuario_demo AS usuario_propietario_demo;


-- ============================================================
-- 2. NEGOCIOS
-- ============================================================


-- ------------------------------------------------------------
-- PANADERÍA LA JUANA
-- ------------------------------------------------------------

INSERT INTO negocios (
    usuario_id,
    nombre_negocio,
    business_type,
    lat,
    lon,
    direccion,
    telefono,
    correo,
    descripcion,
    horario_dia_inicio,
    horario_dia_fin,
    horario_hora_inicio,
    horario_hora_fin,
    imagen_banner,
    imagen_perfil,
    valoracion
)
SELECT
    @usuario_demo,
    'Panadería La Juana',
    'Panadería',
    -33.5415,
    -70.6435,
    'San Ramón, Santiago',
    '+56 9 4567 1122',
    'lajuana@almaceb.cl',
    'Panadería de barrio con pan fresco, masas dulces y productos preparados durante el día.',
    'Lunes',
    'Sábado',
    '07:30:00',
    '20:30:00',
    'imgs/products/6.jpg',
    'imgs/default-business.png',
    4.8
WHERE @usuario_demo IS NOT NULL
AND NOT EXISTS (
    SELECT 1
    FROM negocios
    WHERE nombre_negocio = 'Panadería La Juana'
);


-- ------------------------------------------------------------
-- CAFÉ AURORA
-- ------------------------------------------------------------

INSERT INTO negocios (
    usuario_id,
    nombre_negocio,
    business_type,
    lat,
    lon,
    direccion,
    telefono,
    correo,
    descripcion,
    horario_dia_inicio,
    horario_dia_fin,
    horario_hora_inicio,
    horario_hora_fin,
    imagen_banner,
    imagen_perfil,
    valoracion
)
SELECT
    @usuario_demo,
    'Café Aurora',
    'Cafetería',
    -33.5395,
    -70.6460,
    'San Ramón, Santiago',
    '+56 9 6678 2233',
    'aurora@almaceb.cl',
    'Cafetería local con café, preparaciones dulces y opciones para compartir.',
    'Lunes',
    'Sábado',
    '08:00:00',
    '20:00:00',
    'imgs/products/4.jpg',
    'imgs/default-business.png',
    4.6
WHERE @usuario_demo IS NOT NULL
AND NOT EXISTS (
    SELECT 1
    FROM negocios
    WHERE nombre_negocio = 'Café Aurora'
);


-- ------------------------------------------------------------
-- PASTELERÍA DULCE BARRIO
-- ------------------------------------------------------------

INSERT INTO negocios (
    usuario_id,
    nombre_negocio,
    business_type,
    lat,
    lon,
    direccion,
    telefono,
    correo,
    descripcion,
    horario_dia_inicio,
    horario_dia_fin,
    horario_hora_inicio,
    horario_hora_fin,
    imagen_banner,
    imagen_perfil,
    valoracion
)
SELECT
    @usuario_demo,
    'Pastelería Dulce Barrio',
    'Pastelería',
    -33.5440,
    -70.6480,
    'San Ramón, Santiago',
    '+56 9 7789 3344',
    'dulcebarrio@almaceb.cl',
    'Pastelería de barrio especializada en tortas, berlines, galletas y preparaciones dulces.',
    'Martes',
    'Domingo',
    '09:00:00',
    '19:30:00',
    'imgs/products/2.jpg',
    'imgs/default-business.png',
    4.9
WHERE @usuario_demo IS NOT NULL
AND NOT EXISTS (
    SELECT 1
    FROM negocios
    WHERE nombre_negocio = 'Pastelería Dulce Barrio'
);


-- ------------------------------------------------------------
-- ALMACÉN EL ENCUENTRO
-- ------------------------------------------------------------

INSERT INTO negocios (
    usuario_id,
    nombre_negocio,
    business_type,
    lat,
    lon,
    direccion,
    telefono,
    correo,
    descripcion,
    horario_dia_inicio,
    horario_dia_fin,
    horario_hora_inicio,
    horario_hora_fin,
    imagen_banner,
    imagen_perfil,
    valoracion
)
SELECT
    @usuario_demo,
    'Almacén El Encuentro',
    'Almacén',
    -33.5460,
    -70.6415,
    'San Ramón, Santiago',
    '+56 9 8890 4455',
    'encuentro@almaceb.cl',
    'Almacén familiar con productos para las compras cotidianas del barrio.',
    'Lunes',
    'Domingo',
    '08:30:00',
    '21:00:00',
    'imgs/products/5.jpg',
    'imgs/default-business.png',
    4.5
WHERE @usuario_demo IS NOT NULL
AND NOT EXISTS (
    SELECT 1
    FROM negocios
    WHERE nombre_negocio = 'Almacén El Encuentro'
);


-- ============================================================
-- 3. OBTENER LOS ID DE LOS NEGOCIOS
-- ============================================================

SET @panaderia_id := (
    SELECT id FROM negocios
    WHERE nombre_negocio = 'Panadería La Juana'
    LIMIT 1
);

SET @cafe_id := (
    SELECT id FROM negocios
    WHERE nombre_negocio = 'Café Aurora'
    LIMIT 1
);

SET @pasteleria_id := (
    SELECT id FROM negocios
    WHERE nombre_negocio = 'Pastelería Dulce Barrio'
    LIMIT 1
);

SET @almacen_id := (
    SELECT id FROM negocios
    WHERE nombre_negocio = 'Almacén El Encuentro'
    LIMIT 1
);


-- ============================================================
-- 4. PRODUCTOS - PANADERÍA LA JUANA
-- ============================================================

INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @panaderia_id,
    'Hallullas',
    'Hallullas frescas preparadas durante la mañana.',
    1200,
    'imgs/products/6.jpg'
WHERE @panaderia_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @panaderia_id
      AND nombre_producto = 'Hallullas'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @panaderia_id,
    'Pan amasado',
    'Pan amasado tradicional recién horneado.',
    1500,
    'imgs/products/5.jpg'
WHERE @panaderia_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @panaderia_id
      AND nombre_producto = 'Pan amasado'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @panaderia_id,
    'Croissant',
    'Croissant de masa suave y dorada.',
    1300,
    'imgs/products/4.jpg'
WHERE @panaderia_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @panaderia_id
      AND nombre_producto = 'Croissant'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @panaderia_id,
    'Palmerita',
    'Masa dulce horneada ideal para acompañar el café.',
    1000,
    'imgs/products/8.jpg'
WHERE @panaderia_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @panaderia_id
      AND nombre_producto = 'Palmerita'
);


-- ============================================================
-- 5. PRODUCTOS - CAFÉ AURORA
-- ============================================================

INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @cafe_id,
    'Café + Croissant',
    'Café caliente acompañado de un croissant recién preparado.',
    2990,
    'imgs/products/4.jpg'
WHERE @cafe_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @cafe_id
      AND nombre_producto = 'Café + Croissant'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @cafe_id,
    'Berlines',
    'Berlines dulces para acompañar tu café.',
    1500,
    'imgs/products/1.jpg'
WHERE @cafe_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @cafe_id
      AND nombre_producto = 'Berlines'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @cafe_id,
    'Galletas artesanales',
    'Galletas rellenas ideales para compartir.',
    1800,
    'imgs/products/3.jpg'
WHERE @cafe_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @cafe_id
      AND nombre_producto = 'Galletas artesanales'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @cafe_id,
    'Cupcake del día',
    'Cupcake preparado diariamente con distintos sabores.',
    2000,
    'imgs/products/7.jpg'
WHERE @cafe_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @cafe_id
      AND nombre_producto = 'Cupcake del día'
);


-- ============================================================
-- 6. PRODUCTOS - PASTELERÍA DULCE BARRIO
-- ============================================================

INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @pasteleria_id,
    'Torta de chocolate',
    'Porción de torta de chocolate con crema.',
    3500,
    'imgs/products/2.jpg'
WHERE @pasteleria_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @pasteleria_id
      AND nombre_producto = 'Torta de chocolate'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @pasteleria_id,
    'Berlines rellenos',
    'Berlines rellenos con crema pastelera.',
    1600,
    'imgs/products/1.jpg'
WHERE @pasteleria_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @pasteleria_id
      AND nombre_producto = 'Berlines rellenos'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @pasteleria_id,
    'Galletas de frambuesa',
    'Galletas dulces con centro de frambuesa.',
    2200,
    'imgs/products/3.jpg'
WHERE @pasteleria_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @pasteleria_id
      AND nombre_producto = 'Galletas de frambuesa'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @pasteleria_id,
    'Caja de cupcakes',
    'Selección de cupcakes decorados de distintos sabores.',
    6990,
    'imgs/products/7.jpg'
WHERE @pasteleria_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @pasteleria_id
      AND nombre_producto = 'Caja de cupcakes'
);


-- ============================================================
-- 7. PRODUCTOS - ALMACÉN EL ENCUENTRO
-- ============================================================

INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @almacen_id,
    'Pan para once',
    'Selección de pan fresco disponible durante el día.',
    1800,
    'imgs/products/6.jpg'
WHERE @almacen_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @almacen_id
      AND nombre_producto = 'Pan para once'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @almacen_id,
    'Galletas dulces',
    'Galletas para acompañar la once.',
    1500,
    'imgs/products/3.jpg'
WHERE @almacen_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @almacen_id
      AND nombre_producto = 'Galletas dulces'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @almacen_id,
    'Pack de hallullas',
    'Pack de hallullas frescas.',
    2000,
    'imgs/products/5.jpg'
WHERE @almacen_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @almacen_id
      AND nombre_producto = 'Pack de hallullas'
);


INSERT INTO productos
(negocio_id, nombre_producto, descripcion, precio, imagen)
SELECT
    @almacen_id,
    'Dulces surtidos',
    'Selección de productos dulces para compartir.',
    2990,
    'imgs/products/7.jpg'
WHERE @almacen_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM productos
    WHERE negocio_id = @almacen_id
      AND nombre_producto = 'Dulces surtidos'
);


-- ============================================================
-- 8. PROMOCIONES
-- ============================================================


-- PANADERÍA

INSERT INTO promociones
(
    negocio_id,
    nombre_promocion,
    precio,
    descripcion,
    imagen,
    fecha_inicio,
    fecha_fin
)
SELECT
    @panaderia_id,
    '2 Hallullas + Café',
    '$1.990',
    'Llévate dos hallullas y un café a precio especial.',
    'imgs/products/6.jpg',
    '2026-08-27',
    '2026-08-30'
WHERE @panaderia_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM promociones
    WHERE negocio_id = @panaderia_id
      AND nombre_promocion = '2 Hallullas + Café'
);


INSERT INTO promociones
(
    negocio_id,
    nombre_promocion,
    precio,
    descripcion,
    imagen,
    fecha_inicio,
    fecha_fin
)
SELECT
    @panaderia_id,
    '20% de descuento en pan dulce',
    '20% OFF',
    'Promoción válida en productos seleccionados durante la feria.',
    'imgs/products/8.jpg',
    '2026-08-27',
    '2026-09-02'
WHERE @panaderia_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM promociones
    WHERE negocio_id = @panaderia_id
      AND nombre_promocion = '20% de descuento en pan dulce'
);


-- CAFÉ

INSERT INTO promociones
(
    negocio_id,
    nombre_promocion,
    precio,
    descripcion,
    imagen,
    fecha_inicio,
    fecha_fin
)
SELECT
    @cafe_id,
    'Café + Croissant',
    '$2.990',
    'Café caliente más croissant a precio promocional.',
    'imgs/products/4.jpg',
    '2026-08-27',
    '2026-08-31'
WHERE @cafe_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM promociones
    WHERE negocio_id = @cafe_id
      AND nombre_promocion = 'Café + Croissant'
);


INSERT INTO promociones
(
    negocio_id,
    nombre_promocion,
    precio,
    descripcion,
    imagen,
    fecha_inicio,
    fecha_fin
)
SELECT
    @cafe_id,
    'Segundo café al 50%',
    '50% OFF',
    'Compra un café y obtén el segundo con 50% de descuento.',
    'imgs/products/1.jpg',
    '2026-08-28',
    '2026-09-04'
WHERE @cafe_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM promociones
    WHERE negocio_id = @cafe_id
      AND nombre_promocion = 'Segundo café al 50%'
);


-- PASTELERÍA

INSERT INTO promociones
(
    negocio_id,
    nombre_promocion,
    precio,
    descripcion,
    imagen,
    fecha_inicio,
    fecha_fin
)
SELECT
    @pasteleria_id,
    'Torta del día',
    '$6.990',
    'Promoción especial en una selección de tortas del día.',
    'imgs/products/2.jpg',
    '2026-08-27',
    '2026-08-30'
WHERE @pasteleria_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM promociones
    WHERE negocio_id = @pasteleria_id
      AND nombre_promocion = 'Torta del día'
);


INSERT INTO promociones
(
    negocio_id,
    nombre_promocion,
    precio,
    descripcion,
    imagen,
    fecha_inicio,
    fecha_fin
)
SELECT
    @pasteleria_id,
    '3 Berlines por $3.500',
    '$3.500',
    'Elige tres berlines y llévalos por un precio especial.',
    'imgs/products/1.jpg',
    '2026-08-27',
    '2026-09-05'
WHERE @pasteleria_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM promociones
    WHERE negocio_id = @pasteleria_id
      AND nombre_promocion = '3 Berlines por $3.500'
);


-- ALMACÉN

INSERT INTO promociones
(
    negocio_id,
    nombre_promocion,
    precio,
    descripcion,
    imagen,
    fecha_inicio,
    fecha_fin
)
SELECT
    @almacen_id,
    'Pack para la once',
    '$4.990',
    'Pack de productos seleccionados ideal para compartir durante la once.',
    'imgs/products/5.jpg',
    '2026-08-27',
    '2026-09-03'
WHERE @almacen_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM promociones
    WHERE negocio_id = @almacen_id
      AND nombre_promocion = 'Pack para la once'
);


INSERT INTO promociones
(
    negocio_id,
    nombre_promocion,
    precio,
    descripcion,
    imagen,
    fecha_inicio,
    fecha_fin
)
SELECT
    @almacen_id,
    '10% en productos seleccionados',
    '10% OFF',
    'Descuento válido en una selección de productos del almacén.',
    'imgs/products/7.jpg',
    '2026-08-28',
    '2026-09-06'
WHERE @almacen_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM promociones
    WHERE negocio_id = @almacen_id
      AND nombre_promocion = '10% en productos seleccionados'
);


-- ============================================================
-- 9. COMPROBAR EL RESULTADO
-- ============================================================

SELECT
    n.id,
    n.nombre_negocio,
    n.business_type,
    n.usuario_id,
    COUNT(DISTINCT p.id) AS productos,
    COUNT(DISTINCT pr.id) AS promociones
FROM negocios n
LEFT JOIN productos p
    ON p.negocio_id = n.id
LEFT JOIN promociones pr
    ON pr.negocio_id = n.id
WHERE n.nombre_negocio IN (
    'Panadería La Juana',
    'Café Aurora',
    'Pastelería Dulce Barrio',
    'Almacén El Encuentro'
)
GROUP BY
    n.id,
    n.nombre_negocio,
    n.business_type,
    n.usuario_id
ORDER BY n.id;