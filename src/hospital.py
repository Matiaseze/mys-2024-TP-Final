import numpy as np
import matplotlib.pyplot as plt
import math
# Tiempo simulacion


# Valores promedios
PROMEDIO_KITS_MENSUALES = 130 # sigue una distribucion de poisson
MEDIA_PACIENTES_DIARIOS = 110 # sigue una distribucion de poisson
PROMEDIO_TIEMPO_CIRUGIA = 1.5 # tiempo en horas
PROB_RESERVA_QUIRONAFO = 0.43 # 43% Uniforme
PROMEDIO_TIEMPO_INTERNACION = 2  # dias, sigue una distribucion exponencial
PROMEDIO_CIRUGIAS_DIARIAS = 8 # por quirofano

# Parametros iniciales de la simulacion



# Paciente. Atributos: DIA DE INTERNACION Y DIA DE ALTA
paciente_base = {
    'dia_internacion': 0,
    'dia_alta': 0,
}


# Calcular probabilidades
def generar_demanda_diaria():
    return np.random.poisson(MEDIA_PACIENTES_DIARIOS) # CANTIDAD DE PACIENTES QUE INGRESAN DIARIAMENTE

def generar_dias_internacion():
    return np.random.exponential(PROMEDIO_TIEMPO_INTERNACION) # TIEMPO EN EL QUE LOS PACIENTES ESTAN INTERNADOS OCUPANDO UNA CAMA

def generar_cantidad_cirugias_diarias():
    return np.random.poisson(PROMEDIO_CIRUGIAS_DIARIAS)

def determinar_tiempo_operacion():
    return np.random.exponential(PROMEDIO_TIEMPO_CIRUGIA) # TIEMPO DE SALIDA DE PACIENTE DEL QUIROFANO

def asignar_cama(estado_sistema, dia, cant_dias_internacion):

    for dia_estadia in range(dia, dia+cant_dias_internacion):
        estado_sistema['disponibilidad_camas'][dia_estadia] -= 1

def crear_paciente(dia_internacion, dia_alta):
    paciente = paciente_base.copy()
    paciente['dia_internacion'] = dia_internacion
    paciente['dia_alta'] = dia_alta
    return paciente

def asignar_quirofano(paciente,quirofanos, quirofano):
    quirofanos[quirofano].append(paciente)

def procesar_pacientes(estado_sistema, dia, quirofanos, cantidad_pacientes):

    quirofano_counter = 0
    quirofano_keys = list(quirofanos.keys())
    num_quirofanos = len(quirofanos)
    pacientes_sin_reserva = 0
    pacientes_con_reserva = 0

    for i in range(cantidad_pacientes):               
        cant_dias_internacion = generar_dias_internacion()
        cant_dias_internacion = 1 if cant_dias_internacion < 1 else cant_dias_internacion # Tomamos los pacientes < 0 dias internacion como = 1(un) dia de internacion
        dias_int = int(cant_dias_internacion)
        if dia+dias_int <= estado_sistema['dias_simulacion']:
            asignar_cama(estado_sistema, dia, dias_int)
            necesita_quirofano = np.random.uniform(0,1)
            if necesita_quirofano >= 0.43:
                paciente = crear_paciente(dia, dia+cant_dias_internacion)
                quirofano = quirofano_keys[np.random.randint(0,num_quirofanos)]
                asignar_quirofano(paciente,quirofanos, quirofano)
                quirofano_counter += 1
                pacientes_con_reserva += 1
            else:
                pacientes_sin_reserva += 1
                
        else:
            break
    estado_sistema['reservas_por_dia'].append(pacientes_con_reserva)
    estado_sistema['pacientes_sin_reserva_por_dia'].append(pacientes_sin_reserva)    

def hay_kits(kits_disponibles):
    return kits_disponibles > 0

def inicializar_quirofanos(cantidad_quirofanos):
    quirofanos = {f'quirofano {i+1}': [] for i in range(cantidad_quirofanos)}
    ocupacion_quirofanos = {f'quirofano {i+1}': 0 for i in range(cantidad_quirofanos)}
    return quirofanos, ocupacion_quirofanos

