from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiar_en_produccion'

# Archivo para guardar configuración
CONFIG_FILE = 'config.json'
RESERVAS_FILE = 'reservas.json'

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
        'duracion_turno': 90  # minutos
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
        
        # Crear reserva
        reservas[clave_fecha_hora][cancha_id] = {
            'nombre': nombre_cliente,
            'fecha_reserva': datetime.now().isoformat()
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
        fecha = data.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        horario = data['horario']
        cancha_id = data['cancha_id']
        
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
