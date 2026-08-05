from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pymysql
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura' # Cambia esto por algo único

# Tu función de conexión existente
def obtener_conexion():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='sistema_login',
        cursorclass=pymysql.cursors.DictCursor
    )

# --- RUTA DE LOGIN ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        flash('Ya has iniciado sesión, redireccionando al mapa...', 'info')
        return redirect(url_for('mostrar_mapa'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Buscamos al usuario por su nombre o username
                sql = "SELECT id, username, password FROM usuarios WHERE username = %s"
                cursor.execute(sql, (username,))
                usuario = cursor.fetchone()

            if usuario and check_password_hash(usuario['password'], password):
                # Guardamos los datos clave en la sesión de Flask
                session['usuario_id'] = usuario['id']
                session['username'] = usuario['username']
                flash('¡Inicio de sesión correcto!', 'success')
                return redirect(url_for('mostrar_mapa')) # Redirige a la ruta de tu mapa
            else:
                flash('Usuario o contraseña incorrectos.', 'danger')
        except Exception as e:
            print(f"Error en Login: {e}")
            flash('Hubo un error al procesar el ingreso.', 'danger')
        finally:
            conexion.close()

    return render_template('login.html')

# --- RUTA DE TU MAPA (PROTEGIDA) ---
@app.route('/mapa')
def mostrar_mapa():
    # Si no ha iniciado sesión, lo mandamos de vuelta al Login
    if 'usuario_id' not in session:
        flash('Por favor, inicia sesión primero.', 'warning')
        return redirect(url_for('login'))

    # Buscamos los datos actualizados del usuario en la BD para pasarlos al mapa
    conexion = obtener_conexion()
    usuarios_lista = []
    try:
        with conexion.cursor() as cursor:
            sql = "SELECT id, username AS nombre, latitud, longitud FROM usuarios WHERE id = %s"
            cursor.execute(sql, (session['usuario_id'],))
            usuario_actual = cursor.fetchone()
            if usuario_actual:
                usuarios_lista.append(usuario_actual)
    finally:
        conexion.close()

    # Le pasamos la lista 'usuarios' a tu HTML tal como lo tenías antes
    return render_template('interactiveMap.html', usuarios=usuarios_lista)

# --- RUTA PARA GUARDAR UBICACIÓN (ACTUALIZADA CON SESIÓN SECRETA) ---
@app.route('/guardar-ubicacion', methods=['POST'])
def guardar_ubicacion():
    # Validamos con la sesión, eliminando el riesgo de que alteren IDs desde el JS
    if 'usuario_id' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    try:
        datos = request.get_json()
        latitud = datos.get('latitud')
        longitud = datos.get('longitud')
        id_usuario = session['usuario_id']

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "UPDATE usuarios SET latitud = %s, longitud = %s WHERE id = %s"
            cursor.execute(sql, (latitud, longitud, id_usuario))
        conexion.commit()
        conexion.close()

        return jsonify({'status': 'success', 'message': 'Ubicación guardada mediante sesión'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'Error interno'}), 500

# --- RUTA DE CERRAR SESIÓN ---
@app.route('/Cerrar-sesión')
def cerrar_sesion():
    session.clear() # Borra toda la sesión activa
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)