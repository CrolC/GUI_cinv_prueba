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

COLOR_CUERPO_PRINCIPAL = "#f4f8f7"

class FormNuevoProceso(ctk.CTkFrame):
    def __init__(self, panel_principal, user_id):
        super().__init__(panel_principal, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.user_id = user_id
        self.serial_connection = None  # Conexión serial
        self.pack(fill="both", expand=True) 
        
        self.proceso_en_ejecucion = False
        self.proceso_pausado = False
        self.fase_actual = 0
        self.tiempo_inicio_fase = 0
        self.tiempo_pausa = 0
        self.hilo_proceso = None
        self.fase_contador = 1
        self.fases_datos = {}
        self.valvulas_activas = {}

        
        self.configurar_puerto_serial()

        
        self.validar_cmd = self.register(self.validar_entrada)

        
        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

        self.tabview = ctk.CTkTabview(self.scrollable_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.agregar_fase("Fase 1")

        
        self.botones_generales_frame = ctk.CTkFrame(self.main_frame)
        self.botones_generales_frame.pack(fill="x", padx=10, pady=(0, 10))

        #Btn reiniciar
        self.reiniciar_btn = ctk.CTkButton(
            self.botones_generales_frame, 
            text="Reiniciar Rutina", 
            fg_color="#D9534F", 
            command=self.reiniciar_rutina
        )
        self.reiniciar_btn.pack(side="right", padx=5)

        # Btn pausar
        self.pausar_btn = ctk.CTkButton(
            self.botones_generales_frame, 
            text="Pausar Rutina", 
            fg_color="#F0AD4E",
            command=self.pausar_proceso,
            state="disabled"
        )
        self.pausar_btn.pack(side="right", padx=5)

        # Btn ejecutar
        self.ejecutar_btn = ctk.CTkButton(
            self.botones_generales_frame, 
            text="Ejecutar Rutina", 
            fg_color="#06918A", 
            command=self.iniciar_proceso
        )
        self.ejecutar_btn.pack(side="right", padx=5)


    def configurar_puerto_serial(self):
        """Configura el puerto serial automáticamente"""
        try:
            puertos = serial.tools.list_ports.comports()

            if not puertos:
                messagebox.showwarning("Sin conexión", "No se detectaron puertos seriales. Asegúrate de que la ESP32 esté conectada.")
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
                        print(f"Conectado a {puerto.device}")
                        return
                    except Exception as e:
                        print(f"No se pudo abrir {puerto.device}: {e}")

            
            messagebox.showerror("ESP32 no detectada", 
                "No se encontró un dispositivo ESP32.\n\n"
                "Verifica que esté correctamente conectada y que el driver esté instalado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo configurar el puerto serial: {str(e)}")
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

        elementos = ["Al", "As", "Ga", "I", "N", "Mn", "Be", "Mg", "Si"]
        self.fases_datos[nombre_fase] = []

        #Encabezados
        header = ctk.CTkFrame(frame_fase)
        header.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(header, text="Válvula", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Apertura", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Cierre", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Ciclos", width=60).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Dirección", width=100).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Progreso", width=100).pack(side="left", padx=5)

        for i, elemento in enumerate(elementos):
            fila = ctk.CTkFrame(frame_fase)
            fila.pack(fill="x", padx=5, pady=5)

            # Switch para activar/desactivar válvula
            switch = ctk.CTkSwitch(fila, text=elemento)
            switch.pack(side="left", padx=5)

            # Config de apertura
            apertura_frame = ctk.CTkFrame(fila)
            apertura_frame.pack(side="left", padx=5)
            apertura = ctk.CTkEntry(apertura_frame, width=50, validate="key", 
                                  validatecommand=(self.validar_cmd, "%P"))
            apertura.pack(side="left")
            apertura_unidad = ctk.CTkOptionMenu(apertura_frame, values=["s", "min", "h"], width=50)
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
                                 validatecommand=(self.validar_cmd, "%P"))
            cierre.pack(side="left")
            cierre_unidad = ctk.CTkOptionMenu(cierre_frame, values=["s", "min", "h"], width=50)
            cierre_unidad.set("s")
            cierre_unidad.pack(side="left", padx=5)
            cierre.bind("<KeyRelease>", lambda e, ent=cierre, unidad=cierre_unidad: 
                       self.validar_tiempo(ent, unidad))
            cierre_unidad.configure(command=lambda v, ent=cierre, unidad=cierre_unidad: 
                                  self.validar_tiempo(ent, unidad))

            # Config de ciclos
            ciclos = ctk.CTkEntry(fila, width=60, validate="key", 
                                validatecommand=(self.validar_cmd, "%P"))
            ciclos.pack(side="left", padx=5)

            # Config de dirección
            dir_var = ctk.StringVar(value="N")
            btn_izq = ctk.CTkButton(fila, text="I", width=40, 
                                   command=lambda v=dir_var: self.seleccionar_direccion(v, btn_izq, btn_der, "I"))
            btn_der = ctk.CTkButton(fila, text="D", width=40, 
                                   command=lambda v=dir_var: self.seleccionar_direccion(v, btn_izq, btn_der, "D"))
            btn_izq.pack(side="left", padx=5)
            btn_der.pack(side="left", padx=5)

            
            progreso = ctk.CTkLabel(fila, text="0/0", width=100)
            progreso.pack(side="left", padx=5)

            
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
                'tiempo_transcurrido': 0
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
        else:
            messagebox.showwarning("Advertencia", "No puedes eliminar la última fase")

    def iniciar_proceso(self):
        """Inicia el proceso de ejecución de rutina"""
        if not self.proceso_en_ejecucion:
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
                                    'progreso': valvula['progreso']
                                }
                                if ciclos > 0:
                                    valvula['progreso'].configure(text=f"0/{ciclos}")
                                else:
                                    valvula['progreso'].configure(text=f"T: {tiempo}s")
                        except Exception as e:
                            print(f"Error al procesar válvula: {e}")
                            pass
        
            if not valvulas_configuradas:
                messagebox.showwarning("Advertencia", "Debe configurar al menos una válvula con tiempo de apertura válido")
                return
            
            if not self.enviar_cadena_serial():
                return
            
            self.proceso_en_ejecucion = True
            self.proceso_pausado = False
            self.fase_actual = 0
            self.pausar_btn.configure(state="normal", text="Pausar Rutina")
            self.ejecutar_btn.configure(state="disabled")
            
            self.hilo_proceso = threading.Thread(target=self.ejecutar_proceso, daemon=True)
            self.hilo_proceso.start()
            
            messagebox.showinfo("Éxito", "Proceso iniciado correctamente")

    def enviar_cadena_serial(self):
        """Envía la cadena de comandos al dispositivo ESP32 por serial"""
        try:
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cadenas_fases = []
        
            for fase_idx, (nombre_fase, valvulas) in enumerate(self.fases_datos.items()):
                cadenas = []
                for valvula_idx, valvula in enumerate(valvulas, start=1):
                    if valvula['switch'].get():
                        # Construir datos para DB
                        tiempo = self.convertir_a_segundos(valvula['apertura'].get(), valvula['apertura_unidad'].get())
                        ciclos = valvula['ciclos'].get() if valvula['ciclos'].get() else 0
                        
                        datos = {
                            'fecha_inicio': fecha_actual,
                            'fecha_fin': '',
                            'hora_instruccion': fecha_actual,
                            'valvula': f"Válvula {valvula_idx}",
                            'tiempo': tiempo,
                            'ciclos': ciclos,
                            'estado': 'A'
                        }
                        self.guardar_proceso_db(datos)
                    
                        # Construir cadena para ESP32
                        motor = f"M{valvula_idx}"
                        direccion = valvula['dir_var'].get()
                        ciclos_val = valvula['ciclos'].get().zfill(4) if valvula['ciclos'].get() else "0000"
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
                
                # Enviar por serial si hay conexión
                if self.serial_connection and self.serial_connection.is_open:
                    self.serial_connection.write(cadena_final.encode('utf-8'))
                    print("Cadena enviada a ESP32")
                    
                    # Esperar confirmación
                    time.sleep(0.1)
                    if self.serial_connection.in_waiting:
                        respuesta = self.serial_connection.readline().decode('utf-8').strip()
                        print(f"Respuesta ESP32: {respuesta}")
                        
                        if "OK" not in respuesta:
                            messagebox.showerror("Error", "El dispositivo no confirmó la recepción")
                            return False
                else:
                    messagebox.showerror("Error", "No hay conexión serial establecida")
                    return False
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar la cadena: {str(e)}")
            print(f"Error detallado: {traceback.format_exc()}")
            return False

    def ejecutar_proceso(self):
        """Ejecuta el proceso fase por fase"""
        while self.fase_actual < len(self.fases_datos) and self.proceso_en_ejecucion:
            # Obtener válvulas activas de esta fase
            valvulas_fase = {k: v for k, v in self.valvulas_activas.items() if v['fase'] == self.fase_actual}
            
            if not valvulas_fase:
                self.fase_actual += 1
                continue
            
            # Iniciar tiempo de fase
            self.tiempo_inicio_fase = time.time()
            tiempo_pausa = 0
            fase_completada = False
            
            while not fase_completada and self.proceso_en_ejecucion:
                if self.proceso_pausado:
                    tiempo_pausa = time.time()
                    while self.proceso_pausado and self.proceso_en_ejecucion:
                        time.sleep(0.1)
                    if not self.proceso_en_ejecucion:
                        break
                    
                    self.tiempo_inicio_fase += time.time() - tiempo_pausa
                
                # Calcular tiempo transcurrido en esta fase
                tiempo_actual = time.time()
                tiempo_transcurrido_fase = tiempo_actual - self.tiempo_inicio_fase
                
                # Actualizar todas las válvulas de esta fase
                fase_completada = True
                for key, valvula in valvulas_fase.items():
                    if valvula['ciclos_totales'] > 0:  # Válvula con ciclos
                        if valvula['ciclos_completados'] < valvula['ciclos_totales']:
                            ciclos_completos = int(tiempo_transcurrido_fase / valvula['tiempo_ciclo'])
                            ciclos_completos = min(ciclos_completos, valvula['ciclos_totales'])
                            
                            if ciclos_completos > valvula['ciclos_completados']:
                                valvula['ciclos_completados'] = ciclos_completos
                                valvula['progreso'].configure(text=f"{ciclos_completos}/{valvula['ciclos_totales']}")
                            
                            if valvula['ciclos_completados'] < valvula['ciclos_totales']:
                                fase_completada = False
                    else:  # Válvula sin ciclos (solo tiempo)
                        if tiempo_transcurrido_fase < valvula['tiempo_ciclo']:
                            tiempo_restante = max(0, valvula['tiempo_ciclo'] - tiempo_transcurrido_fase)
                            valvula['progreso'].configure(text=f"T: {int(tiempo_restante)}s")
                            fase_completada = False
                        else:
                            valvula['progreso'].configure(text="Completado")
                
                time.sleep(0.1)
            
            if fase_completada:
                self.fase_actual += 1
        
        # Finalizar proceso
        if self.proceso_en_ejecucion:
            self.proceso_en_ejecucion = False
            self.ejecutar_btn.configure(state="normal")
            self.pausar_btn.configure(state="disabled")
            messagebox.showinfo("Éxito", "Proceso completado correctamente")

    def pausar_proceso(self):
        """Pausa o reanuda el proceso"""
        if self.proceso_en_ejecucion:
            self.proceso_pausado = not self.proceso_pausado
            if self.proceso_pausado:
                self.tiempo_pausa = time.time()
                self.pausar_btn.configure(text="Reanudar Rutina")
                
                # Enviar comando de pausa a ESP32
                if self.serial_connection and self.serial_connection.is_open:
                    self.serial_connection.write(b"PAUSE")
            else:
                self.tiempo_inicio_fase += time.time() - self.tiempo_pausa
                self.pausar_btn.configure(text="Pausar Rutina")
                
                # Enviar comando de reanudar a ESP32
                if self.serial_connection and self.serial_connection.is_open:
                    self.serial_connection.write(b"RESUME")

    def reiniciar_rutina(self):
        """Reinicia completamente la rutina"""
        if self.proceso_en_ejecucion:
            self.proceso_en_ejecucion = False
            if self.hilo_proceso and self.hilo_proceso.is_alive():
                self.hilo_proceso.join(timeout=1)
            
            # Enviar comando de detener a ESP32
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.write(b"STOP")
        
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

    def guardar_proceso_db(self, datos_proceso):
        """Guarda los datos del proceso en la base de datos"""
        try:
            conn = sqlite3.connect("procesos.db")
            cursor = conn.cursor()
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS procesos (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER,
                           fecha_inicio TEXT,
                           fecha_fin TEXT,
                           hora_instruccion TEXT,
                           valvula_activada TEXT,
                           tiempo_valvula INTEGER,
                           ciclos INTEGER,
                           estado_valvula TEXT)''')
            
            cursor.execute('''INSERT INTO procesos 
                           (user_id, fecha_inicio, fecha_fin, hora_instruccion, 
                            valvula_activada, tiempo_valvula, ciclos, estado_valvula)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (self.user_id,
                         datos_proceso['fecha_inicio'],
                         datos_proceso['fecha_fin'],
                         datos_proceso['hora_instruccion'],
                         datos_proceso['valvula'],
                         datos_proceso['tiempo'],
                         datos_proceso['ciclos'],
                         datos_proceso['estado']))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al guardar en DB: {e}")
            return False

    def __del__(self):
        """Cerrar conexión serial al destruir el objeto"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Conexión serial cerrada")
