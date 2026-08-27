from mysqlconnection import connectToMySQL
from datetime import datetime, time as time_type

DB_NAME = 'almaceb_red'
MAX_BUSINESSES_PER_USER = 4

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

def esta_abierto(business):
    """Devuelve True si el negocio está abierto en este momento, False si no,
    y None si el negocio no configuró un horario."""

    if not (business.horario_dia_inicio and business.horario_dia_fin
            and business.horario_hora_inicio and business.horario_hora_fin):
        return None

    ahora = datetime.now()
    dia_actual = DIAS_SEMANA[ahora.weekday()]  # weekday(): Lunes=0 ... Domingo=6
    hora_actual = ahora.time()

    idx_inicio = DIAS_SEMANA.index(business.horario_dia_inicio)
    idx_fin = DIAS_SEMANA.index(business.horario_dia_fin)
    idx_actual = DIAS_SEMANA.index(dia_actual)

    # 1. Comprobar si HOY cae dentro del rango de días
    if idx_inicio <= idx_fin:
        dia_valido = idx_inicio <= idx_actual <= idx_fin
    else:
        # el rango cruza el fin de semana, ej: Viernes a Lunes
        dia_valido = idx_actual >= idx_inicio or idx_actual <= idx_fin

    if not dia_valido:
        return False

    # 2. Comprobar si la HORA actual cae dentro del rango horario
    hora_inicio = business.horario_hora_inicio
    hora_fin = business.horario_hora_fin

    # Si vienen como timedelta (típico de PyMySQL con columnas TIME), conviértelos a time
    if not isinstance(hora_inicio, time_type):
        hora_inicio = (datetime.min + hora_inicio).time()
    if not isinstance(hora_fin, time_type):
        hora_fin = (datetime.min + hora_fin).time()

    if hora_inicio <= hora_fin:
        return hora_inicio <= hora_actual <= hora_fin
    else:
        # el horario cruza la medianoche, ej: 22:00 a 02:00
        return hora_actual >= hora_inicio or hora_actual <= hora_fin

class Business:
    def __init__(self, data):
        self.id = data['id']
        self.usuario_id = data.get('usuario_id')
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
        self.valoracion = float(data.get('valoracion') or 0)

    @classmethod
    def save(cls, usuario_id, nombre_negocio, business_type, lat, lon, direccion=None,
              telefono=None, correo=None, descripcion=None,
              horario_dia_inicio=None, horario_dia_fin=None,
              horario_hora_inicio=None, horario_hora_fin=None,
              imagen_banner=None, imagen_perfil=None):

        if not usuario_id or not nombre_negocio or lat is None or lon is None:
            raise ValueError("Missing required fields")

        if business_type not in BUSINESS_TYPES:
            raise ValueError("Invalid business type")

        if cls.count_by_user(usuario_id) >= MAX_BUSINESSES_PER_USER:
            raise ValueError("Has alcanzado el límite de 4 negocios por cuenta")

        query = """
            INSERT INTO negocios (
                usuario_id, nombre_negocio, business_type, lat, lon, direccion,
                telefono, correo, descripcion,
                horario_dia_inicio, horario_dia_fin,
                horario_hora_inicio, horario_hora_fin,
                imagen_banner, imagen_perfil
            )
            VALUES (
                %(usuario_id)s, %(nombre_negocio)s, %(business_type)s, %(lat)s, %(lon)s, %(direccion)s,
                %(telefono)s, %(correo)s, %(descripcion)s,
                %(horario_dia_inicio)s, %(horario_dia_fin)s,
                %(horario_hora_inicio)s, %(horario_hora_fin)s,
                %(imagen_banner)s, %(imagen_perfil)s
            )
        """
        data = {
            'usuario_id': usuario_id,
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
    def get_by_user(cls, usuario_id):
        query = """
            SELECT * FROM negocios
            WHERE usuario_id = %(usuario_id)s
            ORDER BY updated_at DESC, id DESC;
        """
        results = connectToMySQL(DB_NAME).query_db(query, {"usuario_id": usuario_id})

        if results is False:
            raise RuntimeError("Failed to fetch businesses for user")

        return [cls(row) for row in results]

    @classmethod
    def get_featured(cls, category='Todos', order='valoracion'):
        filter_categories = ['Panadería', 'Pastelería', 'Almacén', 'Cafetería', 'Verdulería']
        query = "SELECT * FROM negocios"
        data = {}

        if category in filter_categories:
            query += " WHERE business_type = %(category)s"
            data['category'] = category
        elif category == 'Otras':
            placeholders = []
            for index, category_name in enumerate(filter_categories):
                key = f'category_{index}'
                placeholders.append(f'%({key})s')
                data[key] = category_name
            query += f" WHERE business_type NOT IN ({', '.join(placeholders)})"

        if order == 'valoracion':
            query += " ORDER BY valoracion DESC, updated_at DESC, nombre_negocio ASC"

        # Cuando exista una columna o relación real de seguidores, se podrá habilitar:
        # elif order == 'seguidores':
        #     query += " ORDER BY seguidores DESC, valoracion DESC, nombre_negocio ASC"

        query += " LIMIT 6;"
        results = connectToMySQL(DB_NAME).query_db(query, data)

        if results is False:
            raise RuntimeError("Failed to fetch featured businesses")

        return [cls(row) for row in results]

    @classmethod
    def count_by_user(cls, usuario_id):
        query = "SELECT COUNT(*) AS total FROM negocios WHERE usuario_id = %(usuario_id)s;"
        results = connectToMySQL(DB_NAME).query_db(query, {"usuario_id": usuario_id})

        if results is False:
            raise RuntimeError("Failed to count businesses for user")

        return int(results[0]['total'])

    @classmethod
    def get_by_id(cls, negocio_id):
        query = "SELECT * FROM negocios WHERE id = %(id)s;"
        data = {"id": negocio_id}

        results = connectToMySQL(DB_NAME).query_db(query, data)

        if not results:
            return None

        return cls(results[0])

    @classmethod
    def get_by_id_for_user(cls, negocio_id, usuario_id):
        query = """
            SELECT * FROM negocios
            WHERE id = %(id)s AND usuario_id = %(usuario_id)s;
        """
        data = {"id": negocio_id, "usuario_id": usuario_id}
        results = connectToMySQL(DB_NAME).query_db(query, data)

        if not results:
            return None

        return cls(results[0])

    @classmethod
    def update(cls, negocio_id, usuario_id, nombre_negocio, business_type, lat, lon,
               direccion=None, telefono=None, correo=None, descripcion=None,
               horario_dia_inicio=None, horario_dia_fin=None,
               horario_hora_inicio=None, horario_hora_fin=None,
               imagen_banner=None, imagen_perfil=None):

        if not usuario_id or not nombre_negocio or lat is None or lon is None:
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
            WHERE id = %(id)s AND usuario_id = %(usuario_id)s;
        """
        data = {
            "id": negocio_id,
            "usuario_id": usuario_id,
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
