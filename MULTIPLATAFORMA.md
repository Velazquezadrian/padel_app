# 🌐 Compatibilidad Multiplataforma

## ✅ Plataformas Soportadas

| Plataforma | Estado | Versión Mínima | Formato Ejecutable |
|------------|--------|----------------|-------------------|
| **Windows** | ✅ Completo | Windows 10 | .exe |
| **macOS** | ✅ Completo | macOS 10.13+ | .app / .dmg |
| **Linux** | ⚠️ Experimental | Ubuntu 20.04+ | AppImage |

## 🔧 Dependencias por Plataforma

### Windows
```
- Python 3.8+
- pywebview (usa Edge WebView2)
- No requiere dependencias adicionales
```

### macOS
```
- Python 3.8+
- pywebview (usa WebKit nativo)
- PyObjC-framework-Cocoa
- PyObjC-framework-WebKit
- Xcode Command Line Tools (para compilar)
```

### Linux (Experimental)
```
- Python 3.8+
- pywebview (usa GTK WebKit2)
- python3-gi
- gir1.2-webkit2-4.0
- libgtk-3-dev
```

## 📊 Sistema de Licencias por Plataforma

El hardware binding funciona de forma diferente en cada plataforma:

### Windows
- **UUID del sistema** (BIOS UUID)
- **MAC Address** de la tarjeta de red principal
- **ProcessorId** del CPU

### macOS
- **IOPlatformUUID** (identificador único del hardware)
- **MAC Address** de la interfaz principal (en0)
- **CPU Model** del procesador

### Linux
- **Machine ID** (/etc/machine-id)
- **MAC Address** de la interfaz principal
- **CPU Model** del procesador

**Importante:** Las licencias generadas en una plataforma NO son compatibles con otras plataformas debido a las diferencias en el hardware binding.

## 🎨 Interfaz de Usuario

### Renderizado Web

| Plataforma | Motor Web | Versión |
|------------|-----------|---------|
| Windows | Edge WebView2 | Chromium 90+ |
| macOS | WebKit | Safari 12+ |
| Linux | WebKit2GTK | 2.26+ |

Todos los motores soportan:
- ✅ HTML5
- ✅ CSS3
- ✅ JavaScript ES6+
- ✅ LocalStorage
- ✅ Canvas

### Apariencia

- **Windows:** Usa estilos de Windows 11/10
- **macOS:** Integración nativa con el theme del sistema (Light/Dark mode)
- **Linux:** Tema GTK del sistema

## 📦 Distribución

### Windows
```
Cliente_SistemaTurnosPadel_v2.0.zip (15 MB)
├── SistemaTurnosPadel.exe
├── _internal/
└── LEEME_CLIENTE.txt

Admin_GeneradorSeriales_v2.0.zip (13 MB)
├── GeneradorSeriales.exe
└── INSTRUCCIONES_ADMIN.txt
```

### macOS
```
Cliente_SistemaTurnosPadel_v2.0_macOS.dmg (16 MB)
└── SistemaTurnosPadel.app

Admin_GeneradorSeriales_v2.0_macOS.dmg (14 MB)
└── GeneradorSeriales.app
```

### Linux
```
Cliente_SistemaTurnosPadel_v2.0_Linux.AppImage (18 MB)
Admin_GeneradorSeriales_v2.0_Linux.AppImage (15 MB)
```

## 🚀 Compilación Cruzada

**⚠️ Limitación importante:** No es posible compilar ejecutables de una plataforma en otra.

Para generar ejecutables para todas las plataformas necesitas:

### Opción 1: Múltiples Máquinas
- Máquina Windows para compilar .exe
- Mac para compilar .app
- Linux para compilar AppImage

### Opción 2: GitHub Actions (Recomendado)

Crear workflow que compile en todas las plataformas automáticamente:

```yaml
name: Build Multi-Platform

on: [push, release]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pyinstaller SistemaTurnosPadel.spec
      
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: ./setup_mac.sh
      - run: ./build_mac.sh
      
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: ./setup_linux.sh
      - run: ./build_linux.sh
```

## 🐛 Problemas Conocidos

### Windows
- ✅ Funciona perfectamente
- Requiere Edge WebView2 (instalado por defecto en Windows 11)

### macOS
- ✅ Funciona perfectamente
- Primera ejecución requiere permisos de seguridad
- Firma de código recomendada para distribución

### Linux (Experimental)
- ⚠️ Puede requerir instalación manual de dependencias GTK
- ⚠️ Soporte de WebKit2GTK varía por distribución
- ⚠️ No probado extensivamente

## 📱 Roadmap

### v2.1 (Próxima versión)
- [ ] Soporte completo y probado para Linux
- [ ] Instaladores nativos (.msi para Windows, .pkg para macOS)
- [ ] Auto-actualización

### v2.2 (Futuro)
- [ ] Versión web (sin instalación)
- [ ] App móvil (iOS/Android)
- [ ] Sincronización en la nube (opcional)

## 🔗 Enlaces Útiles

- **PyWebView Docs:** https://pywebview.flowrl.com/
- **PyInstaller Docs:** https://pyinstaller.org/
- **GitHub Actions:** https://github.com/features/actions

## 💡 Consejos

1. **Probar en VM:** Usa máquinas virtuales para probar en múltiples plataformas
2. **GitHub Actions:** Automatiza la compilación para todas las plataformas
3. **Beta Testing:** Consigue testers en cada plataforma antes del lanzamiento
4. **Documentación:** Mantén README específicos para cada plataforma actualizados

## 🤝 Contribuciones

Si tienes experiencia con Linux y quieres ayudar a mejorar el soporte:
1. Prueba la aplicación en tu distribución
2. Reporta issues específicos de la plataforma
3. Contribuye con scripts de instalación/compilación

---

⭐ Este proyecto se esfuerza por ser verdaderamente multiplataforma!
