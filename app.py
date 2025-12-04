from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import json
import os
import sys

# Detectar si estamos ejecutando desde PyInstaller
if getattr(sys, 'frozen', False):
    # Ejecutable empaquetado
    application_path = sys._MEIPASS
    # Usar carpeta de datos del usuario
    data_path = os.path.join(os.environ['APPDATA'], 'PadelApp')
    if not os.path.exists(data_path):
        os.makedirs(data_path)
else:
    # Modo desarrollo
    application_path = os.path.dirname(os.path.abspath(__file__))
    data_path = application_path

app = Flask(__name__, 
            template_folder=os.path.join(application_path, 'templates'),
            static_folder=os.path.join(application_path, 'static'))
app.secret_key = 'tu_clave_secreta_aqui_cambiar_en_produccion'

# Archivos para guardar configuración (en carpeta de datos del usuario)
CONFIG_FILE = os.path.join(data_path, 'config.json')
RESERVAS_FILE = os.path.join(data_path, 'reservas.json')
TURNOS_FIJOS_FILE = os.path.join(data_path, 'turnos_fijos.json')
AUSENCIAS_FILE = os.path.join(data_path, 'ausencias.json')
TEMA_FILE = os.path.join(data_path, 'tema.json')

def cargar_config():
    """Carga la configuración del sistema"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Configuración por defecto
    return {
        'cantidad_canchas': 2,
        'horario_inicio': '08:00',
        'horario_fin': '22:00',
        'duracion_turno': 90,  # minutos
        'precio_turno_regular': 10000,  # Precio por turno normal
        'precio_turno_fijo': 9000,  # Precio por turno fijo (puede ser menor)
        'descuento_promocion': 0  # Porcentaje de descuento (0-100)
    }

def guardar_config(config):
    """Guarda la configuración del sistema"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def cargar_reservas():
    """Carga las reservas existentes"""
    if os.path.exists(RESERVAS_FILE):
        with open(RESERVAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def guardar_reservas(reservas):
    """Guarda las reservas"""
    with open(RESERVAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reservas, f, indent=4)

def cargar_turnos_fijos():
    """Carga los turnos fijos/recurrentes"""
    if os.path.exists(TURNOS_FIJOS_FILE):
        with open(TURNOS_FIJOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_turnos_fijos(turnos_fijos):
    """Guarda los turnos fijos"""
    with open(TURNOS_FIJOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(turnos_fijos, f, indent=4)

def cargar_ausencias():
    """Carga las ausencias de turnos fijos"""
    if os.path.exists(AUSENCIAS_FILE):
        with open(AUSENCIAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_ausencias(ausencias):
    """Guarda las ausencias"""
    with open(AUSENCIAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ausencias, f, indent=4)

def cargar_tema():
    """Carga el tema seleccionado por el usuario"""
    if os.path.exists(TEMA_FILE):
        with open(TEMA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'tema': 'clasico'}

def guardar_tema(tema):
    """Guarda el tema seleccionado por el usuario"""
    with open(TEMA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'tema': tema}, f, indent=4)

def aplicar_turnos_fijos(fecha, horario, canchas):
    """Aplica turnos fijos a la disponibilidad de canchas"""
    turnos_fijos = cargar_turnos_fijos()
    ausencias = cargar_ausencias()
    fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
    dia_semana = fecha_obj.weekday()  # 0=Lunes, 6=Domingo
    
    for turno in turnos_fijos:
        if turno['dia_semana'] == dia_semana and turno['horario'] == horario:
            # Verificar si hay una ausencia para esta fecha
            clave_ausencia = f"{fecha}_{horario}_{turno['cancha_id']}"
            tiene_ausencia = any(a['clave'] == clave_ausencia for a in ausencias)
            
            # Buscar la cancha y marcarla como ocupada por el turno fijo
            for cancha in canchas:
                if cancha['id'] == turno['cancha_id']:
                    if tiene_ausencia:
                        # Mantener disponible pero indicar que es turno fijo con ausencia
                        cancha['turno_fijo_ausente'] = {
                            'nombre': turno['nombre_cliente'],
                            'telefono': turno.get('telefono_cliente', ''),
                            'id_turno_fijo': turno['id']
                        }
                    else:
                        # Ocupada por turno fijo normal
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
    """Genera lista de horarios disponibles"""
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
    """API para agregar productos extras a una reserva existente"""
    try:
        data = request.get_json()
        fecha = data['fecha']
        horario = data['horario']
        cancha_id = data['cancha_id']
        es_fijo = data.get('es_fijo', False)
        id_turno_fijo = data.get('id_turno_fijo', None)
        productos_extras = data.get('productos_extras', '')
        precio_extras = float(data.get('precio_extras', 0))
        
        if es_fijo and id_turno_fijo:
            # Actualizar turno fijo
            turnos_fijos = cargar_turnos_fijos()
            for turno in turnos_fijos:
                if turno['id'] == id_turno_fijo:
                    turno['productos_extras'] = productos_extras
                    turno['precio_extras'] = precio_extras
                    break
            guardar_turnos_fijos(turnos_fijos)
        else:
            # Actualizar reserva regular
            reservas = cargar_reservas()
            clave_fecha_hora = f"{fecha}_{horario}"
            
            if clave_fecha_hora in reservas and cancha_id in reservas[clave_fecha_hora]:
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
        
        guardar_tema(tema)
        return jsonify({'success': True, 'tema': tema})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/obtener_tema', methods=['GET'])
def api_obtener_tema():
    """Obtiene el tema actual"""
    try:
        tema_data = cargar_tema()
        return jsonify({'success': True, 'tema': tema_data.get('tema', 'clasico')})
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
