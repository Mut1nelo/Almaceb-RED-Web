# ======================================================================================
# Jose, tratemos de usar enrutamientos sin tildes porque nos confunde siempre y da error
# ======================================================================================

# Desarrollo y enrutamientos lo maneja Javier Faúndez, back-end y base de datos lo maneja Jose Moena
from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
from difflib import SequenceMatcher
from usuario import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from mysqlconnection import connectToMySQL
import requests
from local import Business, BUSINESS_TYPES
import json

app = Flask(__name__)

app.secret_key = "clavehipermegasupersecretayiaaaa" #Cambiala hijo de tu mamita


#Aqui van todas las funciones q tengamos q declarar fuera d una ruta

def calcular_similitud(query, texto):
    if not texto:
        return 0
    return SequenceMatcher(None, query.lower(), str(texto).lower()).ratio()


def buscar_en_lista(query, lista, campos_busqueda):
    if not query or len(query.strip()) < 2:
        return lista

    query = query.strip()
    resultados = []

    for item in lista:
        max_similitud = 0
        for campo in campos_busqueda:
            valor_campo = getattr(item, campo, None)
            if valor_campo:
                similitud = calcular_similitud(query, valor_campo)
                max_similitud = max(max_similitud, similitud)

        if max_similitud >= 0.3:
            resultados.append({"item": item, "relevancia": max_similitud})

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
    #Si no estan en la sesion los manda a logearse jijiji, no ya no lo hace 😞
    if 'user_id' not in session:
        account_type = 'invitado'

    usuarios = Usuario.get_all_users()
    username = session.get('username', 'invitado')
    account_type = session.get('account_type', 'invitado')
    print(f"DEBUG: username={username}, account_type={account_type}")  

    businesses = Business.get_all()
    businesses_json = json.dumps([
        {
            'id': b.id,
            'nombre_negocio': b.nombre_negocio,
            'business_type': b.business_type,
            'lat': float(b.lat),
            'lon': float(b.lon)
        }
        for b in businesses
    ])

    return render_template(
        "map.html",
        usuarios=usuarios,
        username=username,
        account_type=account_type,
        businesses_json=businesses_json)

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
        #flasheamos confianza | Estaba mal enrutada, con razón siempre me daba error de JINJA
        return redirect(url_for('login_page'))

    # Soy un maldito desarrollador
    # Aqui me tienes haciendo codigos de mierda
    # Por que alguien no mueve su maldito gordo trasero para ayudarme 🗣‼

    # No soy chatbot Claude 🗣‼

    if check_password_hash(usuario_encontrado.password, request.form['password']):
        session['user_id'] = usuario_encontrado.id
        session['username'] = usuario_encontrado.username
        session['account_type'] = usuario_encontrado.account_type
        print(f"DEBUG LOGIN: account_type set to {session['account_type']}")
        return redirect('/Mapa')
    
    flash("Usuario o contraseña incorrectos.", "login")
    return redirect(url_for('login_page'))

# Claude me hizo otra funcion jejej

# @app.route("/Mi-negocio", methods=["GET", "POST"])
# def mi_negocio():
#     if 'user_id' not in session:
#         return redirect('/Iniciar-sesion')
    
#     user_id = session['user_id']
#     account_type = session.get('account_type')
#     if account_type != 'business':
#         flash("Solo usuarios de tipo negocio pueden acceder aquí", "error")
#         return redirect('/Mapa')
    
#     if request.method == "POST":
#         nombre_local = request.form.get('nombre_local')
#         direccion = request.form.get('direccion')
        
#         if nombre_local and direccion:
#             geocode_result = geocode_das_address(direccion)
            
#             if geocode_result:
#                 data = {
#                     'usuario_id': user_id,
#                     'nombre_local': nombre_local,
#                     'direccion': direccion,
#                     'lat': float(geocode_result['lat']),
#                     'lon': float(geocode_result['lon'])
#                 }
#                 LocalNegocio.save(data)
#                 flash("Ubicación guardada correctamente", "success")
#                 return redirect('/Mi-negocio')
#             else:
#                 flash("No se encontraron coordenadas para esa dirección", "error")
#         else:
#             flash("Por favor completa todos los campos", "error")
    
