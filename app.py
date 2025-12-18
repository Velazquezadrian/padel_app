# ================================================================================
# SISTEMA DE TURNOS DE PADEL - BACKEND (Flask)
# ================================================================================
# Este archivo contiene toda la lógica del servidor:
# - API REST con 19 endpoints
# - Gestión de reservas (puntuales y fijos)
# - Sistema de finanzas y reportes
# - Backup/Restore de datos
# - Integración con sistema de licencias
# ================================================================================

from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta
import json
import os
import sys
from io import BytesIO
from licencia_manager import LicenciaManager

# ================================================================================
# CONFIGURACIÓN DE RUTAS Y DIRECTORIOS
# ================================================================================
# Detecta si estamos en modo desarrollo o ejecutable empaquetado (PyInstaller)

if getattr(sys, 'frozen', False):
    # MODO EJECUTABLE: Rutas para versión empaquetada con PyInstaller
    application_path = sys._MEIPASS  # Carpeta temporal donde PyInstaller extrae archivos
    data_path = os.path.join(os.environ['APPDATA'], 'PadelApp')  # Datos persistentes en AppData
    if not os.path.exists(data_path):
        os.makedirs(data_path)
else:
    # MODO DESARROLLO: Usa carpeta del proyecto
    application_path = os.path.dirname(os.path.abspath(__file__))
    data_path = application_path

# ================================================================================
# INICIALIZACIÓN DE FLASK
# ================================================================================

app = Flask(__name__, 
            template_folder=os.path.join(application_path, 'templates'),
            static_folder=os.path.join(application_path, 'static'))
app.secret_key = 'tu_clave_secreta_aqui_cambiar_en_produccion'

# ================================================================================
# RUTAS DE ARCHIVOS JSON (Base de datos persistente)
# ================================================================================

CONFIG_FILE = os.path.join(data_path, 'config.json')          # Configuración del sistema
RESERVAS_FILE = os.path.join(data_path, 'reservas.json')      # Reservas puntuales
TURNOS_FIJOS_FILE = os.path.join(data_path, 'turnos_fijos.json')  # Turnos recurrentes
AUSENCIAS_FILE = os.path.join(data_path, 'ausencias.json')    # Ausencias de turnos fijos
TEMA_FILE = os.path.join(data_path, 'tema.json')              # Tema visual seleccionado

# ================================================================================
# FUNCIONES DE PERSISTENCIA - Cargar/Guardar datos en JSON
# ================================================================================

