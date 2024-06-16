import numpy as np
import matplotlib.pyplot as plt
import random

# Tiempo simulacion
ANIOS_SIMULACION = 2
# DIAS_SIMULACION = 365 * ANIOS_SIMULACION # 730 dias
DIAS_SIMULACION = 20
# Valores promedios
PROMEDIO_KITS_MENSUALES = 130 # sigue una distribucion de poisson
MEDIA_PACIENTES_DIARIOS = 110 # sigue una distribucion de poisson
PROMEDIO_TIEMPO_CIRUGIA = 1.5 # tiempo en horas
PROB_RESERVA_QUIRONAFO = 0.43 # 43% Uniforme
PROMEDIO_TIEMPO_INTERNACION = 2  # dias, sigue una distribucion exponencial
PROMEDIO_CIRUGIAS_DIARIAS = 8 # por quirofano

# Parametros iniciales de la simulacion
KITS_INICIALES = np.random.poisson(PROMEDIO_KITS_MENSUALES)
CAMAS_TOTALES = 210 # parametro de entrada para comprarar con los objetivos propuestos
CANT_QUIROFANOS = 4 # parametro de entrada para comparar con los objetivos propuestos
CANT_HORAS_ATENCION_QUIROFANO = 12 # tiempo en horas
KITS_REPOSICION_DIARIA = 4 # parametro de entrada para comprarar con los objetivos propuestos

# Colas
quirofanos = {
    'quirofano 1' : [],
    'quirofano 2' : [],
    'quirofano 3' : [],
    'quirofano 4' : []
}

# Paciente. Atributos: DIA DE INTERNACION Y DIA DE ALTA
paciente_base = {
    'dia_internacion': 0,
    'dia_alta': 0,
}

# Arrays
disponibilidad_camas = [CAMAS_TOTALES] * DIAS_SIMULACION

# Calcular probabilidades
def generar_demanda_diaria():
    return np.random.poisson(MEDIA_PACIENTES_DIARIOS) # CANTIDAD DE PACIENTES QUE INGRESAN DIARIAMENTE

def generar_dias_internacion():
    return np.random.exponential(PROMEDIO_TIEMPO_INTERNACION) # TIEMPO EN EL QUE LOS PACIENTES ESTAN INTERNADOS OCUPANDO UNA CAMA

def generar_cantidad_cirugias_diarias():
    return np.random.poisson(PROMEDIO_CIRUGIAS_DIARIAS)

def determinar_tiempo_operacion():
    return np.random.exponential(PROMEDIO_TIEMPO_CIRUGIA) # TIEMPO DE SALIDA DE PACIENTE DEL QUIROFANO

def asignar_cama(dia, cant_dias_internacion):

    for dia_estadia in range(dia, dia+cant_dias_internacion):
        disponibilidad_camas[dia_estadia] -= 1

def crear_paciente(dia_internacion, dia_alta):
    paciente = paciente_base.copy()
    paciente['dia_internacion'] = dia_internacion
    paciente['dia_alta'] = dia_alta
    return paciente

# def determinar_quirofano_con_disponibilidad(ocupacion_quirofanos):
#     for key, ocupacion in ocupacion_quirofanos.items():
#         if ocupacion <= CANT_HORAS_ATENCION_QUIROFANO:
#             return key
#     return None

def determinar_quirofano():
    quirofanos_keys = list(quirofanos.keys())
    key = quirofanos_keys[random.randint(0,3)]
    return key


def asignar_quirofano(paciente, quirofano):
    quirofanos[quirofano].append(paciente)

def procesar_pacientes(dia, ocupacion_quirofanos, cantidad_pacientes):
    for i in range(cantidad_pacientes):               
        cant_dias_internacion = generar_dias_internacion()
        cant_dias_internacion = 1 if cant_dias_internacion < 1 else cant_dias_internacion # Tomamos los pacientes < 0 dias internacion como = 1(un) dia de internacion
        dias_int = int(cant_dias_internacion)
        if dia+dias_int <= DIAS_SIMULACION:
            asignar_cama(dia, dias_int)
            necesita_quirofano = np.random.uniform(0,1)
            if necesita_quirofano >= 0.43:
                paciente = crear_paciente(dia, dia+cant_dias_internacion)
                quirofano = determinar_quirofano()
                asignar_quirofano(paciente, quirofano)
        else:
            break

def hay_kits(kits_disponibles):
    return kits_disponibles > 0

def agregar_quirofano():
    pass

def inicializar_tiempo_ocupacion_quirofano():
    pass

def simulacion():

    # Contadores globales totales
    total_kits_utilizados = []
    total_ocupacion_quirofanos = []
    tiempo_espera_quirofanos = []
    total_operaciones_concretadas_diarias = []
    cirugias_reprogramadas = 0
    cirugias_concretadas = 0
    cirugias_rechazadas = 0
    pacientes_rechazados = 0

    kits_disponibles = 4
    
    for dia in range(DIAS_SIMULACION):
        
        ocupacion_quirofanos = {
            'quirofano 1' : 0,
            'quirofano 2' : 0,
            'quirofano 3' : 0,
            'quirofano 4' : 0
        }

        kits_disponibles += KITS_REPOSICION_DIARIA #Incrementar kits diariamente
        
        '''ORGANIZACION DE LA DEMANDA'''

        llegadas = generar_demanda_diaria()

        if disponibilidad_camas[dia] >= llegadas:
            procesar_pacientes(dia, ocupacion_quirofanos, llegadas)
        else:
            pacientes_rechazados += llegadas - disponibilidad_camas[dia]
            camas_disponibles = disponibilidad_camas[dia]
            procesar_pacientes(dia, ocupacion_quirofanos, camas_disponibles)

        '''INICIO HORARIO ATENCION'''

       
        for key in quirofanos:
            while (ocupacion_quirofanos[key] <= CANT_HORAS_ATENCION_QUIROFANO and len(quirofanos[key]) > 0 and hay_kits(kits_disponibles)):
                paciente = quirofanos[key].pop(0)
                if dia <= paciente['dia_alta']:
                    if hay_kits(kits_disponibles):
                        ocupacion_quirofanos[key] += determinar_tiempo_operacion()
                        kits_disponibles -= 1
                        cirugias_concretadas += 1
                        tiempo_espera_quirofanos.append(dia - paciente['dia_internacion'])
                    else:
                        cirugias_reprogramadas_por_insumos += 1
                        quirofanos[key].insert(0, paciente)
  
                else:
                    pacientes_rechazados += 1
                    cirugias_rechazadas += 1
            if kits_disponibles == 0:
                cirugias_reprogramadas_por_insumos += len(quirofanos[key])
            else:
                cirugias_reprogramadas_por_tiempo += len(quirofanos[key])                    
        
        total_operaciones_concretadas_diarias.append(cirugias_concretadas)
        total_kits_utilizados.append(kits_disponibles)
        total_ocupacion_quirofanos.append(ocupacion_quirofanos)

    print('tiempo total de ocupacion del quirofano', total_ocupacion_quirofanos)
    print('quirofanos con pacientes', quirofanos)
    print('tiempo de espera quirofano', tiempo_espera_quirofanos)
    print('camas disponibles', disponibilidad_camas)
    print('pacientes rechazados', pacientes_rechazados)
    print('cirugias reprogramadas', cirugias_reprogramadas)
    print('cirugias concretadas', cirugias_concretadas)
    print('cirugias rechazadas', cirugias_rechazadas)
    print('kits_disponibles', kits_disponibles)


if __name__ == '__main__':
    simulacion()



