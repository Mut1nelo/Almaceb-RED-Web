# ======================================================================================
# Jose, tratemos de usar enrutamientos sin tildes porque nos confunde siempre y da error
# ======================================================================================
# Bueno -J

# Desarrollo y enrutamientos lo maneja Javier Faúndez, back-end y base de datos lo maneja Jose Moena
from flask import Flask, render_template, request, redirect, session, jsonify, flash, url_for
from difflib import SequenceMatcher
from usuario import Usuario
from report import Report
from werkzeug.security import generate_password_hash, check_password_hash
from mysqlconnection import connectToMySQL
import requests
from local import Business, BUSINESS_TYPES, MAX_BUSINESSES_PER_USER, esta_abierto
import json
import os
from werkzeug.utils import secure_filename
from uuid import uuid4
from PIL import Image
from producto import Producto
from promocion import Promocion
from decimal import Decimal, InvalidOperation

app = Flask(__name__)

app.secret_key = "clavehipermegasupersecretayiaaaa" # Cambiala hijo de tu mamita

# Límite global de tamaño de subida (aplica a TODO el request, no solo imágenes)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
UPLOAD_SUBFOLDER = 'imgs/negocios' #adentro de static

# Tamaños máximos por tipo de imagen (ancho, alto) en píxeles
MAX_DIMENSIONS = {
    'banner': (1600, 900),
    'perfil': (500, 500),
    'usuario': (500, 500)
}


@app.context_processor
def inject_session_user():
    """Mantiene nombre, tipo de cuenta y avatar disponibles en todas las plantillas."""
    current_user = None
    user_id = session.get('user_id')

    if user_id:
        current_user = Usuario.get_by_id(user_id)

        if current_user is None:
            session.clear()
        else:
            session['username'] = current_user.username
            session['account_type'] = current_user.account_type

    username = current_user.username if current_user else 'invitado'
    account_type = current_user.account_type if current_user else 'invitado'
    profile_image = (
        current_user.foto_perfil
        if current_user and current_user.foto_perfil
        else 'imgs/default.jpg'
    )

    return {
        'current_user': current_user,
        'username': username,
        'account_type': account_type,
        'profile_image': profile_image
    }

# Aqui van todas las funciones q tengamos q declarar fuera d una ruta

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def guardar_imagen(file_storage, tipo, subfolder=UPLOAD_SUBFOLDER):
    """tipo debe ser 'banner' o 'perfil', para saber a qué tamaño redimensionar."""
    if not file_storage or file_storage.filename == '':
        return None

    if not allowed_file(file_storage.filename):
        raise ValueError(f"Tipo de archivo no permitido: {file_storage.filename}")

    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    nombre_seguro = f"{uuid4().hex}.{ext}"

    carpeta_destino = os.path.join(app.root_path, 'static', subfolder)
    os.makedirs(carpeta_destino, exist_ok=True)
    ruta_completa = os.path.join(carpeta_destino, nombre_seguro)

    try:
        imagen = Image.open(file_storage.stream)
        imagen = imagen.convert('RGB') if ext in ('jpg', 'jpeg') else imagen

        max_ancho, max_alto = MAX_DIMENSIONS.get(tipo, (1600, 900))
        imagen.thumbnail((max_ancho, max_alto), Image.LANCZOS)  # mantiene proporción, no la deforma

        imagen.save(ruta_completa, optimize=True, quality=85)
    except Exception as e:
        raise ValueError(f"No se pudo procesar la imagen: {e}")

    return f"{subfolder}/{nombre_seguro}"

def calcular_similitud(query, texto):
    if not texto:
        return 0

    normalized_query = query.strip().casefold()
    normalized_text = str(texto).strip().casefold()

    if normalized_query == normalized_text:
        return 1
    if normalized_query in normalized_text:
        return 0.95

    whole_text_score = SequenceMatcher(None, normalized_query, normalized_text).ratio()
    word_score = max(
        (
            SequenceMatcher(None, normalized_query, word).ratio()
            for word in normalized_text.split()
        ),
        default=0
    )
    return max(whole_text_score, word_score * 0.9)

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

        if max_similitud >= 0.45:
            resultados.append({"item": item, "relevancia": max_similitud})

    resultados.sort(key=lambda x: x["relevancia"], reverse=True)
    return [r["item"] for r in resultados]


