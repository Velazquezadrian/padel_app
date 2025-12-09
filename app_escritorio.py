# -*- coding: utf-8 -*-
import webview
import threading
import time
import sys
import os
import ctypes
from werkzeug.serving import make_server
from app import app
from licencia_manager import LicenciaManager

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

def verificar_y_mostrar_licencia():
    """
    Verifica la licencia antes de iniciar la aplicación
    Retorna True si es válida, False si no
    """
    # Detectar si estamos en PyInstaller
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    archivo_licencia = os.path.join(base_path, 'licencia.dat')
    manager = LicenciaManager(archivo_licencia)
    
    # Si no existe licencia, crear una trial de 15 días
    if not os.path.exists(archivo_licencia):
        resultado_trial = manager.crear_licencia_trial()
        
        if resultado_trial is None:
            # Trial expirado, no puede crear uno nuevo
            es_valida = False
            dias_restantes = 0
            mensaje = "El período de prueba de 15 días ya expiró. Para continuar usando la aplicación, active una licencia ingresando un serial válido en la sección 'Licencia'."
        elif not resultado_trial:
            # Ya existe licencia
            es_valida, dias_restantes, mensaje = manager.verificar_licencia()
        else:
            # Trial creado/restaurado exitosamente
            es_valida, dias_restantes, mensaje = manager.verificar_licencia()
    else:
        es_valida, dias_restantes, mensaje = manager.verificar_licencia()
    
    if not es_valida:
        # Mostrar ventana de error
        def mostrar_error_licencia():
            html_error = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 15px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                        max-width: 500px;
                        text-align: center;
                    }}
                    .icon {{
                        font-size: 80px;
                        margin-bottom: 20px;
                    }}
                    h1 {{
                        color: #e74c3c;
                        margin-bottom: 20px;
                    }}
                    p {{
                        color: #555;
                        line-height: 1.6;
                        margin-bottom: 15px;
                    }}
                    .contacto {{
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 10px;
                        margin-top: 20px;
                    }}
                    .contacto strong {{
                        color: #667eea;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon" style="color: #e74c3c; font-weight: bold; font-size: 100px;">[X]</div>
                    <h1>Licencia No Valida</h1>
                    <p>{mensaje}</p>
                    <div class="contacto">
                        <strong>Para renovar su licencia, contacte al proveedor</strong>
                    </div>
                </div>
            </body>
            </html>
            """
            
            window = webview.create_window(
                title='Error de Licencia',
                html=html_error,
                width=600,
                height=500,
                resizable=False
            )
            webview.start()
        
        mostrar_error_licencia()
        return False
    
    # Licencia válida - continuar
    pass
    
    return True

def start_app():
    """Iniciar la aplicación de escritorio"""
    # Verificar licencia primero
    if not verificar_y_mostrar_licencia():
        return
    
    # Configurar ícono de la aplicación en Windows
    if sys.platform == 'win32':
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        icono_path = os.path.join(base_path, 'icono_padel.ico')
        if os.path.exists(icono_path):
            # Cambiar el ícono de la aplicación en la barra de tareas
            myappid = 'padel.reservas.app.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    # Iniciar Flask en un thread
    global server_thread
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()
    
    # Esperar a que Flask inicie
    time.sleep(1.5)
    
    # Crear ventana de la aplicación
    window = webview.create_window(
        title='Sistema de Turnos - Padel',
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
    # Ejecutable standalone - no mostrar mensajes en consola
    start_app()
