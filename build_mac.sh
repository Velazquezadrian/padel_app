#!/bin/bash
# Script de compilación para macOS
# Uso: ./build_mac.sh

echo "================================"
echo "Compilando para macOS"
echo "================================"

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script debe ejecutarse en macOS"
    exit 1
fi

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "Activando entorno virtual..."
    source venv/bin/activate
else
    echo "⚠️  No se encontró venv, asegúrate de tener las dependencias instaladas"
fi

# Instalar dependencias específicas de macOS
echo "Instalando dependencias de macOS..."
pip install pyobjc-framework-Cocoa pyobjc-framework-WebKit

# Compilar aplicación principal
echo ""
echo "Compilando SistemaTurnosPadel.app..."
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

if [ -d "dist/SistemaTurnosPadel.app" ]; then
    echo "✅ SistemaTurnosPadel.app compilado exitosamente"
else
    echo "❌ Error al compilar SistemaTurnosPadel.app"
    exit 1
fi

# Compilar generador de serials
echo ""
echo "Compilando GeneradorSeriales.app..."
pyinstaller --clean --noconfirm \
    --name="GeneradorSeriales" \
    --windowed \
    --icon="icono_padel.icns" \
    --hidden-import=licencia_manager \
    --hidden-import=cryptography \
    --hidden-import=json \
    --osx-bundle-identifier=com.padel.generador \
    generador_seriales_gui.py

if [ -d "dist/GeneradorSeriales.app" ]; then
    echo "✅ GeneradorSeriales.app compilado exitosamente"
else
    echo "❌ Error al compilar GeneradorSeriales.app"
    exit 1
fi

# Crear DMG para distribución (opcional)
echo ""
echo "¿Quieres crear archivos DMG para distribución? (s/n)"
read -r crear_dmg

if [[ "$crear_dmg" == "s" || "$crear_dmg" == "S" ]]; then
    echo "Creando DMGs..."
    
    # DMG Cliente
    hdiutil create -volname "Sistema Turnos Padel" \
        -srcfolder "dist/SistemaTurnosPadel.app" \
        -ov -format UDZO \
        "Cliente_SistemaTurnosPadel_v2.0_macOS.dmg"
    
    # DMG Admin
    hdiutil create -volname "Generador Seriales" \
        -srcfolder "dist/GeneradorSeriales.app" \
        -ov -format UDZO \
        "Admin_GeneradorSeriales_v2.0_macOS.dmg"
    
    echo "✅ DMGs creados"
fi

echo ""
echo "================================"
echo "✅ Compilación completada!"
echo "================================"
echo ""
echo "Archivos generados:"
echo "  📱 dist/SistemaTurnosPadel.app"
echo "  🔧 dist/GeneradorSeriales.app"

if [[ "$crear_dmg" == "s" || "$crear_dmg" == "S" ]]; then
    echo "  💿 Cliente_SistemaTurnosPadel_v2.0_macOS.dmg"
    echo "  💿 Admin_GeneradorSeriales_v2.0_macOS.dmg"
fi

echo ""
echo "Para probar: open dist/SistemaTurnosPadel.app"
