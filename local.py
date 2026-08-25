from mysqlconnection import connectToMySQL

DB_NAME = 'almaceb_red'

BUSINESS_TYPES = [
    'Almacén',
    'Bazar',
    'Cafetería',
    'Comida rápida',
    'Panadería',
    'Pastelería',
    'Restaurante',
    'Verdulería'
]

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']


class Business:
    def __init__(self, data):
        self.id = data['id']
        self.nombre_negocio = data['nombre_negocio']
        self.business_type = data['business_type']
        self.lat = data['lat']
        self.lon = data['lon']
        self.direccion = data.get('direccion')
        self.telefono = data.get('telefono')
        self.correo = data.get('correo')
        self.descripcion = data.get('descripcion')
        self.horario_dia_inicio = data.get('horario_dia_inicio')
        self.horario_dia_fin = data.get('horario_dia_fin')
        self.horario_hora_inicio = data.get('horario_hora_inicio')
        self.horario_hora_fin = data.get('horario_hora_fin')
        self.imagen_banner = data.get('imagen_banner')
        self.imagen_perfil = data.get('imagen_perfil')

    @classmethod
    def save(cls, nombre_negocio, business_type, lat, lon, direccion=None,
              telefono=None, correo=None, descripcion=None,
              horario_dia_inicio=None, horario_dia_fin=None,
              horario_hora_inicio=None, horario_hora_fin=None,
              imagen_banner=None, imagen_perfil=None):

        if not nombre_negocio or lat is None or lon is None:
            raise ValueError("Missing required fields")

        if business_type not in BUSINESS_TYPES:
            raise ValueError("Invalid business type")

        query = """
            INSERT INTO negocios (
                nombre_negocio, business_type, lat, lon, direccion,
                telefono, correo, descripcion,
                horario_dia_inicio, horario_dia_fin,
                horario_hora_inicio, horario_hora_fin,
                imagen_banner, imagen_perfil
            )
            VALUES (
                %(nombre_negocio)s, %(business_type)s, %(lat)s, %(lon)s, %(direccion)s,
                %(telefono)s, %(correo)s, %(descripcion)s,
                %(horario_dia_inicio)s, %(horario_dia_fin)s,
                %(horario_hora_inicio)s, %(horario_hora_fin)s,
                %(imagen_banner)s, %(imagen_perfil)s
            )
        """
        data = {
            'nombre_negocio': nombre_negocio,
            'business_type': business_type,
            'lat': lat,
            'lon': lon,
            'direccion': direccion,
            'telefono': telefono,
            'correo': correo,
            'descripcion': descripcion,
            'horario_dia_inicio': horario_dia_inicio,
            'horario_dia_fin': horario_dia_fin,
            'horario_hora_inicio': horario_hora_inicio,
            'horario_hora_fin': horario_hora_fin,
            'imagen_banner': imagen_banner,
            'imagen_perfil': imagen_perfil
        }

        result = connectToMySQL(DB_NAME).query_db(query, data)

        if result is False:
            raise RuntimeError("Failed to save business (possibly a duplicate name)")

        return result

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM negocios"
        results = connectToMySQL(DB_NAME).query_db(query)

        if results is False:
            raise RuntimeError("Failed to fetch businesses")

        return [cls(row) for row in results]

    @classmethod
    def get_by_id(cls, negocio_id):
        query = "SELECT * FROM negocios WHERE id = %(id)s;"
        data = {"id": negocio_id}

        results = connectToMySQL(DB_NAME).query_db(query, data)

        if not results:
            return None

        return cls(results[0])

    @classmethod
    def update(cls, negocio_id, nombre_negocio, business_type, lat, lon,
               direccion=None, telefono=None, correo=None, descripcion=None,
               horario_dia_inicio=None, horario_dia_fin=None,
               horario_hora_inicio=None, horario_hora_fin=None,
               imagen_banner=None, imagen_perfil=None):

        if not nombre_negocio or lat is None or lon is None:
            raise ValueError("Missing required fields")

        if business_type not in BUSINESS_TYPES:
            raise ValueError("Invalid business type")

        query = """
            UPDATE negocios
            SET
                nombre_negocio = %(nombre_negocio)s,
                business_type = %(business_type)s,
                lat = %(lat)s,
                lon = %(lon)s,
                direccion = %(direccion)s,
                telefono = %(telefono)s,
                correo = %(correo)s,
                descripcion = %(descripcion)s,
                horario_dia_inicio = %(horario_dia_inicio)s,
                horario_dia_fin = %(horario_dia_fin)s,
                horario_hora_inicio = %(horario_hora_inicio)s,
                horario_hora_fin = %(horario_hora_fin)s,
                imagen_banner = %(imagen_banner)s,
                imagen_perfil = %(imagen_perfil)s
            WHERE id = %(id)s;
        """
        data = {
            "id": negocio_id,
            "nombre_negocio": nombre_negocio,
            "business_type": business_type,
            "lat": lat,
            "lon": lon,
            "direccion": direccion,
            "telefono": telefono,
            "correo": correo,
            "descripcion": descripcion,
            "horario_dia_inicio": horario_dia_inicio,
            "horario_dia_fin": horario_dia_fin,
            "horario_hora_inicio": horario_hora_inicio,
            "horario_hora_fin": horario_hora_fin,
            "imagen_banner": imagen_banner,
            "imagen_perfil": imagen_perfil
        }

        result = connectToMySQL(DB_NAME).query_db(query, data)

        if result is False:
            raise RuntimeError("Failed to update business")

        return result