def media_url(path, fallback):
    """Convierte una ruta guardada en la BD en una URL pública de /static."""
    normalized_path = str(path or fallback).replace('\\', '/').strip()

    if normalized_path.startswith(('http://', 'https://')):
        return normalized_path
    if normalized_path.startswith('/static/'):
        return normalized_path
    if normalized_path.startswith('static/'):
        normalized_path = normalized_path[len('static/'):]

    return url_for('static', filename=normalized_path.lstrip('/'))

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


def require_business_account():
    if 'user_id' not in session:
        flash("Debes iniciar sesión con una cuenta de negocio para acceder.", "login")
        return redirect(url_for('login_page'))

    current_user = Usuario.get_by_id(session['user_id'])

    if current_user is None:
        session.clear()
        flash("Tu sesión ya no es válida. Inicia sesión nuevamente.", "login")
        return redirect(url_for('login_page'))

    session['username'] = current_user.username
    session['account_type'] = current_user.account_type

    if current_user.account_type != 'business':
        flash("Esta sección está disponible solo para cuentas de negocio.", "error")
        return redirect(url_for('map'))

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
    active_promotion_counts = Promocion.get_active_counts([business.id for business in businesses])
    businesses_json = json.dumps([
        {
            'id': b.id,
            'nombre_negocio': b.nombre_negocio,
            'business_type': b.business_type,
            'direccion': b.direccion,
            'lat': float(b.lat),
            'lon': float(b.lon),
            'image_url': media_url(b.imagen_perfil, 'imgs/default-business.png'),
            'card_image_url': media_url(
                b.imagen_banner or b.imagen_perfil,
                'imgs/default-business.png'
            ),
            'active_promotions': active_promotion_counts.get(b.id, 0),
            'featured': b.valoracion > 0,
            'url': url_for('negocio', negocio_id=b.id)
        }
        for b in businesses
    ])

    # La consulta viene ordenada por actualización: conservamos solo la promoción
    # activa más reciente de cada negocio para evitar que uno monopolice el panel.
    promotions_by_business = {}
    for promotion in Promocion.get_active_searchable():
        promotions_by_business.setdefault(promotion.negocio_id, promotion)

    promotions_json = json.dumps([
        {
            'id': promotion.id,
            'business_id': promotion.negocio_id,
            'business_name': promotion.nombre_negocio,
            'business_type': promotion.business_type,
            'promotion_name': promotion.nombre_promocion,
            'description': promotion.descripcion,
            'price': str(promotion.precio).strip() if promotion.precio is not None else None,
            'banner_url': media_url(
                promotion.banner_negocio,
                'imgs/default-business.png'
            ),
            'logo_url': media_url(
                promotion.imagen_negocio,
                'imgs/default-business.png'
            ),
            'lat': float(promotion.lat),
            'lon': float(promotion.lon),
            'end_date': promotion.fecha_fin.isoformat() if promotion.fecha_fin else None,
            'url': f"{url_for('negocio', negocio_id=promotion.negocio_id)}#promociones"
        }
        for promotion in promotions_by_business.values()
    ])

    return render_template(
        "map.html",
        usuarios=usuarios,
        username=username,
        account_type=account_type,
        businesses_json=businesses_json,
        promotions_json=promotions_json)

@app.route("/Registrarse")
def register():
    return render_template("form-register.html")

