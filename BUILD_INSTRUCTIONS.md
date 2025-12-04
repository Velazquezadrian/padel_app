# 📦 Compilación e Instalador - Padel App

## Requisitos Previos

### Para compilar el ejecutable:
- Python 3.x instalado
- Entorno virtual configurado (`venv`)

### Para crear el instalador:
- **Inno Setup** descargado e instalado
  - Descargar desde: https://jrsoftware.org/isdl.php
  - Instalar con opciones por defecto

## Pasos para crear el instalador

### 1. Compilar el ejecutable

Ejecutar el archivo `build.bat`:

```cmd
build.bat
```

Este script:
- ✅ Activa el entorno virtual
- ✅ Instala PyInstaller
- ✅ Compila la aplicación en un solo archivo ejecutable
- ✅ Incluye templates y static
- ✅ Genera `dist\PadelApp.exe`

### 2. Crear el instalador

1. Abrir **Inno Setup Compiler**
2. Abrir el archivo `setup.iss`
3. Click en **Build** → **Compile**
4. El instalador se generará en: `installer\PadelApp_Setup.exe`

### 3. Distribuir

El archivo `PadelApp_Setup.exe` es el instalador final que puedes distribuir a tus clientes.

## Características del Instalador

✅ Instalación profesional con asistente
✅ Icono en el menú inicio
✅ Opción de icono en el escritorio
✅ Desinstalador incluido
✅ Datos del usuario guardados en `%APPDATA%\PadelApp`
✅ No requiere Python instalado en la PC del cliente

## Estructura de archivos

```
dist/
  └── PadelApp.exe          # Ejecutable compilado

installer/
  └── PadelApp_Setup.exe    # Instalador final

%APPDATA%\PadelApp/         # Datos del usuario (después de instalar)
  ├── config.json
  ├── reservas.json
  ├── turnos_fijos.json
  ├── ausencias.json
  └── tema.json
```

## Notas Importantes

- ⚠️ Los archivos de datos (config.json, reservas.json, etc.) NO se incluyen en el instalador
- ✅ Se crean automáticamente en la primera ejecución
- ✅ Se guardan en la carpeta del usuario para evitar problemas de permisos
- ✅ Cada usuario puede tener su propia configuración

## Solución de Problemas

### Error: "PyInstaller no encontrado"
```cmd
pip install pyinstaller
```

### Error: "Inno Setup no puede compilar"
- Verificar que `dist\PadelApp.exe` existe
- Verificar que `icon.ico` existe (o comentar esa línea en setup.iss)

### El ejecutable no inicia
- Verificar que todas las dependencias estén instaladas en el venv
- Revisar el archivo `app.py` para rutas correctas
