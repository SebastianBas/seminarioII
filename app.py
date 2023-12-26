from flask import Flask
from flask import send_from_directory
from flask import request, Response, session
import os
from flask import make_response
from flask import abort
from flask import render_template
from flask import redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_paginate import Pagination, get_page_args

from flask_sqlalchemy import SQLAlchemy

from flask_mysqldb import MySQL, MySQLdb

from MySQLdb import OperationalError

#inicializar aplicacion
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/img'


app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='gimnasio'
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql = MySQL(app)


@app.route('/acceso-login', methods=["GET", "POST"])
def login():
    try:
        if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
            _correo = request.form['txtCorreo']
            _contraseña = request.form['txtPassword']

            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM usuarios WHERE correo = %s AND contraseña = %s', (_correo, _contraseña,))
            account = cur.fetchone()

            if account:
                session['logueado'] = True
                session['id'] = account['id']
                session['id_rol'] = account['id_rol']
                session['nombre_usuario'] = account['nombre']  

                if session['id_rol'] == 1:
                    return redirect(url_for('prod'))  
                elif session['id_rol'] == 2:
                    return redirect(url_for('ropa'))  # Redirige a la página de usuario

        return render_template('login.html')

    except OperationalError:
        # Captura un error operativo relacionado con la base de datos y muestra la página de error 500
        return abort(500)
    except Exception as e:
        # Captura cualquier otro error y muestra la página de error 500
        print(f"Error inesperado: {str(e)}")
        return abort(500)
    

@app.route('/cerrar-sesion')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM productos')
        productos = cur.fetchall()

        return render_template('admin.html', productos=productos)

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return abort(500)


@app.route('/crear-registro', methods=["GET", "POST"])
def registro():
    try:
        if request.method == 'POST':
            nombre = request.form['txtNombre']
            correo = request.form['txtCorreo']
            contraseña = request.form['txtPassword']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (nombre, correo, contraseña, id_rol) VALUES (%s, %s, %s, '2')", (nombre, correo, contraseña))
            mysql.connection.commit()

            return render_template('login.html')

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return abort(500)
    return render_template('registro.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory (os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

#rutas venv
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')



@app.route('/acercade')
def acercade():
    return render_template('acercade.html')

from flask_paginate import Pagination, get_page_args

@app.route('/productos', methods=['GET'])
def ropa():
    page = request.args.get('page', 1, type=int)

    # Definir la cantidad de productos por página
    productos_per_page = 9

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()

    # Calcular el índice de inicio y fin para los productos en la página actual
    start_index = (page - 1) * productos_per_page
    end_index = start_index + productos_per_page

    # Seleccionar los productos correspondientes a la página actual
    productos_pagina = productos[start_index:end_index]

    # Configurar la paginación
    pagination = Pagination(page=page, total=len(productos), per_page=productos_per_page, css_framework='bootstrap4')

    return render_template('ropa.html', productos=productos_pagina, pagination=pagination)


@app.route('/horarios', methods=['GET'])
def horario1():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM horario")
    horarios = cur.fetchall()
    
    return render_template('horario.html', horarios=horarios)

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

@app.route('/membresias')
def membresias():
    return render_template('membresias.html')

@app.route('/personalizado')
def personalizado():
    return render_template('personalizado.html')


#--------------Producto-------------------

@app.route('/producto', methods=['GET'])
def prod():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()

    return render_template('admin.html', productos=productos)

@app.route('/agregar-productos', methods=['POST'])
def agregarPro():
    try:
        nombre = request.form['nombre']
        colores = request.form['colores']
        tallas = request.form['tallas']
        precio = request.form['precio']
        
        imagen = request.files['imagen']

        if not (nombre and colores and tallas and precio and imagen):
            # Redirige a la página de error 500 si faltan campos en el formulario
            return abort(404)

        # Guarda la imagen en tu directorio de imágenes estáticas
        imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(imagen.filename)))

        # Obtén la ruta de la imagen para almacenarla en la base de datos
        imagen_path = secure_filename(imagen.filename)

        cur = mysql.connection.cursor()
        sql = "INSERT INTO productos (nombre, colores, tallas, precio, imagen) VALUES (%s, %s, %s, %s, %s)"
        data = (nombre, colores, tallas, precio, imagen_path)
        cur.execute(sql, data)
        mysql.connection.commit()
        
        return redirect('/producto')

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return abort(500)

