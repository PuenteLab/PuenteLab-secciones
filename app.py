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
    conn = sqlite3.connect(DB_PATH, timeout=10)
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

    conn = conectar_db()
    try:
        conn.execute(
            """INSERT INTO usuarios (nombre, email, password, edad, genero, orientacion, estudio)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (nombre, email, password, edad, genero, orientacion, estudio)
        )
        conn.commit()
        return redirect(url_for("login"))
    except sqlite3.IntegrityError:
        return "Ese correo ya está registrado. <a href='/'>Volver</a>"
    finally:
        conn.close()

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

# ==========================================
# PARTE DE DELFI (Ver, editar y eliminar Perfil)
# ==========================================
@app.route("/perfil")
def perfil():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = conectar_db()
    usuario = conn.execute("SELECT * FROM usuarios WHERE id = ?", (session["usuario_id"],)).fetchone()
    conn.close()

    return render_template("perfil.html", usuario=usuario)

@app.route("/perfil/editar", methods=["POST"])
def editar_perfil():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    nombre = request.form.get("nombre")
    edad = request.form.get("edad")
    genero = request.form.get("genero")
    orientacion = request.form.get("orientacion")
    estudio = request.form.get("estudio")

    conn = conectar_db()
    conn.execute("""
        UPDATE usuarios
        SET nombre = ?, edad = ?, genero = ?, orientacion = ?, estudio = ?
        WHERE id = ?
    """, (nombre, edad, genero, orientacion, estudio, session["usuario_id"]))
    conn.commit()
    conn.close()

    return redirect(url_for("perfil"))

@app.route("/perfil/eliminar", methods=["POST"])
def eliminar_perfil():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = conectar_db()
    conn.execute("DELETE FROM usuarios WHERE id = ?", (session["usuario_id"],))
    conn.commit()
    conn.close()

    session.clear()
    return redirect(url_for("index"))

# ==========================================
# ARRANQUE DEL SERVIDOR (Siempre al final)
# ==========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)