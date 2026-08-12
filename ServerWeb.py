# Este servidor solo tiene los enrutamientos, back-end lo ves tu Jose
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

# Enrutamiento de las páginas web
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/Mapa")
def map():
    return render_template("map.html")

@app.route("/Registro")
def register():
    return render_template("form-register.html")

@app.route("/Iniciar-sesión")
def login():
    return render_template("form-login.html")

@app.route("/Reportes")
def report():
    return render_template("report.html")

if __name__ == "__main__":
    app.run(debug=True)