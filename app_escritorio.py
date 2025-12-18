# -*- coding: utf-8 -*-
# ================================================================================
# APLICACIÓN DE ESCRITORIO - Sistema de Turnos de Pádel
# ================================================================================
# Este archivo es el punto de entrada de la aplicación de escritorio.
# 
# FUNCIONAMIENTO:
# 1. Verifica la licencia antes de iniciar
# 2. Inicia un servidor Flask en segundo plano (localhost:5000)
# 3. Abre una ventana de escritorio con PyWebView que carga la interfaz web
# 4. El servidor Flask sigue corriendo en un thread daemon hasta cerrar la app
#
# COMPONENTES:
# - PyWebView: Crea ventana nativa del sistema operativo
# - Flask: Servidor web local que sirve la aplicación
# - Threading: Permite ejecutar Flask en segundo plano
# ================================================================================

import webview
import threading
import time
import sys
import os
import ctypes
from werkzeug.serving import make_server
from app import app
from licencia_manager import LicenciaManager

# ================================================================================
# VARIABLES GLOBALES para control del servidor Flask
# ================================================================================

server = None          # Instancia del servidor Flask
server_thread = None   # Thread donde corre el servidor

# ================================================================================
# FUNCIONES DE GESTIÓN DEL SERVIDOR FLASK
# ================================================================================

def run_flask():
    """
    Ejecuta el servidor Flask en un thread separado (daemon)
    El servidor escucha en localhost:5000 y queda en segundo plano
    """
    global server
    # Silenciar logs de Werkzeug redirigiendo a devnull
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    server = make_server('127.0.0.1', 5000, app, threaded=True)
    server.serve_forever()

def shutdown_server():
    """
    Detiene el servidor Flask de forma segura
    Se llama al cerrar la ventana de la aplicación
    """
    global server
    if server:
        server.shutdown()

def on_closing():
    """
    Callback que se ejecuta cuando el usuario cierra la ventana
    Asegura que el servidor Flask se detenga correctamente
    """
    shutdown_server()

# ================================================================================
# FUNCIÓN DE VERIFICACIÓN DE LICENCIAS
# ================================================================================

def verificar_y_mostrar_licencia():
    """
    Verifica la licencia antes de iniciar la aplicación
    
    FLUJO:
    1. Busca archivo licencia.dat
    2. Si no existe, crea un trial de 15 días automáticamente
    3. Si existe, verifica que esté vigente
    4. Si la licencia es inválida, muestra ventana de error y cierra la app
    5. Si es válida, retorna True y permite continuar
    
    Returns:
        bool: True si la licencia es válida, False si no lo es
    """
    # Detectar ruta correcta según modo de ejecución
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)  # Modo ejecutable
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))  # Modo desarrollo
    
    archivo_licencia = os.path.join(base_path, 'licencia.dat')
    manager = LicenciaManager(archivo_licencia)
    
    # ============================================================
    # CASO 1: No existe licencia - Intentar crear trial
    # ============================================================
    if not os.path.exists(archivo_licencia):
        resultado_trial = manager.crear_licencia_trial()
        
        if resultado_trial is None:
            # Trial ya fue usado previamente y expiró
            es_valida = False
            dias_restantes = 0
            mensaje = "El período de prueba de 15 días ya expiró. Para continuar usando la aplicación, active una licencia ingresando un serial válido en la sección 'Licencia'."
        elif not resultado_trial:
            # Caso extraño: no debería llegar aquí
            es_valida, dias_restantes, mensaje = manager.verificar_licencia()
        else:
            # Trial creado exitosamente
            es_valida, dias_restantes, mensaje = manager.verificar_licencia()
    else:
        # ============================================================
        # CASO 2: Existe licencia - Verificar validez
        # ============================================================
        es_valida, dias_restantes, mensaje = manager.verificar_licencia()
    
    # ============================================================
    # Si la licencia NO es válida, mostrar error y cerrar
    # ============================================================
    if not es_valida:
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
        width=1200,
        height=800,
        resizable=True,
        fullscreen=False,
        min_size=(900, 650)
    )

    # Registrar evento de cierre
    window.events.closed += on_closing

    # Iniciar la interfaz gráfica
    webview.start(debug=False)

if __name__ == '__main__':
    # Ejecutable standalone - no mostrar mensajes en consola
    start_app()
