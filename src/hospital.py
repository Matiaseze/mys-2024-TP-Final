import numpy as np
import matplotlib.pyplot as plt
import os
import random
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
        'cantidad_de_quirofanos': CANT_QUIROFANOS,
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
        'total_pacientes_rechazados_por_internacion_agotada': 0,
        'tiempo_espera_promedio_de_quirofanos' : 0


    }

    
    kits_disponibles = KITS_INICIALES

    
    quirofanos, ocupacion_quirofanos = inicializar_quirofanos(CANT_QUIROFANOS)
    
    for dia in range(DIAS_SIMULACION):

        cirugias_concretadas = 0
        cirugias_rechazadas = 0
        pacientes_rechazados_por_ausencia_camas = 0
        pacientes_rechazados_por_internacion_agotada = 0
        lista_tiempo_espera = []
        
        ocupacion_quirofanos = {key: 0 for key in ocupacion_quirofanos}

        kits_disponibles += KITS_REPOSICION_DIARIA # Incrementar kits diariamente
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
        quirofanos_keys = list(quirofanos.keys())
        random.shuffle(quirofanos_keys)

        for quirofano in quirofanos_keys:
            
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
                    
            if not hay_kits(kits_disponibles):
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
    estado_sistema['tiempo_espera_promedio_de_quirofanos'] = np.mean(estado_sistema['tiempo_espera_diario_quirofanos'])
    estado_sistema['total_cirugias_concretadas'] = sum(estado_sistema['cirugias_concretadas_por_dia'])
    estado_sistema['total_cirugias_rechazadas'] = sum(estado_sistema['cirugias_rechazadas_por_dia'])
    estado_sistema['total_pacientes_rechazados_por_ausencia_camas'] = sum(estado_sistema['pacientes_rechazados_por_ausencia_camas'])
    estado_sistema['total_pacientes_rechazados_por_internacion_agotada'] = sum(estado_sistema['pacientes_rechazados_por_internacion_agotada'])


    return estado_sistema

def calcular_porentaje_ocupacion_quirofanos_total(estado_sistema):
    totales = {k: 0 for k in estado_sistema["ocupacion_diaria_quirofanos"][0].keys()}
    
    for quirofanos in estado_sistema["ocupacion_diaria_quirofanos"]:
        for k, v in quirofanos.items():
                totales[k] += v

    for k, v in totales.items():
        totales[k] = round((totales[k] * 100) / (estado_sistema["dias_simulacion"] * 12))
    
    return totales

def calcular_promedio_de_horas_de_ocupacion_quirofanos_mensual(estado_sistema):
    totales = {k: [] for k in estado_sistema["ocupacion_diaria_quirofanos"][0].keys()}

    for k in totales.keys():

        for i in range(0, len(estado_sistema["ocupacion_diaria_quirofanos"]), 30):

            uso_mes = [estado_sistema['ocupacion_diaria_quirofanos'][j][k] for j in range(i, min(i+30, len(estado_sistema["ocupacion_diaria_quirofanos"])))]
            promedio_mes = np.mean(uso_mes)
            totales[k].append(promedio_mes)

    return totales



