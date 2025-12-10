#!/bin/bash
# Script de instalación y configuración para macOS
# Uso: ./setup_mac.sh

echo "================================"
echo "Configuración para macOS"
echo "================================"

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "Instala Python desde: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python $(python3 --version) detectado"

# Crear entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "⚠️  El entorno virtual ya existe"
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Instalar dependencias específicas de macOS para PyWebView
echo "Instalando dependencias de macOS..."
pip install pyobjc-framework-Cocoa pyobjc-framework-WebKit

# Instalar PyInstaller
echo "Instalando PyInstaller..."
pip install pyinstaller

# Verificar instalación
echo ""
echo "Verificando instalación..."
python3 -c "import flask; import webview; import cryptography; print('✅ Todas las dependencias instaladas correctamente')"

# Crear archivo de configuración si no existe
if [ ! -f "config.json" ]; then
    echo "Creando config.json..."
    cp config.example.json config.json
    echo "✅ config.json creado"
fi

# Convertir icono PNG a ICNS (si no existe)
if [ ! -f "icono_padel.icns" ] && [ -f "icono_padel.png" ]; then
    echo "Convirtiendo icono a formato macOS (.icns)..."
    mkdir -p icono_padel.iconset
    
    # Crear múltiples tamaños
    sips -z 16 16     icono_padel.png --out icono_padel.iconset/icon_16x16.png
    sips -z 32 32     icono_padel.png --out icono_padel.iconset/icon_16x16@2x.png
    sips -z 32 32     icono_padel.png --out icono_padel.iconset/icon_32x32.png
    sips -z 64 64     icono_padel.png --out icono_padel.iconset/icon_32x32@2x.png
    sips -z 128 128   icono_padel.png --out icono_padel.iconset/icon_128x128.png
    sips -z 256 256   icono_padel.png --out icono_padel.iconset/icon_128x128@2x.png
    sips -z 256 256   icono_padel.png --out icono_padel.iconset/icon_256x256.png
    sips -z 512 512   icono_padel.png --out icono_padel.iconset/icon_256x256@2x.png
    sips -z 512 512   icono_padel.png --out icono_padel.iconset/icon_512x512.png
    sips -z 1024 1024 icono_padel.png --out icono_padel.iconset/icon_512x512@2x.png
    
    iconutil -c icns icono_padel.iconset
    rm -rf icono_padel.iconset
    
    echo "✅ Icono .icns creado"
fi

# Dar permisos de ejecución a scripts
chmod +x build_mac.sh

echo ""
echo "================================"
echo "✅ Configuración completada!"
echo "================================"
echo ""
echo "Próximos pasos:"
echo "1. Ejecutar la app en modo desarrollo:"
echo "   python3 app_escritorio.py"
echo ""
echo "2. Compilar para distribución:"
echo "   ./build_mac.sh"
echo ""
echo "Nota: La primera vez que ejecutes las apps compiladas,"
echo "macOS puede pedir permisos de seguridad en:"
echo "Preferencias del Sistema > Seguridad y Privacidad"
