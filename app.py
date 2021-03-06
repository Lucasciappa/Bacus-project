from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash
from flaskext.mysql import MySQL
from datetime import datetime
import os

app = Flask(__name__)

mysql = MySQL()
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "bacus"

mysql.init_app(app)

#Referencia a mi archivos
CARPETA = os.path.join("uploads")
app.config["CARPETA"] = CARPETA

app.secret_key = "miClave"


@app.route("/")
def index():
    sql  = "SELECT id, nombre, foto, descripcion, cepa FROM productos;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    productos = cursor.fetchall()
    # print(productos)

    return render_template("bacus/index.html", productos = productos)


@app.route("/create")
def create():

    return render_template("bacus/create.html")

@app.route("/store", methods=["POST"])
def storage():
    _nombre = request.form["txtNombre"]
    _descripcion = request.form["txtDescripcion"]
    _cepa = request.form["txtCepa"]
    _precio = request.form["txtPrecio"]
    _foto = request.files["txtFoto"]
    _id_marca = request.form["txtMarca"]
    _id_categoria = request.form["txtCategoria"]

    # Validacion de datos
    if _nombre == "" or _descripcion == "" or _cepa == "" or _precio == "" or _foto == "" or _id_marca == "" or _id_categoria == "":
        flash("Faltan ingresar datos!") #TO-DO
        return redirect(url_for("create"))

    ahora = datetime.now()
    tiempo = ahora.strftime("%Y%H%M%S")

    if _foto.filename != "":
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)

    sql  = "INSERT INTO `productos` (`nombre`, `descripcion`, `cepa`, `precio`, `foto`) VALUES (%s, %s, %s, %s, %s);"
    datos= (_nombre, _descripcion, _cepa, _precio, nuevoNombreFoto)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    return redirect("/")

@app.route("/destroy/<int:id>")
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute('SELECT foto FROM productos WHERE id = %s', id)
    fila = cursor.fetchone()
    print(fila)
    os.remove(os.path.join(app.config["CARPETA"], fila[0]))

    cursor.execute("DELETE FROM productos WHERE id=%s", id)
    conn.commit()
    print(fila)
    return redirect("/")



@app.route("/edit/<int:id>")
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE id=%s", id)
    producto = cursor.fetchone()

    return render_template("bacus/edit.html", producto = producto)

@app.route("/update", methods=["POST"])
def update():
    _nombre = request.form["txtNombre"]
    _descripcion = request.form["txtDescripcion"]
    _cepa = request.form["txtCepa"]
    _precio = request.form["txtPrecio"]
    _foto = request.files["txtFoto"]
    id = request.form["txtId"]

    sql = "UPDATE productos SET nombre = %s, descripcion = %s, cepa = %s, precio = %s  WHERE id = %s;"
    datos= (_nombre, _descripcion, _cepa, _precio, id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)

    ahora = datetime.now()
    tiempo = ahora.strftime("%Y%H%M%S")
    if _foto.filename != "":
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)
        cursor.execute('SELECT foto FROM productos WHERE id = %s', id)
        fila = cursor.fetchone()
        os.remove(os.path.join(app.config["CARPETA"], fila[0]))
        cursor.execute('UPDATE productos SET foto = %s WHERE id = %s', (nuevoNombreFoto, id))

    conn.commit() # Grabo las modif en mi BD
    
    return redirect("/")


@app.route("/uploads/<nombreFoto>")
def uploads(nombreFoto):
    return send_from_directory(app.config["CARPETA"], nombreFoto)

if __name__ == "__main__":
    app.run(debug=True)
