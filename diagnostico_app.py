"""

Script de diagnóstico para app_escritorio.py
"""

import sys
import os
import socket
import traceback

print("=" * 60)
print("🔧 DIAGNÓSTICO PARA app_escritorio.py")
print("=" * 60)
print()

# 1. Verificar Python
print("1. 📦 VERIFICANDO PYTHON...")
print(f"   Versión: {sys.version}")
print(f"   Ejecutable: {sys.executable}")
print()

# 2. Verificar importaciones
print("2. 🔍 VERIFICANDO IMPORTACIONES...")

try:
    import webview
    print(f"   ✅ PyWebView: {webview.__version__}")
except ImportError as e:
    print(f"   ❌ PyWebView NO INSTALADO: {e}")
    print("   💡 Instalar con: pip install pywebview")

try:
    import flask
    print(f"   ✅ Flask: {flask.__version__}")
except ImportError as e:
    print(f"   ❌ Flask NO INSTALADO: {e}")
    print("   💡 Instalar con: pip install flask")

try:
    from werkzeug.serving import make_server
    print("   ✅ Werkzeug disponible")
except ImportError as e:
    print(f"   ❌ Werkzeug NO INSTALADO: {e}")
    print("   💡 Instalar con: pip install werkzeug")

print()

# 3. Verificar archivos
print("3. 📁 VERIFICANDO ARCHIVOS...")
archivos = [
    "app_escritorio.py",
    "app.py",
    "licencia_manager.py",
    "static/js/main.js",
    "static/css/styles.css",
    "templates/index.html",
    "icono_padel.ico"
]

todos_ok = True
for archivo in archivos:
    if os.path.exists(archivo):
        print(f"   ✅ {archivo}")
    else:
        print(f"   ❌ {archivo} - NO ENCONTRADO")
        todos_ok = False

print()

# 4. Verificar puerto
print("4. 🔌 VERIFICANDO PUERTO 5000...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    resultado = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()
    
    if resultado == 0:
        print("   ❌ Puerto 5000 está en uso")
        print("   💡 Cerrar otros programas o cambiar puerto")
    else:
        print("   ✅ Puerto 5000 disponible")
except Exception as e:
    print(f"   ⚠️  Error verificando puerto: {e}")

print()

# 5. Probar importación de módulos locales
print("5. 🧪 PROBANDO MÓDULOS LOCALES...")

try:
    from app import app
    print("   ✅ Módulo 'app' importado")
    
    # Probar ruta básica
    with app.test_client() as client:
        respuesta = client.get('/')
        if respuesta.status_code == 200:
            print("   ✅ Flask responde correctamente")
        else:
            print(f"   ❌ Flask error: código {respuesta.status_code}")
except Exception as e:
    print(f"   ❌ Error en 'app': {e}")
    traceback.print_exc()

try:
    from licencia_manager import LicenciaManager
    print("   ✅ 'licencia_manager' importado")
    
    # Probar creación
    manager = LicenciaManager("test_temp.dat")
    if os.path.exists("test_temp.dat"):
        os.remove("test_temp.dat")
        
except Exception as e:
    print(f"   ❌ Error en 'licencia_manager': {e}")
    traceback.print_exc()

print()

# 6. Crear versión de prueba
print("6. 🛠️ CREANDO VERSIÓN DE PRUEBA...")

contenido_prueba = '''# app_prueba.py - Versión simplificada
import webview
import threading
import time
from flask import Flask

# App Flask simple
app_test = Flask(__name__)

@app_test.route('/')
def index():
    return "<h1 style='color: green;'>✅ Flask funciona</h1>"

def run_test():
    app_test.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def start_test():
    print("Iniciando prueba...")
    
    # Flask en thread
    thread = threading.Thread(target=run_test, daemon=True)
    thread.start()
    
    time.sleep(2)
    
    # Ventana
    window = webview.create_window(
        title="PRUEBA - Sistema Pádel",
        url="http://127.0.0.1:5000",
        width=800,
        height=600
    )
    
    webview.start()

if __name__ == '__main__':
    start_test()
'''

try:
    with open("app_prueba.py", "w", encoding="utf-8") as f:
        f.write(contenido_prueba)
    print("   ✅ app_prueba.py creado")
except Exception as e:
    print(f"   ❌ Error creando archivo: {e}")

print()
print("=" * 60)
print("🎯 SOLUCIONES RECOMENDADAS:")
print("=" * 60)
print()
print("1. 🔧 EJECUTAR VERSIÓN DE PRUEBA:")
print("   python app_prueba.py")
print()
print("2. 🔍 VER ERRORES EN CONSOLA:")
print("   Modificar app_escritorio.py línea ~134:")
print("   Cambiar: webview.start(debug=False)")
print("   Por:     webview.start(debug=True)")
print()
print("3. ⏭️  SALTAR VERIFICACIÓN DE LICENCIA (temporal):")
print("   En app_escritorio.py, comentar líneas 115-116:")
print("   # if not verificar_y_mostrar_licencia():")
print("   #     return")
print()
print("4. 🐛 EJECUTAR CON MÁS INFORMACIÓN:")
print("   python -c \"""")
print("   import traceback")
print("   try:")
print("       import app_escritorio")
print("       app_escritorio.start_app()")
print("   except Exception as e:")
print("       traceback.print_exc()")
print("   \"""")
print()
print("=" * 60)
print("💡 Primero prueba la opción 1 para ver si PyWebView funciona")
print("=" * 60)
"