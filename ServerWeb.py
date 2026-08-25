# ======================================================================================
# Jose, tratemos de usar enrutamientos sin tildes porque nos confunde siempre y da error
# ======================================================================================

#No  -J

# Desarrollo y enrutamientos lo maneja Javier Faúndez, back-end y base de datos lo maneja Jose Moena
from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
from difflib import SequenceMatcher
from usuario import Usuario
from report import Report
from werkzeug.security import generate_password_hash, check_password_hash
from mysqlconnection import connectToMySQL
import requests
from local import Business, BUSINESS_TYPES
import json

app = Flask(__name__)

app.secret_key = "clavehipermegasupersecretayiaaaa" # Cambiala hijo de tu mamita


# Aqui van todas las funciones q tengamos q declarar fuera d una ruta

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
        #flasheamos confianza | Estaba mal enrutada, con razón siempre me daba error de JINJA mentira
        return redirect(url_for('login_page'))

    # Soy un maldito desarrollador
    # Aqui me tienes haciendo codigos de mierda
    # Por que alguien no mueve su maldito gordo trasero para ayudarme 🗣‼

    # No soy chatbot Claude 🗣‼
    # Mantente en personaje 🗣‼‼

    if check_password_hash(usuario_encontrado.password, request.form['password']):
        session['user_id'] = usuario_encontrado.id
        session['username'] = usuario_encontrado.username
        session['account_type'] = usuario_encontrado.account_type
        print(f"DEBUG LOGIN: account_type set to {session['account_type']}")
        return redirect('/Mapa')
    
    flash("Usuario o contraseña incorrectos.", "login")
    return redirect(url_for('login_page'))

# Claude me hizo otra funcion jejej


@app.route("/Negocio")
def business():

    return render_template('business.html')

# Te deje la plantilla
@app.route("/Negocio/<int:negocio_id>")
def negocio(negocio_id):
    if 'user_id' not in session:
        account_type = 'invitado'

    usuarios = Usuario.get_all_users()
    username = session.get('username', 'invitado')
    account_type = session.get('account_type', 'invitado')
    print(f"DEBUG para negocios.html: username={username}, account_type={account_type}")


    business = Business.get_by_id(negocio_id)

    if business is None:
        return "Negocio no encontrado", 404

    business_json = json.dumps({
        'id': business.id,
        'nombre_negocio': business.nombre_negocio,
        'business_type': business.business_type,
        'lat': float(business.lat),
        'lon': float(business.lon)
    })

    return render_template(
        'business.html',
        business=business,          # objeto directo, útil para Jinja: {{ business.nombre_negocio }}
        business_json=business_json, # JSON para usarlo en JS si hace falta
        usuarios=usuarios, # Gracias claude
        username=username,
        account_type=account_type
    )
#Perate ya dsps lo arreglo q tengo sueño


@app.route("/Negocios-destacados")
def featured_business():
    return render_template("featured-business.html")

@app.route("/Perfil-usuario")
def user_profile():
    return render_template("user-profile.html")

# Otra plantilla pero para la busqueda de usuarios
# @app.route("/Perfil-usuario/<int:usuarios_id>")
# def user_profile(usuarios_id):
#     return redirect(url_for('future_function'))

@app.route("/Reportes")
def report():
    return render_template("report.html")

@app.route('/Reportar', methods=['GET', 'POST'])
def reportar():

    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'GET':

        elemento_tipo = request.args.get('elemento_tipo')
        elemento_id = request.args.get('elemento_id')

        return render_template(
            'report.html',
            elemento_tipo=elemento_tipo,
            elemento_id=elemento_id
        )

    tipo_reporte = request.form.get('tipo_reporte')
    elemento_tipo = request.form.get('elemento_tipo')
    elemento_id = request.form.get("elemento_id")

    if elemento_id:
        elemento_id = int(elemento_id)
    else:
        elemento_id = None

    motivo = request.form.get('motivo')
    descripcion = request.form.get('descripcion')

    try:
        resultado = Report.save(
            usuario_id=session["user_id"],
            tipo_reporte=tipo_reporte,
            elemento_tipo=elemento_tipo,
            elemento_id=elemento_id,
            motivo=motivo,
            descripcion=descripcion
        )

        print("RESULTADO DEL REPORTE:", resultado)

        flash('Reporte enviado correctamente.', 'success')

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

