import webview
import threading
import time
import sys
import os
from werkzeug.serving import make_server
from app import app

# Variable para controlar el servidor
server = None
server_thread = None

def run_flask():
    """Ejecutar Flask en un thread separado"""
    global server
    server = make_server('127.0.0.1', 5000, app, threaded=True)
    server.serve_forever()

def shutdown_server():
    """Detener el servidor Flask"""
    global server
    if server:
        server.shutdown()

def on_closing():
    """Función que se ejecuta al cerrar la ventana"""
    shutdown_server()

def start_app():
    """Iniciar la aplicación de escritorio"""
    # Iniciar Flask en un thread
    global server_thread
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()
    
    # Esperar a que Flask inicie
    time.sleep(1.5)
    
    # Crear ventana de la aplicación
    window = webview.create_window(
        title='🎾 Sistema de Turnos - Pádel',
        url='http://127.0.0.1:5000',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(1000, 700)
    )
    
    # Registrar evento de cierre
    window.events.closed += on_closing
    
    # Iniciar la interfaz gráfica
    webview.start(debug=False)

if __name__ == '__main__':
    print("=" * 60)
    print("  🎾 SISTEMA DE TURNOS DE PÁDEL - APLICACIÓN DE ESCRITORIO")
    print("=" * 60)
    print()
    print("✅ Iniciando aplicación...")
    print("📱 La ventana se abrirá en unos segundos...")
    print()
    print("=" * 60)
    print()
    
    start_app()
