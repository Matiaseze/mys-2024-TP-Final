from flask import Flask, request, render_template, jsonify
# from config import config
from hospital import *

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

        estado = simulacion(anios_simulacion,cantidad_camas,cantidad_quirofanos,horas_atencion_quirofanos,inventario_inicial,reposicion_diaria_inventario)
        return jsonify(estado) 
    
    return render_template('simuladorHospital.html')

if __name__ == '__main__':
    
    app.run(debug=True,host="0.0.0.0", port=80)