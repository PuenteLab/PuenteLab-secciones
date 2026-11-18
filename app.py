import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "clave_secreta_puentelab"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "puentelab.db")
SQL_PATH = os.path.join(BASE_DIR, "database.sql")

def conectar_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def crear_tabla():
    conn = conectar_db()
    with open(SQL_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

crear_tabla()

# ==========================================
# PARTE DE BENJA (Registro e Inicio de sesión)
# ==========================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registro", methods=["POST"])
def registro():
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    password = generate_password_hash(request.form.get("password"))
    edad = request.form.get("edad")
    genero = request.form.get("genero")
    orientacion = request.form.get("orientacion")
    estudio = request.form.get("estudio")

    try:
        conn = conectar_db()
        conn.execute(
            """INSERT INTO usuarios (nombre, email, password, edad, genero, orientacion, estudio)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (nombre, email, password, edad, genero, orientacion, estudio)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    except sqlite3.IntegrityError:
        return "Ese correo ya está registrado. <a href='/'>Volver</a>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = conectar_db()
        usuario = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        conn.close()

        if usuario and check_password_hash(usuario["password"], password):
            session["usuario_id"] = usuario["id"]
            return redirect(url_for("inicio"))
        return "Correo o contraseña incorrectos. <a href='/login'>Intentar de nuevo</a>"

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)

    # ==========================================
# PARTE DE Oriana (Inicio personalizado y menú)
# ==========================================
@app.route("/inicio")
def inicio():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = conectar_db()
    usuario = conn.execute("SELECT * FROM usuarios WHERE id = ?", (session["usuario_id"],)).fetchone()
    conn.close()

    return render_template("seccion-inicio.html", usuario=usuario)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/mentorias")
def mentorias():
    return render_template("mentorias.html")

@app.route("/oportunidades")
def oportunidades():
    return render_template("oportunidades.html")

@app.route("/proyectos")
def proyectos():
    return render_template("proyectos.html")