def cargar_config():
    """
    Carga la configuración del sistema desde config.json
    Retorna configuración por defecto si el archivo no existe
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Configuración por defecto al iniciar por primera vez
    return {
        'cantidad_canchas': 2,
        'horario_inicio': '08:00',
        'horario_fin': '22:00',
        'duracion_turno': 90,
        'precio_turno_regular': 10000,
        'precio_turno_fijo': 9000,
        'descuento_promocion': 0
    }

def guardar_config(config):
    """Guarda la configuración del sistema en config.json"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def cargar_reservas():
    """
    Carga todas las reservas puntuales desde reservas.json
    Formato: { "fecha_hora": { "cancha_id": { datos_reserva } } }
    """
    if os.path.exists(RESERVAS_FILE):
        with open(RESERVAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def guardar_reservas(reservas):
    """Guarda todas las reservas puntuales en reservas.json"""
    with open(RESERVAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reservas, f, indent=4)

def cargar_turnos_fijos():
    """
    Carga los turnos fijos/recurrentes desde turnos_fijos.json
    Los turnos fijos se repiten todas las semanas en el mismo día/horario
    """
    if os.path.exists(TURNOS_FIJOS_FILE):
        with open(TURNOS_FIJOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_turnos_fijos(turnos_fijos):
    """Guarda los turnos fijos en turnos_fijos.json"""
    with open(TURNOS_FIJOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(turnos_fijos, f, indent=4)

def cargar_ausencias():
    """
    Carga las ausencias de turnos fijos desde ausencias.json
    Las ausencias permiten "liberar" un turno fijo en una fecha específica
    """
    if os.path.exists(AUSENCIAS_FILE):
        with open(AUSENCIAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_ausencias(ausencias):
    """Guarda las ausencias en ausencias.json"""
    with open(AUSENCIAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ausencias, f, indent=4)

def cargar_tema():
    """Carga el tema visual seleccionado por el usuario desde tema.json"""
    if os.path.exists(TEMA_FILE):
        with open(TEMA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'tema': 'clasico', 'tamano': 'normal'}

def guardar_tema(tema, tamano=None):
    """Guarda el tema visual y/o tamaño en tema.json"""
    # Cargar configuración existente
    config = cargar_tema()
    
    # Actualizar tema si se proporciona
    if tema:
        config['tema'] = tema
    
    # Actualizar tamaño si se proporciona
    if tamano:
        config['tamano'] = tamano
    
    # Guardar
    with open(TEMA_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

# ================================================================================
# FUNCIONES HELPER - Lógica de negocio reutilizable
# ================================================================================

def aplicar_turnos_fijos(fecha, horario, canchas):
    """
    Aplica los turnos fijos recurrentes a la disponibilidad de canchas
    
    Busca turnos fijos que coincidan con el día de la semana y horario,
    y marca las canchas correspondientes como ocupadas.
    También verifica si hay ausencias marcadas para ese día específico.
    """
    turnos_fijos = cargar_turnos_fijos()
    ausencias = cargar_ausencias()
    fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
    dia_semana = fecha_obj.weekday()  # 0=Lunes, 6=Domingo
    
    # Recorrer todos los turnos fijos configurados
    for turno in turnos_fijos:
        if turno['dia_semana'] == dia_semana and turno['horario'] == horario:
            # Verificar si hay una ausencia marcada para esta fecha específica
            clave_ausencia = f"{fecha}_{horario}_{turno['cancha_id']}"
            tiene_ausencia = any(a['clave'] == clave_ausencia for a in ausencias)
            
            # Buscar la cancha correspondiente y actualizar su estado
            for cancha in canchas:
                if cancha['id'] == turno['cancha_id']:
                    if tiene_ausencia:
                        # Ausencia marcada: cancha disponible pero muestra info del turno fijo
                        cancha['turno_fijo_ausente'] = {
                            'nombre': turno['nombre_cliente'],
                            'telefono': turno.get('telefono_cliente', ''),
                            'id_turno_fijo': turno['id']
                        }
                    else:
                        # Sin ausencia: cancha ocupada por turno fijo
                        cancha['disponible'] = False
                        cancha['reserva'] = {
                            'nombre': turno['nombre_cliente'],
                            'telefono': turno.get('telefono_cliente', ''),
                            'es_fijo': True,
                            'id_turno_fijo': turno['id']
                        }
                    break
    
    return canchas

def generar_horarios(hora_inicio, hora_fin, duracion):
    """
    Genera lista de horarios disponibles entre hora_inicio y hora_fin
    
    Ejemplo: inicio='08:00', fin='22:00', duracion=90
    Resultado: ['08:00', '09:30', '11:00', '12:30', ...]
    """
    horarios = []
    inicio = datetime.strptime(hora_inicio, '%H:%M')
    fin = datetime.strptime(hora_fin, '%H:%M')
    
    actual = inicio
    while actual < fin:
        horarios.append(actual.strftime('%H:%M'))
        actual += timedelta(minutes=duracion)
    
    return horarios

@app.route('/')
def index():
    """Página principal con los turnos"""
    config = cargar_config()
    horarios = generar_horarios(
        config['horario_inicio'],
        config['horario_fin'],
        config['duracion_turno']
    )
    return render_template('index.html', 
                         config=config, 
                         horarios=horarios)

@app.route('/configuracion')
def configuracion():
    """Página de configuración"""
    config = cargar_config()
    return render_template('configuracion.html', config=config)

@app.route('/api/guardar_config', methods=['POST'])
def guardar_configuracion():
    """API para guardar configuración"""
    try:
        data = request.get_json()
        config = {
            'cantidad_canchas': int(data['cantidad_canchas']),
            'horario_inicio': data['horario_inicio'],
            'horario_fin': data['horario_fin'],
            'duracion_turno': int(data['duracion_turno'])
        }
        guardar_config(config)
        return jsonify({'success': True, 'message': 'Configuración guardada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/obtener_disponibilidad', methods=['POST'])
def obtener_disponibilidad():
    """API para obtener disponibilidad de canchas en un horario"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Datos recibidos: {data}")
        
        fecha = data.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        horario = data['horario']
        print(f"[DEBUG] Fecha: {fecha}, Horario: {horario}")
        
        config = cargar_config()
        print(f"[DEBUG] Config cargada: {config}")
        
        reservas = cargar_reservas()
        print(f"[DEBUG] Reservas: {reservas}")
        
        # Crear clave para buscar reservas
        clave_fecha_hora = f"{fecha}_{horario}"
        reservas_horario = reservas.get(clave_fecha_hora, {})
        
        # Generar disponibilidad de canchas
        canchas = []
        for i in range(1, config['cantidad_canchas'] + 1):
            cancha_id = f"cancha_{i}"
            reservada = cancha_id in reservas_horario
            canchas.append({
                'id': cancha_id,
                'numero': i,
                'disponible': not reservada,
                'reserva': reservas_horario.get(cancha_id, {})
            })
        
        # Aplicar turnos fijos
        canchas = aplicar_turnos_fijos(fecha, horario, canchas)
        
        print(f"[DEBUG] Canchas generadas: {canchas}")
        
        response = {
            'success': True,
            'canchas': canchas,
            'horario': horario,
            'fecha': fecha
        }
        print(f"[DEBUG] Respuesta: {response}")
        
        return jsonify(response)
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/reservar', methods=['POST'])
def reservar_turno():
    """API para reservar un turno"""
    try:
        data = request.get_json()
        fecha = data.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        horario = data['horario']
        cancha_id = data['cancha_id']
        nombre_cliente = data.get('nombre_cliente', 'Sin nombre')
        telefono_cliente = data.get('telefono_cliente', '')
        es_fijo = data.get('es_fijo', False)
        productos_extras = data.get('productos_extras', '')
        precio_extras = float(data.get('precio_extras', 0))
        
        if es_fijo:
            # Crear turno fijo recurrente
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            dia_semana = fecha_obj.weekday()
            
            turnos_fijos = cargar_turnos_fijos()
            
            # Generar ID único
            nuevo_id = max([t.get('id', 0) for t in turnos_fijos], default=0) + 1
            
            # Verificar si ya existe un turno fijo para ese día/horario/cancha
            for turno in turnos_fijos:
                if (turno['dia_semana'] == dia_semana and 
                    turno['horario'] == horario and 
                    turno['cancha_id'] == cancha_id):
                    return jsonify({
                        'success': False,
                        'message': 'Ya existe un turno fijo para este día y horario en esta cancha'
                    }), 400
            
            # Calcular precios
            config = cargar_config()
            precio_base = config.get('precio_turno_fijo', 9000)
            descuento_porcentaje = config.get('descuento_promocion', 0)
            descuento_aplicado = precio_base * (descuento_porcentaje / 100)
            precio_final = precio_base - descuento_aplicado
            
            # Crear turno fijo
            turno_fijo = {
                'id': nuevo_id,
                'dia_semana': dia_semana,
                'dia_nombre': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][dia_semana],
                'horario': horario,
                'cancha_id': cancha_id,
                'nombre_cliente': nombre_cliente,
                'telefono_cliente': telefono_cliente,
                'fecha_creacion': datetime.now().isoformat(),
                'precio_base': precio_base,
                'descuento_porcentaje': descuento_porcentaje,
                'descuento_aplicado': descuento_aplicado,
                'precio_final': precio_final,
                'productos_extras': productos_extras,
                'precio_extras': precio_extras
            }
            
            turnos_fijos.append(turno_fijo)
            guardar_turnos_fijos(turnos_fijos)
            
            return jsonify({
                'success': True,
                'message': f'Turno fijo creado para todos los {turno_fijo["dia_nombre"]}'
            })
        else:
            # Reserva normal (no recurrente)
            reservas = cargar_reservas()
            clave_fecha_hora = f"{fecha}_{horario}"
            
            # Inicializar si no existe
            if clave_fecha_hora not in reservas:
                reservas[clave_fecha_hora] = {}
            
            # Verificar si ya está reservada
            if cancha_id in reservas[clave_fecha_hora]:
                return jsonify({
                    'success': False, 
                    'message': 'Esta cancha ya está reservada para este horario'
                }), 400
            
            # Calcular precios
            config = cargar_config()
            precio_base = config.get('precio_turno_regular', 10000)
            descuento_porcentaje = config.get('descuento_promocion', 0)
            descuento_aplicado = precio_base * (descuento_porcentaje / 100)
            precio_final = precio_base - descuento_aplicado
            
            # Crear reserva
            reservas[clave_fecha_hora][cancha_id] = {
                'nombre': nombre_cliente,
                'telefono': telefono_cliente,
                'fecha_reserva': datetime.now().isoformat(),
                'es_fijo': False,
                'precio_base': precio_base,
                'descuento_porcentaje': descuento_porcentaje,
                'descuento_aplicado': descuento_aplicado,
                'precio_final': precio_final,
                'productos_extras': productos_extras,
                'precio_extras': precio_extras
            }
            
            guardar_reservas(reservas)
            
            return jsonify({
                'success': True,
                'message': 'Reserva realizada correctamente'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/cancelar_reserva', methods=['POST'])
def cancelar_reserva():
    """API para cancelar una reserva"""
    try:
        data = request.get_json()
        id_turno_fijo = data.get('id_turno_fijo')
        
        # Si es un turno fijo, eliminarlo
        if id_turno_fijo:
            turnos_fijos = cargar_turnos_fijos()
            turnos_fijos = [t for t in turnos_fijos if t['id'] != id_turno_fijo]
            guardar_turnos_fijos(turnos_fijos)
            
            return jsonify({
                'success': True,
                'message': 'Turno fijo eliminado correctamente'
            })
        
        # Si no es turno fijo, cancelar reserva normal
        fecha = data.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        horario = data.get('horario')
        cancha_id = data.get('cancha_id')
        
        if not horario or not cancha_id:
            return jsonify({
                'success': False,
                'message': 'Faltan datos para cancelar la reserva'
            }), 400
        
        # Cancelar reserva normal
        reservas = cargar_reservas()
        clave_fecha_hora = f"{fecha}_{horario}"
        
        if clave_fecha_hora in reservas and cancha_id in reservas[clave_fecha_hora]:
            del reservas[clave_fecha_hora][cancha_id]
            
            # Limpiar si no hay más reservas en ese horario
            if not reservas[clave_fecha_hora]:
                del reservas[clave_fecha_hora]
            
            guardar_reservas(reservas)
            
            return jsonify({
                'success': True,
                'message': 'Reserva cancelada correctamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No se encontró la reserva'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/obtener_turnos_fijos', methods=['GET'])
def obtener_turnos_fijos():
    """API para obtener todos los turnos fijos"""
    try:
        turnos_fijos = cargar_turnos_fijos()
        return jsonify({
            'success': True,
            'turnos_fijos': turnos_fijos
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/marcar_ausencia', methods=['POST'])
def marcar_ausencia():
    """API para marcar una ausencia en un turno fijo"""
    try:
        data = request.get_json()
        fecha = data['fecha']
        horario = data['horario']
        cancha_id = data['cancha_id']
        id_turno_fijo = data['id_turno_fijo']
        
        ausencias = cargar_ausencias()
        clave_ausencia = f"{fecha}_{horario}_{cancha_id}"
        
        # Verificar si ya existe
        if any(a['clave'] == clave_ausencia for a in ausencias):
            return jsonify({
                'success': False,
                'message': 'Ya existe una ausencia marcada para este turno'
            }), 400
        
        # Crear ausencia
        ausencia = {
            'clave': clave_ausencia,
            'fecha': fecha,
            'horario': horario,
            'cancha_id': cancha_id,
            'id_turno_fijo': id_turno_fijo,
            'fecha_marcado': datetime.now().isoformat()
        }
        
        ausencias.append(ausencia)
        guardar_ausencias(ausencias)
        
        return jsonify({
            'success': True,
            'message': 'Ausencia marcada correctamente. La cancha estará disponible para este día.'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/cancelar_ausencia', methods=['POST'])
def cancelar_ausencia():
    """API para cancelar una ausencia y restaurar el turno fijo"""
    try:
        data = request.get_json()
        fecha = data['fecha']
        horario = data['horario']
        cancha_id = data['cancha_id']
        
        ausencias = cargar_ausencias()
        clave_ausencia = f"{fecha}_{horario}_{cancha_id}"
        
        # Filtrar la ausencia
        ausencias = [a for a in ausencias if a['clave'] != clave_ausencia]
        guardar_ausencias(ausencias)
        
        return jsonify({
            'success': True,
            'message': 'Ausencia cancelada. El turno fijo se restauró.'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/agregar_productos', methods=['POST'])
def api_agregar_productos():
    """
    API para agregar productos extras a una reserva existente
    Ahora maneja una lista de productos con nombre y precio individual
    """
    try:
        data = request.get_json()
        fecha = data['fecha']
        horario = data['horario']
        cancha_id = data['cancha_id']
        es_fijo = data.get('es_fijo', False)
        id_turno_fijo = data.get('id_turno_fijo', None)
        productos_lista = data.get('productos_lista', [])
        
        # Calcular precio total
        precio_extras = sum(p['precio'] for p in productos_lista)
        
        # Generar descripción de productos (para compatibilidad)
        productos_extras = ', '.join([f"{p['nombre']} (${p['precio']})" for p in productos_lista])
        
        if es_fijo and id_turno_fijo:
            # Actualizar turno fijo
            turnos_fijos = cargar_turnos_fijos()
            for turno in turnos_fijos:
                if turno['id'] == id_turno_fijo:
                    turno['productos_lista'] = productos_lista
                    turno['productos_extras'] = productos_extras
                    turno['precio_extras'] = precio_extras
                    break
            guardar_turnos_fijos(turnos_fijos)
        else:
            # Actualizar reserva regular
            reservas = cargar_reservas()
            clave_fecha_hora = f"{fecha}_{horario}"
            
            if clave_fecha_hora in reservas and cancha_id in reservas[clave_fecha_hora]:
                reservas[clave_fecha_hora][cancha_id]['productos_lista'] = productos_lista
                reservas[clave_fecha_hora][cancha_id]['productos_extras'] = productos_extras
                reservas[clave_fecha_hora][cancha_id]['precio_extras'] = precio_extras
                guardar_reservas(reservas)
            else:
                return jsonify({'success': False, 'message': 'Reserva no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Productos agregados correctamente'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/guardar_tema', methods=['POST'])
def api_guardar_tema():
    """Guarda el tema seleccionado por el usuario"""
    try:
        data = request.get_json()
        tema = data.get('tema', 'clasico')
        
        # Validar que el tema es válido
        temas_validos = ['clasico', 'oceano', 'atardecer', 'noche']
        if tema not in temas_validos:
            return jsonify({'success': False, 'message': 'Tema no válido'}), 400
        
        guardar_tema(tema, None)
        return jsonify({'success': True, 'tema': tema})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/obtener_tema', methods=['GET'])
def api_obtener_tema():
    """Obtiene el tema actual y tamaño"""
    try:
        tema_data = cargar_tema()
        return jsonify({
            'success': True, 
            'tema': tema_data.get('tema', 'clasico'),
            'tamano': tema_data.get('tamano', 'normal')
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/guardar_tamano', methods=['POST'])
def api_guardar_tamano():
    """Guarda el tamaño de interfaz seleccionado"""
    try:
        data = request.get_json()
        tamano = data.get('tamano', 'normal')
        
        # Validar que el tamaño es válido
        tamanos_validos = ['compacto', 'normal', 'grande']
        if tamano not in tamanos_validos:
            return jsonify({'success': False, 'message': 'Tamaño no válido'}), 400
        
        guardar_tema(None, tamano)
        return jsonify({'success': True, 'tamano': tamano})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/finanzas/reporte_diario', methods=['POST'])
def api_reporte_finanzas():
    """Genera reporte financiero para una fecha específica"""
    try:
        data = request.get_json()
        fecha = data.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        
        reservas = cargar_reservas()
        turnos_fijos = cargar_turnos_fijos()
        ausencias = cargar_ausencias()
        config = cargar_config()
        
        # Parse fecha
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
        dia_semana = fecha_obj.weekday()
        
        total_recaudado = 0
        turnos_regulares_count = 0
        turnos_fijos_count = 0
        total_descuentos = 0
        total_extras = 0
        detalle_turnos = []
        
        # Revisar turnos fijos para ese día
        for turno_fijo in turnos_fijos:
            if turno_fijo['dia_semana'] == dia_semana:
                # Verificar si no está ausente
                clave_ausencia = f"{fecha}_{turno_fijo['horario']}_{turno_fijo['cancha_id']}"
                esta_ausente = any(a['clave'] == clave_ausencia for a in ausencias)
                
                if not esta_ausente:
                    precio_final = turno_fijo.get('precio_final', turno_fijo.get('precio_base', config.get('precio_turno_fijo', 9000)))
                    descuento = turno_fijo.get('descuento_aplicado', 0)
                    precio_extras = turno_fijo.get('precio_extras', 0)
                    
                    total_recaudado += precio_final + precio_extras
                    total_descuentos += descuento
                    total_extras += precio_extras
                    turnos_fijos_count += 1
                    
                    detalle_turnos.append({
                        'tipo': 'Turno Fijo',
                        'horario': turno_fijo['horario'],
                        'cancha': turno_fijo['cancha_id'],
                        'cliente': turno_fijo['nombre_cliente'],
                        'precio_base': turno_fijo.get('precio_base', config.get('precio_turno_fijo', 9000)),
                        'descuento': descuento,
                        'precio_final': precio_final,
                        'productos_extras': turno_fijo.get('productos_extras', ''),
                        'precio_extras': precio_extras
                    })
        
        # Revisar reservas regulares para esa fecha
        for clave_fecha_hora, canchas in reservas.items():
            if clave_fecha_hora.startswith(fecha):
                for cancha_id, reserva in canchas.items():
                    if not reserva.get('es_fijo', False):  # Solo contar regulares
                        horario = clave_fecha_hora.split('_')[1]
                        precio_final = reserva.get('precio_final', reserva.get('precio_base', config.get('precio_turno_regular', 10000)))
                        descuento = reserva.get('descuento_aplicado', 0)
                        precio_extras = reserva.get('precio_extras', 0)
                        
                        total_recaudado += precio_final + precio_extras
                        total_descuentos += descuento
                        total_extras += precio_extras
                        turnos_regulares_count += 1
                        
                        detalle_turnos.append({
                            'tipo': 'Turno Regular',
                            'horario': horario,
                            'cancha': cancha_id,
                            'cliente': reserva['nombre'],
                            'precio_base': reserva.get('precio_base', config.get('precio_turno_regular', 10000)),
                            'descuento': descuento,
                            'precio_final': precio_final,
                            'productos_extras': reserva.get('productos_extras', ''),
                            'precio_extras': precio_extras
                        })
        
        return jsonify({
            'success': True,
            'fecha': fecha,
            'resumen': {
                'total_recaudado': total_recaudado,
                'turnos_regulares': turnos_regulares_count,
                'turnos_fijos': turnos_fijos_count,
                'total_turnos': turnos_regulares_count + turnos_fijos_count,
                'total_descuentos': total_descuentos,
                'total_extras': total_extras,
                'descuento_promocion_actual': config.get('descuento_promocion', 0)
            },
            'detalle': detalle_turnos
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/exportar_backup', methods=['GET'])
def exportar_backup():
    """Exporta todos los datos a un archivo JSON legible"""
    try:
        config = cargar_config()
        reservas = cargar_reservas()
        turnos_fijos = cargar_turnos_fijos()
        ausencias = cargar_ausencias()
        
        datos_completos = {
            "_INFORMACION": {
                "descripcion": "Backup completo - Sistema de Turnos Pádel",
                "fecha_exportacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "version": "1.0",
                "nota": "Este archivo puede editarse con cualquier editor de texto y luego importarse"
            },
            "configuracion": {
                "cantidad_canchas": config.get('cantidad_canchas', 2),
                "horario_inicio": config.get('horario_inicio', '08:00'),
                "horario_fin": config.get('horario_fin', '22:00'),
                "duracion_turno_minutos": config.get('duracion_turno', 90),
                "precio_turno_regular": config.get('precio_turno_regular', 10000),
                "precio_turno_fijo": config.get('precio_turno_fijo', 9000),
                "descuento_promocion_porcentaje": config.get('descuento_promocion', 0)
            },
            "reservas": reservas,
            "turnos_fijos": turnos_fijos,
            "ausencias": ausencias,
            "estadisticas": {
                "total_reservas": len(reservas),
                "total_turnos_fijos": len(turnos_fijos) if isinstance(turnos_fijos, list) else len(turnos_fijos.keys()),
                "total_ausencias": sum(len(fechas) if isinstance(fechas, list) else 0 for fechas in ausencias.values()) if isinstance(ausencias, dict) else 0
            }
        }
        
        json_str = json.dumps(datos_completos, ensure_ascii=False, indent=2)
        
        # Guardar en la carpeta de Descargas del usuario
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Guardar JSON (para importar)
        filename_json = f'PadelApp_Backup_{fecha_actual}.json'
        filepath_json = os.path.join(downloads_path, filename_json)
        with open(filepath_json, 'w', encoding='utf-8') as f:
            f.write(json_str)
        
        # Crear versión legible en texto plano
        filename_txt = f'PadelApp_Backup_{fecha_actual}_LEGIBLE.txt'
        filepath_txt = os.path.join(downloads_path, filename_txt)
        
        texto_legible = []
        texto_legible.append("═" * 80)
        texto_legible.append("           BACKUP - SISTEMA DE TURNOS DE PÁDEL")
        texto_legible.append("═" * 80)
        texto_legible.append(f"\nFecha de exportación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        texto_legible.append("\nEste archivo es solo para lectura. Para importar, use el archivo .json\n")
        
        # CONFIGURACIÓN
        texto_legible.append("\n" + "─" * 80)
        texto_legible.append("⚙️  CONFIGURACIÓN DEL SISTEMA")
        texto_legible.append("─" * 80)
        texto_legible.append(f"  • Cantidad de canchas: {config.get('cantidad_canchas', 2)}")
        texto_legible.append(f"  • Horario: {config.get('horario_inicio', '08:00')} a {config.get('horario_fin', '22:00')}")
        texto_legible.append(f"  • Duración por turno: {config.get('duracion_turno', 90)} minutos")
        texto_legible.append(f"  • Precio turno regular: ${config.get('precio_turno_regular', 10000):,.0f}")
        texto_legible.append(f"  • Precio turno fijo: ${config.get('precio_turno_fijo', 9000):,.0f}")
        texto_legible.append(f"  • Descuento promoción: {config.get('descuento_promocion', 0)}%")
        
        # RESERVAS
        texto_legible.append("\n" + "─" * 80)
        texto_legible.append("📅 RESERVAS REGISTRADAS")
        texto_legible.append("─" * 80)
        
        if reservas:
            reservas_ordenadas = sorted(reservas.items())
            for fecha_hora, canchas in reservas_ordenadas:
                fecha, hora = fecha_hora.split('_')
                fecha_formateada = datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y')
                
                for cancha_id, reserva in canchas.items():
                    texto_legible.append(f"\n  📍 {fecha_formateada} - {hora} - {cancha_id}")
                    texto_legible.append(f"     Cliente: {reserva.get('nombre', 'N/A')}")
                    if reserva.get('telefono'):
                        texto_legible.append(f"     Teléfono: {reserva.get('telefono')}")
                    texto_legible.append(f"     Tipo: {'Turno Fijo' if reserva.get('es_fijo') else 'Turno Regular'}")
                    texto_legible.append(f"     Precio final: ${reserva.get('precio_final', 0):,.0f}")
                    if reserva.get('descuento_aplicado', 0) > 0:
                        texto_legible.append(f"     Descuento aplicado: ${reserva.get('descuento_aplicado', 0):,.0f}")
                    if reserva.get('productos_extras'):
                        texto_legible.append(f"     Productos extras: {reserva.get('productos_extras')}")
                        texto_legible.append(f"     Precio extras: ${reserva.get('precio_extras', 0):,.0f}")
        else:
            texto_legible.append("\n  (No hay reservas registradas)")
        
        # TURNOS FIJOS
        texto_legible.append("\n" + "─" * 80)
        texto_legible.append("🔁 TURNOS FIJOS (RECURRENTES)")
        texto_legible.append("─" * 80)
        
        if turnos_fijos and len(turnos_fijos) > 0:
            for turno in turnos_fijos if isinstance(turnos_fijos, list) else turnos_fijos.values():
                estado = "✅ Activo" if turno.get('activo', True) else "❌ Inactivo"
                texto_legible.append(f"\n  🔄 {turno.get('dia_semana', 'N/A')} - {turno.get('hora', 'N/A')} - {turno.get('cancha', 'N/A')}")
                texto_legible.append(f"     Cliente: {turno.get('nombre', 'N/A')}")
                if turno.get('telefono'):
                    texto_legible.append(f"     Teléfono: {turno.get('telefono')}")
                texto_legible.append(f"     Desde: {turno.get('fecha_inicio', 'N/A')}")
                texto_legible.append(f"     Estado: {estado}")
        else:
            texto_legible.append("\n  (No hay turnos fijos registrados)")
        
        # AUSENCIAS
        texto_legible.append("\n" + "─" * 80)
        texto_legible.append("🔵 AUSENCIAS DE TURNOS FIJOS")
        texto_legible.append("─" * 80)
        
        if ausencias and isinstance(ausencias, dict) and len(ausencias) > 0:
            total_ausencias = 0
            for turno_id, fechas in ausencias.items():
                if isinstance(fechas, list) and len(fechas) > 0:
                    # Buscar info del turno
                    turno_info = "ID: " + turno_id
                    if isinstance(turnos_fijos, list):
                        for turno in turnos_fijos:
                            if str(turno.get('id', '')) == turno_id:
                                turno_info = f"{turno.get('nombre', 'N/A')} - {turno.get('dia_semana', 'N/A')} {turno.get('hora', 'N/A')}"
                                break
                    
                    texto_legible.append(f"\n  👤 {turno_info}")
                    fechas_ordenadas = sorted(fechas)
                    for fecha in fechas_ordenadas:
                        fecha_formateada = datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y')
                        texto_legible.append(f"     • {fecha_formateada}")
                        total_ausencias += 1
            
            if total_ausencias == 0:
                texto_legible.append("\n  (No hay ausencias registradas)")
        else:
            texto_legible.append("\n  (No hay ausencias registradas)")
        
        # ESTADÍSTICAS
        texto_legible.append("\n" + "─" * 80)
        texto_legible.append("📊 ESTADÍSTICAS")
        texto_legible.append("─" * 80)
        texto_legible.append(f"  • Total de reservas: {len(reservas)}")
        texto_legible.append(f"  • Total de turnos fijos: {len(turnos_fijos) if isinstance(turnos_fijos, list) else len(turnos_fijos.keys())}")
        total_aus = sum(len(fechas) if isinstance(fechas, list) else 0 for fechas in ausencias.values()) if isinstance(ausencias, dict) else 0
        texto_legible.append(f"  • Total de ausencias: {total_aus}")
        
        texto_legible.append("\n" + "═" * 80)
        texto_legible.append("Fin del backup")
        texto_legible.append("═" * 80)
        
        with open(filepath_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(texto_legible))
        
        return jsonify({
            'success': True,
            'message': f'Backup guardado exitosamente',
            'archivos': [filename_json, filename_txt],
            'ruta': downloads_path
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al exportar: {str(e)}'}), 400

@app.route('/api/descargar_backup/<filename>')
def descargar_backup(filename):
    """Descarga el archivo de backup ya generado"""
    try:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        filepath = os.path.join(downloads_path, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            json_str = f.read()
        
        output = BytesIO(json_str.encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al exportar: {str(e)}'}), 400

@app.route('/api/importar_backup', methods=['POST'])
def importar_backup():
    """Importa datos desde un archivo JSON de backup"""
    try:
        if 'archivo' not in request.files:
            return jsonify({'success': False, 'message': 'No se recibió ningún archivo'}), 400
        
        archivo = request.files['archivo']
        
        if archivo.filename == '':
            return jsonify({'success': False, 'message': 'No se seleccionó ningún archivo'}), 400
        
        if not archivo.filename.endswith('.json'):
            return jsonify({'success': False, 'message': 'El archivo debe ser .json'}), 400
        
        contenido = archivo.read().decode('utf-8')
        datos = json.loads(contenido)
        
        if 'configuracion' not in datos or 'reservas' not in datos:
            return jsonify({'success': False, 'message': 'Formato de archivo inválido'}), 400
        
        config_data = datos['configuracion']
        config_dict = {
            'cantidad_canchas': config_data.get('cantidad_canchas', 2),
            'horario_inicio': config_data.get('horario_inicio', '08:00'),
            'horario_fin': config_data.get('horario_fin', '22:00'),
            'duracion_turno': config_data.get('duracion_turno_minutos', 90),
            'precio_turno_regular': config_data.get('precio_turno_regular', 10000),
            'precio_turno_fijo': config_data.get('precio_turno_fijo', 9000),
            'descuento_promocion': config_data.get('descuento_promocion_porcentaje', 0)
        }
        
        reservas_dict = datos.get('reservas', {})
        turnos_fijos_data = datos.get('turnos_fijos', [])
        ausencias_dict = datos.get('ausencias', {})
        
        guardar_config(config_dict)
        guardar_reservas(reservas_dict)
        guardar_turnos_fijos(turnos_fijos_data)
        guardar_ausencias(ausencias_dict)
        
        return jsonify({
            'success': True,
            'message': 'Datos importados correctamente',
            'estadisticas': {
                'reservas': len(reservas_dict),
                'turnos_fijos': len(turnos_fijos_data) if isinstance(turnos_fijos_data, list) else len(turnos_fijos_data.keys()),
                'ausencias': sum(len(fechas) if isinstance(fechas, list) else 0 for fechas in ausencias_dict.values()) if isinstance(ausencias_dict, dict) else 0
            }
        })
        
    except json.JSONDecodeError:
        return jsonify({'success': False, 'message': 'El archivo JSON no es válido'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al importar: {str(e)}'}), 400

@app.route('/licencia')
def pagina_licencia():
    """Página de gestión de licencia"""
    return render_template('licencia.html')

@app.route('/api/info_licencia', methods=['GET'])
def info_licencia():
    """Obtiene información de la licencia actual"""
    try:
        # Detectar ruta de licencia
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        archivo_licencia = os.path.join(base_path, 'licencia.dat')
        manager = LicenciaManager(archivo_licencia)
        
        es_valida, dias_restantes, mensaje = manager.verificar_licencia()
        info = manager.obtener_info_licencia()
        
        if info:
            fecha_exp = datetime.fromisoformat(info['fecha_expiracion'])
            return jsonify({
                'success': True,
                'valida': es_valida,
                'cliente': info.get('cliente', 'N/A'),
                'tipo': info.get('tipo', 'N/A'),
                'fecha_expiracion': fecha_exp.strftime('%d/%m/%Y'),
                'dias_restantes': dias_restantes,
                'mensaje': mensaje
            })
        else:
            return jsonify({
                'success': False,
                'valida': False,
                'mensaje': 'No se encontró archivo de licencia'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'mensaje': f'Error al verificar licencia: {str(e)}'
        }), 400

@app.route('/api/aplicar_serial', methods=['POST'])
def aplicar_serial():
    """Aplica un serial de licencia"""
    try:
        data = request.get_json()
        serial = data.get('serial', '').strip()
        
        if not serial:
            return jsonify({
                'success': False,
                'mensaje': 'Serial vacío'
            }), 400
        
        # Detectar ruta de licencia
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        archivo_licencia = os.path.join(base_path, 'licencia.dat')
        manager = LicenciaManager(archivo_licencia)
        
        exito, mensaje = manager.aplicar_serial(serial)
        
        return jsonify({
            'success': exito,
            'mensaje': mensaje
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'mensaje': f'Error al aplicar serial: {str(e)}'
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
