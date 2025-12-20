# Sistema de Turnos de Pádel

## Introducción
El Sistema de Turnos de Pádel es una aplicación diseñada para gestionar reservas de canchas de pádel, tanto para turnos puntuales como recurrentes. Incluye una interfaz de escritorio y un backend basado en Flask, con persistencia de datos en archivos JSON. Además, cuenta con un sistema de licencias para controlar el acceso a la aplicación.

### Tecnologías utilizadas
- **Python**: Lenguaje principal del proyecto.
- **Flask**: Framework para el backend.
- **PyWebView**: Para la interfaz de escritorio.
- **JSON**: Almacenamiento de datos persistentes.
- **Cryptography**: Encriptación para el sistema de licencias.

---

## Requisitos previos

### Software necesario
1. **Python 3.10 o superior**
   - Descargue e instale Python desde [python.org](https://www.python.org/).
   - Asegúrese de agregar Python al PATH durante la instalación.

2. **Pip**
   - Viene incluido con Python.

3. **Virtualenv** (opcional pero recomendado)
   - Instale con: `pip install virtualenv`

4. **PyInstaller** (para generar ejecutables)
   - Instale con: `pip install pyinstaller`

### Dependencias
Las dependencias del proyecto están listadas en `requirements.txt`. Incluyen:
- Flask
- PyWebView
- Cryptography
- Otros módulos necesarios.

---

## Estructura del proyecto

### Archivos principales
- **`app.py`**: Contiene la lógica del servidor Flask.
- **`app_escritorio.py`**: Punto de entrada para la aplicación de escritorio.
- **`licencia_manager.py`**: Gestión de licencias.

### Carpetas importantes
- **`static/`**: Archivos estáticos (CSS, JS, imágenes).
- **`templates/`**: Plantillas HTML para la interfaz.
- **`build/`**: Archivos generados por PyInstaller.
- **`Paquetes_Finales/`**: Distribuciones finales para usuarios.

### Archivos de configuración
- **`config.json`**: Configuración del sistema (horarios, precios, etc.).
- **`reservas.json`**: Almacena las reservas puntuales.
- **`turnos_fijos.json`**: Almacena los turnos recurrentes.
- **`tema.json`**: Configuración del tema visual.

---

## Instalación

### Clonar el repositorio
```bash
# Clonar el repositorio
$ git clone <URL_DEL_REPOSITORIO>
$ cd Padel
```

### Crear un entorno virtual
```bash
# Crear y activar un entorno virtual
$ virtualenv venv
$ .\venv\Scripts\activate  # En Windows
```

### Instalar dependencias
```bash
# Instalar las dependencias
$ pip install -r requirements.txt
```

---

## Configuración

### Archivo `config.json`
Ejemplo de configuración:
```json
{
  "cantidad_canchas": 2,
  "horario_inicio": "08:00",
  "horario_fin": "22:00",
  "duracion_turno": 90,
  "precio_turno_regular": 10000,
  "precio_turno_fijo": 9000,
  "descuento_promocion": 0
}
```
- **`cantidad_canchas`**: Número de canchas disponibles.
- **`horario_inicio` y `horario_fin`**: Horarios de apertura y cierre.
- **`duracion_turno`**: Duración de cada turno en minutos.
- **`precio_turno_regular` y `precio_turno_fijo`**: Precios de los turnos.
- **`descuento_promocion`**: Descuento aplicado a todos los turnos.

---

## Uso

### Ejecutar la aplicación de escritorio
```bash
$ python app_escritorio.py
```
Esto abrirá una ventana con la interfaz de usuario.

### Ejecutar el servidor Flask
```bash
$ python app.py
```
El servidor estará disponible en `http://127.0.0.1:5000`.

---

## Detalles técnicos

### `app.py`
- **Backend Flask**: Proporciona endpoints para gestionar reservas, turnos fijos, y más.
- **Persistencia**: Utiliza archivos JSON para almacenar datos.
- **Endpoints clave**:
  - `/api/reservar`: Realiza reservas.
  - `/api/guardar_config`: Actualiza configuraciones.
  - `/api/finanzas/reporte_diario`: Genera reportes financieros.

### `app_escritorio.py`
- **PyWebView**: Crea una ventana nativa que carga la interfaz web.
- **Servidor Flask**: Se ejecuta en un hilo separado.
- **Gestión de licencias**: Verifica la validez de la licencia antes de iniciar.

### `licencia_manager.py`
- **Gestión de licencias**: Genera y verifica licencias basadas en hardware y fechas de expiración.
- **Encriptación**: Usa `cryptography.Fernet` para proteger datos sensibles.

---

## Distribución

### Generar ejecutables con PyInstaller
Ejecute el siguiente comando para crear un ejecutable:
```bash
$ pyinstaller --clean --noconfirm --name="SistemaTurnosPadel" --windowed --icon="icono_padel.ico" --add-data="templates;templates" --add-data="static;static" app_escritorio.py
```
Esto generará un ejecutable en la carpeta `dist/`.

---

## Mantenimiento y desarrollo

### Agregar nuevas funcionalidades
1. **Backend**: Modifique `app.py` para agregar nuevos endpoints.
2. **Frontend**: Actualice las plantillas en `templates/` y los scripts en `static/js/`.
3. **Persistencia**: Agregue nuevos archivos JSON si es necesario.

### Pruebas y depuración
- Use `print` y logs para depurar.
- Verifique los archivos JSON para asegurar la integridad de los datos.

---

## Contacto
Para soporte o consultas, contacte al desarrollador en `soporte@padelapp.com`.