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

    @classmethod
    def save(cls, negocio_id, nombre_promocion, precio=None, descripcion=None,
              imagen=None, fecha_inicio=None, fecha_fin=None):
        if not nombre_promocion:
            raise ValueError("Missing required fields")

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
    def delete(cls, promocion_id):
        query = "DELETE FROM promociones WHERE id = %(id)s"
        return connectToMySQL(DB_NAME).query_db(query, {'id': promocion_id})