from flask import Flask
from flask import send_from_directory
from flask import request
import os
from flask import make_response
from flask import abort
from flask import render_template
from flask import redirect, url_for

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory (os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

#rutas venv
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

@app.route('/horario')
def horario():
    return render_template('horario.html')



@app.route('/acercade')
def acercade():
    return render_template('acercade.html')

@app.route('/productos')
def productos():
    return render_template('ropa.html')

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

@app.route('/membresias')
def membresias():
    return render_template('membresias.html')

@app.route('/entrenadores')
def entrenadores():
    return render_template('entrenadores.html')

@app.route('/personalizado')
def personalizado():
    return render_template('personalizado.html')

@app.errorhandler(404)
def page_error(error):
    return '''
    <style>
        body, html {
            height: 100%;
            margin: 0;
        }

        .bg {
            background-image: url("''' + url_for('static', filename='img/not-found.jpeg') + '''");
            height: 100%;
            background-position: center;
            background-repeat: no-repeat;
            background-size: contain;
            background-color: #000;  /* puedes cambiar esto al color que prefieras */
        }
    </style>
    <div class="bg"></div>
    ''', 404



if __name__ == "__main__":
    app.run(port=8090, debug=True)