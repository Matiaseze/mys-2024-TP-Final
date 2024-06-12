import numpy as np
import matplotlib.pyplot as plt


# Parametros iniciales de la simulacion
quirofanos = 4 # parametro de entrada para comparar con los objetivos propuestos
camas_totales = 210 # parametro de entrada para comprarar con los objetivos propuestos
kits_reposicion_diaria = 4 # parametro de entrada para comprarar con los objetivos propuestos
dias_simulacion = 365
anios_simulacion = 2
dias_meses = 30 # se toma que cada mes tiene 30 dias

# Valores promedios
promedio_kits_mensuales = 130 # distribucion de poisson
promedio_llegadas_diarias = 110 # distribucion de poisson
prob_reserva_quirofano = 0.43 # 43%
promedio_tiempo_internacion = 2  # tiempo en dias
promedio_cirugias_diarias = 8 # por quirofano
promedio_tiempo_cirugia = 1.5 / 12  # tiempo en horas




# Colecciones
espera_camas = []
espera_quirofanos = []
cirugias_reprogramadas = []
ocupacion_camas = []
ocupacion_quirofanos = []

def simulacion():

    # Inicializar valores
    kits_iniciales = np.random.poisson(promedio_kits_mensuales) # valor inicial
    pacientes_internados = 0
    cirugias_realizadas = 0
    pacientes_esperando_camas = 0
    pacientes_esperando_quirofano = 0
    kits_disponibles = kits_iniciales # valor inicial
    camas_disponibles = camas_totales # valor inicial
    
    for anio in range(anios_simulacion):
        for dia in range(dias_simulacion):
            
            llegadas_pacientes = np.random.poisson(promedio_llegadas_diarias)
            reservas_quirofano = np.sum(np.random.uniform(0, 1, llegadas_pacientes) < prob_reserva_quirofano)
            
            for i in range(llegadas_pacientes):
                if camas_disponibles > 0:
                    camas_disponibles -= 1
                    pacientes_internados += 1
                else:
                    pacientes_esperando_camas += 1

            for j in range(reservas_quirofano):
                if cirugias_realizadas < quirofanos * np.random.poisson(promedio_cirugias_diarias) > 0: # añadirlo en la condicion
                    cirugias_realizadas += 1
                    kits_disponibles -= 1 # asumiento que un kit se usa en una operacion se deberia descontar un kit
                else:
                    pacientes_esperando_quirofano += 1

            kits_disponibles += kits_reposicion_diaria

            camas_libres = np.random.poisson(camas_totales)
            camas_disponibles = min(camas_disponibles + camas_libres, camas_totales)

            ocupacion_camas.append(camas_totales - camas_disponibles)
            ocupacion_quirofanos.append(cirugias_realizadas)
            espera_camas.append(pacientes_esperando_camas)
            espera_quirofanos.append(pacientes_esperando_quirofano)
            cirugias_reprogramadas.append(reservas_quirofano - cirugias_realizadas)
    
    print("ocupacion de camas", ocupacion_camas)
    print("ocupacion de quirofanos", ocupacion_quirofanos)
    print("camas en espera", espera_camas)
    print("espera de quirofanos", espera_quirofanos)
    print("pacientes con cirugias reprogramadas", cirugias_reprogramadas)