def simulacion(anios_simulacion,cantidad_camas,cantidad_quirofanos,horas_atencion_quirofanos,inventario_inicial,reposicion_diaria_inventario):

    DIAS_SIMULACION = 365 * anios_simulacion # 730 dias
    CAMAS_TOTALES = cantidad_camas # parametro de entrada para comprarar con los objetivos propuestos
    CANT_QUIROFANOS = cantidad_quirofanos
    CANT_HORAS_ATENCION_QUIROFANO = horas_atencion_quirofanos # tiempo en horas
    KITS_INICIALES = inventario_inicial
    KITS_REPOSICION_DIARIA = reposicion_diaria_inventario # parametro de entrada para comprarar con los objetivos propuestos

    # Contadores globales totales

    estado_sistema = {

        'dias_simulacion': DIAS_SIMULACION,
        'cantidad de quirofanos:': CANT_QUIROFANOS,
        'kits_iniciales': KITS_INICIALES,
        'llegadas_por_dia': [],
        'reservas_por_dia': [],
        'disponibilidad_camas': [CAMAS_TOTALES] * DIAS_SIMULACION,

        'pacientes_rechazados_por_dia': [],
        'pacientes_rechazados_por_ausencia_camas': [],
        'pacientes_rechazados_por_internacion_agotada': [],
        'pacientes_sin_reserva_por_dia': [], 
        'kits_diarios_disponibles': [],
        'kits_diarios_utilizados': [],
        'ocupacion_diaria_quirofanos': [],
        'tiempo_espera_diario_quirofanos': [],
        'cirugias_rechazadas_por_dia' : [],
        'cirugias_concretadas_por_dia' : [],
        'cirugias_reprogramadas_por_insumos': [],
        'cirugias_reprogramadas_por_tiempo': [],
        'cirugias_reprogramadas_por_cuota_diaria': [],

        'total_cirugias_reprogramadas_por_insumos': 0,
        'total_cirugias_reprogramadas_por_tiempo': 0,
        'total_cirugias_reprogramadas_por_cuota_diaria': 0,
        'total_cirugias_concretadas': 0,
        'total_cirugias_rechazadas': 0,
        'total_pacientes_rechazados_por_ausencia_camas': 0,
        'total_pacientes_rechazados_por_internacion_agotada': 0


    }

    cirugias_concretadas = 0
    cirugias_rechazadas = 0
    pacientes_rechazados_por_ausencia_camas = 0
    pacientes_rechazados_por_internacion_agotada = 0
    
    kits_disponibles = estado_sistema['kits_iniciales']

    
    quirofanos, ocupacion_quirofanos = inicializar_quirofanos(CANT_QUIROFANOS)
    
    for dia in range(DIAS_SIMULACION):

        lista_tiempo_espera = []
        
        ocupacion_quirofanos = {key: 0 for key in ocupacion_quirofanos}

        kits_disponibles += KITS_REPOSICION_DIARIA #Incrementar kits diariamente
        kits_utilizados = 0

        '''ORGANIZACION DE LA DEMANDA'''

        llegadas = generar_demanda_diaria()

        estado_sistema['llegadas_por_dia'].append(llegadas)

        if estado_sistema['disponibilidad_camas'][dia] >= llegadas:
            procesar_pacientes(estado_sistema, dia, quirofanos, llegadas)
        else:
            pacientes_rechazados_por_ausencia_camas += llegadas - estado_sistema['disponibilidad_camas'][dia]
            camas_disponibles = estado_sistema['disponibilidad_camas'][dia]
            procesar_pacientes(estado_sistema, dia, quirofanos, camas_disponibles)

        '''INICIO HORARIO ATENCION'''

        for quirofano in quirofanos:
            
            cantidad_cirugias = generar_cantidad_cirugias_diarias()
            contador_cirugia = 0
            cirugias_reprogramadas_por_insumos = 0
            cirugias_reprogramadas_por_tiempo = 0
            cirugias_reprogramadas_por_cuota_diaria = 0

            while (contador_cirugia <= cantidad_cirugias 
                   and ocupacion_quirofanos[quirofano] <= CANT_HORAS_ATENCION_QUIROFANO 
                   and len(quirofanos[quirofano]) > 0 
                   and hay_kits(kits_disponibles)):
                
                paciente = quirofanos[quirofano].pop(0)
                if dia <= paciente['dia_alta']:
                    contador_cirugia += 1
                    if hay_kits(kits_disponibles):
                        ocupacion_quirofanos[quirofano] += determinar_tiempo_operacion()
                        kits_disponibles -= 1
                        kits_utilizados += 1
                        cirugias_concretadas += 1
                        lista_tiempo_espera.append(dia - paciente['dia_internacion'])
                         # El tiempo que esperan los pacientes para ingresar al quirofano
                    else:
                        cirugias_reprogramadas_por_insumos += 1
                        quirofanos[quirofano].insert(0, paciente)

                else: # Caso de rechazo
                    pacientes_rechazados_por_internacion_agotada += 1
                    cirugias_rechazadas += 1
                    
            if kits_disponibles == 0:
                cirugias_reprogramadas_por_insumos = len(quirofanos[quirofano])
            elif ocupacion_quirofanos[quirofano] > CANT_HORAS_ATENCION_QUIROFANO:
                cirugias_reprogramadas_por_tiempo = len(quirofanos[quirofano])
            else:
                cirugias_reprogramadas_por_cuota_diaria = len(quirofanos[quirofano])

            estado_sistema['total_cirugias_reprogramadas_por_insumos'] += cirugias_reprogramadas_por_insumos
            estado_sistema['total_cirugias_reprogramadas_por_tiempo'] += cirugias_reprogramadas_por_tiempo
            estado_sistema['total_cirugias_reprogramadas_por_cuota_diaria'] += cirugias_reprogramadas_por_cuota_diaria
        tiempo_espera_max = max(lista_tiempo_espera) if len(lista_tiempo_espera) > 0 else 0
        estado_sistema['tiempo_espera_diario_quirofanos'].append(tiempo_espera_max)

        # Contadores que son por dia.
        estado_sistema['kits_diarios_utilizados'].append(kits_utilizados)
        estado_sistema['kits_diarios_disponibles'].append(kits_disponibles)
        estado_sistema['ocupacion_diaria_quirofanos'].append(ocupacion_quirofanos)
        estado_sistema['pacientes_rechazados_por_ausencia_camas'].append(pacientes_rechazados_por_ausencia_camas)
        estado_sistema['pacientes_rechazados_por_internacion_agotada'].append(pacientes_rechazados_por_internacion_agotada)

        estado_sistema['cirugias_rechazadas_por_dia'].append(cirugias_rechazadas)
        estado_sistema['cirugias_concretadas_por_dia'].append(cirugias_concretadas)
        estado_sistema['cirugias_reprogramadas_por_insumos'].append(cirugias_reprogramadas_por_insumos)
        estado_sistema['cirugias_reprogramadas_por_tiempo'].append(cirugias_reprogramadas_por_tiempo)
        estado_sistema['cirugias_reprogramadas_por_cuota_diaria'].append(cirugias_reprogramadas_por_cuota_diaria)
    
    # Contadores totales

    estado_sistema['total_cirugias_concretadas'] += cirugias_concretadas
    estado_sistema['total_cirugias_rechazadas'] += cirugias_rechazadas
    estado_sistema['total_pacientes_rechazados_por_ausencia_camas'] += pacientes_rechazados_por_ausencia_camas
    estado_sistema['total_pacientes_rechazados_por_internacion_agotada'] += pacientes_rechazados_por_internacion_agotada

    
    # print(f'Cantidad de quirofanos:', estado_sistema['cantidad de quirofanos:'],'\n',
    #       'Kits iniciales:', estado_sistema['kits_iniciales'], '\n',
    #       'Kits disponibles:', estado_sistema['kits_diarios_disponibles'], '\n',
    #       'kits utilizados por dia:', estado_sistema['kits_diarios_utilizados'], '\n',
    #       'llegada de pacientes por dia:', estado_sistema['llegadas_por_dia'], '\n',
    #       'reservas de quirofano por dia:', estado_sistema['reservas_por_dia'], '\n',
    #       'disponibilidad de camas por dia:', estado_sistema['disponibilidad_camas'], '\n',
    #       'ocupacion diaria quirofanos (en horas):', estado_sistema['ocupacion_diaria_quirofanos'], '\n',
    #       'cuanto esperan los pacientes por dia en ser operados:', estado_sistema['tiempo_espera_diario_quirofanos'] , '\n',
    #       'pacientes que solo se internaron:', estado_sistema['pacientes_sin_reserva_por_dia'], '\n',
    #       'pacientes rechazados por dia:', estado_sistema['pacientes_rechazados_por_dia'], '\n',
    #       'cirugias concretadas por dia:', estado_sistema['cirugias_concretadas_por_dia'], '\n',
    #       'cirugias diarias reprogramadas por falta de insumos:', estado_sistema['cirugias_reprogramadas_por_insumos'], '\n',
    #       'cirugias diaria reprogramadas al otro dia por ocupacion del quirofano:', estado_sistema['cirugias_reprogramadas_por_tiempo'], '\n',
    #       'cirugias diaria reprogramadas al otro dia por cuota diria:', estado_sistema['cirugias_reprogramadas_por_cuota_diaria'], '\n',
    #       'Total de cirugias reprogramadas por falta insumos:', estado_sistema['total_cirugias_reprogramadas_por_insumos'], '\n',
    #       'Total de cirugias reprogramadas por falta de tiempo:', estado_sistema['total_cirugias_reprogramadas_por_tiempo'], '\n',
    #       'Total de cirugias reprogramadas por cuota diaria:', estado_sistema['total_cirugias_reprogramadas_por_cuota_diaria'], '\n',
    #       'Total cirugias concretadas:', estado_sistema['total_cirugias_concretadas'], '\n',
    #       'Total cirugias rechazadas:', estado_sistema['total_cirugias_rechazadas'], '\n',
    #       'Total pacientes rechazados:', estado_sistema['total_pacientes_rechazados']

    #       )

    return estado_sistema



