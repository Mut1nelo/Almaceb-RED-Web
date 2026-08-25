# Importamos la función que devolverá una instancia de una conexión
from mysqlconnection import connectToMySQL

DB_NAME = 'almaceb_red'

# Creamos la clase basada en la tabla de usuarios (si, esto me lo robe de la tarea q hicimos jijiji)
class Usuario:
   def __init__( self , data ):
      self.id = data['id']
      self.username = data['username']
      self.email = data['email']
      self.password = data['password_hash']
      self.account_type = data['account_type']
      self.created_at = data['created_at']
      self.updated_at = data['updated_at']

   # Creamos un método de clase para consultar nuestra base de datos
   @classmethod
   def get_all_users(cls):
       query = "SELECT * FROM usuarios;"

       # Llamamos a función connectToMySQL con el esquema al que te diriges
       resultados = connectToMySQL(DB_NAME).query_db(query)

       # instancias bien lindas bonitas hermosas
       usuarios = []

       # Iteramos sobre los resultados de la base de datos y crear instancias del fokin usuario con fokin cls
       for usuario in resultados:
           usuarios.append( cls(usuario) )
       return usuarios

   @classmethod
   def save(cls, data):
    query = "INSERT INTO usuarios (username, email, password_hash, account_type) VALUES (%(username)s,%(email)s,%(password)s, %(account_type)s)"
    return connectToMySQL(DB_NAME).query_db(query, data)

   @classmethod
   def check_users(cls, data):
      #esto se explica solo la vdd, si no cachas le preguntas a chatjepete
      query = "SELECT * FROM usuarios WHERE email = %(email)s"
      resultado = connectToMySQL(DB_NAME).query_db(query, data)

      if len(resultado) < 1: #si es mas chico q 1 no retorna nada 
         return False
      return cls(resultado[0])

   @classmethod
   def get_by_id(cls, user_id):
    query = "SELECT * FROM usuarios WHERE id = %(id)s"
    resultado = connectToMySQL(DB_NAME).query_db(
        query,
        {"id": user_id}
    )

    if not resultado:
        return None

    return cls(resultado[0])

   @classmethod
   def update_location(cls, user_id, address, lat, lon):
      query = "UPDATE usuarios SET direccion = %(direccion)s, lat = %(lat)s, lan =%(lan)s WHERE id = %(id)s"
      data = {
         'id': user_id,
         'direccion': address,
         'lat': lat,
         'lon': lon
      }
      return connectToMySQL(DB_NAME).query_db(query, data)