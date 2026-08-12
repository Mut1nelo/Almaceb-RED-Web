# Importamos la función que devolverá una instancia de una conexión
from mysqlconnection import connectToMySQL

# Creamos la clase basada en la tabla de mascotas
class Usuario:
   def __init__( self , data ):
      self.id = data['id']
      self.nombre = data['username']
      self.apellido = data['apellido']
      self.email = data['email']
      self.created_at = data['created_at']
      self.updated_at = data['updated_at']

   # Creamos un método de clase para consultar nuestra base de datos
   @classmethod
   def get_all(cls):
       query = "SELECT * FROM usuarios;"

       # Llamamos a función connectToMySQL con el esquema al que te diriges
       resultados = connectToMySQL('usuarios_cr').query_db(query)

       # Creamos una lista vacía para agregar nuestras instancias de mascota
       usuarios = []

       # Iteramos sobre los resultados de la base de datos y crear instancias de mascota con cls
       for usuario in resultados:
           usuarios.append( cls(usuario) )
       return usuarios

   @classmethod
   def save(cls, data):
    query = "INSERT INTO usuarios (nombre, apellido, email) VALUES (%(nombre)s,%(apellido)s,%(email)s)"
    return connectToMySQL('usuarios_cr').query_db(query, data)