# 🎾 SISTEMA DE TURNOS DE PÁDEL

## ✨ VERSIÓN DE ESCRITORIO DISPONIBLE

Ahora tenés **2 formas de usar la aplicación:**

### 🖥️ OPCIÓN 1: Aplicación de Escritorio (RECOMENDADO)
**Ventana independiente, NO requiere navegador**

```
Doble clic en: INICIAR_ESCRITORIO.bat
```

**Ventajas:**
- ✅ Aplicación nativa de Windows
- ✅ No abre navegador
- ✅ Ventana propia con icono
- ✅ Más rápida y fluida
- ✅ Se ve como programa profesional

---

### 🌐 OPCIÓN 2: Versión Navegador (Clásica)
**Se abre en tu navegador predeterminado**

```
Doble clic en: INICIAR_APP.bat
```

**Ventajas:**
- ✅ Familiar (usas tu navegador)
- ✅ Accesible desde otras PCs en red
- ✅ Más ligera en recursos

---

## 🚀 INSTALACIÓN RÁPIDA

### Primera vez:

1. **Verifica Python instalado** (https://www.python.org/downloads/)
   - ⚠️ Marca ✅ "Add Python to PATH" al instalar

2. **Ejecuta:**
   - Para app escritorio: `INICIAR_ESCRITORIO.bat`
   - Para navegador: `INICIAR_APP.bat`

3. La primera vez instalará todo automáticamente (1-2 minutos)

4. **¡Listo!** Las siguientes veces inicia al instante

---

## 🎮 CÓMO USAR

### 1️⃣ Configurar (Primera vez)

- Clic en **"⚙️ Configuración"**
- Define:
  - 🎾 Cantidad de canchas (1-10)
  - 🌅 Horario inicio (ej: 08:00)
  - 🌙 Horario cierre (ej: 22:00)
  - ⏱️ Duración turnos (60/90/120 min)
- Guarda

### 2️⃣ Reservar Turno

1. **Selecciona fecha** 📅
2. **Mira los semáforos** 🚦
   - 🟢 Verde = Todas disponibles
   - 🟡 Amarillo = Algunas ocupadas
   - 🔴 Rojo = Turno completo
3. **Clic en horario** ⏰
4. **Aparecen las canchas** con tu imagen
5. **Clic "Reservar"** en la cancha que quieras
6. **Ingresa nombre** del cliente
7. **Confirma**

### 3️⃣ Cancelar Reserva

1. Selecciona fecha y horario
2. Clic **"Cancelar Reserva"**
3. Confirma

---

## 📸 PERSONALIZAR

### Tu imagen de cancha:
Ya está usando: `static/images/Padel.jpg` ✅

Para cambiarla: reemplaza ese archivo con otra imagen.

---

## 📁 ARCHIVOS PRINCIPALES

```
INICIAR_ESCRITORIO.bat  ← APP DE ESCRITORIO (nuevo!)
INICIAR_APP.bat         ← Versión navegador
CREAR_ACCESO_DIRECTO.bat ← Crea icono en escritorio

app_escritorio.py       ← Motor de la app escritorio
iniciar_app.py          ← Motor navegador
app.py                  ← Servidor Flask

config.json             ← Tu configuración (se crea solo)
reservas.json           ← Tus reservas (se crea solo)
```

---

## 🔧 REQUISITOS TÉCNICOS

**Solo necesitas:**
- ✅ Python 3.7+ instalado
- ✅ Windows (7/8/10/11)
- ✅ 50 MB espacio en disco

**Dependencias (se instalan automáticamente):**
- Flask 3.0.0 (servidor web)
- PyWebView 5.1 (ventana de escritorio)

---

## ❓ PROBLEMAS COMUNES

### "Python no está instalado"
👉 https://www.python.org/downloads/
👉 Marca ✅ "Add Python to PATH"
👉 Reinicia PC

### "No se abre la ventana de escritorio"
👉 Elimina carpeta `venv`
👉 Ejecuta `INICIAR_ESCRITORIO.bat` de nuevo
👉 O usa `INICIAR_APP.bat` (navegador)

### "Error al instalar dependencias"
👉 Abre PowerShell como Administrador
👉 Ejecuta: `Set-ExecutionPolicy RemoteSigned`
👉 Vuelve a ejecutar el BAT

---

## 💾 RESPALDO DE DATOS

**Archivos importantes:**
- `config.json` → Tu configuración
- `reservas.json` → Todas tus reservas

**Para backup:** Copia esos 2 archivos a lugar seguro

**Para restaurar:** Pégalos de vuelta en la carpeta

---

## 🌐 USAR EN RED LOCAL

**Servidor en una PC, acceso desde otras:**

1. En PC principal, usa: `INICIAR_APP.bat` (no escritorio)
2. Abre PowerShell: `ipconfig`
3. Busca tu IP (ej: 192.168.1.100)
4. En otras PCs: `http://192.168.1.100:5000`

---

## 🆕 NOVEDADES DE ESTA VERSIÓN

✅ **Aplicación de escritorio nativa**
✅ **Sistema de semáforo** en horarios (🟢🟡🔴)
✅ **Jugadores animados** en imagen de cancha
✅ **Tu propia imagen** de cancha personalizada
✅ **Instalación automática** en 1 clic
✅ **Sin dependencias complejas**

---

## 🎨 CARACTERÍSTICAS

- ✅ **100% Personalizable** - Canchas y horarios a medida
- ✅ **Sistema visual** - Semáforos de disponibilidad
- ✅ **Fácil de usar** - Interfaz intuitiva
- ✅ **Sin internet** - Funciona offline
- ✅ **Multiplataforma** - App escritorio o navegador
- ✅ **Datos locales** - Privacidad total
- ✅ **Responsive** - Se adapta a cualquier pantalla

---

## 📞 SOPORTE

1. Lee este archivo completo
2. Revisa "Problemas Comunes"
3. Elimina `venv` y reinstala
4. Verifica que Python esté bien instalado

---

## 🔒 PRIVACIDAD

✅ **100% local** - Todo en tu PC
✅ **No requiere internet**
✅ **Cero telemetría**
✅ **Datos privados**

---

**¡Disfrutá tu sistema de turnos profesional! 🎾**

Desarrollado con ❤️ para simplificar la gestión de pádel
