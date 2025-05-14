import customtkinter as ctk
import datetime
from tkinter import messagebox
import threading
import time
import sqlite3
from datetime import datetime

class FormPaneldeControl(ctk.CTkFrame):
    def __init__(self, panel_principal, user_id):  
        super().__init__(panel_principal)
        self.user_id = user_id
        
        
        self.valvulas = ["Al", "As", "Ga", "I", "N", "Mn", "Be", "Mg", "Si"]
        self.estados_valvulas = [False] * 9  # True = abierto, False = cerrado
        self.tiempos_inicio = [None] * 9
        self.contadores_ciclos = [0] * 9
        self.hilos_ejecucion = [None] * 9
        
        # Layout
        self.grid_columnconfigure(0, weight=1)  # Proceso Cíclico
        self.grid_columnconfigure(1, weight=1)  # Proceso Puntual
        self.grid_rowconfigure(0, weight=1)
        
        # Frame para Proceso Cíclico
        self.frame_ciclico = ctk.CTkFrame(self, fg_color="#f0f0f0")
        self.frame_ciclico.grid(row=0, column=0, padx=(10,5), pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.frame_ciclico, 
                    text="PROCESO CÍCLICO",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,10))
        
        frame_headers = ctk.CTkFrame(self.frame_ciclico)
        frame_headers.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(frame_headers, text="Válvula", width=60, anchor="w").pack(side="left")
        ctk.CTkLabel(frame_headers, text="Activar", width=60).pack(side="left", padx=5)
        ctk.CTkLabel(frame_headers, text="Apertura", width=120).pack(side="left", padx=5)
        ctk.CTkLabel(frame_headers, text="Cierre", width=120).pack(side="left", padx=5)
        ctk.CTkLabel(frame_headers, text="Ciclos", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(frame_headers, text="Actual", width=80).pack(side="left", padx=5)
        
        # Validación de entrada
        self.validar_cmd = self.register(self.validar_entrada)
        
        
        self.controles_ciclicos = []
        for i in range(9):
            frame_control = ctk.CTkFrame(self.frame_ciclico)
            frame_control.pack(fill="x", padx=5, pady=2)
            
            
            ctk.CTkLabel(frame_control, text=self.valvulas[i], width=60, anchor="w").pack(side="left")
            
            
            switch = ctk.CTkSwitch(frame_control, text="")
            switch.pack(side="left", padx=5)
            
            #Apertura
            apertura_frame = ctk.CTkFrame(frame_control, fg_color="transparent")
            apertura_frame.pack(side="left", padx=5)
            apertura = ctk.CTkEntry(apertura_frame, width=50, validate="key", validatecommand=(self.validar_cmd, "%P"))
            apertura.pack(side="left")
            apertura_unidad = ctk.CTkOptionMenu(apertura_frame, values=["s", "min", "h"], width=50)
            apertura_unidad.set("s")
            apertura_unidad.pack(side="left", padx=5)
            apertura.bind("<KeyRelease>", lambda e, ent=apertura, unidad=apertura_unidad: self.validar_tiempo(ent, unidad))
            apertura_unidad.configure(command=lambda v, ent=apertura, unidad=apertura_unidad: self.validar_tiempo(ent, unidad))
            
            # Cierre
            cierre_frame = ctk.CTkFrame(frame_control, fg_color="transparent")
            cierre_frame.pack(side="left", padx=5)
            cierre = ctk.CTkEntry(cierre_frame, width=50, validate="key", validatecommand=(self.validar_cmd, "%P"))
            cierre.pack(side="left")
            cierre_unidad = ctk.CTkOptionMenu(cierre_frame, values=["s", "min", "h"], width=50)
            cierre_unidad.set("s")
            cierre_unidad.pack(side="left", padx=5)
            cierre.bind("<KeyRelease>", lambda e, ent=cierre, unidad=cierre_unidad: self.validar_tiempo(ent, unidad))
            cierre_unidad.configure(command=lambda v, ent=cierre, unidad=cierre_unidad: self.validar_tiempo(ent, unidad))
            
            # Ciclos deseados
            ciclos_deseados = ctk.CTkEntry(frame_control, width=60, validate="key", validatecommand=(self.validar_cmd, "%P"))
            ciclos_deseados.pack(side="left", padx=5)
            
            # Ciclos actuales
            ciclos_actual = ctk.CTkLabel(frame_control, text="0", width=60)
            ciclos_actual.pack(side="left", padx=5)
            
            self.controles_ciclicos.append((switch, apertura, apertura_unidad, cierre, cierre_unidad, ciclos_deseados, ciclos_actual))

        
        btn_ejecutar = ctk.CTkButton(self.frame_ciclico, text="EJECUCIÓN SIMULTÁNEA", 
                                    fg_color="#06918A", command=self.iniciar_proceso_ciclico)
        btn_ejecutar.pack(pady=(10, 5), anchor="e", padx=(0, 10))
        
        # Frame para Proceso Puntual
        self.frame_puntual = ctk.CTkFrame(self, fg_color="#f0f0f0")
        self.frame_puntual.grid(row=0, column=1, padx=(5,10), pady=10, sticky="nsew")
        
        
        ctk.CTkLabel(self.frame_puntual, 
                    text="PROCESO PUNTUAL",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,10))
        
        
        frame_headers = ctk.CTkFrame(self.frame_puntual)
        frame_headers.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(frame_headers, text="Válvula", width=60, anchor="w").pack(side="left")
        ctk.CTkLabel(frame_headers, text="Estado", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(frame_headers, text="Tiempo", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(frame_headers, text="T. Abierto", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(frame_headers, text="Acciones", width=120).pack(side="left", padx=5)
        
        
        self.controles_puntuales = []
        for i in range(9):
            frame_control = ctk.CTkFrame(self.frame_puntual)
            frame_control.pack(fill="x", padx=5, pady=2)
            
            
            ctk.CTkLabel(frame_control, text=self.valvulas[i], width=60, anchor="w").pack(side="left")
            
            # (LED)
            estado = ctk.CTkLabel(frame_control, text="CERRADO", width=80, fg_color="red", corner_radius=5)
            estado.pack(side="left", padx=5)
            
            # t de apertura
            tiempo_frame = ctk.CTkFrame(frame_control, fg_color="transparent")
            tiempo_frame.pack(side="left", padx=5)
            tiempo = ctk.CTkEntry(tiempo_frame, width=50, validate="key", validatecommand=(self.validar_cmd, "%P"))
            tiempo.pack(side="left")
            tiempo_unidad = ctk.CTkOptionMenu(tiempo_frame, values=["s", "min", "h"], width=50)
            tiempo_unidad.set("s")
            tiempo_unidad.pack(side="left", padx=5)
            tiempo.bind("<KeyRelease>", lambda e, ent=tiempo, unidad=tiempo_unidad: self.validar_tiempo(ent, unidad))
            tiempo_unidad.configure(command=lambda v, ent=tiempo, unidad=tiempo_unidad: self.validar_tiempo(ent, unidad))
            
            # t transcurrido
            tiempo_transcurrido = ctk.CTkLabel(frame_control, text="00:00", width=80)
            tiempo_transcurrido.pack(side="left", padx=5)
            
            
            frame_acciones = ctk.CTkFrame(frame_control, fg_color="transparent")
            frame_acciones.pack(side="left", padx=5)
            
            
            btn_invertir = ctk.CTkButton(frame_acciones, text="Invertir", width=60,
                                       command=lambda idx=i: self.invertir_sentido(idx))
            btn_invertir.pack(side="left", padx=2)
            
            
            btn_ejecutar = ctk.CTkButton(frame_acciones, text="Ejecutar", width=60,
                                       command=lambda idx=i: self.ejecutar_valvula_puntual(idx))
            btn_ejecutar.pack(side="left", padx=2)
            
            self.controles_puntuales.append((estado, tiempo, tiempo_unidad, tiempo_transcurrido, btn_invertir, btn_ejecutar))

        self.pack(padx=10, pady=10, fill="both", expand=True)

    def validar_entrada(self, text):
        if text == "":
            return True
        if text.isdigit():
            try:
                val = int(text)
                if val <= 9999:
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False

    def validar_tiempo(self, entry, unidad_menu):
        try:
            valor = float(entry.get()) if entry.get() else 0
            unidad = unidad_menu.get()
            segundos = self.convertir_a_segundos(valor, unidad)

            if segundos > 9999:
                entry.configure(border_color="red")
                return False
            else:
                entry.configure(border_color="gray")
                return True
        except:
            entry.configure(border_color="red")
            return False

    def convertir_a_segundos(self, valor, unidad):
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

    def format_tiempo(self, segundos):
        mins, secs = divmod(segundos, 60)
        return f"{mins:02d}:{secs:02d}"

    def guardar_proceso_db(self, datos_proceso):
        """Guarda los datos del proceso en la base de datos"""
        conn = None
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
                         datos_proceso.get('fecha_fin', ''),
                         datos_proceso['hora_instruccion'],
                         datos_proceso['valvula'],
                         datos_proceso['tiempo'],
                         datos_proceso.get('ciclos', 0),
                         datos_proceso['estado']))
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

    def actualizar_proceso_db(self, idx, fecha_fin, ciclos_completados=None):
        """Actualiza un proceso existente en la base de datos"""
        conn = None
        try:
            conn = sqlite3.connect("procesos.db")
            cursor = conn.cursor()
            
            valvula = f"Válvula {self.valvulas[idx]}"
            
            
            cursor.execute('''SELECT id FROM procesos 
                           WHERE valvula_activada = ? AND fecha_fin = '' 
                           ORDER BY id DESC LIMIT 1''',
                        (valvula,))
            resultado = cursor.fetchone()
            
            if resultado:
                id_proceso = resultado[0]
                
                if ciclos_completados is not None:
                    # Actualizar proceso cíclico
                    cursor.execute('''UPDATE procesos 
                                   SET fecha_fin = ?, ciclos = ?
                                   WHERE id = ?''',
                                (fecha_fin, ciclos_completados, id_proceso))
                else:
                    # Actualizar proceso puntual
                    cursor.execute('''UPDATE procesos 
                                   SET fecha_fin = ?
                                   WHERE id = ?''',
                                (fecha_fin, id_proceso))
                
                conn.commit()
                return True
            return False
        except sqlite3.Error as e:
            print(f"Error de SQLite al actualizar proceso en DB: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado al actualizar proceso en DB: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def iniciar_proceso_ciclico(self):
        try:
            cadenas = []
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for i, (switch, apertura, apertura_unidad, cierre, cierre_unidad, ciclos_deseados, ciclos_actual) in enumerate(self.controles_ciclicos, start=1):
                if switch.get():
                    # Validar tiempos
                    apertura_val = self.convertir_a_segundos(apertura.get(), apertura_unidad.get())
                    cierre_val = self.convertir_a_segundos(cierre.get(), cierre_unidad.get())
                    
                    if apertura_val > 9999 or cierre_val > 9999:
                        messagebox.showerror("Error", f"Los tiempos para {self.valvulas[i-1]} no pueden exceder 9999 segundos (o equivalentes)")
                        return
                    
                    # Stop hilo previo
                    if self.hilos_ejecucion[i-1] and self.hilos_ejecucion[i-1].is_alive():
                        self.hilos_ejecucion[i-1].do_run = False
                    
                    # Cadena para ESP32
                    motor = f"M{i}"
                    ciclos_val = ciclos_deseados.get().zfill(4) if ciclos_deseados.get() else "0000"
                    
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

                    cadena = f"{motor}{tarea}N{ciclos_val}{apertura_str}{cierre_str}"
                    cadenas.append(cadena)
                    
                    # Guardar en DB
                    datos = {
                        'fecha_inicio': fecha_actual,
                        'fecha_fin': '',
                        'hora_instruccion': fecha_actual,
                        'valvula': f"Válvula {self.valvulas[i-1]}",
                        'tiempo': apertura_val,
                        'ciclos': ciclos_val,
                        'estado': 'A'
                    }
                    self.guardar_proceso_db(datos)
                    
                    # Start hilo de ejecución
                    self.contadores_ciclos[i-1] = 0
                    ciclos_actual.configure(text="0")
                    
                    hilo = threading.Thread(target=self.ejecutar_ciclos, args=(i-1, apertura_val, cierre_val, int(ciclos_val) if ciclos_val.isdigit() else 0))
                    hilo.do_run = True
                    hilo.start()
                    self.hilos_ejecucion[i-1] = hilo
            
            if cadenas:
                cadena_final = "".join(cadenas)
                print(f"Cadena enviada a ESP32: {cadena_final}")
                messagebox.showinfo("Éxito", "Proceso cíclico iniciado correctamente")
            else:
                messagebox.showwarning("Advertencia", "No hay válvulas activadas para ejecutar")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el proceso: {str(e)}")

    def ejecutar_ciclos(self, idx, tiempo_apertura, tiempo_cierre, ciclos_deseados):
        switch, _, _, _, _, ciclos_deseados_entry, ciclos_actual = self.controles_ciclicos[idx]
        
        ciclos = 0
        try:
            while getattr(threading.current_thread(), "do_run", True) and (ciclos_deseados == 0 or ciclos < ciclos_deseados):
                # Apertura
                inicio = time.time()
                while time.time() - inicio < tiempo_apertura and getattr(threading.current_thread(), "do_run", True):
                    time.sleep(0.1)
                
                if not getattr(threading.current_thread(), "do_run", True):
                    break
                    
                # Cierre
                inicio = time.time()
                while time.time() - inicio < tiempo_cierre and getattr(threading.current_thread(), "do_run", True):
                    time.sleep(0.1)
                
                if not getattr(threading.current_thread(), "do_run", True):
                    break
                    
                ciclos += 1
                self.after(0, lambda: ciclos_actual.configure(text=str(ciclos)))
            
            # Notificación cuando finaliza
            if ciclos_deseados > 0 and ciclos >= ciclos_deseados:
                self.after(0, lambda: messagebox.showinfo("Proceso completado", 
                        f"Válvula {self.valvulas[idx]} ha completado {ciclos_deseados} ciclos"))
                
            # Actualizar base de datos con fecha de finalización (Nota: tengo que modificar a hora de fin)
            fecha_fin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.actualizar_proceso_db(idx, fecha_fin, ciclos)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Error en válvula {self.valvulas[idx]}: {str(e)}"))

    def ejecutar_valvula_puntual(self, idx):
        estado, tiempo, tiempo_unidad, tiempo_transcurrido, _, _ = self.controles_puntuales[idx]
        
        if self.estados_valvulas[idx]:
            messagebox.showwarning("Advertencia", f"La válvula {self.valvulas[idx]} ya está abierta")
            return
            
        # Validar tiempo
        segundos = self.convertir_a_segundos(tiempo.get(), tiempo_unidad.get())
        if segundos > 9999:
            messagebox.showerror("Error", "El tiempo no puede exceder 9999 segundos (o equivalentes)")
            tiempo.configure(border_color="red")
            return
        
        # Construccion cadena (para impresión)
        motor = f"M{idx+1}"
        tarea = "A"
        direccion = "D"
        cadena = f"{motor}{tarea}{direccion}0000{str(segundos).zfill(4)}0000"
        print(f"Cadena enviada a ESP32: {cadena}")
        
        # Guardar en DB
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datos = {
            'fecha_inicio': fecha_actual,
            'fecha_fin': '',
            'hora_instruccion': fecha_actual,
            'valvula': f"Válvula {self.valvulas[idx]}",
            'tiempo': segundos,
            'ciclos': 0,
            'estado': 'A'
        }
        self.guardar_proceso_db(datos)
        
        # Actualiza
        self.estados_valvulas[idx] = True
        self.tiempos_inicio[idx] = time.time()
        estado.configure(text="ABIERTO", fg_color="green")
        
        #Inico de temporizador
        self.actualizar_tiempo_transcurrido(idx, segundos)

    def actualizar_tiempo_transcurrido(self, idx, duracion_total):
        estado, _, _, tiempo_transcurrido, _, _ = self.controles_puntuales[idx]
        
        if not self.estados_valvulas[idx]:
            return
            
        tiempo_transcurrido_seg = int(time.time() - self.tiempos_inicio[idx])
        tiempo_restante = max(0, duracion_total - tiempo_transcurrido_seg)
        
        tiempo_transcurrido.configure(text=self.format_tiempo(tiempo_transcurrido_seg))
        
        if tiempo_restante > 0:
            self.after(1000, lambda: self.actualizar_tiempo_transcurrido(idx, duracion_total))
        else:
            self.estados_valvulas[idx] = False
            estado.configure(text="CERRADO", fg_color="red")
            tiempo_transcurrido.configure(text="00:00")
            
            # Notificación de finalización
            messagebox.showinfo("Proceso completado", 
                             f"Válvula {self.valvulas[idx]} ha completado su tiempo de apertura")
            
            # Actualizar fecha de finalización en DB (Nota: tengo que modificar a hora de fin)
            fecha_fin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.actualizar_proceso_db(idx, fecha_fin)

    def invertir_sentido(self, idx):
        messagebox.showinfo("Info", f"Sentido de la válvula {self.valvulas[idx]} invertido")