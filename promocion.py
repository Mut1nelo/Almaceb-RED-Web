from mysqlconnection import connectToMySQL

DB_NAME = 'almaceb_red'


class Promocion:
    def __init__(self, data):
        self.id = data['id']
        self.negocio_id = data['negocio_id']
        self.nombre_promocion = data['nombre_promocion']
        self.precio = data.get('precio')
        self.descripcion = data.get('descripcion')
        self.imagen = data.get('imagen')
        self.fecha_inicio = data.get('fecha_inicio')
        self.fecha_fin = data.get('fecha_fin')
        self.nombre_negocio = data.get('nombre_negocio')
        self.business_type = data.get('business_type')
        self.direccion_negocio = data.get('direccion_negocio')
        self.imagen_negocio = data.get('imagen_negocio')
        self.banner_negocio = data.get('banner_negocio')
        self.lat = data.get('lat')
        self.lon = data.get('lon')

    @classmethod
    def save(cls, negocio_id, nombre_promocion, precio=None, descripcion=None,
              imagen=None, fecha_inicio=None, fecha_fin=None):
        if not nombre_promocion:
            raise ValueError("Missing required fields")

        if len(nombre_promocion) > 100:
            raise ValueError("El nombre de la promoción no puede superar los 100 caracteres")

        query = """
            INSERT INTO promociones
                (negocio_id, nombre_promocion, precio, descripcion, imagen, fecha_inicio, fecha_fin)
            VALUES
                (%(negocio_id)s, %(nombre_promocion)s, %(precio)s, %(descripcion)s,
                 %(imagen)s, %(fecha_inicio)s, %(fecha_fin)s)
        """
        data = {
            'negocio_id': negocio_id,
            'nombre_promocion': nombre_promocion,
            'precio': precio,
            'descripcion': descripcion,
            'imagen': imagen,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }

        result = connectToMySQL(DB_NAME).query_db(query, data)
        if result is False:
            raise RuntimeError("Failed to save promocion")
        return result

    @classmethod
    def get_by_negocio(cls, negocio_id):
        query = "SELECT * FROM promociones WHERE negocio_id = %(negocio_id)s ORDER BY created_at DESC"
        results = connectToMySQL(DB_NAME).query_db(query, {'negocio_id': negocio_id})

        if results is False:
            raise RuntimeError("Failed to fetch promociones")

        return [cls(row) for row in results]

    @classmethod
    def get_by_id_for_business(cls, promocion_id, negocio_id):
        query = """
            SELECT * FROM promociones
            WHERE id = %(id)s AND negocio_id = %(negocio_id)s
        """
        results = connectToMySQL(DB_NAME).query_db(query, {
            'id': promocion_id,
            'negocio_id': negocio_id
        })

        if not results:
            return None
        return cls(results[0])

    @classmethod
    def update(cls, promocion_id, negocio_id, nombre_promocion, precio=None,
               descripcion=None, imagen=None, fecha_inicio=None, fecha_fin=None):
        if not nombre_promocion:
            raise ValueError("El nombre de la promoción es obligatorio")

        if len(nombre_promocion) > 100:
            raise ValueError("El nombre de la promoción no puede superar los 100 caracteres")

        query = """
            UPDATE promociones
            SET nombre_promocion = %(nombre_promocion)s,
                precio = %(precio)s,
                descripcion = %(descripcion)s,
                imagen = %(imagen)s,
                fecha_inicio = %(fecha_inicio)s,
                fecha_fin = %(fecha_fin)s
            WHERE id = %(id)s AND negocio_id = %(negocio_id)s
        """
        result = connectToMySQL(DB_NAME).query_db(query, {
            'id': promocion_id,
            'negocio_id': negocio_id,
            'nombre_promocion': nombre_promocion,
            'precio': precio,
            'descripcion': descripcion,
            'imagen': imagen,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        })

        if result is False:
            raise RuntimeError("Failed to update promocion")
        return result

    @classmethod
    def get_active_counts(cls, negocio_ids=None):
        """Devuelve la cantidad de promociones activas agrupada por negocio."""
        if negocio_ids is not None and not negocio_ids:
            return {}

        query = """
            SELECT negocio_id, COUNT(*) AS total
            FROM promociones
            WHERE (fecha_inicio IS NULL OR fecha_inicio <= CURDATE())
              AND (fecha_fin IS NULL OR fecha_fin >= CURDATE())
        """
        data = {}

        if negocio_ids is not None:
            placeholders = []
            for index, negocio_id in enumerate(negocio_ids):
                key = f'negocio_{index}'
                placeholders.append(f'%({key})s')
                data[key] = negocio_id
            query += f" AND negocio_id IN ({', '.join(placeholders)})"

        query += " GROUP BY negocio_id"
        results = connectToMySQL(DB_NAME).query_db(query, data)

        if results is False:
            raise RuntimeError("Failed to count active promotions")

        return {int(row['negocio_id']): int(row['total']) for row in results}

    @classmethod
    def get_active_searchable(cls):
        """Obtiene promociones activas junto con los datos públicos del negocio."""
        query = """
            SELECT
                p.*,
                n.nombre_negocio,
                n.business_type,
                n.direccion AS direccion_negocio,
                n.imagen_perfil AS imagen_negocio,
                n.imagen_banner AS banner_negocio,
                n.lat,
                n.lon
            FROM promociones p
            INNER JOIN negocios n ON n.id = p.negocio_id
            WHERE (p.fecha_inicio IS NULL OR p.fecha_inicio <= CURDATE())
              AND (p.fecha_fin IS NULL OR p.fecha_fin >= CURDATE())
            ORDER BY p.updated_at DESC, p.id DESC;
        """
        results = connectToMySQL(DB_NAME).query_db(query)

        if results is False:
            raise RuntimeError("Failed to fetch active promotions")

        return [cls(row) for row in results]

    @classmethod
    def delete(cls, promocion_id):
        query = "DELETE FROM promociones WHERE id = %(id)s"
        return connectToMySQL(DB_NAME).query_db(query, {'id': promocion_id})