@app.route("/Registro", methods=["POST"])
def registrar_usuario():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    account_type = request.form.get("account_type", "client")

    if password != confirm_password:
        flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("register"))

    if account_type not in ("client", "business"):
        flash("Tipo de cuenta no válido.", "error")
        return redirect(url_for("register"))

    if Usuario.check_users({"email": email}):
        flash("Ya existe una cuenta con ese correo.", "error")
        return redirect(url_for("register"))

    try:
        foto_perfil = guardar_imagen(
            request.files.get("foto_perfil"),
            tipo="usuario",
            subfolder="imgs/usuarios"
        )

        user_id = Usuario.save({
            "username": username,
            "email": email,
            "password": generate_password_hash(password),
            "account_type": account_type,
            "telefono": request.form.get("telefono", "").strip() or None,
            "bio": request.form.get("bio", "").strip() or None,
            "foto_perfil": foto_perfil
        })

        if not user_id:
            flash("No se pudo crear la cuenta.", "error")
            return redirect(url_for("register"))

    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("register"))

    session["user_id"] = user_id
    session["username"] = username
    session["account_type"] = account_type

    return redirect(url_for("map"))

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
    #Por que url for??

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

    abierto = esta_abierto(business)
    productos = Producto.get_by_negocio(negocio_id)
    promociones = Promocion.get_by_negocio(negocio_id)

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
        abierto=abierto,
        productos=productos,
        promociones=promociones,
        usuarios=usuarios, # Gracias claude
        username=username,
        account_type=account_type,
        is_business_owner=session.get('user_id') == business.usuario_id
    )

@app.route("/Negocios-destacados")
def featured_business():
    featured_categories = {
        "Todos", "Panadería", "Pastelería", "Almacén",
        "Cafetería", "Verdulería", "Otras"
    }
    selected_category = request.args.get("categoria", "Todos")
    if selected_category not in featured_categories:
        selected_category = "Todos"

    selected_order = request.args.get("orden", "valoracion")
    if selected_order != "valoracion":
        selected_order = "valoracion"

    businesses = Business.get_featured(
        category=selected_category,
        order=selected_order
    )

    return render_template(
        "featured-business.html",
        businesses=businesses,
        selected_category=selected_category,
        selected_order=selected_order
    )

@app.route("/Perfil-usuario")
@app.route("/Perfil-usuario/<int:usuarios_id>")
def user_profile(usuarios_id=None):
    """Muestra el perfil público solicitado o el del usuario autenticado."""
    if usuarios_id is None:
        if 'user_id' not in session:
            flash("Inicia sesión para ver tu perfil público.", "login")
            return redirect(url_for('login_page'))
        usuarios_id = session['user_id']

    usuario = Usuario.get_by_id(usuarios_id)
    if usuario is None:
        return render_template('error.html', error="Usuario no encontrado"), 404

    is_owner = session.get('user_id') == usuario.id
    businesses = []

    if usuario.account_type == 'business':
        businesses = Business.get_by_user(usuario.id)
        promotion_counts = Promocion.get_active_counts([business.id for business in businesses])
        for business in businesses:
            business.active_promotions = promotion_counts.get(business.id, 0)

    meses = (
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    )
    member_since = (
        f"{meses[usuario.created_at.month - 1]} de {usuario.created_at.year}"
        if usuario.created_at else "fecha no disponible"
    )

    return render_template(
        "user-profile.html",
        usuario=usuario,
        businesses=businesses,
        is_owner=is_owner,
        member_since=member_since
    )

# Rutas para crear y editar promociones y productos

def owned_business_or_redirect(negocio_id):
    """Restringe la administración de contenido al propietario del negocio."""
    access_redirect = require_business_account()
    if access_redirect:
        return None, access_redirect

    negocio = Business.get_by_id_for_user(negocio_id, session['user_id'])
    if not negocio:
        flash("El negocio no existe o no pertenece a tu cuenta.", "error")
        return None, redirect(url_for('my_businesses'))

    return negocio, None


def validate_product_form():
    nombre_producto = (request.form.get('nombre_producto') or '').strip()
    descripcion = (request.form.get('descripcion') or '').strip() or None
    precio_text = (request.form.get('precio') or '').strip()

    if not nombre_producto:
        raise ValueError("Escribe el nombre del producto")

    try:
        precio = Decimal(precio_text)
    except (InvalidOperation, ValueError):
        raise ValueError("Ingresa un precio válido")

    if precio < 0:
        raise ValueError("El precio no puede ser negativo")

    return nombre_producto, descripcion, precio


