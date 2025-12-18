"""
Generador de Seriales - Interfaz Gráfica
Sistema de Turnos de Pádel

Aplicación standalone para generar seriales de licencia
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import json
from datetime import datetime, timedelta
import traceback

# Agregar path para imports
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)

from licencia_manager import LicenciaManager

class GeneradorSerialesGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Seriales - Sistema Turnos Pádel")
        self.root.geometry("700x750")
        self.root.resizable(False, False)
        
        # Colores
        self.color_primario = "#4CAF50"
        self.color_secundario = "#45a049"
        self.color_fondo = "#f5f5f5"
        self.color_texto = "#333333"
        
        self.root.configure(bg=self.color_fondo)
        
        # Manager de licencias
        self.manager = LicenciaManager()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Centrar ventana
        self.centrar_ventana()
    
    def centrar_ventana(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def crear_interfaz(self):
        # Header
        header_frame = tk.Frame(self.root, bg=self.color_primario, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        titulo = tk.Label(
            header_frame,
            text="Generador de Seriales",
            font=("Segoe UI", 20, "bold"),
            bg=self.color_primario,
            fg="white"
        )
        titulo.pack(pady=10)
        
        subtitulo = tk.Label(
            header_frame,
            text="Sistema de Turnos de Pádel - Administrador",
            font=("Segoe UI", 10),
            bg=self.color_primario,
            fg="white"
        )
        subtitulo.pack()
        
        # Contenedor principal
        main_frame = tk.Frame(self.root, bg=self.color_fondo)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Sección: Datos del cliente
        datos_frame = tk.LabelFrame(
            main_frame,
            text="  Datos del Cliente  ",
            font=("Segoe UI", 11, "bold"),
            bg=self.color_fondo,
            fg=self.color_texto
        )
        datos_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Nombre
        tk.Label(
            datos_frame,
            text="Nombre:",
            font=("Segoe UI", 10),
            bg=self.color_fondo,
            fg=self.color_texto
        ).grid(row=0, column=0, sticky=tk.W, padx=15, pady=10)
        
        self.entry_nombre = tk.Entry(
            datos_frame,
            font=("Segoe UI", 10),
            width=30
        )
        self.entry_nombre.grid(row=0, column=1, padx=15, pady=10, sticky=tk.W)
        
        # Apellido
        tk.Label(
            datos_frame,
            text="Apellido:",
            font=("Segoe UI", 10),
            bg=self.color_fondo,
            fg=self.color_texto
        ).grid(row=1, column=0, sticky=tk.W, padx=15, pady=10)
        
        self.entry_apellido = tk.Entry(
            datos_frame,
            font=("Segoe UI", 10),
            width=30
        )
        self.entry_apellido.grid(row=1, column=1, padx=15, pady=10, sticky=tk.W)
        
        # Email o Teléfono
        tk.Label(
            datos_frame,
            text="Email/Teléfono:",
            font=("Segoe UI", 10),
            bg=self.color_fondo,
            fg=self.color_texto
        ).grid(row=2, column=0, sticky=tk.W, padx=15, pady=10)
        
        self.entry_contacto = tk.Entry(
            datos_frame,
            font=("Segoe UI", 10),
            width=30
        )
        self.entry_contacto.grid(row=2, column=1, padx=15, pady=10, sticky=tk.W)
        
        # Sección: Tipo de plan
        plan_frame = tk.LabelFrame(
            main_frame,
            text="  Tipo de Plan  ",
            font=("Segoe UI", 11, "bold"),
            bg=self.color_fondo,
            fg=self.color_texto
        )
        plan_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Radio buttons para planes
        self.plan_var = tk.StringVar(value="mensual")
        
        planes = [
            ("Trial (15 días)", "trial", 15),
            ("Mensual (30 días)", "mensual", 30),
            ("Trimestral (90 días)", "trimestral", 90),
            ("Semestral (180 días)", "semestral", 180),
            ("Anual (365 días)", "anual", 365),
        ]
        
        for i, (texto, valor, dias) in enumerate(planes):
            rb = tk.Radiobutton(
                plan_frame,
                text=texto,
                variable=self.plan_var,
                value=valor,
                font=("Segoe UI", 10),
                bg=self.color_fondo,
                fg=self.color_texto,
                activebackground=self.color_fondo,
                command=lambda d=dias: self.actualizar_dias(d)
            )
            rb.grid(row=i//2, column=i%2, sticky=tk.W, padx=20, pady=5)
        
        # Plan personalizado
        custom_frame = tk.Frame(plan_frame, bg=self.color_fondo)
        custom_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=20, pady=5)
        
        rb_custom = tk.Radiobutton(
            custom_frame,
            text="Personalizada:",
            variable=self.plan_var,
            value="personalizada",
            font=("Segoe UI", 10),
            bg=self.color_fondo,
            fg=self.color_texto,
            activebackground=self.color_fondo,
            command=self.activar_custom
        )
        rb_custom.pack(side=tk.LEFT)
        
        self.entry_dias = tk.Entry(
            custom_frame,
            font=("Segoe UI", 10),
            width=10,
            state=tk.DISABLED
        )
        self.entry_dias.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            custom_frame,
            text="días",
            font=("Segoe UI", 10),
            bg=self.color_fondo,
            fg=self.color_texto
        ).pack(side=tk.LEFT)
        
        self.dias_actuales = 30
        
        # Frame para botones
        botones_frame = tk.Frame(main_frame, bg=self.color_fondo)
        botones_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Botón generar
        btn_generar = tk.Button(
            botones_frame,
            text="Generar Serial",
            font=("Segoe UI", 12, "bold"),
            bg=self.color_primario,
            fg="white",
            activebackground=self.color_secundario,
            activeforeground="white",
            cursor="hand2",
            command=self.generar_serial,
            height=2
        )
        btn_generar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Botón ver registros
        btn_registros = tk.Button(
            botones_frame,
            text="Ver Registros",
            font=("Segoe UI", 12, "bold"),
            bg="#FF9800",
            fg="white",
            activebackground="#F57C00",
            activeforeground="white",
            cursor="hand2",
            command=self.ver_registros,
            height=2
        )
        btn_registros.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Resultado
        resultado_frame = tk.LabelFrame(
            main_frame,
            text="  Serial Generado  ",
            font=("Segoe UI", 11, "bold"),
            bg=self.color_fondo,
            fg=self.color_texto
        )
        resultado_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_resultado = scrolledtext.ScrolledText(
            resultado_frame,
            font=("Courier New", 9),
            height=12,
            wrap=tk.WORD,
            bg="white"
        )
        self.text_resultado.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botón copiar
        btn_copiar = tk.Button(
            resultado_frame,
            text="Copiar Serial al Portapapeles",
            font=("Segoe UI", 10, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            activeforeground="white",
            cursor="hand2",
            command=self.copiar_serial
        )
        btn_copiar.pack(pady=(0, 10))
        
        self.serial_actual = ""
    
    def actualizar_dias(self, dias):
        self.dias_actuales = dias
        self.entry_dias.delete(0, tk.END)
        self.entry_dias.config(state=tk.DISABLED)
    
    def activar_custom(self):
        self.entry_dias.config(state=tk.NORMAL)
        self.entry_dias.focus()
    
    def guardar_registro(self, nombre, apellido, contacto, tipo, dias, serial, datos):
        """Guarda el registro del cliente y serial en un archivo JSON"""
        archivo_registro = os.path.join(base_path, "registro_clientes.json")

        # Cargar registros existentes (manejar archivo vacío o corrupto)
        registros = []
        if os.path.exists(archivo_registro):
            try:
                with open(archivo_registro, 'r', encoding='utf-8') as f:
                    registros = json.load(f)
                    if not isinstance(registros, list):
                        registros = []
            except json.JSONDecodeError:
                # Archivo vacío o contenido inválido -> reiniciar registros
                registros = []
            except Exception as e:
                messagebox.showerror("Error al leer registros", f"No se pudo leer el archivo de registros:\n{str(e)}")
                registros = []
        
        # Crear nuevo registro
        fecha_generacion = datetime.now()
        fecha_expiracion = fecha_generacion + timedelta(days=dias)
        
        nuevo_registro = {
            "id": len(registros) + 1,
            "nombre": nombre,
            "apellido": apellido,
            "nombre_completo": f"{nombre} {apellido}",
            "contacto": contacto,
            "tipo_plan": tipo,
            "dias": dias,
            "fecha_generacion": fecha_generacion.strftime('%Y-%m-%d %H:%M:%S'),
            "fecha_expiracion": fecha_expiracion.strftime('%Y-%m-%d'),
            "serial": serial,
            "serial_id": datos['serial_id'],
            "activo": True
        }
        
        registros.append(nuevo_registro)
        
        # Guardar registros
        with open(archivo_registro, 'w', encoding='utf-8') as f:
            json.dump(registros, f, indent=2, ensure_ascii=False)
    
    def generar_serial(self):
        # Validar nombre
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Por favor ingrese el nombre del cliente")
            self.entry_nombre.focus()
            return
        
        # Validar apellido
        apellido = self.entry_apellido.get().strip()
        if not apellido:
            messagebox.showerror("Error", "Por favor ingrese el apellido del cliente")
            self.entry_apellido.focus()
            return
        
        # Validar contacto
        contacto = self.entry_contacto.get().strip()
        if not contacto:
            messagebox.showerror("Error", "Por favor ingrese email o teléfono del cliente")
            self.entry_contacto.focus()
            return
        
        # Obtener tipo de plan
        tipo = self.plan_var.get()
        
        # Obtener días
        if tipo == "personalizada":
            try:
                dias = int(self.entry_dias.get())
                if dias <= 0:
                    messagebox.showerror("Error", "Los días deben ser mayor a 0")
                    return
            except ValueError:
                messagebox.showerror("Error", "Ingrese un número válido de días")
                return
        else:
            dias = self.dias_actuales
        
        try:
            # Generar serial con nombre completo
            nombre_completo = f"{nombre} {apellido}"
            serial, datos = self.manager.generar_serial(nombre_completo, dias, tipo)
            self.serial_actual = serial
            
            # Guardar registro del cliente
            self.guardar_registro(nombre, apellido, contacto, tipo, dias, serial, datos)
            
            # Calcular fecha de expiración
            fecha_exp = datetime.now() + timedelta(days=dias)
            
            # Mostrar resultado
            resultado = f"""
{'='*70}
SERIAL GENERADO EXITOSAMENTE
{'='*70}

