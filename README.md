# 🎾 Sistema de Turnos para Pádel con Licencias

Sistema completo de gestión de reservas de canchas de pádel con sistema de licencias offline.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Características Principales

### 📅 Gestión de Turnos
- **Múltiples canchas** - Configura la cantidad de canchas disponibles
- **Horarios flexibles** - Define rango horario y duración de turnos
- **Calendario interactivo** - Reserva para cualquier día
- **Indicadores visuales** - Sistema de colores para disponibilidad
- **Persistencia automática** - Reservas guardadas en JSON

### 👥 Gestión de Clientes
- **Base de datos** de clientes
- **Historial** de reservas por cliente
- **Búsqueda rápida** de clientes

### 🔐 Sistema de Licencias
- **Hardware Binding** - Licencias ligadas al equipo
- **Single-Use Serials** - Cada serial se usa una sola vez
- **Trial Persistence** - Control de períodos de prueba
- **Offline** - Funciona 100% sin internet
- **Múltiples planes** - Trial, Mensual, Trimestral, Semestral, Anual

### 📊 Funcionalidades Avanzadas
- **Backup/Restore** - Exporta e importa toda la base de datos
- **Reportes PDF** - Genera comprobantes de reserva
- **Turnos fijos** - Para clientes recurrentes
- **Ausencias** - Gestiona días cerrados

## 🏗️ Arquitectura

```
padel-turnos/
├── app.py                      # Backend Flask (API REST)
├── app_escritorio.py           # Frontend PyWebView (Desktop)
├── licencia_manager.py         # Sistema de licencias
├── generador_seriales_gui.py   # Generador de serials (Admin)
├── templates/                  # Plantillas HTML
│   └── index.html
├── static/                     # CSS, JS, imágenes
│   ├── css/
│   ├── js/
│   └── images/
├── requirements.txt            # Dependencias Python
└── config.example.json         # Configuración de ejemplo
```

## 🚀 Inicio Rápido

### Requisitos
- Python 3.13+
- Windows 10/11 (ejecutables compilados para Windows)

### Instalación para Desarrollo

1. **Clonar repositorio**
```bash
git clone https://github.com/Velazquezadrian/padel_app.git
cd padel_app
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar aplicación**
```bash
copy config.example.json config.json
```

5. **Ejecutar aplicación**
```bash
python app_escritorio.py
```

### Uso de Ejecutables (Cliente)

1. Descargar `SistemaTurnosPadel_v1.0_Portable.zip`
2. Extraer en cualquier carpeta
3. Ejecutar `SistemaTurnosPadel.exe`
4. Ingresar serial de licencia (o usar trial de 15 días)

## 🔑 Sistema de Licencias

### Para Administradores

1. **Generar serials**
   - Ejecutar `GeneradorSeriales.exe`
   - Completar datos del cliente (nombre, apellido, contacto)
   - Seleccionar tipo de plan
   - Copiar serial generado

2. **Distribución**
   - Enviar serial al cliente por email/WhatsApp
   - Cliente ingresa serial en la aplicación
   - Activación automática

3. **Registro de clientes**
   - Archivo `registro_clientes.json` guarda todos los datos
   - Ver historial con botón "Ver Registros"
   - Backup regular recomendado

### Tipos de Planes

| Plan | Duración | Uso Recomendado |
|------|----------|-----------------|
| Trial | 15 días | Prueba gratuita |
| Mensual | 30 días | Suscripción básica |
| Trimestral | 90 días | Plan económico |
| Semestral | 180 días | Plan semestral |
| Anual | 365 días | Mejor descuento |
| Personalizado | Variable | A medida |

## 📦 Compilación de Ejecutables

### Aplicación Principal

```bash
pyinstaller SistemaTurnosPadel.spec
```

### Generador de Seriales

```bash
pyinstaller --onefile --windowed --name="GeneradorSeriales" ^
            --icon="icono_padel.ico" ^
            --hidden-import=licencia_manager ^
            --hidden-import=cryptography ^
            --hidden-import=json ^
            generador_seriales_gui.py
```

## 🔧 Configuración

El archivo `config.json` permite personalizar:

```json
{
  "cantidad_canchas": 4,
  "hora_inicio": "08:00",
  "hora_fin": "23:00",
  "duracion_turno": 90,
  "imagen_cancha": "static/images/cancha.jpg"
}
```

## 📝 Documentación

- **INICIO_RAPIDO.txt** - Guía de inicio en 5 minutos
- **INSTRUCCIONES_ADMIN.txt** - Manual del generador de serials
- **REGISTRO_CLIENTES.txt** - Sistema de registro de clientes
- **LEEME_CLIENTE.txt** - Instrucciones para usuarios finales
- **RESUMEN_PROYECTO.txt** - Documentación técnica completa

## 🛠️ Tecnologías

- **Backend**: Flask 3.0.0
- **Frontend Desktop**: PyWebView 5.1
- **Base de Datos**: SQLite/JSON
- **Seguridad**: Cryptography 41.0.7 (Fernet AES-128)
- **GUI Generador**: Tkinter
- **Compilación**: PyInstaller 6.17.0

## 🔒 Seguridad

- ✅ Licencias encriptadas con AES-128
- ✅ Hardware binding (UUID + MAC + Processor)
- ✅ Serials de un solo uso
- ✅ Trial persistence
- ✅ Sin conexión a internet requerida

## 📊 Estructura de Datos

### Reservas (`reservas.json`)
```json
{
  "2025-12-09": {
    "cancha_1": {
      "14:00": {
        "cliente": "Juan Pérez",
        "telefono": "+54 9 11 1234-5678",
        "observaciones": "Torneo amistoso"
      }
    }
  }
}
```

### Registro de Clientes (`registro_clientes.json`)
```json
[
  {
    "id": 1,
    "nombre": "Juan",
    "apellido": "Pérez",
    "contacto": "juan@email.com",
    "tipo_plan": "trimestral",
    "dias": 90,
    "fecha_generacion": "2025-12-09 13:00:00",
    "fecha_expiracion": "2026-03-09",
    "serial": "Z0FBQUFBQn...",
    "serial_id": "abc123..."
  }
]
```

## 🤝 Contribuir

Las contribuciones son bienvenidas:

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit cambios (`git commit -m 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Adrian Velazquez**
- GitHub: [@Velazquezadrian](https://github.com/Velazquezadrian)

## 🙏 Agradecimientos

- Comunidad de Python y Flask
- Contribuidores de PyWebView
- Usuarios beta testers

## 📮 Soporte

Para soporte, abrir un issue en GitHub o contactar directamente.

---

⭐ Si te gusta este proyecto, dale una estrella en GitHub!
