import customtkinter as ctk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from datetime import datetime
import numpy as np
from matplotlib.patches import Rectangle
import re

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
        
        # Variables para la animación de crecimiento por fases
        self.fases_crecimiento = {}  # Diccionario para almacenar datos por fase
        self.tiempo_inicio_proceso = None
        self.ultima_actualizacion = 0
        self.estado_valvulas = {elemento: {'estado': 'C', 'tiempo': 0} 
                               for elemento in ['Al', 'As', 'Ga', 'In', 'N', 'Mn', 'Be', 'Mg', 'Si']}
        
        # Configurar interfaz simplificada
        self._crear_interfaz()
        
        # Registrar este panel para recibir mensajes seriales
        self.master_panel.registrar_panel_serial("monitoreo", self)
        
        # Iniciar monitoreo
        self.iniciar_monitoreo()

    def _crear_interfaz(self):
        """Crea la interfaz simplificada del panel de monitoreo con solo la gráfica de crecimiento"""
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame para controles superiores
        self.controles_frame = ctk.CTkFrame(self)
        self.controles_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Título
        ctk.CTkLabel(
            self.controles_frame,
            text="MONITOREO DE CRECIMIENTO POR FASES",
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
        
        # Frame para la gráfica de crecimiento
        self.grafica_frame = ctk.CTkFrame(self)
        self.grafica_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        
        # Gráfica de crecimiento de capas por fases
        self.fig_crecimiento = Figure(figsize=(10, 6), dpi=100)
        self.ax_crecimiento = self.fig_crecimiento.add_subplot(111)
        self.canvas_crecimiento = FigureCanvasTkAgg(self.fig_crecimiento, master=self.grafica_frame)
        self.canvas_crecimiento.get_tk_widget().pack(fill="both", expand=True)
        
        # Configurar gráfica inicial
        self._configurar_grafica_crecimiento_inicial()

    def _configurar_grafica_crecimiento_inicial(self):
        """Configura la gráfica de crecimiento con estado inicial"""
        self.ax_crecimiento.clear()
        self.ax_crecimiento.set_title("CRECIMIENTO POR FASES", pad=10, fontsize=14, weight='bold')
        self.ax_crecimiento.set_xlabel("Tiempo (segundos)", labelpad=10)
        self.ax_crecimiento.set_ylabel("Espesor (u.a.)", labelpad=10)
        self.ax_crecimiento.grid(True, linestyle='--', alpha=0.7)
        
        # Mostrar estructura inicial vacía
        self.ax_crecimiento.set_xlim(0, 100)
        self.ax_crecimiento.set_ylim(0, 10)
        self.ax_crecimiento.text(0.5, 0.5, 'Seleccione un proceso para monitorear', 
                               horizontalalignment='center',
                               verticalalignment='center',
                               transform=self.ax_crecimiento.transAxes,
                               fontsize=12,
                               color='gray')
        self.canvas_crecimiento.draw()

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

    def _actualizar_lista_procesos(self):
        """Actualiza la lista de procesos en el combobox"""
        procesos = self._obtener_procesos_activos()
        current = self.proceso_combobox.get()
        
        self.proceso_combobox.configure(values=procesos)
        
        if current not in procesos:
            self.proceso_combobox.set(procesos[0] if procesos else "-- Seleccione --")
            self._configurar_grafica_crecimiento_inicial()

    def _cambiar_proceso_monitoreado(self, choice):
        """Cambia el proceso que se está monitoreando"""
        if choice in ["-- Seleccione --", "-- Error --"]:
            self._configurar_grafica_crecimiento_inicial()
            return
            
        self.proceso_activo = choice
        self.detener_monitoreo.set()  # Detener cualquier monitoreo previo
        
        # Reiniciar variables de crecimiento
        self.fases_crecimiento = {}
        self.tiempo_inicio_proceso = None
        self.ultima_actualizacion = 0
        
        # Esperar a que el hilo anterior termine
        time.sleep(0.1)
        
        # Reiniciar monitoreo
        self.detener_monitoreo.clear()
        
        if not self._hilo_monitoreo or not self._hilo_monitoreo.is_alive():
            self._hilo_monitoreo = threading.Thread(
                target=self._monitorear_proceso, 
                daemon=True
            )
            self._hilo_monitoreo.start()

    def _monitorear_proceso(self):
        """Monitorea el proceso seleccionado y actualiza las fases"""
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
                        tipo_proceso,
                        fase
                    FROM procesos 
                    WHERE proceso_id=?
                    ORDER BY hora_instruccion ASC
                """, (self.proceso_activo,))
                
                datos = cursor.fetchall()
                conn.close()
                
                # Procesar datos y agrupar por fases
                self.after(0, self._procesar_datos_por_fase, datos)
                time.sleep(1)  # Intervalo de actualización más largo para reducir carga
                
            except Exception as e:
                print(f"Error al monitorear: {e}")
                time.sleep(2)

    def _procesar_datos_por_fase(self, datos):
        """Procesa los datos y los agrupa por fases para la animación"""
        if not datos:
            return
            
        # Obtener información de fases
        fases = {}
        for registro in datos:
            fase = registro[5]  # Índice de la columna fase
            if fase not in fases:
                fases[fase] = {
                    'valvulas': [],
                    'inicio': None,
                    'fin': None,
                    'elementos': set()
                }
            
            # Extraer solo el nombre del elemento de "Válvula X"
            valvula = registro[0]
            elemento = valvula.replace("Válvula ", "").strip() if "Válvula" in valvula else valvula
            
            fases[fase]['elementos'].add(elemento)
            
            # Determinar tiempos de inicio y fin
            hora_instruccion = datetime.strptime(registro[3], '%Y-%m-%d %H:%M:%S')
            if fases[fase]['inicio'] is None or hora_instruccion < fases[fase]['inicio']:
                fases[fase]['inicio'] = hora_instruccion
                
            if registro[1] == 'C':  # Si está cerrado
                if fases[fase]['fin'] is None or hora_instruccion > fases[fase]['fin']:
                    fases[fase]['fin'] = hora_instruccion
        
        # Actualizar datos de fases para la animación
        for fase, datos_fase in fases.items():
            if fase not in self.fases_crecimiento:
                # Nueva fase detectada
                self.fases_crecimiento[fase] = {
                    'elementos': list(datos_fase['elementos']),
                    'tiempo_inicio': (datos_fase['inicio'] - fases[1]['inicio']).total_seconds() if 1 in fases else 0,
                    'tiempo_fin': (datos_fase['fin'] - fases[1]['inicio']).total_seconds() if datos_fase['fin'] and 1 in fases else None,
                    'espesor': 1.0,  # Espesor base para cada fase
                    'color': self._obtener_color_fase(fase)
                }
        
        # Actualizar animación
        tiempo_actual = time.time()
        if self.tiempo_inicio_proceso is None:
            self.tiempo_inicio_proceso = tiempo_actual
            
        tiempo_transcurrido = tiempo_actual - self.tiempo_inicio_proceso
        
        # Solo actualizar la animación si ha pasado suficiente tiempo
        if tiempo_actual - self.ultima_actualizacion >= 1.0:  # Actualizar cada segundo
            self._dibujar_fases_crecimiento(tiempo_transcurrido)
            self.ultima_actualizacion = tiempo_actual

    def _obtener_color_fase(self, fase):
        """Devuelve un color único para cada fase"""
        colores = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        return colores[(int(fase) - 1) % len(colores)]

    def _dibujar_fases_crecimiento(self, tiempo_transcurrido):
        """Dibuja las fases de crecimiento en la gráfica"""
        self.ax_crecimiento.clear()
        
        # Configuración básica de la gráfica
        self.ax_crecimiento.set_title(f"CRECIMIENTO POR FASES: {self.proceso_activo}", pad=10, fontsize=14, weight='bold')
        self.ax_crecimiento.set_xlabel("Tiempo (segundos)", labelpad=10)
        self.ax_crecimiento.set_ylabel("Espesor (u.a.)", labelpad=10)
        self.ax_crecimiento.grid(True, linestyle='--', alpha=0.7)
        
        if not self.fases_crecimiento:
            self.ax_crecimiento.text(0.5, 0.5, 'No hay datos de fases para mostrar', 
                                   horizontalalignment='center',
                                   verticalalignment='center',
                                   transform=self.ax_crecimiento.transAxes,
                                   fontsize=12,
                                   color='gray')
            self.canvas_crecimiento.draw()
            return
        
        # Calcular límites del gráfico
        max_tiempo = max([fase['tiempo_inicio'] + 10 for fase in self.fases_crecimiento.values()] + [tiempo_transcurrido + 10])
        max_espesor = len(self.fases_crecimiento) * 1.5 + 1
        self.ax_crecimiento.set_xlim(0, max_tiempo)
        self.ax_crecimiento.set_ylim(0, max_espesor)
        
        # Dibujar cada fase como una capa
        espesor_acumulado = 0
        for fase_num, fase_data in sorted(self.fases_crecimiento.items(), key=lambda x: int(x[0])):
            # Determinar si la fase está activa, completada o pendiente
            if tiempo_transcurrido >= fase_data['tiempo_inicio']:
                if fase_data['tiempo_fin'] is None or tiempo_transcurrido <= fase_data['tiempo_fin']:
                    # Fase activa
                    tiempo_fin_dibujo = tiempo_transcurrido
                    estado = "ACTIVA"
                    alpha = 0.9
                else:
                    # Fase completada
                    tiempo_fin_dibujo = fase_data['tiempo_fin']
                    estado = "COMPLETADA"
                    alpha = 0.7
                
                # Dibujar rectángulo para la fase
                rect = Rectangle((fase_data['tiempo_inicio'], espesor_acumulado),
                               tiempo_fin_dibujo - fase_data['tiempo_inicio'],
                               fase_data['espesor'],
                               facecolor=fase_data['color'],
                               edgecolor='black',
                               alpha=alpha)
                self.ax_crecimiento.add_patch(rect)
                
                # Añadir etiqueta con información de la fase
                texto = f"Fase {fase_num}\n({', '.join(fase_data['elementos'])})"
                self.ax_crecimiento.text(fase_data['tiempo_inicio'] + (tiempo_fin_dibujo - fase_data['tiempo_inicio'])/2,
                                       espesor_acumulado + fase_data['espesor']/2,
                                       texto,
                                       ha='center', va='center',
                                       color='black',
                                       fontsize=8,
                                       bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
                
                espesor_acumulado += fase_data['espesor']
        
        # Dibujar línea de tiempo actual
        self.ax_crecimiento.axvline(x=tiempo_transcurrido, color='red', linestyle='--', alpha=0.7, linewidth=2)
        
        # Añadir leyenda de fases
        handles = []
        labels = []
        for fase_num, fase_data in sorted(self.fases_crecimiento.items(), key=lambda x: int(x[0])):
            handles.append(Rectangle((0, 0), 1, 1, facecolor=fase_data['color']))
            labels.append(f"Fase {fase_num} ({', '.join(fase_data['elementos'])})")
        
        self.ax_crecimiento.legend(handles, labels, title="Fases", 
                                 bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.fig_crecimiento.tight_layout()
        self.canvas_crecimiento.draw()

    def procesar_mensaje(self, mensaje):
        """Procesa mensajes seriales para actualizar el estado de las válvulas"""
        # Este método puede usarse para actualizaciones en tiempo real si es necesario
        pass

    def iniciar_monitoreo(self):
        """Inicia el monitoreo del proceso seleccionado"""
        self._actualizar_lista_procesos()

    def __del__(self):
        """Limpia recursos al destruir el panel"""
        try:
            self.detener_monitoreo.set()
            if hasattr(self, '_hilo_monitoreo') and self._hilo_monitoreo is not None and self._hilo_monitoreo.is_alive():
                self._hilo_monitoreo.join(timeout=1)
            if hasattr(self, 'fig_crecimiento'):
                plt.close(self.fig_crecimiento)
            # Desregistrar este panel para dejar de recibir mensajes seriales
            if hasattr(self, 'master_panel') and hasattr(self.master_panel, 'desregistrar_panel_serial'):
                self.master_panel.desregistrar_panel_serial("monitoreo")
        except Exception as e:
            print(f"Error en limpieza de Monitoreo: {e}")