INFORMACION DEL CLIENTE:
  Nombre:               {nombre} {apellido}
  Contacto:             {contacto}

INFORMACION DEL PLAN:
  Tipo de Plan:         {datos['tipo'].upper()}
  Duracion:             {dias} dias
  Fecha de Expiracion:  {fecha_exp.strftime('%d/%m/%Y')}
  Serial ID:            {datos['serial_id']}

{'='*70}
SERIAL (Copiar y enviar al cliente):
{'='*70}

{serial}

{'='*70}

INSTRUCCIONES PARA EL CLIENTE:
1. Abrir la aplicacion Sistema de Turnos de Padel
2. Hacer clic en el boton "Licencia"
3. Pegar el serial completo en el campo
4. Hacer clic en "Activar"
5. La licencia {datos['tipo'].upper()} se activara automaticamente

IMPORTANTE:
- Este serial solo puede usarse UNA VEZ
- Se vinculara al hardware de la PC del cliente
- No se puede compartir con otras personas

{'='*70}
"""
            
            self.text_resultado.delete(1.0, tk.END)
            self.text_resultado.insert(1.0, resultado)
            
            # Limpiar campos
            self.entry_nombre.delete(0, tk.END)
            self.entry_apellido.delete(0, tk.END)
            self.entry_contacto.delete(0, tk.END)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "Exito",
                f"Serial {datos['tipo'].upper()} generado correctamente!\n\n"
                f"Cliente: {nombre} {apellido}\n"
                f"Contacto: {contacto}\n"
                f"Duracion: {dias} dias\n\n"
                "El registro se guardo en 'registro_clientes.json'\n"
                "Usa el boton 'Copiar' para copiar el serial."
            )
            
        except Exception as e:
            # Guardar traceback en archivo de log para diagnóstico
            try:
                log_path = os.path.join(base_path, 'error_log.txt')
                with open(log_path, 'a', encoding='utf-8') as logf:
                    logf.write(f"[{datetime.now().isoformat()}] Error al generar serial:\n")
                    logf.write(traceback.format_exc())
                    logf.write("\n\n")
            except:
                pass

            # Mostrar mensaje más amigable al usuario
            messagebox.showerror(
                "Error",
                f"Error al generar serial:\n{str(e)}\n\nSe registró el detalle en 'error_log.txt' (carpeta de la app)."
            )
    
    def copiar_serial(self):
        if not self.serial_actual:
            messagebox.showwarning("Advertencia", "Primero genera un serial")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(self.serial_actual)
        self.root.update()
        
        messagebox.showinfo("Exito", "Serial copiado al portapapeles!")
    
    def ver_registros(self):
        """Abre una ventana con el historial de clientes"""
        archivo_registro = os.path.join(base_path, "registro_clientes.json")

        if not os.path.exists(archivo_registro):
            messagebox.showinfo("Registros", "Aun no hay clientes registrados")
            return

        # Cargar registros con manejo de errores
        try:
            with open(archivo_registro, 'r', encoding='utf-8') as f:
                registros = json.load(f)
        except Exception as e:
            messagebox.showerror("Error al leer registros", f"No se pudo leer el archivo de registros:\n{str(e)}")
            return
        
        if not registros:
            messagebox.showinfo("Registros", "Aun no hay clientes registrados")
            return
        
        # Crear ventana de registros
        ventana_registros = tk.Toplevel(self.root)
        ventana_registros.title("Registro de Clientes")
        ventana_registros.geometry("900x600")
        ventana_registros.configure(bg=self.color_fondo)
        
        # Header
        header = tk.Label(
            ventana_registros,
            text=f"Registro de Clientes ({len(registros)} clientes)",
            font=("Segoe UI", 16, "bold"),
            bg=self.color_primario,
            fg="white",
            height=2
        )
        header.pack(fill=tk.X)
        
        # Frame con scroll
        frame_contenedor = tk.Frame(ventana_registros, bg=self.color_fondo)
        frame_contenedor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(frame_contenedor)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget para mostrar registros
        text_registros = tk.Text(
            frame_contenedor,
            font=("Consolas", 9),
            bg="white",
            yscrollcommand=scrollbar.set,
            wrap=tk.NONE
        )
        text_registros.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_registros.yview)
        
        # Formato de tabla
        contenido = ""
        contenido += "="*120 + "\n"
        contenido += f"{'ID':<5} {'NOMBRE COMPLETO':<25} {'CONTACTO':<25} {'PLAN':<12} {'DIAS':<6} {'GENERADO':<20} {'EXPIRA':<12}\n"
        contenido += "="*120 + "\n"
        
        for reg in sorted(registros, key=lambda x: x['id'], reverse=True):
            contenido += f"{reg['id']:<5} "
            contenido += f"{reg['nombre_completo'][:24]:<25} "
            contenido += f"{reg['contacto'][:24]:<25} "
            contenido += f"{reg['tipo_plan'].upper():<12} "
            contenido += f"{reg['dias']:<6} "
            contenido += f"{reg['fecha_generacion']:<20} "
            contenido += f"{reg['fecha_expiracion']:<12}\n"
            contenido += "-"*120 + "\n"
        
        contenido += "\n\n"
        contenido += "DETALLES DE LOS ULTIMOS 5 CLIENTES:\n"
        contenido += "="*120 + "\n\n"
        
        for reg in sorted(registros, key=lambda x: x['id'], reverse=True)[:5]:
            contenido += f"ID: {reg['id']}\n"
            contenido += f"Cliente: {reg['nombre_completo']}\n"
            contenido += f"Contacto: {reg['contacto']}\n"
            contenido += f"Plan: {reg['tipo_plan'].upper()} ({reg['dias']} dias)\n"
            contenido += f"Generado: {reg['fecha_generacion']}\n"
            contenido += f"Expira: {reg['fecha_expiracion']}\n"
            contenido += f"Serial ID: {reg['serial_id']}\n"
            contenido += f"Serial: {reg['serial'][:50]}...\n"
            contenido += "-"*120 + "\n\n"
        
        text_registros.insert(1.0, contenido)
        text_registros.config(state=tk.DISABLED)
        
        # Botón cerrar
        btn_cerrar = tk.Button(
            ventana_registros,
            text="Cerrar",
            font=("Segoe UI", 10, "bold"),
            bg="#757575",
            fg="white",
            command=ventana_registros.destroy,
            cursor="hand2"
        )
        btn_cerrar.pack(pady=10)

def main():
    root = tk.Tk()
    app = GeneradorSerialesGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
