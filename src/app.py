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
        graficar(estado)
        
        return render_template('simuladorHospital.html',
                                aniosSimulacion = anios_simulacion,
                                cantidadCamas = cantidad_camas,
                                cantidadQuirofanos = cantidad_quirofanos,
                                cantidadHorasAtencionQuirofanos = horas_atencion_quirofanos,
                                inventarioInicial = inventario_inicial,
                                reposicionDiariaInventario = reposicion_diaria_inventario,
                                huboSimulacion = True) 
    
    return render_template('simuladorHospital.html',                                 
                           aniosSimulacion = 2,
                           cantidadCamas = 210,
                           cantidadQuirofanos = 4,
                           cantidadHorasAtencionQuirofanos = 12,
                           inventarioInicial = 130,
                           reposicionDiariaInventario = 4,
                           huboSimulacion = False)

if __name__ == '__main__':
    
    app.run(debug=True,host="0.0.0.0", port=80)