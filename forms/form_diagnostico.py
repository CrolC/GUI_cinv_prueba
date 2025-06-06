import customtkinter as ctk
import serial.tools.list_ports
import threading
import time
from tkinter import messagebox

class FormDiagnostico(ctk.CTkFrame):
    def __init__(self, panel_principal, user_id):
        super().__init__(panel_principal)
        self.user_id = user_id
        self.serial_connection = None
        self.configure(fg_color="#f4f8f7")
        self.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Variables de estado
        self.estado_micro = "rojo"  # rojo/amarillo/verde
        self.modo_proceso = "Inactivo"  # Automático/Semiautomático/Inactivo
        self.estado_proceso = "Inactivo"  # En espera/En ejecución/Inactivo
        self.valvulas_estado = {
            'Al': {'estado': 'C', 'tiempo': 0},
            'As': {'estado': 'C', 'tiempo': 0},
            'Ga': {'estado': 'C', 'tiempo': 0},
            'In': {'estado': 'C', 'tiempo': 0},
            'N': {'estado': 'C', 'tiempo': 0},
            'Mn': {'estado': 'C', 'tiempo': 0},
            'Be': {'estado': 'C', 'tiempo': 0},
            'Mg': {'estado': 'C', 'tiempo': 0},
            'Si': {'estado': 'C', 'tiempo': 0}
        }
        
        # Configurar interfaz
        self._crear_interfaz()
        
        # Iniciar hilo de monitoreo
        self.monitorear_estado()

    def _crear_interfaz(self):
        """Crea la interfaz con los tres frames principales"""
        # Frame principal con grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # FRAME 1 - Estado de las válvulas
        self.frame_valvulas = ctk.CTkFrame(self)
        self.frame_valvulas.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self._crear_frame_valvulas()
        
        # Frame contenedor para frames 2 y 3
        self.frame_derecha = ctk.CTkFrame(self)
        self.frame_derecha.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.frame_derecha.grid_columnconfigure(0, weight=1)
        self.frame_derecha.grid_rowconfigure(0, weight=1)
        self.frame_derecha.grid_rowconfigure(1, weight=1)
        
        # FRAME 2 - Estado del microcontrolador
        self.frame_micro = ctk.CTkFrame(self.frame_derecha)
        self.frame_micro.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self._crear_frame_micro()
        
        # FRAME 3 - Estado del proceso
        self.frame_proceso = ctk.CTkFrame(self.frame_derecha)
        self.frame_proceso.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self._crear_frame_proceso()

    def _crear_frame_valvulas(self):
        """Crea el frame con el estado de las válvulas"""
        # Encabezados
        header_frame = ctk.CTkFrame(self.frame_valvulas)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.frame_valvulas, text="Estado del Microcontrolador", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkLabel(header_frame, text="⏳ Tiempo").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="🔓 Abierto").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="🔒 Cerrado").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Válvula").pack(side="left", padx=10)
        
        # Contenedor para las válvulas
        self.valvulas_container = ctk.CTkScrollableFrame(self.frame_valvulas)
        self.valvulas_container.pack(fill="both", expand=True)
        
        # Elementos para cada válvula
        self.valvula_widgets = {}
        for elemento in ['Al', 'As', 'Ga', 'In', 'N', 'Mn', 'Be', 'Mg', 'Si']:
            frame = ctk.CTkFrame(self.valvulas_container)
            frame.pack(fill="x", pady=2)
            
            # Tiempo
            tiempo_label = ctk.CTkLabel(frame, text="0000", width=60)
            tiempo_label.pack(side="left", padx=5)
            
            # LED Abierto (verde)
            led_abierto = ctk.CTkLabel(frame, text="", width=20, height=20, corner_radius=10)
            led_abierto.pack(side="left", padx=5)
            
            # LED Cerrado (gris)
            led_cerrado = ctk.CTkLabel(frame, text="", width=20, height=20, corner_radius=10)
            led_cerrado.pack(side="left", padx=5)
            
            # Nombre válvula
            ctk.CTkLabel(frame, text=elemento).pack(side="left", padx=5)
            
            self.valvula_widgets[elemento] = {
                'tiempo': tiempo_label,
                'led_abierto': led_abierto,
                'led_cerrado': led_cerrado
            }
        
        # Botón de actualización manual
        ctk.CTkButton(
            self.frame_valvulas, 
            text="Actualizar Estados", 
            command=self.actualizar_estados_valvulas
        ).pack(side="bottom", pady=10)

    def _crear_frame_micro(self):
        """Crea el frame con el estado del microcontrolador"""
        ctk.CTkLabel(self.frame_micro, text="Estado del Microcontrolador", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Semaforo
        self.semaforo_micro = ctk.CTkFrame(self.frame_micro)
        self.semaforo_micro.pack(pady=10)
        
        self.led_rojo_micro = ctk.CTkLabel(self.semaforo_micro, text="", width=30, height=30, corner_radius=15, fg_color="red")
        self.led_rojo_micro.pack(pady=2)
        
        self.led_amarillo_micro = ctk.CTkLabel(self.semaforo_micro, text="", width=30, height=30, corner_radius=15, fg_color="gray")
        self.led_amarillo_micro.pack(pady=2)
        
        self.led_verde_micro = ctk.CTkLabel(self.semaforo_micro, text="", width=30, height=30, corner_radius=15, fg_color="gray")
        self.led_verde_micro.pack(pady=2)
        
        # Descripción estados
        desc_frame = ctk.CTkFrame(self.frame_micro, fg_color="transparent")
        desc_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(desc_frame, text="🔴 No hay conexión").pack(anchor="w")
        ctk.CTkLabel(desc_frame, text="🟡 Instrucciones enviadas").pack(anchor="w")
        ctk.CTkLabel(desc_frame, text="🟢 Confirmación recibida").pack(anchor="w")
        
        # Botón de prueba de conexión
        ctk.CTkButton(
            self.frame_micro, 
            text="Probar Conexión", 
            command=self.probar_conexion
        ).pack(pady=10)

    def _crear_frame_proceso(self):
        """Crea el frame con el estado del proceso"""
        ctk.CTkLabel(self.frame_proceso, text="Estado del Proceso", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Modo de trabajo
        self.modo_label = ctk.CTkLabel(self.frame_proceso, text="Modo: Inactivo")
        self.modo_label.pack(pady=5)
        
        # Semaforo estado
        self.semaforo_proceso = ctk.CTkFrame(self.frame_proceso)
        self.semaforo_proceso.pack(pady=10)
        
        self.led_rojo_proceso = ctk.CTkLabel(self.semaforo_proceso, text="", width=30, height=30, corner_radius=15, fg_color="red")
        self.led_rojo_proceso.pack(pady=2)
        
        self.led_amarillo_proceso = ctk.CTkLabel(self.semaforo_proceso, text="", width=30, height=30, corner_radius=15, fg_color="gray")
        self.led_amarillo_proceso.pack(pady=2)
        
        self.led_verde_proceso = ctk.CTkLabel(self.semaforo_proceso, text="", width=30, height=30, corner_radius=15, fg_color="gray")
        self.led_verde_proceso.pack(pady=2)
        
        # Descripción estados
        desc_frame = ctk.CTkFrame(self.frame_proceso, fg_color="transparent")
        desc_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(desc_frame, text="🔴 Inactivo").pack(anchor="w")
        ctk.CTkLabel(desc_frame, text="🟡 En espera").pack(anchor="w")
        ctk.CTkLabel(desc_frame, text="🟢 En ejecución").pack(anchor="w")
        
        # Botón de actualización
        ctk.CTkButton(
            self.frame_proceso, 
            text="Actualizar Estado", 
            command=self.actualizar_estado_proceso
        ).pack(pady=10)

    def actualizar_estados_valvulas(self):
        """Actualiza la visualización del estado de las válvulas"""
        for elemento, widgets in self.valvula_widgets.items():
            estado = self.valvulas_estado[elemento]['estado']
            tiempo = self.valvulas_estado[elemento]['tiempo']
            
            widgets['tiempo'].configure(text=f"{tiempo:04d}")
            
            if estado == 'A':
                widgets['led_abierto'].configure(fg_color="green")
                widgets['led_cerrado'].configure(fg_color="gray")
            else:
                widgets['led_abierto'].configure(fg_color="gray")
                widgets['led_cerrado'].configure(fg_color="gray")  # Originalmente sería gris para cerrado

    def actualizar_estado_micro(self):
        """Actualiza el semáforo del microcontrolador"""
        self.led_rojo_micro.configure(fg_color="gray")
        self.led_amarillo_micro.configure(fg_color="gray")
        self.led_verde_micro.configure(fg_color="gray")
        
        if self.estado_micro == "rojo":
            self.led_rojo_micro.configure(fg_color="red")
        elif self.estado_micro == "amarillo":
            self.led_amarillo_micro.configure(fg_color="yellow")
        elif self.estado_micro == "verde":
            self.led_verde_micro.configure(fg_color="green")

    def actualizar_estado_proceso(self):
        """Actualiza el estado del proceso"""
        self.modo_label.configure(text=f"Modo: {self.modo_proceso}")
        
        self.led_rojo_proceso.configure(fg_color="gray")
        self.led_amarillo_proceso.configure(fg_color="gray")
        self.led_verde_proceso.configure(fg_color="gray")
        
        if self.estado_proceso == "Inactivo":
            self.led_rojo_proceso.configure(fg_color="red")
        elif self.estado_proceso == "En espera":
            self.led_amarillo_proceso.configure(fg_color="yellow")
        elif self.estado_proceso == "En ejecución":
            self.led_verde_proceso.configure(fg_color="green")

    def probar_conexion(self):
        """Intenta establecer conexión con la ESP32"""
        try:
            puertos = serial.tools.list_ports.comports()
            if not puertos:
                self.estado_micro = "rojo"
                messagebox.showwarning("Sin conexión", "No se detectaron puertos seriales.")
            else:
                for puerto in puertos:
                    if 'USB' in puerto.description or 'Serial' in puerto.description or 'ESP' in puerto.description:
                        try:
                            self.serial_connection = serial.Serial(port=puerto.device, baudrate=115200, timeout=1)
                            self.estado_micro = "amarillo"
                            
                            # Simular respuesta de la ESP32 (en un caso real esto vendría del puerto serial)
                            threading.Thread(target=self.simular_respuesta_esp32).start()
                            
                            break
                        except Exception as e:
                            print(f"No se pudo abrir {puerto.device}: {e}")
                            self.estado_micro = "rojo"
                else:
                    self.estado_micro = "rojo"
                    messagebox.showerror("Error", "No se encontró un dispositivo ESP32 conectado.")
        except Exception as e:
            self.estado_micro = "rojo"
            messagebox.showerror("Error", f"No se pudo configurar el puerto serial: {str(e)}")
        
        self.actualizar_estado_micro()

    def simular_respuesta_esp32(self):
        """Simula la respuesta de la ESP32 después de un tiempo"""
        time.sleep(2)  # Simular demora en la respuesta
        self.estado_micro = "verde"
        self.after(0, self.actualizar_estado_micro)
        
        # Simular actualización de estado de válvulas
        for elemento in self.valvulas_estado:
            self.valvulas_estado[elemento]['estado'] = 'A' if elemento in ['Al', 'Ga'] else 'C'
            self.valvulas_estado[elemento]['tiempo'] = 1234 if elemento in ['Al', 'Ga'] else 0
        
        self.after(0, self.actualizar_estados_valvulas)

    def monitorear_estado(self):
        """Hilo para monitorear constantemente el estado del sistema"""
        #SIMULACIÓN
        
        # Cambiar modo de proceso cada 10 segundos (simulación)
        def cambiar_modo():
            modos = ["Automático", "Semiautomático", "Inactivo"]
            estados = ["En espera", "En ejecución", "Inactivo"]
            
            while True:
                for modo in modos:
                    self.modo_proceso = modo
                    self.after(0, self.actualizar_estado_proceso)
                    
                    for estado in estados:
                        self.estado_proceso = estado
                        self.after(0, self.actualizar_estado_proceso)
                        time.sleep(5)
        
        threading.Thread(target=cambiar_modo, daemon=True).start()

    def __del__(self):
        """Cierra la conexión serial al destruir el objeto"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()