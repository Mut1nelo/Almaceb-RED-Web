# Importamos la función que devolverá una instancia de una conexión
from mysqlconnection import connectToMySQL

# Creamos la clase basada en la tabla de mascotas
class Usuario:
   def __init__( self , data ):
       self.id = data['id']
       self.email = data['email']
       self.password_hash = data['password_hash']
       self.nombre = data['nombre']
       self.direccion = data['direccion']
       self.descripcion = data['descripcion']
       self.horario_apertura = data['horario_apertura']
       self.horario_cierre = data['horario_cierre']
       self.foto_perfil = data['foto_perfil']
       self.rol_id = data['rol_id']
       self.activo = data['activo']
       self.created_at = data['created_at']
       self.updated_at = data['updated_at']

   # Creamos un método de clase para consultar nuestra base de datos
   @classmethod
   def get_all(cls):
       query = "SELECT * FROM usuarios;"

       # Llamamos a función connectToMySQL con el esquema al que te diriges
       resultados = connectToMySQL('almacen_red').query_db(query)

       # Creamos una lista vacía para agregar nuestras instancias de mascota
       usuarios = []

       # Iteramos sobre los resultados de la base de datos y crear instancias de mascota con cls
       for usuario in resultados:
           usuarios.append( cls(usuario) )
       return usuarios
   
   @classmethod
   def search(cls, term):
       query = """
           SELECT * FROM usuarios
           WHERE nombre LIKE %(term)s
              OR email LIKE %(term)s
              OR direccion LIKE %(term)s
              OR descripcion LIKE %(term)s
           ORDER BY nombre ASC;
       """
       parametros = {'term': f"%{term}%"}
       resultados = connectToMySQL('almacen_red').query_db(query, parametros)
       return [cls(usuario) for usuario in resultados]
   
   @classmethod
   def save(cls, data):
    query = "INSERT INTO usuarios (email, password_hash, nombre, direccion, descripcion, foto_perfil, rol_id, activo) VALUES (%(email)s, %(password_hash)s, %(nombre)s, %(direccion)s, %(descripcion)s, %(foto_perfil)s, %(rol_id)s, %(activo)s)"
    return connectToMySQL('almacen_red').query_db(query, data)