@app.route("/eliminar-producto", methods=['POST'])
def borraProducto():
    cur = mysql.connection.cursor()
    producto_id = request.form['producto_id']
    sql = "DELETE FROM productos WHERE producto_id = %s"
    data = (producto_id,)
    cur.execute(sql,data)
    mysql.connection.commit()
    return redirect('/producto')

#-----------------Horario---------------------

@app.route('/horario', methods=['GET'])
def horario():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM horario")
    horarios = cur.fetchall()
    
    return render_template('admin2.html', horarios=horarios)

@app.route('/agregar-horarios', methods=['POST'])
def agregarHorario():

    nombre = request.form['nombre']
    horaInicio = request.form['horaInicio']
    horaFin = request.form['horaFin']
    if not (nombre and horaInicio and horaFin):
        return abort(500)

    cur = mysql.connection.cursor()
    sql = "INSERT INTO horario (nombre, horaInicio, horaFin) VALUES (%s, %s, %s)"
    data = (nombre, horaInicio, horaFin)
    cur.execute(sql, data)
    mysql.connection.commit()

    return redirect('/horario')



@app.route("/eliminar-horario", methods=['POST'])
def borrarHorario():
    cur = mysql.connection.cursor()
    id_horario = request.form['horario_id']
    sql = "DELETE FROM horario WHERE id_horario = %s"
    data = (id_horario,)
    cur.execute(sql, data)
    mysql.connection.commit()
    return redirect('/horario')

#---------------------------Entrenador------------------------------

@app.route('/entrenador', methods=['GET'])
def entrenador():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM entrenadores")
    entrenadores = cur.fetchall()

    return render_template('admin3.html', entrenadores=entrenadores)

@app.route('/entrenadores', methods=['GET'])
def entrenador1():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM entrenadores")
    entrenadores = cur.fetchall()

    return render_template('entrenadores.html', entrenadores=entrenadores)



@app.route('/agregar-entrenador', methods=['POST'])
def agregarEntrenador():
    try:
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        foto = request.files['foto']

        if not (nombre and descripcion and foto):
            return abort(500)
        
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(foto.filename)))

        # Obteniendo la ruta de la foto para almacenarla en la base de datos
        foto_path = secure_filename(foto.filename)

        cur = mysql.connection.cursor()
        sql = "INSERT INTO entrenadores (nombre, descripcion, foto) VALUES (%s, %s, %s)"
        data = (nombre, descripcion, foto_path)
        cur.execute(sql, data)
        mysql.connection.commit()

        return redirect('/entrenador')

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return abort(500)
    
@app.route("/eliminar-entrenador", methods=['POST'])
def eliminarEntrenador():
    try:
        cur = mysql.connection.cursor()
        id_entrenador = request.form['id_entrenador']
        sql = "DELETE FROM entrenadores WHERE id_entrenador = %s"
        data = (id_entrenador,)
        cur.execute(sql, data)
        mysql.connection.commit()

        return redirect('/entrenador')

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return abort(500)



#--------------Errores--------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404

@app.errorhandler(500)
def database_error(e):
    return render_template('database_error.html'), 500


#-------------CARRITO DE COMPRAS------------
from flask import jsonify


@app.route('/ver-carrito')
def ver_carrito():

    if 'id' not in session:
        return redirect(url_for('login'))

    id_usuario = session['id']

    cur = mysql.connection.cursor()
    cur.execute("SELECT carrito.id_carrito, productos.nombre, productos.precio, productos.imagen, carrito.cantidad FROM carrito INNER JOIN productos ON carrito.id_producto = productos.producto_id WHERE carrito.id_usuario = %s", (id_usuario,))
    carrito = cur.fetchall()
    cur.close()

    return render_template('carrito.html', carrito=carrito)



@app.route('/eliminar-del-carrito/<int:id_carrito>', methods=['POST'])
def eliminar_del_carrito(id_carrito):
    try:
        if 'id' not in session:
            return jsonify({'error': 'Usuario no autenticado'}), 401

        id_usuario = session['id']

        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM carrito WHERE id_carrito = %s AND id_usuario = %s", (id_carrito, id_usuario))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Producto eliminado del carrito exitosamente'})

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return jsonify({'error': 'Error al eliminar producto del carrito'}), 500

@app.route('/agregar-al-carrito/<int:producto_id>', methods=['POST'])
def agregar_al_carrito(producto_id):
    if 'id' not in session:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    id_usuario = session['id']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO carrito (id_usuario, id_producto, cantidad) VALUES (%s, %s, 1)", (id_usuario, producto_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Producto agregado al carrito exitosamente'})



if __name__ == "__main__":
    app.secret_key="sebastian_2"
    app.run(debug=True)