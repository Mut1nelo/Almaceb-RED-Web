#Script python de un local
from mysqlconnection import connectToMySQL

class LocalNegocio:
    def __init__(self, data):
        self.id = data['id']
        self.usuario_id = data['usuario_id']
        self.nombre_local = data['nombre_local']
        self.direccion = data['direccion']
        self.lat = data['lat']
        self.lon = data['lon']
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')

    @classmethod
    def get_by_usuario(cls, usuario_id):
        """Get all locations for a business user"""
        query = "SELECT * FROM locales_negocio WHERE usuario_id = %(usuario_id)s"
        resultados = connectToMySQL('almaceb_red').query_db(query, {'usuario_id': usuario_id})
        
        locales = []
        if resultados:
            for resultado in resultados:
                locales.append(cls(resultado))
        return locales

    @classmethod
    def save(cls, data):
        """Save a new business location"""
        query = "INSERT INTO locales_negocio (usuario_id, nombre_local, direccion, lat, lon) VALUES (%(usuario_id)s, %(nombre_local)s, %(direccion)s, %(lat)s, %(lon)s)"
        return connectToMySQL('almaceb_red').query_db(query, data)

    @classmethod
    def delete(cls, locale_id):
        """Delete a business location"""
        query = "DELETE FROM locales_negocio WHERE id = %(id)s"
        return connectToMySQL('almaceb_red').query_db(query, {'id': locale_id})

    @classmethod
    def update(cls, locale_id, data):
        """Update a business location"""
        query = "UPDATE locales_negocio SET nombre_local = %(nombre_local)s, direccion = %(direccion)s, lat = %(lat)s, lon = %(lon)s WHERE id = %(id)s"
        data['id'] = locale_id
        return connectToMySQL('almaceb_red').query_db(query, data)