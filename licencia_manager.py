"""
Sistema de Licencias con Fecha de Expiración
Genera claves encriptadas basadas en fecha de expiración
"""

import hashlib
import json
import os
import uuid
import platform
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64

class LicenciaManager:
    def __init__(self, archivo_licencia='licencia.dat'):
        self.archivo_licencia = archivo_licencia
        # Clave secreta para encriptación (cambiar en producción)
        self.clave_maestra = b'TuClaveSecretaMuySegura2025PadelApp!!'
        # Generar clave Fernet desde la clave maestra
        self.fernet_key = base64.urlsafe_b64encode(hashlib.sha256(self.clave_maestra).digest())
        self.cipher = Fernet(self.fernet_key)
        # Archivo para registrar seriales usados (solo tú tienes acceso)
        self.archivo_seriales_usados = 'seriales_usados.json'
    
    def obtener_hardware_id(self):
        """
        Genera un ID único basado en el hardware de la máquina
        Esto evita que reinstalen para resetear el trial
        """
        try:
            # Obtener información del sistema
            sistema = platform.system()
            nodo = platform.node()
            procesador = platform.processor()
            
            # En Windows, intentar obtener el UUID de la BIOS
            if sistema == 'Windows':
                try:
                    import subprocess
                    resultado = subprocess.check_output('wmic csproduct get uuid', shell=True)
                    uuid_sistema = resultado.decode().split('\n')[1].strip()
                except:
                    uuid_sistema = str(uuid.getnode())
            else:
                uuid_sistema = str(uuid.getnode())
            
            # Crear hash único
            info_hardware = f"{sistema}-{nodo}-{procesador}-{uuid_sistema}"
            hardware_id = hashlib.sha256(info_hardware.encode()).hexdigest()[:16]
            
            return hardware_id
        except:
            # Fallback: usar MAC address
            return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:16]
    
    def generar_licencia(self, nombre_cliente, dias_validez, tipo_licencia='mensual', hardware_id=None):
        """
        Genera una nueva licencia
        tipo_licencia: 'trial', 'mensual', 'anual', etc.
        hardware_id: ID de hardware para vincular la licencia (opcional)
        """
        fecha_inicio = datetime.now()
        fecha_expiracion = fecha_inicio + timedelta(days=dias_validez)
        
        # Si no se proporciona hardware_id, usar el de esta máquina
        if hardware_id is None:
            hardware_id = self.obtener_hardware_id()
        
        datos_licencia = {
            'cliente': nombre_cliente,
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_expiracion': fecha_expiracion.isoformat(),
            'tipo': tipo_licencia,
            'activa': True,
            'version': '1.0',
            'hardware_id': hardware_id,
            'activaciones': 0  # Contador de activaciones
        }
        
        # Convertir a JSON y encriptar
        json_data = json.dumps(datos_licencia).encode('utf-8')
        datos_encriptados = self.cipher.encrypt(json_data)
        
        # Guardar en archivo
        with open(self.archivo_licencia, 'wb') as f:
            f.write(datos_encriptados)
        
        return datos_licencia
    
    def verificar_licencia(self):
        """
        Verifica si la licencia es válida y no ha expirado
        Retorna: (es_valida, dias_restantes, mensaje)
        """
        if not os.path.exists(self.archivo_licencia):
            return False, 0, "No se encontró archivo de licencia. Contacte al proveedor."
        
        try:
            # Leer y desencriptar
            with open(self.archivo_licencia, 'rb') as f:
                datos_encriptados = f.read()
            
            datos_json = self.cipher.decrypt(datos_encriptados)
            datos_licencia = json.loads(datos_json.decode('utf-8'))
            
            # Verificar expiración
            fecha_expiracion = datetime.fromisoformat(datos_licencia['fecha_expiracion'])
            fecha_actual = datetime.now()
            
            if fecha_actual > fecha_expiracion:
                dias_vencida = (fecha_actual - fecha_expiracion).days
                return False, 0, f"Licencia expirada hace {dias_vencida} días. Contacte al proveedor para renovar."
            
            dias_restantes = (fecha_expiracion - fecha_actual).days
            
            # Advertencia si faltan menos de 7 días
            if dias_restantes <= 7:
                return True, dias_restantes, f"⚠️ ADVERTENCIA: La licencia expira en {dias_restantes} días. Renueve pronto."
            
            return True, dias_restantes, f"Licencia válida. Expira: {fecha_expiracion.strftime('%d/%m/%Y')}"
            
        except Exception as e:
            return False, 0, f"Error al verificar licencia: {str(e)}"
    
    def obtener_info_licencia(self):
        """
        Obtiene información detallada de la licencia
        """
        if not os.path.exists(self.archivo_licencia):
            return None
        
        try:
            with open(self.archivo_licencia, 'rb') as f:
                datos_encriptados = f.read()
            
            datos_json = self.cipher.decrypt(datos_encriptados)
            datos_licencia = json.loads(datos_json.decode('utf-8'))
            
            return datos_licencia
            
        except:
            return None
    
    def renovar_licencia(self, dias_adicionales):
        """
        Renueva la licencia agregando días adicionales
        """
        info = self.obtener_info_licencia()
        if not info:
            return False, "No se pudo leer la licencia actual"
        
        # Calcular nueva fecha desde la expiración actual o desde hoy (lo que sea mayor)
        fecha_expiracion_actual = datetime.fromisoformat(info['fecha_expiracion'])
        fecha_base = max(datetime.now(), fecha_expiracion_actual)
        nueva_fecha_expiracion = fecha_base + timedelta(days=dias_adicionales)
        
        info['fecha_expiracion'] = nueva_fecha_expiracion.isoformat()
        
        # Guardar licencia renovada
        json_data = json.dumps(info).encode('utf-8')
        datos_encriptados = self.cipher.encrypt(json_data)
        
        with open(self.archivo_licencia, 'wb') as f:
            f.write(datos_encriptados)
        
        return True, f"Licencia renovada hasta {nueva_fecha_expiracion.strftime('%d/%m/%Y')}"
    
    def verificar_serial_usado(self, serial_id):
        """
        Verifica si un serial ya fue usado (solo para administrador)
        """
        if not os.path.exists(self.archivo_seriales_usados):
            return False
        
        try:
            with open(self.archivo_seriales_usados, 'r') as f:
                usados = json.load(f)
            return serial_id in usados
        except:
            return False
    
    def marcar_serial_usado(self, serial_id, hardware_id):
        """
        Marca un serial como usado (solo para administrador)
        """
        try:
            usados = {}
            if os.path.exists(self.archivo_seriales_usados):
                with open(self.archivo_seriales_usados, 'r') as f:
                    usados = json.load(f)
            
            usados[serial_id] = {
                'hardware_id': hardware_id,
                'fecha_activacion': datetime.now().isoformat()
            }
            
            with open(self.archivo_seriales_usados, 'w') as f:
                json.dump(usados, f, indent=2)
            
            return True
        except:
            return False
    
    def aplicar_serial(self, serial_encriptado):
        """
        Aplica un serial de licencia encriptado
        El serial solo puede usarse UNA VEZ y se vincula al hardware
        """
        try:
            # Decodificar de base64
            datos_encriptados = base64.b64decode(serial_encriptado.encode('utf-8'))
            
            # Desencriptar
            datos_json = self.cipher.decrypt(datos_encriptados)
            datos_compactos = json.loads(datos_json.decode('utf-8'))
            
            # Expandir datos compactos a formato completo
            # Soportar tanto formato compacto nuevo como formato antiguo
            if 'c' in datos_compactos:
                # Formato compacto nuevo
                datos_licencia = {
                    'cliente': datos_compactos.get('c', 'Cliente'),
                    'fecha_expiracion': datos_compactos.get('e', ''),
                    'tipo': datos_compactos.get('t', 'trial'),
                    'serial_id': datos_compactos.get('s', ''),
                    'hardware_id': datos_compactos.get('h'),
                    'activaciones': datos_compactos.get('a', 0),
                    'activa': True,
                    'version': '1.0',
                    'fecha_inicio': datetime.now().isoformat()
                }
            else:
                # Formato antiguo (compatibilidad)
                datos_licencia = datos_compactos
            
            # Validar que tenga los campos necesarios
            if 'fecha_expiracion' not in datos_licencia or 'tipo' not in datos_licencia:
                return False, "Serial inválido: formato incorrecto"
            
            # Obtener ID único del serial
            serial_id = datos_licencia.get('serial_id', '')
            if not serial_id:
                return False, "Serial inválido: falta identificador"
            
            # Verificar que no esté expirado
            fecha_exp_str = datos_licencia['fecha_expiracion']
            # Manejar formato corto (YYYY-MM-DD) y formato ISO completo
            try:
                if 'T' in fecha_exp_str:
                    fecha_expiracion = datetime.fromisoformat(fecha_exp_str)
                else:
                    fecha_expiracion = datetime.strptime(fecha_exp_str, '%Y-%m-%d')
            except:
                return False, "Serial inválido: fecha incorrecta"
                
            if datetime.now() > fecha_expiracion:
                return False, "Serial expirado. Contacte al proveedor."
            
            # Obtener hardware ID de esta máquina
            hardware_id_actual = self.obtener_hardware_id()
            
            # Verificar si el serial ya fue usado
            if self.verificar_serial_usado(serial_id):
                # Si ya fue usado, verificar si es en la misma máquina
                try:
                    with open(self.archivo_seriales_usados, 'r') as f:
                        usados = json.load(f)
                    
                    if usados[serial_id]['hardware_id'] == hardware_id_actual:
                        # Mismo hardware, permitir reinstalación
                        pass
                    else:
                        return False, "Este serial ya fue activado en otra computadora. Contacte al proveedor."
                except:
                    return False, "Serial ya utilizado"
            
            # Vincular el serial al hardware actual
            datos_licencia['hardware_id'] = hardware_id_actual
            datos_licencia['activaciones'] = datos_licencia.get('activaciones', 0) + 1
            
            # Marcar serial como usado
            self.marcar_serial_usado(serial_id, hardware_id_actual)
            
            # Guardar la licencia
            json_data = json.dumps(datos_licencia).encode('utf-8')
            datos_encriptados_nuevos = self.cipher.encrypt(json_data)
            
            with open(self.archivo_licencia, 'wb') as f:
                f.write(datos_encriptados_nuevos)
            
            dias_restantes = (fecha_expiracion - datetime.now()).days
            return True, f"Licencia activada exitosamente. Tipo: {datos_licencia['tipo']}. Válida por {dias_restantes} días."
            
        except Exception as e:
            return False, f"Error al aplicar serial: {str(e)}"
    
    def generar_serial(self, nombre_cliente, dias_validez, tipo_licencia='mensual'):
        """
        Genera un serial (string base64) que puede copiarse y pegarse
        SOLO PARA USO DEL ADMINISTRADOR - No incluir en versión del cliente
        """
        fecha_inicio = datetime.now()
        fecha_expiracion = fecha_inicio + timedelta(days=dias_validez)
        
        # Generar ID único para el serial (más corto: primeros 16 caracteres)
        serial_id = hashlib.sha256(f"{fecha_inicio.isoformat()}{uuid.uuid4()}".encode()).hexdigest()[:16]
        
        # Datos compactos (solo lo esencial)
        datos_licencia = {
            'c': nombre_cliente,                          # cliente
            'e': fecha_expiracion.strftime('%Y-%m-%d'),   # expiracion (formato corto)
            't': tipo_licencia,                           # tipo
            's': serial_id,                               # serial_id
            'h': None,                                    # hardware_id
            'a': 0                                        # activaciones
        }
        
        # Convertir a JSON compacto y encriptar
        json_data = json.dumps(datos_licencia, separators=(',', ':')).encode('utf-8')
        datos_encriptados = self.cipher.encrypt(json_data)
        
        # Convertir a base64 para que sea copiable
        serial = base64.b64encode(datos_encriptados).decode('utf-8')
        
        # Datos expandidos para retornar (para mostrar al admin)
        datos_expandidos = {
            'cliente': nombre_cliente,
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_expiracion': fecha_expiracion.isoformat(),
            'tipo': tipo_licencia,
            'activa': True,
            'version': '1.0',
            'serial_id': serial_id,
            'hardware_id': None,
            'activaciones': 0
        }
        
        return serial, datos_expandidos
    
    def verificar_trial_previo(self):
        """
        Verifica si ya se usó el trial en esta máquina
        Evita que reinstalen para obtener trial nuevamente
        """
        hardware_id = self.obtener_hardware_id()
        archivo_trials = 'trials_usados.json'
        
        # Archivo oculto en AppData para evitar que lo borren
        try:
            if platform.system() == 'Windows':
                appdata = os.environ.get('APPDATA')
                if appdata:
                    archivo_trials = os.path.join(appdata, '.padel_trials')
        except:
            pass
        
        if os.path.exists(archivo_trials):
            try:
                with open(archivo_trials, 'r') as f:
                    trials_usados = json.load(f)
                
                if hardware_id in trials_usados:
                    # Ya usó el trial en esta máquina
                    info = trials_usados[hardware_id]
                    fecha_expiracion = datetime.fromisoformat(info['fecha_expiracion'])
                    
                    if datetime.now() < fecha_expiracion:
                        # Trial aún válido, restaurarlo
                        return True, info
                    else:
                        # Trial expirado
                        return False, None
                
            except:
                pass
        
        return False, None
    
    def registrar_trial(self, datos_licencia):
        """
        Registra que se usó el trial en esta máquina
        """
        hardware_id = self.obtener_hardware_id()
        archivo_trials = 'trials_usados.json'
        
        try:
            if platform.system() == 'Windows':
                appdata = os.environ.get('APPDATA')
                if appdata:
                    archivo_trials = os.path.join(appdata, '.padel_trials')
        except:
            pass
        
        try:
            trials_usados = {}
            if os.path.exists(archivo_trials):
                with open(archivo_trials, 'r') as f:
                    trials_usados = json.load(f)
            
            trials_usados[hardware_id] = {
                'fecha_inicio': datos_licencia['fecha_inicio'],
                'fecha_expiracion': datos_licencia['fecha_expiracion'],
                'fecha_registro': datetime.now().isoformat()
            }
            
            with open(archivo_trials, 'w') as f:
                json.dump(trials_usados, f)
            
            # En Windows, ocultar el archivo
            if platform.system() == 'Windows':
                try:
                    import subprocess
                    subprocess.run(['attrib', '+H', archivo_trials], check=False)
                except:
                    pass
                    
        except:
            pass
    
    def crear_licencia_trial(self):
        """
        Crea una licencia de prueba de 15 días automáticamente
        Solo si no existe una licencia previa Y no se usó trial antes
        """
        if os.path.exists(self.archivo_licencia):
            return False, "Ya existe una licencia"
        
        # Verificar si ya usó el trial
        ya_uso_trial, info_trial = self.verificar_trial_previo()
        
        if ya_uso_trial and info_trial:
            # Restaurar el trial existente
            datos_licencia = self.generar_licencia(
                "Usuario Trial", 
                15, 
                'trial'
            )
            # Actualizar con las fechas originales
            datos_licencia['fecha_inicio'] = info_trial['fecha_inicio']
            datos_licencia['fecha_expiracion'] = info_trial['fecha_expiracion']
            
            # Guardar
            json_data = json.dumps(datos_licencia).encode('utf-8')
            datos_encriptados = self.cipher.encrypt(json_data)
            with open(self.archivo_licencia, 'wb') as f:
                f.write(datos_encriptados)
            
            return datos_licencia
        
        elif ya_uso_trial and not info_trial:
            # Trial expirado, no crear nuevo
            return None
        
        # Primera vez, crear trial nuevo
        datos_licencia = self.generar_licencia("Usuario Trial", 15, 'trial')
        self.registrar_trial(datos_licencia)
        
        return datos_licencia
    
    def desactivar_licencia(self):
        """
        Desactiva la licencia (para casos de abuso)
        """
        if os.path.exists(self.archivo_licencia):
            os.remove(self.archivo_licencia)
            return True
        return False