def validate_promotion_form():
    nombre_promocion = (request.form.get('nombre_promocion') or '').strip()
    precio = (request.form.get('precio') or '').strip() or None
    descripcion = (request.form.get('descripcion') or '').strip() or None
    fecha_inicio = request.form.get('fecha_inicio') or None
    fecha_fin = request.form.get('fecha_fin') or None

    if not nombre_promocion:
        raise ValueError("Escribe el nombre de la promoción")

    if len(nombre_promocion) > 100:
        raise ValueError("El nombre de la promoción no puede superar los 100 caracteres")

    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        raise ValueError("La fecha de término no puede ser anterior a la fecha de inicio")

    return nombre_promocion, precio, descripcion, fecha_inicio, fecha_fin


@app.route('/Negocio/<int:negocio_id>/Agregar-producto', methods=['GET', 'POST'])
def agregar_producto(negocio_id):
    negocio, access_redirect = owned_business_or_redirect(negocio_id)
    if access_redirect:
        return access_redirect

    if request.method == 'GET':
        return render_template('form-producto.html', negocio=negocio, editando=False)

    try:
        nombre_producto, descripcion, precio = validate_product_form()
        imagen = guardar_imagen(
            request.files.get('imagen'),
            tipo='perfil',
            subfolder='imgs/productos'
        )
        Producto.save(
            negocio_id, nombre_producto, precio,
            descripcion=descripcion, imagen=imagen
        )
        flash("Producto publicado correctamente.", "success")
        return redirect(url_for('negocio', negocio_id=negocio_id))

    except ValueError as error:
        return render_template(
            'form-producto.html', negocio=negocio, editando=False,
            form_error=str(error)
        ), 400
    except Exception:
        app.logger.exception("No se pudo crear el producto")
        return render_template('error.html', error="No se pudo guardar el producto."), 500


@app.route('/Negocio/<int:negocio_id>/Producto/<int:producto_id>/Editar', methods=['GET', 'POST'])
def editar_producto(negocio_id, producto_id):
    negocio, access_redirect = owned_business_or_redirect(negocio_id)
    if access_redirect:
        return access_redirect

    producto = Producto.get_by_id_for_business(producto_id, negocio_id)
    if not producto:
        flash("El producto no existe en este negocio.", "error")
        return redirect(url_for('negocio', negocio_id=negocio_id))

    if request.method == 'GET':
        return render_template(
            'form-producto.html', negocio=negocio,
            producto=producto, editando=True
        )

    try:
        nombre_producto, descripcion, precio = validate_product_form()
        imagen_nueva = guardar_imagen(
            request.files.get('imagen'),
            tipo='perfil',
            subfolder='imgs/productos'
        )
        Producto.update(
            producto_id, negocio_id, nombre_producto, precio,
            descripcion=descripcion,
            imagen=imagen_nueva or producto.imagen
        )
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for('negocio', negocio_id=negocio_id))

    except ValueError as error:
        return render_template(
            'form-producto.html', negocio=negocio,
            producto=producto, editando=True, form_error=str(error)
        ), 400
    except Exception:
        app.logger.exception("No se pudo actualizar el producto")
        return render_template('error.html', error="No se pudo actualizar el producto."), 500


@app.route('/Negocio/<int:negocio_id>/Agregar-promocion', methods=['GET', 'POST'])
def agregar_promocion(negocio_id):
    negocio, access_redirect = owned_business_or_redirect(negocio_id)
    if access_redirect:
        return access_redirect

    if request.method == 'GET':
        return render_template('form-promocion.html', negocio=negocio, editando=False)

    try:
        nombre_promocion, precio, descripcion, fecha_inicio, fecha_fin = validate_promotion_form()
        imagen = guardar_imagen(
            request.files.get('imagen'),
            tipo='perfil',
            subfolder='imgs/promociones'
        )
        Promocion.save(
            negocio_id, nombre_promocion,
            precio=precio, descripcion=descripcion, imagen=imagen,
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
        )
        flash("Promoción publicada correctamente.", "success")
        return redirect(url_for('negocio', negocio_id=negocio_id))

    except ValueError as error:
        return render_template(
            'form-promocion.html', negocio=negocio, editando=False,
            form_error=str(error)
        ), 400
    except Exception:
        app.logger.exception("No se pudo crear la promoción")
        return render_template('error.html', error="No se pudo guardar la promoción."), 500


