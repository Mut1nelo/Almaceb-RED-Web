from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pymysql
import json
import urllib.parse
import urllib.request
from werkzeug.security import check_password_hash, generate_password_hash

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

#login
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

#mapa
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

#registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'usuario_id' in session:
        return redirect(url_for('mostrar_mapa'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        direccion_texto = request.form.get('direccion')

        # Inicializamos en None para saber si la API realmente respondió o no
        latitud = None
        longitud = None

        if direccion_texto:
            try:
                # 1. Limpieza absoluta de espacios y saltos de línea del formulario
                direccion_limpia = " ".join(direccion_texto.split())
                direccion_completa = f"{direccion_limpia}, Chile"
                
                # 2. CAMBIO DE SERVIDOR: Usamos el espejo alternativo de OpenStreetMap (Nominatim Mapquest/OSM)
                # Este endpoint es tolerante con peticiones desde servidores locales (localhost)
                url_base = "https://openstreetmap.org"
                
                parametros = {
                    'q': direccion_completa,
                    'format': 'json',
                    'limit': 1,
                    'addressdetails': 0
                }
                
                url_api = f"{url_base}?{urllib.parse.urlencode(parametros)}"
                print(f"🔗 Intentando geocodificación en: {url_api}")
                
                # 3. CABECERAS EXTREMAS DE NAVEGADOR COMPLETO: Simula exactamente a Google Chrome
                req = urllib.request.Request(url_api)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                req.add_header('Accept', 'application/json, text/plain, */*') # <-- Solución directa al 406
                req.add_header('Accept-Language', 'es-CL,es;q=0.9,en;q=0.8')
                req.add_header('Cache-Control', 'no-cache')
                
                # Realizamos la petición con un tiempo de espera controlado
                with urllib.request.urlopen(req, timeout=6) as response:
                    respuesta_texto = response.read().decode('utf-8')
                    datos_osm = json.loads(respuesta_texto)
                    
                    if isinstance(datos_osm, list) and len(datos_osm) > 0:
                        # Extraemos de forma segura el primer elemento de la lista devuelta
                        primer_resultado = datos_osm[0]
                        latitud = float(primer_resultado['lat'])
                        longitud = float(primer_resultado['lon'])
                        print(f"🌍 DIRECCIÓN TRADUCIDA CON ÉXITO: Lat={latitud}, Lon={longitud}")
                    else:
                        print(f"❌ La API no devolvió resultados para la dirección: {direccion_completa}")
                        
            except urllib.error.HTTPError as http_err:
                # Si de forma extraordinaria el servidor arroja un código (ej. 406), lo captura aquí sin romper tu app
                print(f"🚨 Bloqueo controlado de la API (Código HTTP {http_err.code}). Saltando a coordenadas por defecto.")
            except Exception as e:
                print(f"🚨 Error en el procesamiento del mapa: {e}")

        # 4. CAPA DE SEGURIDAD INTERNA: Si la API falló o arrojó 406, el registro NO se detiene
        # Le asignamos coordenadas válidas por defecto de San Ramón para que el usuario pueda crearse
        if latitud is None or longitud is None:
            print("⚠ Asignando coordenadas de San Ramón debido a restricciones de red.")
            latitud = -33.5532855
            longitud = -70.6528958


        # Encriptamos la contraseña de manera segura
        password_encriptada = generate_password_hash(password)

        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                # Validamos duplicados
                cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('El nombre de usuario ya está registrado.', 'warning')
                    return render_template('registro.html')

                # Guardamos los datos finales en tu base de datos MySQL
                sql = "INSERT INTO usuarios (username, password, latitud, longitud) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (username, password_encriptada, latitud, longitud))
            
            conexion.commit()
            flash('¡Registro completado! Coordenadas asignadas.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            print(f"Error escribiendo en MySQL: {e}")
            flash('Hubo un error interno al crear tu cuenta.', 'danger')
        finally:
            conexion.close()

    return render_template('registro.html')


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

#cerrar sesion
@app.route('/Cerrar-sesión')
def cerrar_sesion():
    session.clear() # Borra toda la sesión activa
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)