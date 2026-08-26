from mysqlconnection import connectToMySQL

DB_NAME = 'almaceb_red'


class Producto:
    def __init__(self, data):
        self.id = data['id']
        self.negocio_id = data['negocio_id']
        self.nombre_producto = data['nombre_producto']
        self.descripcion = data.get('descripcion')
        self.precio = data['precio']
        self.imagen = data.get('imagen')

    @classmethod
    def save(cls, negocio_id, nombre_producto, precio, descripcion=None, imagen=None):
        if not nombre_producto or precio is None:
            raise ValueError("Missing required fields")

        query = """
            INSERT INTO productos (negocio_id, nombre_producto, descripcion, precio, imagen)
            VALUES (%(negocio_id)s, %(nombre_producto)s, %(descripcion)s, %(precio)s, %(imagen)s)
        """
        data = {
            'negocio_id': negocio_id,
            'nombre_producto': nombre_producto,
            'descripcion': descripcion,
            'precio': precio,
            'imagen': imagen
        }

        result = connectToMySQL(DB_NAME).query_db(query, data)
        if result is False:
            raise RuntimeError("Failed to save producto")
        return result

    @classmethod
    def get_by_negocio(cls, negocio_id):
        query = "SELECT * FROM productos WHERE negocio_id = %(negocio_id)s ORDER BY created_at DESC"
        results = connectToMySQL(DB_NAME).query_db(query, {'negocio_id': negocio_id})

        if results is False:
            raise RuntimeError("Failed to fetch productos")

        return [cls(row) for row in results]

    @classmethod
    def get_by_id(cls, producto_id):
        query = "SELECT * FROM productos WHERE id = %(id)s"
        results = connectToMySQL(DB_NAME).query_db(query, {'id': producto_id})

        if not results:
            return None
        return cls(results[0])

    @classmethod
    def delete(cls, producto_id):
        query = "DELETE FROM productos WHERE id = %(id)s"
        return connectToMySQL(DB_NAME).query_db(query, {'id': producto_id})