@app.route('/Negocio/<int:negocio_id>/Promocion/<int:promocion_id>/Editar', methods=['GET', 'POST'])
def editar_promocion(negocio_id, promocion_id):
    negocio, access_redirect = owned_business_or_redirect(negocio_id)
    if access_redirect:
        return access_redirect

    promocion = Promocion.get_by_id_for_business(promocion_id, negocio_id)
    if not promocion:
        flash("La promoción no existe en este negocio.", "error")
        return redirect(url_for('negocio', negocio_id=negocio_id))

    if request.method == 'GET':
        return render_template(
            'form-promocion.html', negocio=negocio,
            promocion=promocion, editando=True
        )

    try:
        nombre_promocion, precio, descripcion, fecha_inicio, fecha_fin = validate_promotion_form()
        imagen_nueva = guardar_imagen(
            request.files.get('imagen'),
            tipo='perfil',
            subfolder='imgs/promociones'
        )
        Promocion.update(
            promocion_id, negocio_id, nombre_promocion,
            precio=precio, descripcion=descripcion,
            imagen=imagen_nueva or promocion.imagen,
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
        )
        flash("Promoción actualizada correctamente.", "success")
        return redirect(url_for('negocio', negocio_id=negocio_id))

    except ValueError as error:
        return render_template(
            'form-promocion.html', negocio=negocio,
            promocion=promocion, editando=True, form_error=str(error)
        ), 400
    except Exception:
        app.logger.exception("No se pudo actualizar la promoción")
        return render_template('error.html', error="No se pudo actualizar la promoción."), 500

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

        if elemento_tipo == 'usuario' and str(elemento_id) == str(session['user_id']):
            flash("No puedes reportar tu propio usuario.", "error")
            return redirect(url_for('user_profile', usuarios_id=session['user_id']))

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

    if elemento_tipo == 'usuario' and elemento_id == session['user_id']:
        flash("No puedes reportar tu propio usuario.", "error")
        return redirect(url_for('user_profile', usuarios_id=session['user_id']))

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
    access_redirect = require_business_account()
    if access_redirect:
        return access_redirect

    if Business.count_by_user(session['user_id']) >= MAX_BUSINESSES_PER_USER:
        flash("Has alcanzado el límite de 4 negocios por cuenta.", "error")
        return redirect(url_for('my_businesses'))

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
        imagen_banner = guardar_imagen(request.files.get('imagen_banner'), tipo='banner')
        imagen_perfil = guardar_imagen(request.files.get('imagen_perfil'), tipo='perfil')

        Business.save(
            session['user_id'], nombre_negocio, business_type, lat, lon,
            direccion=direccion,
            telefono=telefono,
            correo=correo,
            descripcion=descripcion,
            horario_dia_inicio=horario_dia_inicio,
            horario_dia_fin=horario_dia_fin,
            horario_hora_inicio=horario_hora_inicio,
            horario_hora_fin=horario_hora_fin,
            imagen_banner=imagen_banner,
            imagen_perfil=imagen_perfil
        )
        flash("Negocio creado correctamente.", "success")
        return redirect(url_for('my_businesses'))

    except ValueError as e:
        return render_template('error.html', error=str(e)), 400
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

    # Ruta de creacion adaptada para fotos
# Para renderizar el mismo formulario pero para editar el negocio
# No mentira 