#     locales = LocalNegocio.get_by_usuario(user_id)
#     username = session.get('username', 'Negocio')
    
#     map_data = {
#         'center_lat': locales[0].lat if locales else -33.8688,  # Default Santiago
#         'center_lon': locales[0].lon if locales else -51.2093,
#         'locales': [
#             {
#                 'id': locale.id,
#                 'nombre': locale.nombre_local,
#                 'lat': locale.lat,
#                 'lon': locale.lon,
#                 'direccion': locale.direccion
#             }
#             for locale in locales
#         ]
#     }
    
#     return render_template(
#         "mi-negocio.html",
#         username=username,
#         locales=locales,
#         map_data=map_data,
#         account_type=account_type
#     )

# @app.route("/Mi-negocio/eliminar/<int:locale_id>", methods=["POST"])
# def eliminar_locale(locale_id):
#     if 'user_id' not in session or session.get('account_type') != 'business':
#         return redirect('/Iniciar-sesion')
    
#     LocalNegocio.delete(locale_id)
#     flash("Ubicación eliminada", "success")
#     return redirect('/Mi-negocio')

@app.route("/Negocio")
def business():
    return redirect(url_for('future_function'))

# Te deje la plantilla
@app.route("/Negocio/<int:negocio_id>")
def negocio(negocio_id):
    return redirect(url_for('future_function'))
#Perate ya dsps lo arreglo q tengo sueño

@app.route("/Negocios-destacados")
def featured_business():
    return render_template("featured-business.html")

@app.route("/Reportes")
def report():
    return render_template("report.html")


@app.route('/Crear-negocio', methods=['GET', 'POST'])
def crear_negocio():
    # Cualquiera podía crear un negocio
    # 1. Comprobar que haya iniciado sesión
    if 'user_id' not in session:
        # Otro error de enrutamiento loco, ya lo corregi
        return redirect(url_for('login_page'))

    # 2. Comprobar que sea una cuenta de negocio
    if session.get('account_type') != 'business':
        # Con ! no puede entrar
        flash("Solo las cuentas de negocio pueden crear un negocio.", "error")
        return redirect(url_for('map'))

    # 3. Si cumple lo anterior, puede ver el formulario
    if request.method == 'GET':
        return render_template('form-business.html')

    #no seria innecesario ya q en el jinja2  se modifica lo q puede y no puede ver el usuario -J
    #igual bien, mas seguro -j

    # 4. POST: recibir datos del formulario
    nombre_negocio = request.form.get('business-name')
    business_type = request.form.get('business-type')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')

    try:
        Business.save(
            nombre_negocio,
            business_type,
            lat,
            lon
        )

        return redirect(url_for('map'))

    except ValueError as e:
        return render_template(
            'error.html',
            error=str(e)
        ), 400

    except Exception as e:
        return render_template(
            'error.html',
            error=str(e)
        ), 500
    # Error.html? Qué es eso? Se come?
    # Es mi poya con ceboya

@app.route("/Cerrar-sesión")
def logout():
    session.clear()
    return redirect("/")

#Esto lo voy a rehacer, ya lo rehice -J
@app.route("/search")
def search():
    query = request.args.get('q', '')

    all_businesses = Business.get_all()
    resultados = buscar_en_lista(query, all_businesses, ['nombre_negocio', 'business_type'])

    return jsonify([
        {
            'id': b.id,
            'nombre_negocio': b.nombre_negocio,
            'business_type': b.business_type,
            'lat': float(b.lat),
            'lon': float(b.lon)
        }
        for b in resultados
    ])

@app.route("/Configuracion")
def config():
    return redirect(url_for('future_function'))

@app.route("/Funciones-futuras")
def future_function():
    return render_template("future-function.html")

@app.route("/Ranking")
def ranking():
    return render_template("ranking.html")

# Para desarrolladores

@app.route("/Dev-page")
def dev_page():
    return render_template("dev-pages.html")

if __name__ == "__main__":
    app.run(debug=True)