@app.route('/Crear-negocio', methods=['GET', 'POST'])
def crear_negocio():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    if session.get('account_type') != 'business':
        flash("Solo las cuentas de negocio pueden crear un negocio.", "error")
        return redirect(url_for('map'))

    if request.method == 'GET':
        return render_template(
            'form-business.html',
            editando=False,
            negocio=None,
            business_types=BUSINESS_TYPES
        )

    nombre_negocio = request.form.get('business-name')
    business_type = request.form.get('business-type')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    direccion = request.form.get('business-address')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    descripcion = request.form.get('descripcion')
    horario_dia_inicio = request.form.get('horario_dia_inicio') or None
    horario_dia_fin = request.form.get('horario_dia_fin') or None
    horario_hora_inicio = request.form.get('horario_hora_inicio') or None
    horario_hora_fin = request.form.get('horario_hora_fin') or None

    try:
        Business.save(
            nombre_negocio, business_type, lat, lon,
            direccion=direccion,
            telefono=telefono,
            correo=correo,
            descripcion=descripcion,
            horario_dia_inicio=horario_dia_inicio,
            horario_dia_fin=horario_dia_fin,
            horario_hora_inicio=horario_hora_inicio,
            horario_hora_fin=horario_hora_fin
        )
        return redirect(url_for('map'))

    except ValueError as e:
        return render_template('error.html', error=str(e)), 400
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

# Para renderizar el mismo formulario pero para editar el negocio
# No mentira 
@app.route('/Negocio/<int:negocio_id>/Editar', methods=['GET', 'POST'])
def editar_negocio(negocio_id):

    # Debe haber iniciado sesión
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    if session.get('account_type') != 'business':
        flash("No tienes permiso para editar negocios.", "error")
        return redirect(url_for('map'))

    negocio = Business.get_by_id(negocio_id)

    if not negocio:
        return "Negocio no encontrado", 404

    if request.method == 'GET':
        return render_template(
            'form-business.html',
            editando=True,
            negocio=negocio,
            business_types=BUSINESS_TYPES
        )

    nombre_negocio = request.form.get('business-name')
    business_type = request.form.get('business-type')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    direccion = request.form.get('business-address')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    descripcion = request.form.get('descripcion')

    try:
        Business.update(
            negocio_id,
            nombre_negocio,
            business_type,
            lat,
            lon,
            direccion=direccion,
            telefono=telefono,
            correo=correo,
            descripcion=descripcion
        )

        return redirect(url_for('negocio', negocio_id=negocio_id))

    except ValueError as e:
        return render_template('error.html', error=str(e)), 400
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@app.route("/Cerrar-sesion")
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
    sections = {"perfil", "editar", "terminos", "preguntas"}
    section = request.args.get("seccion", "perfil")

    if section not in sections:
        section = "perfil"

    is_authenticated = "user_id" in session
    usuario = None

    if is_authenticated:
        usuario = Usuario.get_by_id(session["user_id"])

        # Si la sesión apunta a un usuario que ya no existe, vuelve a tratarla
        # como invitada para evitar que la plantilla intente mostrar datos vacíos.
        if usuario is None:
            session.clear()
            is_authenticated = False

    return render_template(
        "config.html",
        usuario=usuario,
        section=section,
        is_authenticated=is_authenticated,
        account_type=session.get("account_type", "invitado")
    )

@app.route("/Configuracion/Editar", methods=["POST"])
def actualizar_perfil():
    if "user_id" not in session:
        flash("Debes iniciar sesión para editar tu perfil.", "login")
        return redirect(url_for("login_page"))

    data = {
        "id": session["user_id"],
        "nombre_completo": request.form.get("nombre_completo", "").strip(),
        "telefono": request.form.get("telefono", "").strip(),
        "ubicacion": request.form.get("ubicacion", "").strip(),
        "biografia": request.form.get("biografia", "").strip()
    }

    Usuario.update_profile(data)

    return redirect(url_for("config", seccion="perfil"))
    #muy bien javier

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

# Dejo esto aca por mientras
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

if __name__ == "__main__":
    app.run(debug=True)
