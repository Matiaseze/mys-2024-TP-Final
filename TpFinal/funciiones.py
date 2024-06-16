import numpy as np
import matplotlib.pyplot as plt
import random
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
