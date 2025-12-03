# 🎾 SISTEMA DE TURNOS DE PÁDEL

## ✨ APLICACIÓN DE ESCRITORIO

**Ventana independiente, sin ventanas de CMD**

```
Doble clic en: INICIAR.bat
```

**Ventajas:**
- ✅ Aplicación nativa de Windows
- ✅ No abre navegador
- ✅ Sin ventanas de consola visibles
- ✅ Más rápida y fluida
- ✅ Se ve como programa profesional
- ✅ El servidor se cierra automáticamente al cerrar la app

---

## 🚀 INSTALACIÓN RÁPIDA

### Primera vez:

1. **Verifica Python instalado** (https://www.python.org/downloads/)
   - ⚠️ Marca ✅ "Add Python to PATH" al instalar

2. **Ejecuta:** `INICIAR.bat`

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
INICIAR.bat             ← Iniciar la aplicación
app_escritorio.py       ← Motor de la app escritorio
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
👉 Ejecuta `INICIAR.bat` de nuevo

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

Para acceder desde otras PCs, necesitarás modificar `app.py` para que escuche en todas las interfaces de red (cambia `host='127.0.0.1'` por `host='0.0.0.0'`).

---

## 🆕 CARACTERÍSTICAS PRINCIPALES

✅ **Aplicación de escritorio nativa** sin ventanas de CMD
✅ **Sistema de semáforo** en horarios (🟢🟡🔴)
✅ **Jugadores animados** en imagen de cancha
✅ **Tu propia imagen** de cancha personalizada
✅ **Instalación automática** en 1 clic
✅ **Cierre automático** del servidor al cerrar la app

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
