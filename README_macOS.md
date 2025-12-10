# 🍎 Sistema de Turnos de Pádel - Versión macOS

Esta guía explica cómo instalar, ejecutar y compilar el sistema en macOS.

## 📋 Requisitos

- **macOS 10.13 (High Sierra) o superior**
- **Python 3.8+** (recomendado 3.11 o superior)
- **Xcode Command Line Tools** (para compilar)

## 🚀 Instalación Rápida

### 1. Instalar Xcode Command Line Tools (si no lo tienes)

```bash
xcode-select --install
```

### 2. Clonar el repositorio

```bash
git clone https://github.com/Velazquezadrian/padel_app.git
cd padel_app
```

### 3. Ejecutar script de configuración

```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

Este script:
- ✅ Verifica Python
- ✅ Crea entorno virtual
- ✅ Instala todas las dependencias
- ✅ Instala dependencias específicas de macOS (PyObjC)
- ✅ Convierte el icono a formato .icns
- ✅ Crea config.json

## 🎮 Uso en Desarrollo

### Ejecutar la aplicación

```bash
source venv/bin/activate
python3 app_escritorio.py
```

### Ejecutar el generador de serials

```bash
source venv/bin/activate
python3 generador_seriales_gui.py
```

## 📦 Compilar para Distribución

### Compilar aplicaciones .app

```bash
./build_mac.sh
```

Esto genera:
- `dist/SistemaTurnosPadel.app` - Aplicación principal
- `dist/GeneradorSeriales.app` - Generador de serials

### Crear archivos DMG (opcional)

El script `build_mac.sh` te preguntará si quieres crear DMGs para distribución fácil.

## 🔧 Compilación Manual

Si prefieres compilar manualmente:

### Aplicación Principal

```bash
pyinstaller --clean --noconfirm \
    --name="SistemaTurnosPadel" \
    --windowed \
    --icon="icono_padel.icns" \
    --add-data="templates:templates" \
    --add-data="static:static" \
    --add-data="icono_padel.icns:." \
    --hidden-import=licencia_manager \
    --hidden-import=cryptography \
    --osx-bundle-identifier=com.padel.turnos \
    app_escritorio.py
```

### Generador de Serials

```bash
pyinstaller --clean --noconfirm \
    --name="GeneradorSeriales" \
    --windowed \
    --icon="icono_padel.icns" \
    --hidden-import=licencia_manager \
    --hidden-import=cryptography \
    --hidden-import=json \
    --osx-bundle-identifier=com.padel.generador \
    generador_seriales_gui.py
```

## 🍎 Características Específicas de macOS

### PyWebView en macOS

PyWebView usa el **WebKit nativo de macOS**, proporcionando:
- ✅ Mejor integración con el sistema
- ✅ Menor consumo de recursos
- ✅ Apariencia nativa de macOS
- ✅ Soporte completo de CSS y JavaScript moderno

### Icono .icns

macOS usa el formato `.icns` para iconos de aplicación. El script `setup_mac.sh` convierte automáticamente `icono_padel.png` a `.icns` con múltiples resoluciones:

- 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024

### Permisos de Seguridad

La primera vez que ejecutes una app compilada, macOS puede mostrar una advertencia de seguridad:

1. Ve a **Preferencias del Sistema > Seguridad y Privacidad**
2. En la pestaña **General**, haz clic en **Abrir de todas formas**
3. Confirma que quieres abrir la aplicación

O desde terminal:

```bash
xattr -cr dist/SistemaTurnosPadel.app
```

## 📱 Distribución de Aplicaciones

### Crear archivo DMG

```bash
hdiutil create -volname "Sistema Turnos Padel" \
    -srcfolder "dist/SistemaTurnosPadel.app" \
    -ov -format UDZO \
    "Cliente_SistemaTurnosPadel_v2.0_macOS.dmg"
```

### Firmar la aplicación (opcional, requiere Apple Developer Account)

```bash
codesign --deep --force --verify --verbose \
    --sign "Developer ID Application: Tu Nombre" \
    dist/SistemaTurnosPadel.app
```

### Notarizar la aplicación (opcional, requiere Apple Developer Account)

```bash
xcrun notarytool submit Cliente_SistemaTurnosPadel_v2.0_macOS.dmg \
    --apple-id "tu@email.com" \
    --password "app-specific-password" \
    --team-id "TEAM_ID" \
    --wait
```

## 🆚 Diferencias con Windows

| Característica | Windows | macOS |
|---|---|---|
| **Formato ejecutable** | .exe | .app |
| **Motor web** | Edge WebView2 | WebKit nativo |
| **Formato icono** | .ico | .icns |
| **Distribución** | ZIP | DMG |
| **Instalador** | InnoSetup | DMG o PKG |
| **Permisos** | UAC | Gatekeeper |

## 🐛 Solución de Problemas

### Error: "command not found: python3"

Instala Python desde [python.org](https://www.python.org/downloads/mac-osx/)

### Error: "No module named 'PyObjC'"

```bash
pip install pyobjc-framework-Cocoa pyobjc-framework-WebKit
```

### Error: "xcrun: error: invalid active developer path"

Instala Xcode Command Line Tools:

```bash
xcode-select --install
```

### La app no abre (error de permisos)

Quita la cuarentena:

```bash
xattr -cr dist/SistemaTurnosPadel.app
open dist/SistemaTurnosPadel.app
```

### PyWebView no carga correctamente

Verifica que tengas los frameworks de PyObjC:

```bash
python3 -c "import AppKit; import WebKit; print('OK')"
```

## 📊 Hardware Binding en macOS

El sistema de licencias usa el identificador único de hardware de Mac:

- **UUID del sistema** (`IOPlatformUUID`)
- **Dirección MAC** de la interfaz de red principal
- **Modelo del procesador**

Esto asegura que las licencias estén ligadas al equipo específico.

## 🔄 Compilación Cruzada

**Nota importante:** No puedes compilar apps de macOS desde Windows (ni viceversa).

Para generar versiones para ambas plataformas:

1. **Windows:** Compila en una máquina Windows
2. **macOS:** Compila en una Mac

Alternativamente, usa máquinas virtuales o servicios en la nube:
- **GitHub Actions** (gratuito para proyectos públicos)
- **CircleCI**
- **Travis CI**

## 📚 Documentación Adicional

- **PyWebView macOS:** https://pywebview.flowrl.com/guide/installation.html#macos
- **PyInstaller macOS:** https://pyinstaller.org/en/stable/usage.html#macos-specific-options
- **Apple Developer:** https://developer.apple.com/

## 🤝 Contribuir

Las contribuciones son bienvenidas. Si encuentras problemas específicos de macOS, abre un issue en GitHub.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

⭐ Si este proyecto te es útil, dale una estrella en GitHub!
