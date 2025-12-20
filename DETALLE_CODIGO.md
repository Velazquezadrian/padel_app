# Detalle del Código del Proyecto

## Estructura del Proyecto
El proyecto está organizado de la siguiente manera:

### Archivos principales
- **`app.py`**: Contiene la lógica del servidor Flask, que maneja las solicitudes HTTP y gestiona la lógica del backend.
- **`app_escritorio.py`**: Punto de entrada para la aplicación de escritorio, que utiliza PyWebView para mostrar la interfaz.
- **`licencia_manager.py`**: Implementa la lógica para la gestión de licencias, incluyendo la generación y validación de licencias.

### Carpetas importantes
- **`static/`**: Contiene archivos estáticos como CSS, JavaScript e imágenes.
- **`templates/`**: Contiene las plantillas HTML utilizadas por Flask para renderizar las vistas.
- **`build/`**: Carpeta generada por PyInstaller que contiene los archivos temporales para la creación de ejecutables.
- **`Paquetes_Finales/`**: Carpeta donde se almacenan las distribuciones finales del proyecto.

### Archivos de configuración
- **`config.json`**: Almacena la configuración del sistema, como horarios y precios.
- **`reservas.json`**: Almacena las reservas puntuales realizadas por los usuarios.
- **`turnos_fijos.json`**: Almacena los turnos recurrentes.
- **`tema.json`**: Almacena la configuración del tema visual.

---

## Análisis de Archivos Clave

### `app.py`
Este archivo implementa el servidor Flask, que actúa como el backend del sistema. A continuación, se detalla su estructura:

#### Importaciones
```python
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta
import json
import os
import sys
from io import BytesIO
from licencia_manager import LicenciaManager
```
- **`Flask`**: Framework para manejar solicitudes HTTP.
- **`datetime`**: Para manejar fechas y horas.
- **`json`**: Para leer y escribir archivos JSON.
- **`os` y `sys`**: Para manejar rutas y configuraciones del sistema.
- **`LicenciaManager`**: Clase para la gestión de licencias.

#### Configuración de rutas y directorios
```python
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
    data_path = os.path.join(os.environ['APPDATA'], 'PadelApp')
    if not os.path.exists(data_path):
        os.makedirs(data_path)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    data_path = application_path
```
- **Modo ejecutable**: Si el programa está empaquetado con PyInstaller, utiliza rutas específicas.
- **Modo desarrollo**: Usa las rutas locales del proyecto.

#### Inicialización de Flask
```python
app = Flask(__name__, 
            template_folder=os.path.join(application_path, 'templates'),
            static_folder=os.path.join(application_path, 'static'))
app.secret_key = 'tu_clave_secreta_aqui_cambiar_en_produccion'
```
- **`template_folder`**: Carpeta donde se encuentran las plantillas HTML.
- **`static_folder`**: Carpeta donde se encuentran los archivos estáticos.
- **`secret_key`**: Clave secreta para manejar sesiones y cookies.

#### Funciones de persistencia
Estas funciones manejan la lectura y escritura de archivos JSON.

- **`cargar_config`**: Carga la configuración desde `config.json`.
- **`guardar_config`**: Guarda la configuración en `config.json`.
- **`cargar_reservas`**: Carga las reservas desde `reservas.json`.
- **`guardar_reservas`**: Guarda las reservas en `reservas.json`.
- **`cargar_turnos_fijos`**: Carga los turnos fijos desde `turnos_fijos.json`.
- **`guardar_turnos_fijos`**: Guarda los turnos fijos en `turnos_fijos.json`.
- **`cargar_ausencias`**: Carga las ausencias desde `ausencias.json`.
- **`guardar_ausencias`**: Guarda las ausencias en `ausencias.json`.

#### Endpoints principales

1. **`/`**: Página principal.
   - Renderiza `index.html` con la configuración y horarios disponibles.

2. **`/api/reservar`**: Realiza una reserva.
   - Entrada: JSON con datos de la reserva.
   - Salida: Respuesta JSON con el estado de la operación.

3. **`/api/guardar_config`**: Guarda la configuración del sistema.
   - Entrada: JSON con los nuevos parámetros de configuración.
   - Salida: Respuesta JSON con el estado de la operación.

4. **`/api/finanzas/reporte_diario`**: Genera un reporte financiero.
   - Entrada: Fecha específica.
   - Salida: Resumen financiero en formato JSON.

5. **`/api/exportar_backup`**: Exporta todos los datos a un archivo JSON.
   - Salida: Archivo JSON descargable.

6. **`/api/importar_backup`**: Importa datos desde un archivo JSON.
   - Entrada: Archivo JSON.
   - Salida: Respuesta JSON con el estado de la operación.

---

### `app_escritorio.py`
Este archivo implementa la aplicación de escritorio utilizando PyWebView.

#### Flujo de ejecución
1. **Verificación de licencia**:
   - Utiliza `LicenciaManager` para validar la licencia antes de iniciar.

2. **Inicio del servidor Flask**:
   - Ejecuta el servidor en un hilo separado para que funcione en segundo plano.

3. **Creación de la ventana**:
   - Utiliza PyWebView para mostrar la interfaz web servida por Flask.

#### Funciones principales
- **`verificar_y_mostrar_licencia`**: Verifica la validez de la licencia.
- **`run_flask`**: Inicia el servidor Flask en un hilo separado.
- **`start_app`**: Punto de entrada principal para iniciar la aplicación.

---

### `licencia_manager.py`
Este archivo implementa la lógica para la gestión de licencias.

#### Clase `LicenciaManager`
- **`__init__`**: Inicializa la clase con la ruta del archivo de licencia y la clave de encriptación.
- **`obtener_hardware_id`**: Genera un identificador único basado en el hardware del sistema.
- **`crear_licencia_trial`**: Crea una licencia de prueba válida por 15 días.
- **`verificar_licencia`**: Verifica si la licencia es válida.
- **`aplicar_serial`**: Aplica un serial para activar la licencia.

---

## Flujo de Datos
1. **Frontend**:
   - El usuario interactúa con la interfaz servida por Flask.

2. **Backend**:
   - Flask procesa las solicitudes y actualiza los datos en los archivos JSON.

3. **Persistencia**:
   - Los datos se almacenan en archivos JSON para garantizar la persistencia.

4. **Licencias**:
   - `LicenciaManager` asegura que solo los usuarios con licencias válidas puedan acceder a la aplicación.

---

## Interacción entre Componentes
- **`app_escritorio.py`** inicia el servidor Flask y muestra la interfaz.
- **`app.py`** maneja las solicitudes HTTP y gestiona la lógica del backend.
- **`licencia_manager.py`** valida las licencias antes de permitir el acceso.

---

Este documento detalla cada aspecto del código para garantizar que cualquier modificación futura se realice con un entendimiento completo del sistema.