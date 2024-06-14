import numpy as np
import matplotlib.pyplot as plt
import heapq

# Tiempo simulacion
DIAS_SIMULACION = 365
ANIOS_SIMULACION = 2

# Valores promedios
PROMEDIO_KITS_MENSUALES = 130 # distribucion de poisson
MEDIA_PACIENTES_DIARIOS = 110 # distribucion de poisson
PROMEDIO_TIEMPO_CIRUGIA = 1.5 / 12  # tiempo en horas
PROB_RESERVA_QUIRONAFO = 0.43 # 43% Uniforme
PROMEDIO_TIEMPO_INTERNACION = 2  # CONSULTAR TIEMPO
PROMEDIO_CIRUGIAS_DIARIAS = 8 # por quirofano

# Parametros iniciales de la simulacion
KITS_INICIALES = np.random.poisson(PROMEDIO_KITS_MENSUALES)
CAMAS_TOTALES = 210 # parametro de entrada para comprarar con los objetivos propuestos
QUIROFANOS = 4 # parametro de entrada para comparar con los objetivos propuestos
KITS_REPOSICION_DIARIA = 4 # parametro de entrada para comprarar con los objetivos propuestos
TIEMPO_REPOSICION_KITS = 1 # CONSULTAR TIEMPO

# Estado inicial de la simulacion
estado_del_sistema = {
    'reloj': 0, # Ver si esto va en horas o dias
    'camas_ocupadas': 0,
    'kits_disponibles': KITS_INICIALES,
    'cola_pacientes_espera': [], # pacientes que esperan cirugia
    'quirofanos_ocupados': 0,
    'pacientes_rechazados': 0,
    'tiempo_ocupacion_quirofanos': [],    
    'eventos': []
}

# Calcular probabilidades
def calcular_promedio_llegada_pacientes():
    return np.random.poisson(MEDIA_PACIENTES_DIARIOS) # CANTIDAD DE PACIENTES QUE INGRESAN DIARIAMENTE
 
def calcular_promedio_reserva_quirofano(pacientes):
    return np.sum(np.random.uniform(0, 1, pacientes) < PROB_RESERVA_QUIRONAFO) 

def calcular_promedio_paciente_quirofano():
    return np.random.poisson(PROMEDIO_TIEMPO_CIRUGIA) # TIEMPO DE SALIDA DE PACIENTE DEL QUIROFANO

def calcular_promedio_paciente_salida():
    return np.random.exponential(PROMEDIO_TIEMPO_INTERNACION) # TIEMPO EN EL QUE LOS PACIENTES ESTAN INTERNADOS


# Eventos
'''
La funcion heapq.heappush(heap, item) trata a los arreglos como colas 
de prioridad entonces siempre que se agrega un elemento a la cola de 
eventos y lo ordena segun el tiempo (el primer elemento de la tupla).
'''
def agregar_evento(estado, tiempo, tipo):
    heapq.heappush(estado['eventos'], (tiempo, tipo)) # Cola de eventos

def llegada_paciente(estado):
    if estado['camas_ocupadas'] < CAMAS_TOTALES:
        estado['camas_ocupadas'] += 1
    else:
        estado['pacientes_rechazados'] += 1

def programar_cirugia(estado, tiempo_prom_cirugia):
    if estado['quirofanos_ocupados'] < QUIROFANOS and estado['kits_disponibles'] > 0 :
        estado['quirofanos_ocupados'] += 1
        estado['kits_disponibles'] += 1
        tiempo_fin_cirugia = estado['reloj'] + tiempo_prom_cirugia # En horas
        agregar_evento(estado, tiempo_fin_cirugia, 'fin_cirugia')
    else:
        estado['tiempo_ocupacion_quirofanos'].append(estado['reloj'])

def fin_cirugia(estado):
    estado['quirofanos_ocupados'] -= 1
    fin_internacion = estado['reloj'] + calcular_promedio_paciente_salida()
    agregar_evento(estado, fin_internacion, 'salida_paciente')

def salida_paciente(estado):
    estado['camas_ocupadas'] -= 1

def reposicion_kits(estado):
    estado['kits_disponibles'] += KITS_REPOSICION_DIARIA
    proxima_reposicion = estado['reloj'] + TIEMPO_REPOSICION_KITS
    agregar_evento(estado, proxima_reposicion, 'reposicion_kits')

'''
Consultar:
en el caso que se rechace un paciente y tambien el caso de tener que dejarlo en cola de espera de quirofano

'''

def simulacion():
    
    for anio in range(ANIOS_SIMULACION):
        for dia in range(DIAS_SIMULACION):
            #print('DEBUG dia Nro:', dia)
            llegadas_pacientes = calcular_promedio_llegada_pacientes()
            reservas_quirofano = calcular_promedio_reserva_quirofano(llegadas_pacientes)

            for paciente in range(llegadas_pacientes):
                #print('DEBUG paciente Nro:', paciente)
                tiempo_llegada = np.random.poisson(24 * 60 / MEDIA_PACIENTES_DIARIOS) # Tiempo que tarda UN paciente en llegar (en minutos consultar!!!)
                agregar_evento(estado_del_sistema, tiempo_llegada, 'llegada_paciente')

            for reserva in range(reservas_quirofano):
                duracion_cirugia = calcular_promedio_paciente_quirofano()
                agregar_evento(estado_del_sistema, duracion_cirugia, programar_cirugia)

            for evento in estado_del_sistema['eventos']:

                estado_del_sistema['reloj'], tipo_evento = evento
    
                if tipo_evento == 'llegada_paciente':
                    llegada_paciente(estado_del_sistema)
                elif tipo_evento == 'programar_cirugia':
                    programar_cirugia(estado_del_sistema)
                elif tipo_evento == 'fin_cirugia':
                    fin_cirugia(estado_del_sistema)
                elif tipo_evento == 'salida_paciente':
                    salida_paciente(estado_del_sistema)
                elif tipo_evento == 'reposicion_kits':
                    reposicion_kits(estado_del_sistema)    


