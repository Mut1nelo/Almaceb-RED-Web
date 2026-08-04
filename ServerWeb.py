import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.secret_key = "o9OzdHo5STkPOZEXwPpp5xWyIPEpTWaltL8PLN5772V"

# Enrutamiento de las páginas web
@app.route("/")
def iniciar():
    return render_template("index.html")

@app.route("/inicio")
def inicio():
    return render_template("index.html")

@app.route("/Modo desarrollador")
def modo_desarrollador():
    return render_template("desarrollador.html")

@app.route("/En construcción")
def under_construction():
    return render_template("under-construction.html")

@app.route("/Mapa")
def map():
    return render_template("map.html")

@app.route("/Negocios")
def negocios():
    return render_template("business.html")

@app.route("/Cerrar-sesión")
def cerrar_sesion():
    # session.clear()  # Limpiar la sesión
    return render_template("/troll.html")

@app.route("/Negocio")
def negocio():
    return render_template("business.html")

@app.route("/Promociones")
def promociones():
    return render_template("promo.html")

@app.route("/Favoritos")
def favoritos():
    return render_template("favorites.html")

@app.route("/Galeria")
def galeria():
    return render_template("gallery.html")

@app.route("/Información")
def informacion():
    return render_template("info.html")

@app.route("/Denuncias")
def denuncias():
    return render_template("report.html")

@app.route("/Configuración")
def configuracion():
    return render_template("config.html")

@app.route("/Perfil")
def perfil():
    return render_template("profile.html")

@app.route("/Registro")
def registro():
    return render_template("registro.html")

@app.route("/Mostrar información")
def mostrar_informacion():
    return render_template("informacion.html")

# Procesamiento del formulario
@app.route("/procesar_request", methods=['POST'])
def procesar():
    

    if 'archivo' not in request.files:
        return 'Falta el archivo', 400
        
    file = request.files['archivo']
    
    if file.filename == '':
        return 'No se seleccionó ningún archivo', 400
    
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.root_path, 'static', 'uploads', filename))
    
    print(request.form)
    session["nombre"] = request.form["nombre_completo"]
    session["email"] = request.form["email"]
    session["password"] = request.form["password"]
    session['archivo_url'] = f'uploads/{filename}'
    session["tipo_local"] = request.form["tipo_local"]
    session["horario"] = request.form["hora_atencion"]
    session["descripcion"] = request.form["descripcion"]
    

    return redirect("/mostrar_informacion")

@app.route("/mostrar_informacion")
def mostrar():
    if 'nombre' not in session:
        print("No se encontraron datos de usuario, redireccionando a formulario...")
        return redirect("/")
    nombre = session.get('nombre')
    email = session.get('email')
    password = session.get('password')
    archivo = session.get('archivo_url')
    tipo_local = session.get('tipo_local')
    horario = session.get('horario')
    descripcion = session.get('descripcion')

    return render_template("informacion.html", nombre=nombre, email=email, password=password, archivo=archivo, tipo_local=tipo_local, horario=horario, descripcion=descripcion)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear() 
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)