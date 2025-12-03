# 🎾 Sistema de Turnos para Pádel

Aplicación de escritorio/web para gestionar reservas de canchas de pádel. Desarrollada con Flask y PyWebView.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Características

- 🏟️ **Gestión de múltiples canchas** - Configura la cantidad de canchas disponibles
- ⏰ **Horarios personalizables** - Define rango horario y duración de turnos
- 📅 **Selector de fechas** - Reserva para cualquier día
- 🚦 **Indicadores visuales** - Sistema de semáforo (🟢🟡🔴) para disponibilidad
- 💾 **Persistencia automática** - Reservas guardadas en JSON
- 🖥️ **Doble modo** - Aplicación de escritorio o navegador
- 🎨 **Personalizable** - Usa tu propia imagen de cancha

## 🚀 Instalación

### Requisitos previos

- Python 3.8 o superior
- Windows (optimizado para Windows, adaptable a Linux/Mac)

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/TU_USUARIO/padel-turnos.git
cd padel-turnos
```

2. **Instalar dependencias**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. **Crear configuración inicial** (opcional)
```bash
copy config.example.json config.json
```

## 🎮 Uso

### Iniciar la aplicación

Simplemente ejecuta:

```bash
INICIAR.bat
```

Esto abrirá la aplicación de escritorio en una ventana independiente, sin necesidad de navegador y sin ventanas de CMD visibles.

## ⚙️ Configuración

Al iniciar por primera vez, se crea automáticamente `config.json`:

```json
{
    "cantidad_canchas": 2,
    "horario_inicio": "08:00",
    "horario_fin": "22:00",
    "duracion_turno": 90
}
```

Modifica estos valores desde la interfaz (⚙️ Configuración) o editando el archivo.

## 📋 Cómo reservar

1. **Selecciona la fecha** usando el selector de calendario
2. **Revisa disponibilidad** con los semáforos:
   - 🟢 Verde: Todas las canchas disponibles
   - 🟡 Amarillo: Algunas canchas ocupadas  
   - 🔴 Rojo: Sin disponibilidad
3. **Haz clic en un horario** para ver las canchas
4. **Selecciona una cancha** disponible y haz clic en "Reservar"
5. **Ingresa el nombre** del cliente y confirma

## 🎨 Personalización

Reemplaza `static/images/Padel.jpg` con tu propia imagen de cancha.

## 🛠️ Tecnologías

- **Backend**: Flask 3.0.0
- **Frontend**: HTML5, CSS3, JavaScript Vanilla
- **Desktop**: PyWebView 5.1
- **Storage**: JSON
- **Server**: Werkzeug 3.0.1

## 📁 Estructura del proyecto

```
padel-turnos/
├── app.py                      # Servidor Flask
├── app_escritorio.py           # Launcher app escritorio
├── INICIAR.bat                 # Iniciar aplicación
├── requirements.txt            # Dependencias
├── config.example.json         # Ejemplo configuración
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── main.js
│   │   └── configuracion.js
│   └── images/
│       ├── Padel.jpg           # Tu imagen personalizada
│       └── cancha-default.svg  # Imagen por defecto
└── templates/
    ├── index.html
    └── configuracion.html
```

## 🐛 Solución de problemas

### La aplicación no inicia
- Verifica Python instalado: `python --version`
- Reinstala dependencias: `pip install -r requirements.txt`
- Elimina la carpeta `venv` y vuelve a ejecutar

### No se muestran las canchas
- Presiona F5 para recargar
- Revisa la consola del navegador (F12)
- Verifica que el servidor esté corriendo

### Puerto en uso
- Cierra otras aplicaciones que usen el puerto 5000
- O cambia el puerto en `app.py` y `app_escritorio.py`

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👤 Autor

Desarrollado con ❤️ para facilitar la gestión de canchas de pádel

---

⭐ Si te resultó útil, dale una estrella en GitHub!
