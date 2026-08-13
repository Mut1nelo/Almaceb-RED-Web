# Este servidor solo tiene los enrutamientos, back-end lo maneja Jose Moena
from flask import Flask, render_template, request, redirect, session, jsonify, flash
from difflib import SequenceMatcher
from usuario import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from mysqlconnection import connectToMySQL

app = Flask(__name__)

app.secret_key = "clavehipermegasupersecretayiaaaa"

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
    """Calcula la similitud entre el query y un texto (0-1)"""
    return SequenceMatcher(None, query.lower(), texto.lower()).ratio()

def buscar_en_lista(query, lista, campos_busqueda):
    """
    Busca un query en una lista de diccionarios
    Args:
        query: texto de búsqueda
        lista: lista de diccionarios a buscar
        campos_busqueda: lista de nombres de campos donde buscar
    Returns:
        lista ordenada por relevancia
    """
    if not query or len(query.strip()) < 2:
        return []
    
    query = query.strip()
    resultados = []
    
    for item in lista:
        max_similitud = 0
        for campo in campos_busqueda:
            if campo in item:
                similitud = calcular_similitud(query, str(item[campo]))
                max_similitud = max(max_similitud, similitud)
        
        # Incluye el resultado si tiene al menos 30% de similitud
        if max_similitud >= 0.3:
            resultados.append({"item": item, "relevancia": max_similitud})
    
    # Ordena por relevancia (mayor primero)
    resultados.sort(key=lambda x: x["relevancia"], reverse=True)
    return [r["item"] for r in resultados]

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
    return render_template("map.html", usuarios=usuarios, username=username, account_type=account_type)

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

@app.route("/Reportes")
def report():
    return render_template("report.html")

@app.route("/Cerrar-sesión")
def logout():
    session.clear()
    return redirect("/")

@app.route("/search")
def search():
    """Maneja búsquedas de negocios, promociones y usuarios"""
    query = request.args.get("q", "").strip()
    
    # Inicializa variables
    negocios_resultados = []
    promociones_resultados = []
    
    if query and len(query) >= 2:
        # Busca en negocios
        negocios_resultados = buscar_en_lista(
            query, 
            NEGOCIOS, 
            ["nombre", "categoria", "descripcion"]
        )
        
        # Busca en promociones
        promociones_resultados = buscar_en_lista(
            query, 
            PROMOCIONES, 
            ["titulo", "descripcion"]
        )
    
    return render_template(
        "map.html",
        search_query=query,
        usuarios=negocios_resultados,
        promociones=promociones_resultados
    )




























    # Mi espacio abajo para que no de conflictos, tu haz lo demás arriba Jose
    #Callate tonto pesao te odio tonto feo 































if __name__ == "__main__":
    app.run(debug=True)