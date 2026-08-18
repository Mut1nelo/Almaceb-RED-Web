# Este servidor solo tiene los enrutamientos, back-end lo maneja Jose Moena
from flask import Flask, render_template, request, redirect, session, jsonify, flash
from difflib import SequenceMatcher
from usuario import Usuario, Locales
from werkzeug.security import generate_password_hash, check_password_hash
from mysqlconnection import connectToMySQL
import requests
from local import LocalNegocio

app = Flask(__name__)

app.secret_key = "clavehipermegasupersecretayiaaaa" #Cambiala hijo de tu mamita


#Aqui van todas las funciones q tengamos q declarar fuera d una ruta

# Datos de ejemplo - Reemplaza con tu base de datos
NEGOCIOS = [
    {"id": 1, "nombre": "Panadería El Grano", "categoria": "Panadería", "descripcion": "Pan fresco diario", "direccion": "Calle 1 #123"},
    {"id": 2, "nombre": "Almacén Central", "categoria": "Almacén", "descripcion": "Todo para el hogar", "direccion": "Av. Principal 456"},
    {"id": 3, "nombre": "Tienda de Ropa Urban", "categoria": "Ropa", "descripcion": "Moda casual y deportiva", "direccion": "Centro Comercial"},
    {"id": 4, "nombre": "Burger House", "categoria": "Comida Rapida", "descripcion": "Café y pasteles", "direccion": "Plaza Central"},
]

PROMOCIONES = [
    {"id": 1, "titulo": "Descuento 20% en pan", "negocio_id": 1, "descripcion": "Todo el pan con 20% de descuento"},
    {"id": 2, "titulo": "Compra 2 lleva 3", "negocio_id": 2, "descripcion": "Ofertas en artículos seleccionados"},
    {"id": 3, "titulo": "10% off en compras mayores a $50", "negocio_id": 3, "descripcion": "Aplica en prendas seleccionadas"},
]

def calcular_similitud(query, texto):
    if not texto:
        return 0
    return SequenceMatcher(None, query.lower(), str(texto).lower()).ratio()

def buscar_en_lista(query, lista, campos_busqueda):
    # Si la búsqueda está vacía o es muy corta, devolvemos todos los locales de la BD
    if not query or len(query.strip()) < 2:
        return lista
    
    query = query.strip()
    resultados = []
    
    for item in lista:
        max_similitud = 0
        for campo in campos_busqueda:
            # Como 'item' es una instancia de la clase Locales, usamos getattr() para leer sus atributos
            valor_campo = getattr(item, campo, None)
            if valor_campo:
                similitud = calcular_similitud(query, valor_campo)
                max_similitud = max(max_similitud, similitud)
        
        # Filtro de tolerancia (30% de coincidencia mínima)
        if max_similitud >= 0.3:
            resultados.append({"item": item, "relevancia": max_similitud})
    
    # Ordenar de mayor a menor relevancia
    resultados.sort(key=lambda x: x["relevancia"], reverse=True)
    return [r["item"] for r in resultados]

