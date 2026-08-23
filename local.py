from mysqlconnection import connectToMySQL

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

class Business:
    def __init__(self, data):
        self.id = data['id']
        self.nombre_negocio = data['nombre_negocio']
        self.business_type = data['business_type']
    # El formulario de creación pide una dirección y obtiene correctamente las coordenadas, pero Flask solamente guarda esto:
        self.lat = data['lat']
        self.lon = data['lon']
    # La dirección se pierde.

    # La tabla negocios actual no tiene usuario_id, así que no sabemos quién es dueño del negocio.

    # Antes de conectar business.html con Jinja, conviene agregar a la tabla:
    # Nombre, Categoría, Descripción, Dirección, Teléfono, Correo, Horarios, Imagen y las promociones

    @classmethod
    def save(cls, nombre_negocio, business_type, lat, lon):
        if not nombre_negocio or lat is None or lon is None:
            raise ValueError("Missing required fields")

        if business_type not in BUSINESS_TYPES:
            raise ValueError("Invalid business type")

        query = """
            INSERT INTO negocios (nombre_negocio, business_type, lat, lon)
            VALUES (%(nombre_negocio)s, %(business_type)s, %(lat)s, %(lon)s)
        """
        data = {
            'nombre_negocio': nombre_negocio,
            'business_type': business_type,
            'lat': lat,
            'lon': lon
        }

        result = connectToMySQL('almaceb_red').query_db(query, data)

        if result is False:
            # NOTE: nombre_negocio is UNIQUE — a duplicate name will land here too
            raise RuntimeError("Failed to save business (possibly a duplicate name)")

        return result

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM negocios"
        results = connectToMySQL('almaceb_red').query_db(query)

        if results is False:
            raise RuntimeError("Failed to fetch businesses")

        return [cls(row) for row in results]

    @classmethod
    def get_by_id(cls, negocio_id):

        query = """
            SELECT *
            FROM negocios
            WHERE id = %(id)s;
        """

        data = {
            "id": negocio_id
        }

        results = connectToMySQL('almaceb_red').query_db(
            query,
            data
        )

        if not results:
            return None

        return cls(results[0])

    @classmethod
    def update(
        cls,
        negocio_id,
        nombre_negocio,
        business_type,
        lat,
        lon
    ):

        query = """
            UPDATE negocios
            SET
                nombre_negocio = %(nombre_negocio)s,
                business_type = %(business_type)s,
                lat = %(lat)s,
                lon = %(lon)s
            WHERE id = %(id)s;
        """

        data = {
            "id": negocio_id,
            "nombre_negocio": nombre_negocio,
            "business_type": business_type,
            "lat": lat,
            "lon": lon
        }

        return connectToMySQL('almaceb_red').query_db(
            query,
            data
        )