# Herramienta para generar licencias (usar en tu computadora, no distribuir)
def generar_licencia_cliente():
    """
    Script para generar licencias para clientes
    Ejecutar este archivo directamente para generar licencias
    """
    print("=" * 60)
    print("GENERADOR DE LICENCIAS - Sistema de Turnos Pádel")
    print("=" * 60)
    
    nombre = input("\nNombre del cliente: ")
    
    print("\nTipo de licencia:")
    print("1. Prueba (30 días)")
    print("2. Mensual (30 días)")
    print("3. Anual (365 días)")
    print("4. Personalizada")
    
    opcion = input("\nSeleccione opción (1-4): ")
    
    if opcion == '1':
        dias = 30
        tipo = 'prueba'
    elif opcion == '2':
        dias = 30
        tipo = 'mensual'
    elif opcion == '3':
        dias = 365
        tipo = 'anual'
    elif opcion == '4':
        dias = int(input("Ingrese cantidad de días: "))
        tipo = 'personalizada'
    else:
        print("Opción inválida")
        return
    
    archivo_salida = input("\nNombre del archivo de salida (ej: licencia_cliente1.dat): ") or "licencia.dat"
    
    manager = LicenciaManager(archivo_salida)
    licencia = manager.generar_licencia(nombre, dias, tipo)
    
    print("\n" + "=" * 60)
    print("✅ LICENCIA GENERADA EXITOSAMENTE")
    print("=" * 60)
    print(f"Cliente: {licencia['cliente']}")
    print(f"Tipo: {licencia['tipo']}")
    print(f"Válida desde: {licencia['fecha_inicio']}")
    print(f"Expira: {licencia['fecha_expiracion']}")
    print(f"Archivo: {archivo_salida}")
    print("\n📧 Envíe este archivo al cliente para que lo coloque en la carpeta de la aplicación")
    print("=" * 60)


if __name__ == "__main__":
    generar_licencia_cliente()
