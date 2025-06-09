import customtkinter as ctk
import sqlite3
import sys
import traceback
import threading
import time
from tkinter import messagebox
import datetime
import serial
import serial.tools.list_ports
import uuid

COLOR_CUERPO_PRINCIPAL = "#f4f8f7"

class FormNuevoProceso(ctk.CTkFrame):
    def __init__(self, panel_principal, user_id):
        super().__init__(panel_principal, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.user_id = user_id
        self.serial_connection = None
        self.master_panel = panel_principal.master  # Acceso al MasterPanel
        
        self.proceso_en_ejecucion = False
        self.proceso_pausado = False
        self.fase_actual = 0
        self.tiempo_inicio_fase = 0
        self.tiempo_pausa = 0
        self.hilo_proceso = None
        self.fase_contador = 1
        self.fases_datos = {}
        self.valvulas_activas = {}
        self.notificaciones = []
        self.elementos = ["Al", "As", "Ga", "In", "N", "Mn", "Be", "Mg", "Si"]

        # Construir la interfaz primero
        self.validar_cmd = self.register(self.validar_entrada)
        self.construir_interfaz()

        # Configurar el puerto serial después de que la interfaz esté lista
        self.configurar_puerto_serial()

    def construir_interfaz(self):
        """Construye todos los elementos de la interfaz"""
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame superior para contenido principal
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill="both", expand=True)
        
        # Scrollable frame para las fases
        self.scrollable_frame = ctk.CTkFrame(self.top_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

        self.tabview = ctk.CTkTabview(self.scrollable_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.agregar_fase("Fase 1")

        # Frame para botones generales (altura fija)
        self.botones_generales_frame = ctk.CTkFrame(self.top_frame, height=50)
        self.botones_generales_frame.pack(fill="x", padx=10, pady=(5, 5))

        # Botones generales
        self.reiniciar_btn = ctk.CTkButton(
            self.botones_generales_frame, 
            text="⮌ Reiniciar Rutina", 
            fg_color="#D9534F", 
            command=self.reiniciar_rutina
        )
        self.reiniciar_btn.pack(side="right", padx=5)

        self.pausar_btn = ctk.CTkButton(
            self.botones_generales_frame, 
            text="⏸ Pausar Rutina", 
            fg_color="#F0AD4E",
            command=self.pausar_proceso,
            state="disabled"
        )
        self.pausar_btn.pack(side="right", padx=5)

        self.ejecutar_btn = ctk.CTkButton(
            self.botones_generales_frame, 
            text="▶ Ejecutar Rutina", 
            fg_color="#06918A", 
            command=self.iniciar_proceso
        )
        self.ejecutar_btn.pack(side="right", padx=5)

        # Frame para notificaciones (altura fija)
        self.notificaciones_frame = ctk.CTkFrame(self.top_frame, height=150)
        self.notificaciones_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Encabezado centrado
        header_frame = ctk.CTkFrame(self.notificaciones_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(5, 0))

        ctk.CTkLabel(
            header_frame, 
            text="NOTIFICACIONES", 
            font=("Arial", 16, "bold")
        ).pack(expand=True)

        self.notificaciones_text = ctk.CTkTextbox(self.notificaciones_frame, height=100, state="disabled")
        self.notificaciones_text.pack(fill="x", padx=5, pady=5)

        self.limpiar_btn = ctk.CTkButton(
            self.notificaciones_frame,
            text="LIMPIAR",
            fg_color="#6c757d",
            command=self.limpiar_notificaciones,
            width=100
        )
        self.limpiar_btn.pack(side="right", padx=5, pady=(0, 5))

    def agregar_notificacion(self, mensaje):
        """Agrega una notificación al panel de notificaciones"""
        self.notificaciones.append(mensaje)
        self.notificaciones_text.configure(state="normal")
        self.notificaciones_text.insert("end", f"- {mensaje}\n")
        self.notificaciones_text.configure(state="disabled")
        self.notificaciones_text.see("end")

    def limpiar_notificaciones(self):
        """Limpia todas las notificaciones"""
        self.notificaciones = []
        self.notificaciones_text.configure(state="normal")
        self.notificaciones_text.delete("1.0", "end")
        self.notificaciones_text.configure(state="disabled")

    def toggle_campos_valvula(self, switch, campos):
        """Habilita/deshabilita campos según estado del switch"""
        estado = switch.get()
        for campo in campos:
            if campo is not None:
                if hasattr(campo, 'configure'):
                    campo.configure(state="normal" if estado else "disabled")
                elif hasattr(campo, 'config'):
                    campo.config(state="normal" if estado else "disabled")

    def configurar_puerto_serial(self):
        """Configura el puerto serial automáticamente"""
        try:
            puertos = serial.tools.list_ports.comports()

            if not puertos:
                mensaje = "No se detectaron puertos seriales. Asegúrate de que la ESP32 esté conectada."
                messagebox.showwarning("Sin conexión", mensaje)
                self.agregar_notificacion(mensaje)
                print("No se detectaron puertos seriales.")
                return

            print("Puertos detectados:")
            for p in puertos:
                print(f"- {p.device}: {p.description}")

            for puerto in puertos:
                if 'USB' in puerto.description or 'Serial' in puerto.description or 'ESP' in puerto.description:
                    try:
                        self.serial_connection = serial.Serial(
                            port=puerto.device,
                            baudrate=115200,
                            timeout=1
                        )
                        mensaje = f"Conectado a {puerto.device}"
                        print(mensaje)
                        self.agregar_notificacion(mensaje)
                        return
                    except Exception as e:
                        print(f"No se pudo abrir {puerto.device}: {e}")

            mensaje = ("No se encontró un dispositivo ESP32.\n\n"
                      "Verifica que esté correctamente conectada y que el driver esté instalado.")
            messagebox.showerror("ESP32 no detectada", mensaje)
            self.agregar_notificacion("Error: ESP32 no detectada")
        except Exception as e:
            mensaje = f"No se pudo configurar el puerto serial: {str(e)}"
            messagebox.showerror("Error", mensaje)
            self.agregar_notificacion(f"Error serial: {str(e)}")
            print(f"Error al configurar el puerto serial: {e}")

    def validar_entrada(self, text):
        """Validación de entrada numérica"""
        if text == "":
            return True
        if text.isdigit():
            try:
                val = int(text)
                return val <= 9999
            except:
                return False
        return False

    def validar_tiempo(self, entry, unidad_menu):
        """Validación de tiempo de apertura/cierre"""
        try:
            valor = float(entry.get()) if entry.get() else 0
            unidad = unidad_menu.get()
            segundos = self.convertir_a_segundos(valor, unidad)

            if segundos > 9999:
                entry.configure(border_color="red")
            else:
                entry.configure(border_color="gray")
        except:
            entry.configure(border_color="red")

    def seleccionar_direccion(self, dir_var, btn_izq, btn_der, seleccion):
        """Control de selección de dirección"""
        dir_var.set(seleccion)
        btn_izq.configure(fg_color="#06918A" if seleccion == "I" else "#D3D3D3")
        btn_der.configure(fg_color="#06918A" if seleccion == "D" else "#D3D3D3")

    def convertir_a_segundos(self, valor, unidad):
        """Conversión de unidades de tiempo a segundos"""
        try:
            valor = float(valor)
            if unidad == "min":
                return int(valor * 60)
            elif unidad == "h":
                return int(valor * 3600)
            else:
                return int(valor)
        except:
            return 0

    def agregar_fase(self, nombre_fase=None):
        """Agrega una nueva fase al tabview"""
        if nombre_fase is None:
            self.fase_contador += 1
            nombre_fase = f"Fase {self.fase_contador}"

        self.tabview.add(nombre_fase)

        frame_fase = ctk.CTkFrame(self.tabview.tab(nombre_fase))
        frame_fase.pack(fill="both", expand=True, padx=10, pady=10)

        self.fases_datos[nombre_fase] = []

        # Encabezados
        header = ctk.CTkFrame(frame_fase)
        header.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(header, text="Válvula", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Apertura", width=80).pack(side="left", padx=(20,5))
        ctk.CTkLabel(header, text="Cierre", width=80).pack(side="left", padx=(30,5))
        ctk.CTkLabel(header, text="Ciclos", width=60).pack(side="left", padx=(40,5))
        ctk.CTkLabel(header, text="Dirección", width=100).pack(side="left", padx=(15,5))
        ctk.CTkLabel(header, text="Progreso", width=100).pack(side="left", padx=(5,5))

        for i, elemento in enumerate(self.elementos):
            fila = ctk.CTkFrame(frame_fase)
            fila.pack(fill="x", padx=5, pady=5)

            # Switch para activar/desactivar válvula
            switch = ctk.CTkSwitch(fila, text=elemento)
            switch.pack(side="left", padx=5)

            # Config de apertura
            apertura_frame = ctk.CTkFrame(fila)
            apertura_frame.pack(side="left", padx=5)
            apertura = ctk.CTkEntry(apertura_frame, width=50, validate="key", 
                                validatecommand=(self.validar_cmd, "%P"), state="disabled")
            apertura.pack(side="left")
            apertura_unidad = ctk.CTkOptionMenu(apertura_frame, values=["s", "min", "h"], width=50, state="disabled")
            apertura_unidad.set("s")
            apertura_unidad.pack(side="left", padx=5)
            apertura.bind("<KeyRelease>", lambda e, ent=apertura, unidad=apertura_unidad: 
                        self.validar_tiempo(ent, unidad))
            apertura_unidad.configure(command=lambda v, ent=apertura, unidad=apertura_unidad: 
                                    self.validar_tiempo(ent, unidad))

            # Config de cierre
            cierre_frame = ctk.CTkFrame(fila)
            cierre_frame.pack(side="left", padx=5)
            cierre = ctk.CTkEntry(cierre_frame, width=50, validate="key", 
                                validatecommand=(self.validar_cmd, "%P"), state="disabled")
            cierre.pack(side="left")
            cierre_unidad = ctk.CTkOptionMenu(cierre_frame, values=["s", "min", "h"], width=50, state="disabled")
            cierre_unidad.set("s")
            cierre_unidad.pack(side="left", padx=5)
            cierre.bind("<KeyRelease>", lambda e, ent=cierre, unidad=cierre_unidad: 
                    self.validar_tiempo(ent, unidad))
            cierre_unidad.configure(command=lambda v, ent=cierre, unidad=cierre_unidad: 
                                self.validar_tiempo(ent, unidad))

            # Config de ciclos
            ciclos = ctk.CTkEntry(fila, width=60, validate="key", 
                                validatecommand=(self.validar_cmd, "%P"), state="disabled")
            ciclos.pack(side="left", padx=5)

            # Config de dirección
            dir_var = ctk.StringVar(value="N")
            
            # Primero creamos ambos botones
            btn_izq = ctk.CTkButton(fila, text="⭯", width=40, state="disabled")
            btn_der = ctk.CTkButton(fila, text="⭮", width=40, state="disabled")
            
            # Luego configuramos los comandos
            btn_izq.configure(command=lambda v=dir_var, bi=btn_izq, bd=btn_der: self.seleccionar_direccion(v, bi, bd, "I"))
            btn_der.configure(command=lambda v=dir_var, bi=btn_izq, bd=btn_der: self.seleccionar_direccion(v, bi, bd, "D"))
            
            btn_izq.pack(side="left", padx=5)
            btn_der.pack(side="left", padx=5)

            # Progreso
            progreso = ctk.CTkLabel(fila, text="0/0", width=100)
            progreso.pack(side="left", padx=5)

            # Lista de campos a habilitar/deshabilitar
            campos_valvula = [
                apertura, apertura_unidad, 
                cierre, cierre_unidad, 
                ciclos, btn_izq, btn_der
            ]
            
            # Configurar comando para toggle de campos
            switch.configure(command=lambda s=switch, c=campos_valvula: self.toggle_campos_valvula(s, c))
            
            self.fases_datos[nombre_fase].append({
                'switch': switch,
                'dir_var': dir_var,
                'apertura': apertura,
                'apertura_unidad': apertura_unidad,
                'cierre': cierre,
                'cierre_unidad': cierre_unidad,
                'ciclos': ciclos,
                'progreso': progreso,
                'ciclos_completados': 0,
                'tiempo_transcurrido': 0,
                'btn_izq': btn_izq,
                'btn_der': btn_der,
                'elemento': elemento  # Guardamos el nombre del elemento
            })

        # Botones para agregar/eliminar fases
        botones_frame = ctk.CTkFrame(self.tabview.tab(nombre_fase))
        botones_frame.pack(side="bottom", pady=10)
        ctk.CTkButton(botones_frame, text="Agregar Fase", fg_color="#06918A",
                    command=self.agregar_fase).pack(side="right", padx=5)
        ctk.CTkButton(botones_frame, text="Eliminar Fase", fg_color="#D9534F",
                    command=lambda: self.eliminar_fase(nombre_fase)).pack(side="right", padx=5)

        self.tabview.set(nombre_fase)

    def eliminar_fase(self, nombre_fase):
        """Elimina una fase si no es la última"""
        if len(self.tabview._name_list) > 1:
            self.tabview.delete(nombre_fase)
            del self.fases_datos[nombre_fase]
            self.agregar_notificacion(f"Fase {nombre_fase} eliminada")
        else:
            messagebox.showwarning("Advertencia", "No puedes eliminar la última fase")
            self.agregar_notificacion("Intento de eliminar la última fase (no permitido)")

    def iniciar_proceso(self):
        """Inicia el proceso de ejecución de rutina"""
        try:
            if not self.proceso_en_ejecucion:
                # Confirmar bloqueo con el MasterPanel
                if not self.master_panel.verificar_ejecucion("nuevoproceso"):
                    return
                self.master_panel.activar_bloqueo_hardware("nuevoproceso")
                
                # Preparar datos de válvulas activas
                self.valvulas_activas = {}
                valvulas_configuradas = False
                
                for fase_idx, (nombre_fase, valvulas) in enumerate(self.fases_datos.items()):
                    for valvula_idx, valvula in enumerate(valvulas):
                        if valvula['switch'].get():
                            try:
                                tiempo = self.convertir_a_segundos(valvula['apertura'].get(), valvula['apertura_unidad'].get())
                                ciclos = int(valvula['ciclos'].get()) if valvula['ciclos'].get() else 0
                                
                                if tiempo > 0:
                                    valvulas_configuradas = True
                                    key = f"F{fase_idx+1}V{valvula_idx+1}"
                                    self.valvulas_activas[key] = {
                                        'fase': fase_idx,
                                        'valvula_idx': valvula_idx,
                                        'ciclos_totales': ciclos,
                                        'tiempo_ciclo': tiempo,
                                        'ciclos_completados': 0,
                                        'tiempo_transcurrido': 0,
                                        'progreso': valvula['progreso'],
                                        'elemento': valvula['elemento']
                                    }
                                    if ciclos > 0:
                                        valvula['progreso'].configure(text=f"0/{ciclos}")
                                        self.agregar_notificacion(f"Válvula {valvula['elemento']} en {nombre_fase}: {ciclos} ciclos configurados")
                                    else:
                                        valvula['progreso'].configure(text=f"T: {tiempo}s")
                                        self.agregar_notificacion(f"Válvula {valvula['elemento']} en {nombre_fase}: Tiempo {tiempo}s configurado")
                            except Exception as e:
                                print(f"Error al procesar válvula: {e}")
                                pass
            
                if not valvulas_configuradas:
                    mensaje = "Debe configurar al menos una válvula con tiempo de apertura válido"
                    messagebox.showwarning("Advertencia", mensaje)
                    self.agregar_notificacion(mensaje)
                    self.master_panel.liberar_bloqueo_hardware()
                    return
                
                if not self.enviar_cadena_serial():
                    self.master_panel.liberar_bloqueo_hardware()
                    return
                
                self.proceso_en_ejecucion = True
                self.proceso_pausado = False
                self.fase_actual = 0
                self.pausar_btn.configure(state="normal", text="Pausar Rutina")
                self.ejecutar_btn.configure(state="disabled")
                
                self.hilo_proceso = threading.Thread(target=self.ejecutar_proceso, daemon=True)
                self.hilo_proceso.start()
                
                mensaje = "Proceso iniciado correctamente"
                messagebox.showinfo("Éxito", mensaje)
                self.agregar_notificacion(mensaje)
        except Exception as e:
            self.master_panel.liberar_bloqueo_hardware()
            messagebox.showerror("Error", f"Error al iniciar proceso: {str(e)}")
            self.agregar_notificacion(f"Error al iniciar proceso: {str(e)}")

    def enviar_cadena_serial(self):
        try:
            if not self.master_panel.verificar_ejecucion("nuevoproceso"):
                return False
                
            self.master_panel.activar_bloqueo_hardware("nuevoproceso")
            
            proceso_id = str(uuid.uuid4())
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cadenas_fases = []
            
            for fase_idx, (nombre_fase, valvulas) in enumerate(self.fases_datos.items(), start=1):
                cadenas = []
                for valvula_idx, valvula in enumerate(valvulas, start=1):
                    if valvula['switch'].get():
                        tiempo = self.convertir_a_segundos(valvula['apertura'].get(), valvula['apertura_unidad'].get())
                        ciclos = valvula['ciclos'].get() if valvula['ciclos'].get() else 0
                        
                        # Construir datos para DB
                        datos = {
                            'proceso_id': proceso_id,
                            'fase': fase_idx,
                            'fecha_inicio': fecha_actual,
                            'fecha_fin': '',
                            'hora_instruccion': fecha_actual,
                            'valvula': f"Válvula {valvula['elemento']}",
                            'tiempo': tiempo,
                            'ciclos': ciclos,
                            'estado': 'A'
                        }
                        self.guardar_proceso_db(datos)
                    
                        # Resto del código para construir la cadena serial...
                        motor = f"M{valvula_idx}"
                        direccion = valvula['dir_var'].get()
                        ciclos_val = str(ciclos).zfill(4) if ciclos else "0000"
                        apertura_val = tiempo
                        cierre_val = self.convertir_a_segundos(valvula['cierre'].get(), valvula['cierre_unidad'].get())

                        apertura_str = str(min(apertura_val, 9999)).zfill(4)
                        cierre_str = str(min(cierre_val, 9999)).zfill(4)

                        if int(ciclos_val) > 0:
                            tarea = "B"
                        elif apertura_val > 0 and cierre_val > 0:
                            tarea = "C"
                        elif apertura_val > 0:
                            tarea = "A"
                        else:
                            tarea = "E"

                        cadena = f"{motor}{tarea}{direccion}{ciclos_val}{apertura_str}{cierre_str}"
                        cadenas.append(cadena)
        
                if cadenas:
                    fase_cadena = "".join(cadenas)
                    cadenas_fases.append(fase_cadena)

            # Unir todas las fases (separador = &)
            cadena_final = "&".join(cadenas_fases) if cadenas_fases else ""
            
            if cadena_final:
                print(f"Cadena a enviar: {cadena_final}")
                self.agregar_notificacion(f"Enviando instrucciones...")
                
                # Enviar por serial si hay conexión
                if self.serial_connection and self.serial_connection.is_open:
                    self.serial_connection.write(cadena_final.encode('utf-8'))
                    print("Cadena enviada a ESP32")
                    self.agregar_notificacion("Configuración enviada")
                    
                    # Esperar confirmación
                    time.sleep(0.1)
                    if self.serial_connection.in_waiting:
                        respuesta = self.serial_connection.readline().decode('utf-8').strip()
                        print(f"Respuesta ESP32: {respuesta}")
                        
                        if "OK" not in respuesta:
                            self.master_panel.liberar_bloqueo_hardware()
                            messagebox.showerror("Error", "El dispositivo no confirmó la recepción")
                            return False
                else:
                    self.master_panel.liberar_bloqueo_hardware()
                    messagebox.showerror("Error", "No hay conexión serial establecida")
                    return False
            
            return True
        except Exception as e:
            self.master_panel.liberar_bloqueo_hardware()
            messagebox.showerror("Error", f"No se pudo enviar la cadena: {str(e)}")
            self.agregar_notificacion("Error al enviar instrucciones")
            print(f"Error detallado: {traceback.format_exc()}")
            return False

    def pausar_proceso(self):
        """Pausa o reanuda el proceso"""
        if self.proceso_en_ejecucion:
            self.proceso_pausado = not self.proceso_pausado
            if self.proceso_pausado:
                self.tiempo_pausa = time.time()
                self.pausar_btn.configure(text="Reanudar Rutina")
                self.agregar_notificacion("Proceso pausado")
                
                # Enviar comando de pausa a ESP32
                if self.serial_connection and self.serial_connection.is_open:
                    self.serial_connection.write(b"XXXXXXXXXXXXXXXX")  # Comando de pausa
                    print("Comando de pausa enviado a ESP32 = XXXXXXXXXXXXXXXX")
                    self.master_panel.liberar_bloqueo_hardware()
            else:
                self.tiempo_inicio_fase += time.time() - self.tiempo_pausa
                self.pausar_btn.configure(text="Pausar Rutina")
                self.agregar_notificacion("Proceso reanudado")
                
                # Enviar comando de reanudar a ESP32
                if self.serial_connection and self.serial_connection.is_open:
                    if self.master_panel.verificar_ejecucion("nuevoproceso"):
                        self.master_panel.activar_bloqueo_hardware("nuevoproceso")
                        self.serial_connection.write(b"YYYYYYYYYYYYYYYY") # Comando de reanudar
                        print("Comando para reanudar enviado a ESP32 = YYYYYYYYYYYYYYYY")

    def reiniciar_rutina(self):
        """Reinicia completamente la rutina"""
        if self.proceso_en_ejecucion:
            self.proceso_en_ejecucion = False
            if self.hilo_proceso and self.hilo_proceso.is_alive():
                self.hilo_proceso.join(timeout=1)
            
            # Enviar comando de detener a ESP32
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.write(b"PPPPPPPPPPPPPPPP")
                self.agregar_notificacion("Proceso detenido")
                self.master_panel.liberar_bloqueo_hardware()
        
        self.proceso_pausado = False
        self.pausar_btn.configure(text="Pausar Rutina", state="disabled")
        self.ejecutar_btn.configure(state="normal")
        
        # Reiniciar contadores y estados
        for fase, valvulas in self.fases_datos.items():
            for valvula in valvulas:
                valvula['progreso'].configure(text="0/0")
                valvula['ciclos_completados'] = 0
        
        # Eliminar fases adicionales
        for nombre_fase in list(self.fases_datos.keys())[1:]:
            self.tabview.delete(nombre_fase)
            del self.fases_datos[nombre_fase]

        self.fase_contador = 1
        self.fase_actual = 0

        # Reset de la primera fase
        primera_fase = list(self.fases_datos.keys())[0]
        for valvula in self.fases_datos[primera_fase]:
            valvula['switch'].deselect()
            valvula['dir_var'].set("N")
            valvula['apertura'].delete(0, "end")
            valvula['cierre'].delete(0, "end")
            valvula['ciclos'].delete(0, "end")
            valvula['progreso'].configure(text="0/0")
            valvula['ciclos_completados'] = 0
            # Deshabilitar campos
            self.toggle_campos_valvula(valvula['switch'], [
                valvula['apertura'], valvula['apertura_unidad'],
                valvula['cierre'], valvula['cierre_unidad'],
                valvula['ciclos'], valvula['btn_izq'], valvula['btn_der']
            ])
        
        # Liberar bloqueo
        self.master_panel.liberar_bloqueo_hardware()


    def guardar_proceso_db(self, datos_proceso):
        """Guarda los datos del proceso en la base de datos"""
        conn = None
        try:
            conn = sqlite3.connect("procesos.db")
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='procesos'")
            if not cursor.fetchone():
                # Crear tabla nueva con todas las columnas
                cursor.execute('''CREATE TABLE procesos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            proceso_id TEXT,
                            fecha_inicio TEXT,
                            fecha_fin TEXT,
                            hora_instruccion TEXT,
                            valvula_activada TEXT,
                            tiempo_valvula INTEGER,
                            ciclos INTEGER,
                            estado_valvula TEXT,
                            fase INTEGER DEFAULT 1,
                            tipo_proceso TEXT)''')
                print("Tabla 'procesos' creada con la nueva estructura")
            else:
                # Verificar columnas existentes
                cursor.execute("PRAGMA table_info(procesos)")
                columnas_existentes = [col[1] for col in cursor.fetchall()]
                
                # Añadir columnas faltantes
                columnas_faltantes = {
                    'proceso_id': 'TEXT',
                    'fase': 'INTEGER DEFAULT 1',
                    'tipo_proceso': 'TEXT'
                }
                
                for columna, tipo in columnas_faltantes.items():
                    if columna not in columnas_existentes:
                        try:
                            cursor.execute(f"ALTER TABLE procesos ADD COLUMN {columna} {tipo}")
                            print(f"Columna {columna} añadida a la tabla existente")
                        except sqlite3.OperationalError as e:
                            print(f"Error al añadir columna {columna}: {e}")
            
            tipo_proceso = 'ciclico' if int(datos_proceso.get('ciclos', 0)) > 0 else 'puntual'
            
            cursor.execute('''INSERT INTO procesos 
                        (user_id, proceso_id, fecha_inicio, fecha_fin, hora_instruccion, 
                            valvula_activada, tiempo_valvula, ciclos, estado_valvula, fase, tipo_proceso)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (self.user_id,
                        datos_proceso.get('proceso_id', ''),
                        datos_proceso['fecha_inicio'],
                        datos_proceso.get('fecha_fin', ''),
                        datos_proceso['hora_instruccion'],
                        datos_proceso['valvula'],
                        datos_proceso['tiempo'],
                        datos_proceso.get('ciclos', 0),
                        datos_proceso['estado'],
                        datos_proceso.get('fase', 1),
                        tipo_proceso))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error de SQLite al guardar en DB: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado al guardar en DB: {e}")
            return False
        finally:
            if conn:
                conn.close()  

    def __del__(self):
        """Cierra la conexión serial y libera recursos al destruir el objeto"""
        # Liberar bloqueo primero
        if hasattr(self, 'master_panel'):
            self.master_panel.liberar_bloqueo_hardware()
        
        # Detener cualquier proceso en ejecución
        if hasattr(self, 'proceso_en_ejecucion') and self.proceso_en_ejecucion:
            self.proceso_en_ejecucion = False
            if hasattr(self, 'hilo_proceso') and self.hilo_proceso and self.hilo_proceso.is_alive():
                self.hilo_proceso.join(timeout=1)
        
        # Cerrar conexión serial
        if hasattr(self, 'serial_connection') and self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Conexión serial cerrada en NuevoProceso")