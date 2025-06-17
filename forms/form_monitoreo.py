import customtkinter as ctk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from datetime import datetime

class FormMonitoreo(ctk.CTkFrame):
    def __init__(self, panel_principal, user_id):
        super().__init__(panel_principal)
        self.user_id = user_id
        self.master_panel = panel_principal.master  # Acceso al MasterPanel
        self.configure(fg_color="#f4f8f7")
        
        # Variables de estado
        self.proceso_activo = None
        self.datos_proceso = []
        self.detener_monitoreo = threading.Event()
        self._hilo_monitoreo = None
        
        # Configurar interfaz
        self._crear_interfaz()
        
        # Iniciar monitoreo
        self.iniciar_monitoreo()

    def _crear_interfaz(self):
        """Crea la interfaz del panel de monitoreo"""
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Frame de controles
        self.controles_frame = ctk.CTkFrame(self)
        self.controles_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Título
        ctk.CTkLabel(
            self.controles_frame,
            text="MONITOREO DE PROCESOS",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10)
        
        # ComboBox para selección de proceso
        self.proceso_combobox = ctk.CTkComboBox(
            self.controles_frame,
            values=self._obtener_procesos_activos(),
            command=self._cambiar_proceso_monitoreado,
            state="readonly",
            width=250
        )
        self.proceso_combobox.pack(side="left", padx=10)
        
        # Botón de actualización
        ctk.CTkButton(
            self.controles_frame,
            text="🔄 Actualizar",
            width=100,
            command=self._actualizar_lista_procesos
        ).pack(side="left", padx=5)
        
        # Indicador de estado
        self.estado_label = ctk.CTkLabel(
            self.controles_frame,
            text="Estado: Inactivo",
            fg_color="#6c757d",
            corner_radius=5,
            width=120
        )
        self.estado_label.pack(side="right", padx=10)
        
        # Frame para la gráfica
        self.grafica_frame = ctk.CTkFrame(self)
        self.grafica_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.grafica_frame.grid_columnconfigure(0, weight=1)
        self.grafica_frame.grid_rowconfigure(0, weight=1)
        
        # Configurar gráfica matplotlib
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.grafica_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Configurar gráfica inicial
        self._configurar_grafica_inicial()

    def _obtener_procesos_activos(self):
        """Obtiene procesos activos del usuario actual"""
        try:
            conn = sqlite3.connect("procesos.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT proceso_id FROM procesos 
                WHERE user_id=? AND fecha_fin='' 
                ORDER BY fecha_inicio DESC
            """, (self.user_id,))
            procesos = [str(row[0]) for row in cursor.fetchall()]
            conn.close()
            return procesos if procesos else ["-- Seleccione --"]
        except Exception as e:
            print(f"Error al obtener procesos: {e}")
            return ["-- Error --"]

    def _configurar_grafica_inicial(self):
        """Configura la gráfica con estado inicial"""
        self.ax.clear()
        self.ax.set_title("SELECCIONE UN PROCESO PARA MONITOREAR", pad=20)
        self.ax.set_xlabel("Tiempo (segundos)", labelpad=10)
        self.ax.set_ylabel("Estado de Válvulas", labelpad=10)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=self.ax.transAxes,
                    fontsize=12,
                    color='gray')
        self.canvas.draw()

    def _actualizar_lista_procesos(self):
        """Actualiza la lista de procesos en el combobox"""
        self.estado_label.configure(text="Estado: Actualizando...", fg_color="#17a2b8")
        procesos = self._obtener_procesos_activos()
        current = self.proceso_combobox.get()
        
        self.proceso_combobox.configure(values=procesos)
        
        if current not in procesos:
            self.proceso_combobox.set(procesos[0] if procesos else "-- Seleccione --")
            self._configurar_grafica_inicial()
        
        self.estado_label.configure(text="Estado: Listo", fg_color="#28a745")

    def _cambiar_proceso_monitoreado(self, choice):
        """Cambia el proceso que se está monitoreando"""
        if choice in ["-- Seleccione --", "-- Error --"]:
            self._configurar_grafica_inicial()
            self.estado_label.configure(text="Estado: Inactivo", fg_color="#6c757d")
            return
            
        self.proceso_activo = choice
        self.detener_monitoreo.set()  # Detener cualquier monitoreo previo
        
        # Esperar a que el hilo anterior termine
        time.sleep(0.1)
        
        # Reiniciar monitoreo
        self.detener_monitoreo.clear()
        self.estado_label.configure(text="Estado: Monitoreando...", fg_color="#007bff")
        
        if not self._hilo_monitoreo or not self._hilo_monitoreo.is_alive():
            self._hilo_monitoreo = threading.Thread(
                target=self._monitorear_proceso, 
                daemon=True
            )
            self._hilo_monitoreo.start()

    def _monitorear_proceso(self):
        """Monitorea el proceso seleccionado"""
        while not self.detener_monitoreo.is_set() and self.proceso_activo:
            try:
                conn = sqlite3.connect("procesos.db")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        valvula_activada, 
                        estado_valvula, 
                        tiempo_valvula,
                        hora_instruccion,
                        tipo_proceso
                    FROM procesos 
                    WHERE proceso_id=?
                    ORDER BY hora_instruccion ASC
                """, (self.proceso_activo,))
                
                datos = cursor.fetchall()
                conn.close()
                
                # Procesar datos y actualizar gráfica
                self.after(0, self._actualizar_grafica, datos)
                time.sleep(0.1)  # Intervalo de actualización
                
            except Exception as e:
                print(f"Error al monitorear: {e}")
                self.after(0, lambda: self.estado_label.configure(
                    text="Estado: Error", 
                    fg_color="#dc3545"
                ))
                time.sleep(0.5)

    def _actualizar_grafica(self, datos):
        """Actualiza la gráfica con nuevos datos"""
        try:
            self.ax.clear()
            
            if not datos:
                self.ax.set_title(f"{self.proceso_activo} - Sin datos", pad=20)
                self.ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                            horizontalalignment='center',
                            verticalalignment='center',
                            transform=self.ax.transAxes,
                            fontsize=12,
                            color='gray')
                self.canvas.draw()
                return
                
            # Procesamiento de datos
            valvulas = sorted(list(set(d[0] for d in datos)))
            tiempos = [datetime.strptime(d[3], '%Y-%m-%d %H:%M:%S') for d in datos]
            tiempo_inicio = tiempos[0]
            segundos = [(t - tiempo_inicio).total_seconds() for t in tiempos]
            
            # Crear gráfico de estados
            for i, valvula in enumerate(valvulas):
                estados = []
                tiempos_valvula = []
                for d in datos:
                    if d[0] == valvula:
                        estado = 1 if d[1] == 'A' else 0
                        estados.append(estado + i*0.1)  # Desplazamiento vertical
                        tiempos_valvula.append((datetime.strptime(d[3], '%Y-%m-%d %H:%M:%S') - tiempo_inicio).total_seconds())
                
                self.ax.plot(tiempos_valvula, estados, 'o-', label=valvula, markersize=8, linewidth=2)
            
            # Configurar gráfica
            self.ax.set_title(f"MONITOREO: {self.proceso_activo}", pad=20)
            self.ax.set_xlabel("Tiempo transcurrido (segundos)", labelpad=10)
            self.ax.set_ylabel("Estado de válvulas", labelpad=10)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
            
            # Ajustar límites y ticks
            self.ax.set_yticks([0, 1])
            self.ax.set_yticklabels(["Cerrado", "Abierto"])
            self.ax.set_ylim(-0.5, len(valvulas)*0.1 + 1.5)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error al actualizar gráfica: {e}")
            self.estado_label.configure(text="Estado: Error gráfica", fg_color="#dc3545")

    def iniciar_monitoreo(self):
        """Inicia el monitoreo del proceso seleccionado"""
        self._actualizar_lista_procesos()

    def __del__(self):
        """Limpia recursos al destruir el panel"""
        try:
            self.detener_monitoreo.set()
            if hasattr(self, '_hilo_monitoreo') and self._hilo_monitoreo is not None and self._hilo_monitoreo.is_alive():
                self._hilo_monitoreo.join(timeout=1)
            if hasattr(self, 'fig'):
                plt.close(self.fig)
        except Exception as e:
            print(f"Error en limpieza de Monitoreo: {e}")