@app.route('/Negocio/<int:negocio_id>/Editar', methods=['GET', 'POST'])
def editar_negocio(negocio_id):
    access_redirect = require_business_account()
    if access_redirect:
        return access_redirect

    negocio = Business.get_by_id_for_user(negocio_id, session['user_id'])

    if not negocio:
        flash("El negocio no existe o no pertenece a tu cuenta.", "error")
        return redirect(url_for('my_businesses'))

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
    horario_dia_inicio = request.form.get('horario_dia_inicio') or None
    horario_dia_fin = request.form.get('horario_dia_fin') or None
    horario_hora_inicio = request.form.get('horario_hora_inicio') or None
    horario_hora_fin = request.form.get('horario_hora_fin') or None

    imagen_banner_nueva = guardar_imagen(request.files.get('imagen_banner'), tipo='banner')
    imagen_perfil_nueva = guardar_imagen(request.files.get('imagen_perfil'), tipo='perfil')

    imagen_banner = imagen_banner_nueva if imagen_banner_nueva else negocio.imagen_banner
    imagen_perfil = imagen_perfil_nueva if imagen_perfil_nueva else negocio.imagen_perfil


    try:
        Business.update(
        negocio_id, session['user_id'], nombre_negocio, business_type, lat, lon,
        direccion=direccion, telefono=telefono, correo=correo, descripcion=descripcion,
        horario_dia_inicio=horario_dia_inicio, horario_dia_fin=horario_dia_fin,
        horario_hora_inicio=horario_hora_inicio, horario_hora_fin=horario_hora_fin,
        imagen_banner=imagen_banner, imagen_perfil=imagen_perfil
        )

        return redirect(url_for('negocio', negocio_id=negocio_id))

    except ValueError as e:
        return render_template('error.html', error=str(e)), 400
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

@app.route("/Mis-negocios")
def my_businesses():
    access_redirect = require_business_account()
    if access_redirect:
        return access_redirect

    businesses = Business.get_by_user(session['user_id'])
    business_count = len(businesses)

    return render_template(
        "business-admin.html",
        businesses=businesses,
        business_count=business_count,
        business_limit=MAX_BUSINESSES_PER_USER,
        can_create=business_count < MAX_BUSINESSES_PER_USER,
        username=session.get('username', 'Negocio'),
        account_type=session.get('account_type', 'business')
    )


@app.route('/Negocio/<int:negocio_id>/Borrar', methods=['POST'])
def borrar_negocio(negocio_id):
    access_redirect = require_business_account()
    if access_redirect:
        return access_redirect

    negocio = Business.get_by_id_for_user(negocio_id, session['user_id'])
    if not negocio:
        flash("El negocio no existe o no pertenece a tu cuenta.", "error")
        return redirect(url_for('my_businesses'))

    try:
        Business.delete_for_user(negocio_id, session['user_id'])
        flash(f'“{negocio.nombre_negocio}” fue eliminado correctamente.', 'success')
    except RuntimeError:
        flash("No pudimos eliminar el negocio. Inténtalo nuevamente.", "error")

    return redirect(url_for('my_businesses'))

@app.route("/Cerrar-sesion")
def logout():
    session.clear()
    return redirect("/")

@app.route("/search")
def search():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])

    businesses = buscar_en_lista(
        query,
        Business.get_all(),
        ['nombre_negocio', 'business_type', 'direccion']
    )[:8]
    users = buscar_en_lista(query, Usuario.get_all_users(), ['username'])[:8]
    promotions = buscar_en_lista(
        query,
        Promocion.get_active_searchable(),
        ['nombre_promocion', 'descripcion', 'nombre_negocio', 'business_type']
    )[:8]
    active_promotion_counts = Promocion.get_active_counts([business.id for business in businesses])

    results = []

    for business in businesses:
        results.append({
            'result_type': 'business',
            'id': business.id,
            'title': business.nombre_negocio,
            'business_type': business.business_type,
            'location': business.direccion,
            'active_promotions': active_promotion_counts.get(business.id, 0),
            'image_url': media_url(business.imagen_perfil, 'imgs/default-business.png'),
            'marker_business_id': business.id,
            'lat': float(business.lat),
            'lon': float(business.lon),
            'url': url_for('negocio', negocio_id=business.id)
        })

    for user in users:
        results.append({
            'result_type': 'user',
            'id': user.id,
            'title': user.username,
            'account_label': 'Vendedor' if user.account_type == 'business' else 'Cliente',
            'image_url': media_url(user.foto_perfil, 'imgs/default.jpg'),
            'url': url_for('user_profile', usuarios_id=user.id)
        })

    for promotion in promotions:
        results.append({
            'result_type': 'promotion',
            'id': promotion.id,
            'title': promotion.nombre_promocion,
            'business_name': promotion.nombre_negocio,
            'business_type': promotion.business_type,
            'location': promotion.direccion_negocio,
            'price': str(promotion.precio).strip() if promotion.precio is not None else None,
            'image_url': media_url(
                promotion.imagen or promotion.imagen_negocio,
                'imgs/default-business.png'
            ),
            'marker_business_id': promotion.negocio_id,
            'lat': float(promotion.lat),
            'lon': float(promotion.lon),
            'url': f"{url_for('negocio', negocio_id=promotion.negocio_id)}#promociones"
        })

    return jsonify(results)

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
        account_type=session.get("account_type", "invitado"),
        username=session.get("username", "invitado")
    )