def geocode_das_address(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "countrycodes": "cl",
            "limit": 1,
            "accept-language": "es",
        }
        headers = {
            "User-Agent": "AlmacebREDsigmatoilet/6.7 (josefranciscomoenarios@gmail.com)"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else None

    except Exception as e:
        print(f"Error de geolocalizacion", {e} )
        return None


# Enrutamiento de las páginas web
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/Mapa")
def map():
    #Si no estan en la sesion los manda a logearse jijiji
    if 'user_id' not in session:
        return redirect('/Iniciar-sesión')

    usuarios = Usuario.get_all_users()
    username = session.get('username', 'Invitado')
    account_type = session.get('account_type', 'invitado')
    print(f"DEBUG: username={username}, account_type={account_type}")  

    negocios = Locales.get_all_businesess()

    return render_template(
        "map.html",
        usuarios=usuarios,
        username=username,
        account_type=account_type,
        negocios=negocios)

    #Ahora buscamos los negocios
    


    # result = None
    # if request.method == 'POST':
    #     address = request.form.get('address') or user.address
    #     if address:
    #         try:
    #             result = geocode_address(address)
    #             if result:
    #                 user.address = address
    #                 user.lat = float(result['lat'])
    #                 user.lon = float(result['lon'])
    #                 db.session.commit()
    #             else:
    #                 result = []
    #         except requests.exceptions.RequestException:
    #             flash('Error al consultar el servicio de geocodificación. Intenta de nuevo.', 'error')
    #             result = []
    #         except ValueError:
    #             flash('Respuesta no válida del servicio de geocodificación.', 'error')
    #             result = []
    #lo comente pq a lo mejor lo necesitamos dsps 

@app.route("/Registrarse")
def register():
    return render_template("form-register.html")

@app.route("/Registro", methods=["POST"])
def registrar_usuario():

    password_hash = generate_password_hash(request.form['password'])

    data_usuario = {
        "username": request.form['username'],
        "email": request.form['email'],
        "password": password_hash,
        "account_type": request.form['account_type']
    }

    user_id = Usuario.save(data_usuario)

    session['user_id'] = user_id
    session['username'] = request.form['username']
    session['account_type'] = request.form['account_type']

    return redirect('/Mapa')

@app.route("/Login")
def login_page():
    return render_template("form-login.html")

@app.route("/Iniciar-sesion", methods=["POST"])
def login():

    data = {"email": request.form['email']}
    usuario_encontrado = Usuario.check_users(data)
    
    if not usuario_encontrado:
        flash("Usuario o contraseña incorrectos.", "login")
        #flasheamos confianza
        return redirect('/Iniciar-sesión')

    #soy un maldito desarrollador
    #aqui me tienes haciendo codigos de mierda
    #por que alguien no mueve su maldito gordo trasero para ayudarme 🗣‼
    if check_password_hash(usuario_encontrado.password, request.form['password']):
        session['user_id'] = usuario_encontrado.id
        session['username'] = usuario_encontrado.username
        session['account_type'] = usuario_encontrado.account_type
        print(f"DEBUG LOGIN: account_type set to {session['account_type']}")
        return redirect('/Mapa')
    
    flash("Usuario o contraseña incorrectos.", "login")
    return redirect('/Iniciar-sesión')

@app.route("/Mi-negocio", methods=["GET", "POST"])
def mi_negocio():
    if 'user_id' not in session:
        return redirect('/Iniciar-sesión')
    
    user_id = session['user_id']
    account_type = session.get('account_type')
    if account_type != 'business':
        flash("Solo usuarios de tipo negocio pueden acceder aquí", "error")
        return redirect('/Mapa')
    
    if request.method == "POST":
        nombre_local = request.form.get('nombre_local')
        direccion = request.form.get('direccion')
        
        if nombre_local and direccion:
            geocode_result = geocode_das_address(direccion)
            
            if geocode_result:
                data = {
                    'usuario_id': user_id,
                    'nombre_local': nombre_local,
                    'direccion': direccion,
                    'lat': float(geocode_result['lat']),
                    'lon': float(geocode_result['lon'])
                }
                LocalNegocio.save(data)
                flash("Ubicación guardada correctamente", "success")
                return redirect('/Mi-negocio')
            else:
                flash("No se encontraron coordenadas para esa dirección", "error")
        else:
            flash("Por favor completa todos los campos", "error")
    
    locales = LocalNegocio.get_by_usuario(user_id)
    username = session.get('username', 'Negocio')
    
    map_data = {
        'center_lat': locales[0].lat if locales else -33.8688,  # Default Santiago
        'center_lon': locales[0].lon if locales else -51.2093,
        'locales': [
            {
                'id': locale.id,
                'nombre': locale.nombre_local,
                'lat': locale.lat,
                'lon': locale.lon,
                'direccion': locale.direccion
            }
            for locale in locales
        ]
    }
    
    return render_template(
        "mi-negocio.html",
        username=username,
        locales=locales,
        map_data=map_data,
        account_type=account_type
    )

@app.route("/Mi-negocio/eliminar/<int:locale_id>", methods=["POST"])
def eliminar_locale(locale_id):
    if 'user_id' not in session or session.get('account_type') != 'business':
        return redirect('/Iniciar-sesión')
    
    LocalNegocio.delete(locale_id)
    flash("Ubicación eliminada", "success")
    return redirect('/Mi-negocio')

@app.route("/Reportes")
def report():
    return render_template("report.html")

@app.route("/Editar-negocio") #Cambia despues el nombre, lo puse porque no se me ocurrió otro
def form_business():
    return render_template("form-business.html")

@app.route("/Cerrar-sesión")
def logout():
    session.clear()
    return redirect("/")

@app.route("/search", methods=['GET'])
def search_businesses():
    # Capturamos el texto del input 'name="q"' de tu formulario HTML
    query_busqueda = request.args.get('q', '').strip()
    
    # 1. Traemos todos los locales mediante el método que corregimos en tu modelo
    todos_los_locales = Locales.get_all_businesess()
    
    # 2. Ejecutamos tu lógica real de ordenamiento y filtrado por relevancia
    campos_a_evaluar = ['nombre_negocio', 'business_type']
    locales_filtrados = buscar_en_lista(query_busqueda, todos_los_locales, campos_a_evaluar)
    
    # 3. Renderizamos exactamente la misma plantilla del mapa
    # Pasamos únicamente los locales que pasaron el filtro de similitud
    return render_template(
        'map.html', 
        lista_negocios=locales_filtrados,
        username='invitado',     # Sustituye con tu lógica real de sesión si aplica
        account_type='client'    # Sustituye con tu lógica real de sesión si aplica
    )

    @app.route("/Crear-negocio")
def create_business():
    pass

@app.route("/Funciones-futuras")
def future_function():
    return render_template("future-function.html")

# Para desarrolladores

@app.route("/Dev-page")
def dev_page():
    return render_template("dev-pages.html")

if __name__ == "__main__":
    app.run(debug=True)