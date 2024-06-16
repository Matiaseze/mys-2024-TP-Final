import numpy as np
import matplotlib.pyplot as plt
import random
from simulacion import *
from flask import Flask, request, render_template

app = Flask(__name__)


    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Aquí obtenemos los datos del formulario
        anios_simulacion = int(request.form['aniosSimulacion'])
        cantidad_camas = int(request.form['cantidadCamas'])
        cantidad_quirofanos = int(request.form['cantidadQuirofanos'])
        horas_atencion_quirofanos = int(request.form['cantidadHorasAtencionQuirofanos'])
        inventario_inicial = int(request.form['inventarioInicial'])
        reposicion_diaria_inventario = int(request.form['reposicionDiariaInventario'])
        simular(anios_simulacion,cantidad_camas,cantidad_quirofanos,horas_atencion_quirofanos,inventario_inicial,reposicion_diaria_inventario)
    return render_template('simuladorHospital.html')

if __name__ == '__main__':
    app.run(debug=True)