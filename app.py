from flask import Flask
from flask import send_from_directory
from flask import request, Response, session
import os
from flask import make_response
from flask import abort
from flask import render_template, jsonify
from flask import redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_paginate import Pagination, get_page_args


from flask_sqlalchemy import SQLAlchemy

from flask_mysqldb import MySQL, MySQLdb

from MySQLdb import OperationalError
import logging
from pymysql import OperationalError 
from flask_mail import Mail
from flask_mail import Message

from flask_babel import Babel, _
from forms import LanguageForm
from app import LanguageForm


logging.basicConfig(filename="logs.log", format="%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG)

#inicializar aplicacion
app = Flask(__name__)
babel = Babel(app)

app.config['UPLOAD_FOLDER'] = 'static/img'


app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='gimnasio'
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql = MySQL(app)

# Configuración del correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'fariceohb12@gmail.com'  
app.config['MAIL_PASSWORD'] = 'nmmt vfwj hfwh afeg'        
app.config['MAIL_DEFAULT_SENDER'] = 'fariceohb12@gmail.com'  

mail = Mail(app)

app.config['LANGUAGES'] = ['es', 'en']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['DEBUG']=True

#------Traduccion---
@babel.localeselector
def get_locale():
    return session.get('language', 'es')

@app.route('/change-language', methods=['POST'])
def change_language():
    form = LanguageForm()
    if form.validate_on_submit():
        session['language'] = form.language.data
    return redirect(request.referrer or url_for('home'))




@app.route('/acceso-login', methods=["GET", "POST"])
def login():
    try:
        if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
            _correo = request.form['txtCorreo']
            _contraseña = request.form['txtPassword']

            logging.info(f"Intento de inicio de sesión para el usuario {_correo}")

            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM usuarios WHERE correo = %s AND contraseña = %s', (_correo, _contraseña,))
            account = cur.fetchone()

            if account:
                session['logueado'] = True
                session['id'] = account['id']
                session['id_rol'] = account['id_rol']
                session['nombre_usuario'] = account['nombre']  

                if session['id_rol'] == 1:
                    logging.info("Inicio de sesión exitoso para un administrador")
                    return redirect(url_for('prod'))
                elif session['id_rol'] == 2:
                    logging.info("Inicio de sesión exitoso para un usuario")
                    return redirect(url_for('ropa'))  # Redirige a la página de usuario

        return render_template('login.html')

    except OperationalError as e:
        logging.error(f"Error operativo relacionado con la base de datos: {str(e)}")
        # Captura un error operativo relacionado con la base de datos y muestra la página de error 500
        return abort(500)
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        # Captura cualquier otro error y muestra la página de error 500
        return abort(500)

@app.route('/cerrar-sesion')
def cerrar_sesion():
    logging.info("Cierre de sesión")
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

#rutas venv
@app.route('/')
def index():
    form =  LanguageForm()
    return render_template('home.html', form=form)

@app.route('/home')
def home():
    form =  LanguageForm()
    return render_template('home.html',form=form)

@app.route('/servicios')
def servicios():
    form =  LanguageForm()
    return render_template('servicios.html',form=form)



@app.route('/acercade')
def acercade():
    form =  LanguageForm()
    return render_template('acercade.html',form=form)

from flask_paginate import Pagination, get_page_args

@app.route('/productos', methods=['GET'])
def ropa():
    form =  LanguageForm()
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

    return render_template('ropa.html', productos=productos_pagina, pagination=pagination,form=form)


@app.route('/horarios', methods=['GET'])
def horario1():
    form =  LanguageForm()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM horario")
    horarios = cur.fetchall()
    
    return render_template('horario.html', horarios=horarios,form=form)

@app.route('/formulario')
def formulario():
    form =  LanguageForm()
    return render_template('formulario.html',form=form)

@app.route('/membresias')
def membresias():
    form =  LanguageForm()
    return render_template('membresias.html',form=form)

@app.route('/personalizado')
def personalizado():
    form =  LanguageForm()
    return render_template('personalizado.html',form=form)


#--------------Producto-------------------

@app.route('/producto', methods=['GET'])
def prod():
    form =  LanguageForm()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()

    return render_template('admin.html', productos=productos,form=form)

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
    form =  LanguageForm()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM entrenadores")
    entrenadores = cur.fetchall()

    return render_template('admin3.html', entrenadores=entrenadores,form=form)

@app.route('/entrenadores', methods=['GET'])
def entrenador1():
    form =  LanguageForm()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM entrenadores")
    entrenadores = cur.fetchall()

    return render_template('entrenadores.html', entrenadores=entrenadores, form=form)



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
    try:
        form = LanguageForm()
        return render_template('error404.html', form=form), 404
    except Exception as ex:
        print(f"Error al crear el formulario: {str(ex)}")
        return render_template('error404.html'), 404


@app.errorhandler(500)
def database_error(e):
    return render_template('database_error.html'), 500


#-------------CARRITO DE COMPRAS------------
from flask import jsonify


@app.route('/ver-carrito')
def ver_carrito():
    form =  LanguageForm()
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


def enviar_resumen_compra(correo_destino, resumen):
    try:
        subject = 'Resumen de Compra'
        sender = app.config['MAIL_DEFAULT_SENDER']
        message = Message(subject, sender=sender, recipients=[correo_destino])
        message.html = resumen
        mail.send(message)
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")
        return False


def obtener_correo_usuario(id_usuario):
    cur = mysql.connection.cursor()
    cur.execute("SELECT correo FROM usuarios WHERE id = %s", (id_usuario,))
    usuario = cur.fetchone()
    cur.close()

    if usuario:
        return usuario['correo']
    else:
        return None

def calcular_total_compra(carrito):
    total_compra = 0
    for item in carrito:
        total_compra += item['precio'] * item['cantidad']
    return total_compra
    

@app.route('/comprar', methods=['POST'])
def comprar():
    try:
        id_usuario = session['id']
        usuario_correo = obtener_correo_usuario(id_usuario)

        # Obtiene los detalles del carrito
        cur = mysql.connection.cursor()
        cur.execute("SELECT productos.nombre, productos.precio, carrito.cantidad FROM carrito INNER JOIN productos ON carrito.id_producto = productos.producto_id WHERE carrito.id_usuario = %s", (id_usuario,))
        carrito = cur.fetchall()
        cur.close()

        # Calcula el total de la compra
        total_compra = calcular_total_compra(carrito)

        # Genera la factura o resumen en HTML (usando el template resumen_compra.html)
        resumen_html = render_template('resumen.html', carrito=carrito, total_compra=total_compra)

        # Configura el mensaje de correo
        subject = 'Resumen de Compra'
        sender = app.config['MAIL_DEFAULT_SENDER']
        message = Message(subject, sender=sender, recipients=[usuario_correo])
        message.html = resumen_html  # Asigna directamente el HTML generado

        # Envío de correo electrónico con el resumen adjunto
        if enviar_resumen_compra(usuario_correo, resumen_html):
            print("Correo electrónico enviado exitosamente")
            # Eliminación de productos del carrito después de la compra
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM carrito WHERE id_usuario = %s", (id_usuario,))
            mysql.connection.commit()
            cur.close()
            
            return jsonify({'message': 'Compra realizada exitosamente'})
        else:
            print("Error al enviar el correo electrónico")
            return jsonify({'error': 'Error al enviar el correo electrónico'}), 500
        
        
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return jsonify({'error': 'Error al realizar la compra'}), 500
    
#-------APIS-----
@app.route('/listar-producto', methods=['GET'])
def produc():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()

    # Crear una lista de diccionarios con los datos de los productos
    productos_list = []
    for producto in productos:
        producto_dict = {
            'id': producto,
            'nombre': producto,
            'colores': producto,
            'tallas': producto,
            'precio': producto,
            'imagen': producto
        }
        productos_list.append(producto_dict)
    
    

    return jsonify(productos=productos_list)

@app.route('/listar-entrenadores', methods=['GET'])
def listarEntrenadores():
    
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM entrenadores")
        entrenadores = cur.fetchall()

        # Crear una lista de diccionarios con los datos de los entrenadores
        entrenadores_list = []
        for entrenador in entrenadores:
            entrenador_dict = {
                'id': entrenador,
                'nombre': entrenador,
                'descripcion': entrenador,
                'foto': entrenador
            }
            entrenadores_list.append(entrenador_dict)

        return jsonify(entrenadores=entrenadores_list)

    


if __name__ == "__main__":
    mail.init_app(app)

    app.secret_key="sebastian_2"

    app.run(debug=True)