@app.route("/Configuracion/Editar", methods=["POST"])
def actualizar_perfil():
    if "user_id" not in session:
        flash("Debes iniciar sesión para editar tu perfil.", "login")
        return redirect(url_for("login_page"))

    usuario = Usuario.get_by_id(session["user_id"])
    if usuario is None:
        session.clear()
        flash("Tu sesión ya no es válida. Inicia sesión nuevamente.", "login")
        return redirect(url_for("login_page"))

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    telefono = request.form.get("telefono", "").strip() or None
    bio = request.form.get("bio", "").strip() or None

    if len(username) < 2 or len(username) > 100:
        flash("El nombre de usuario debe tener entre 2 y 100 caracteres.", "error")
        return redirect(url_for("config", seccion="editar"))

    if not email or "@" not in email or len(email) > 150:
        flash("Ingresa un correo electrónico válido.", "error")
        return redirect(url_for("config", seccion="editar"))

    if telefono and len(telefono) > 20:
        flash("El teléfono no puede superar los 20 caracteres.", "error")
        return redirect(url_for("config", seccion="editar"))

    if bio and len(bio) > 500:
        flash("La biografía no puede superar los 500 caracteres.", "error")
        return redirect(url_for("config", seccion="editar"))

    conflict = Usuario.find_profile_conflict(session["user_id"], username, email)
    if conflict:
        message = (
            "Ese nombre de usuario ya está en uso."
            if conflict["username"].lower() == username.lower()
            else "Ese correo ya está registrado."
        )
        flash(message, "error")
        return redirect(url_for("config", seccion="editar"))

    try:
        foto_nueva = guardar_imagen(
            request.files.get("foto_perfil"),
            tipo="usuario",
            subfolder="imgs/usuarios"
        )
        Usuario.update_profile({
            "id": session["user_id"],
            "username": username,
            "email": email,
            "telefono": telefono,
            "bio": bio,
            "foto_perfil": foto_nueva or usuario.foto_perfil
        })
    except (ValueError, RuntimeError) as error:
        flash(str(error), "error")
        return redirect(url_for("config", seccion="editar"))

    session["username"] = username
    flash("Perfil actualizado correctamente.", "success")
    return redirect(url_for("config", seccion="perfil"))
    # Muy bien javier

@app.route('/Eliminar-cuenta', methods=['POST'])
def eliminar_cuenta():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    Usuario.delete(session['user_id'])  # borra la fila de la BD
    session.clear()                      # limpia la cookie de sesión

    flash("Tu cuenta ha sido eliminada.", "success")
    return redirect('/')

@app.route("/Funciones-futuras")
def future_function():
    return render_template("future-function.html")

# Manejadores de error

@app.errorhandler(413)
def archivo_muy_grande(e):
    flash("El archivo es demasiado grande. Máximo 5 MB.", "error")
    return redirect(request.referrer or url_for('map'))

if __name__ == "__main__":
    app.run(
        ssl_context=(
        "almaceb-cert.pem",
        "almaceb-key.pem"
    ),
    host="0.0.0.0",
    port=5000,
    debug=True)
    #Cambiar debug a false en la feria