def graficar(path_resultados, estado_sistema):
    # Días de la simulación
    dias_simulacion = estado_sistema['dias_simulacion']
    
    # Calcular el uso de kits mensualmente
    uso_kits_mensual = []
    kits_disponibles_mensual = []
    camas_disponibles_mensual = []
    demanda_mensual = []
    reserva_quirofanos_mensual = []
    cirugias_concretadas_mensual = []
    cirugias_reprogramadas_por_insumos_mensual = []
    cirugias_reprogramadas_por_tiempo_mensual = []
    cirugias_reprogramadas_por_cuota_mensual = []
    pacientes_rechazados_por_falta_de_camas = []
    pacientes_rechazados_por_internacion_agotada = []
    promedio_espera_por_tiempo_espera_quirofanos_mensual = []
    # ocupacion_total_de_quirofanos = {k: 0 for k in estado_sistema["ocupacion_diaria_quirofanos"][0].keys()}
    
    for i in range(0, dias_simulacion, 30):  # Agrupar en meses (aproximadamente 30 días por mes)
        uso_mes = np.mean(estado_sistema['kits_diarios_utilizados'][i:i+30])
        uso_kits_mensual.append(uso_mes)

        kit_mes = np.mean(estado_sistema['kits_diarios_disponibles'][i:i+30])
        kits_disponibles_mensual.append(kit_mes)

        cama_mes = np.mean(estado_sistema['disponibilidad_camas'][i:i+30])
        camas_disponibles_mensual.append(cama_mes)

        demanda_mes = sum(estado_sistema['llegadas_por_dia'][i:i+30])
        demanda_mensual.append(demanda_mes)

        reserva_mes = sum(estado_sistema['reservas_por_dia'][i:i+30])
        reserva_quirofanos_mensual.append(reserva_mes)

        cirugias_concretada_por_mes = np.mean(estado_sistema['cirugias_concretadas_por_dia'][i:i+30])
        cirugias_concretadas_mensual.append(cirugias_concretada_por_mes)

        cirugias_reprogramadas_por_insumos_por_mes = sum(estado_sistema['cirugias_reprogramadas_por_insumos'][i:i+30])
        cirugias_reprogramadas_por_insumos_mensual.append(cirugias_reprogramadas_por_insumos_por_mes)

        cirugias_reprogramadas_por_tiempo_por_mes = sum(estado_sistema['cirugias_reprogramadas_por_tiempo'][i:i+30])
        cirugias_reprogramadas_por_tiempo_mensual.append(cirugias_reprogramadas_por_tiempo_por_mes)

        cirugias_reprogramadas_por_cuota_por_mes = sum(estado_sistema['cirugias_reprogramadas_por_cuota_diaria'][i:i+30])
        cirugias_reprogramadas_por_cuota_mensual.append(cirugias_reprogramadas_por_cuota_por_mes)

        pacientes_rechazados_por_falta_de_camas_por_mes = sum(estado_sistema['pacientes_rechazados_por_ausencia_camas'][i:i+30])
        pacientes_rechazados_por_falta_de_camas.append(pacientes_rechazados_por_falta_de_camas_por_mes)
        
        pacientes_rechazados_por_internacion_agotada_por_mes = np.mean(estado_sistema['pacientes_rechazados_por_internacion_agotada'][i:i+30])
        pacientes_rechazados_por_internacion_agotada.append(pacientes_rechazados_por_internacion_agotada_por_mes)
        
        promedio_espera_por_tiempo_espera_quirofanos_por_mes = np.mean(estado_sistema['tiempo_espera_diario_quirofanos'][i:i+30])
        promedio_espera_por_tiempo_espera_quirofanos_mensual.append(promedio_espera_por_tiempo_espera_quirofanos_por_mes)
        

    # Meses para el gráfico
    meses = np.arange(0, len(uso_kits_mensual))
    
    # Graficar la utilización de kits mensualmente
    plt.figure(figsize=(10, 6))
    plt.bar(meses, uso_kits_mensual, color='red')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Cantidad de Kits')
    plt.title('Uso promedio mensual de Kits')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'uso_mensual_kits.png'), dpi=300)

    # Graficar la diponibilidad de kits mensualmente
    plt.figure(figsize=(10, 6))
    plt.bar(meses, kits_disponibles_mensual, color='red')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Kits disponibles')
    plt.title('Promedio de kits disponibles mensualmente')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'disponibilidad_mensual_kits.png'), dpi=300)
 

        # Graficar la diponibilidad de kits mensualmente
    plt.figure(figsize=(10, 6))
    plt.bar(meses, camas_disponibles_mensual, color='blue')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Camas disponibles')
    plt.title('Promedio de camas disponibles mensualmente')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'disponibilidad_mensual_camas.png'), dpi=300)

        # Graficar la diponibilidad de kits mensualmente
    plt.figure(figsize=(10, 6))
    plt.bar(meses, demanda_mensual , color='blue')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Demanda')
    plt.title('Demanda mensual')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'demanda_mensual.png'), dpi=300)

    plt.figure(figsize=(10, 6))
    plt.bar(meses, reserva_quirofanos_mensual , color='green')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Reserva')
    plt.title('Reserva de quirofanos mensual')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'reserva_mensual.png'), dpi=300)

    plt.figure(figsize=(10, 6))
    plt.bar(meses, cirugias_concretadas_mensual , color='lime')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Cirugias concretadas')
    plt.title('Cirugias concretadas mensuales')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'cirugias_concretadas_mensual.png'), dpi=300)

    plt.figure(figsize=(10, 6))
    plt.bar(meses, cirugias_reprogramadas_por_insumos_mensual, color='lime')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Cirugias reprogramadas por insumos')
    plt.title('Cirugias reprogramadas por insumos por mes')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'cirugias_reprogramadas_por_insumos_mensual.png'), dpi=300)
    

    plt.figure(figsize=(10, 6))
    plt.bar(meses, cirugias_reprogramadas_por_tiempo_mensual, color='lime')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Cirugias reprogramadas por tiempo')
    plt.title('Cirugias reprogramadas por falta de tiempo de internacion por mes')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'cirugias_reprogramadas_por_tiempo_mensual.png'), dpi=300)

    plt.figure(figsize=(10, 6))
    plt.bar(meses, cirugias_reprogramadas_por_cuota_mensual, color='lime')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Cirugias reprogramadas por cuota')
    plt.title('Cirugias reprogramadas por cuota diaria excedida por mes')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'cirugias_reprogramadas_por_cuota_mensual.png'), dpi=300)

    plt.figure(figsize=(10, 6))
    plt.bar(meses, pacientes_rechazados_por_falta_de_camas, color='orange')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Pacientes rechazados por falta de camas')
    plt.title('Pacientes rechazados mensualmente por falta de camas')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'pacientes_rechazados_por_falta_de_camas_por_mes.png'), dpi=300)

    plt.figure(figsize=(10, 6))
    plt.bar(meses, pacientes_rechazados_por_internacion_agotada, color='orange')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Pacientes rechazados por internacion agotada')
    plt.title('Pacientes rechazados mensualmente por internacion agotada')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'pacientes_rechazados_por_internacion_agotada_por_mes.png'), dpi=300)
    
    plt.figure(figsize=(10, 6))
    plt.bar(meses, promedio_espera_por_tiempo_espera_quirofanos_mensual, color='orange')
    plt.xlabel('Mes de Simulación')
    plt.ylabel('Tiempo de espera (dias)')
    plt.title('Promedio que los pacientes esperan internados')
    plt.xticks(meses)
    plt.grid(axis='y')
    plt.savefig(os.path.join(path_resultados, 'promedio_espera_por_tiempo_espera_quirofanos_mensual.png'), dpi=300)

    # for quirofanos in estado_sistema["ocupacion_diaria_quirofanos"]:
    #     for k, v in quirofanos.items():
    #             ocupacion_total_de_quirofanos[k] += v

    # for k, v in ocupacion_total_de_quirofanos.items():
    #     ocupacion_total_de_quirofanos[k] = round((ocupacion_total_de_quirofanos[k] * 100) / (estado_sistema["dias_simulacion"] * 12))
    ocupacion_total_de_quirofanos = calcular_porentaje_ocupacion_quirofanos_total(estado_sistema)
    # meses = np.arange(0, len(ocupacion_total_de_quirofanos))

    etiquetas = ['En uso','Ocioso']
    colores=['skyblue','red']
    # Determina el número de subplots
    cols = 2
    rows = (estado_sistema['cantidad_de_quirofanos'] + 1) // cols

    fig, axs = plt.subplots(rows, cols, figsize=(10, 6))
    for idx, (k, v) in enumerate(ocupacion_total_de_quirofanos.items()):
            ax = axs[idx // cols, idx % cols]
            datos = [v, 100 - v if (100 - v) >= 0 else 0 ]
            titulo = str.replace(f'Porcentaje de ocupacion del {k}','_',' ')
            ax.pie(datos,labels=etiquetas,autopct='%1.1f%%', colors=colores)
            ax.set_title(titulo)
            ax.axis('equal')

    plt.savefig(os.path.join(path_resultados, 'grafico_porcentaje_ocupacion_quirofanos.png'), dpi=300)
    plt.tight_layout()

    promedio_de_horas_de_ocupacion_quirofanos_mensual = calcular_promedio_de_horas_de_ocupacion_quirofanos_mensual(estado_sistema)
    fig, axs = plt.subplots(rows, cols, figsize=(12, 6))
    fig.subplots_adjust(left=0.8, right=0.9, top=0.9, bottom=0.8)
    for idx, (k, v) in enumerate(promedio_de_horas_de_ocupacion_quirofanos_mensual.items()):
            ax = axs[idx // cols, idx % cols]

            datos = promedio_de_horas_de_ocupacion_quirofanos_mensual[k]
            ax.bar(meses, datos, color='skyblue')
            print('DEBUG:', k)
            print('DEBUG:', datos)
            titulo = str.replace(f'Promedio de horas de ocupacion del {k}','_',' ')
            ax.set_title(titulo)
            ax.axis('equal')

    plt.tight_layout()

    plt.savefig(os.path.join(path_resultados, 'grafico_promedio_de_horas_de_ocupacion_quirofanos_mensual.png'), dpi=300)
