import numpy as np
import matplotlib.pyplot as plt
import random
from funciiones import *
def  simular(anios_simulacion,cantidad_camas,cantidad_quirofanos,horas_atencion_quirofanos,inventario_inicial,reposicion_diaria_inventario):
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

    # Tiempo simulacion
    ANIOS_SIMULACION = anios_simulacion
    #Dias simulacion
    DIAS_SIMULACION = ANIOS_SIMULACION*365
    #Cantidad total De Camas 
    CAMAS_TOTALES =cantidad_camas
    #Tiempo De Atencion de los quirofanos por dia(medido en horas )
    CANT_HORAS_ATENCION_QUIROFANO = horas_atencion_quirofanos
    #Total De Quirofanos
    CANT_QUIROFANOS=cantidad_quirofanos
    #Stock inicial de kits medicos (sigue una distribuccion de poisson)
    PROMEDIO_KITS_MENSUALES=inventario_inicial
    
    MEDIA_PACIENTES_DIARIOS = 110 # sigue una distribucion de poisson
    PROMEDIO_TIEMPO_CIRUGIA = 1.5 # tiempo en horas
    PROB_RESERVA_QUIRONAFO = 0.43 # 43% Uniforme
    PROMEDIO_TIEMPO_INTERNACION = 2  # dias, sigue una distribucion exponencial
    PROMEDIO_CIRUGIAS_DIARIAS = 8 # por quirofano
    # Parametros iniciales de la simulacion
    KITS_INICIALES = np.random.poisson(PROMEDIO_KITS_MENSUALES)
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