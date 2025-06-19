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
        
        # Variables para la animación de crecimiento
        self.capas_crecimiento = []
        self.tiempo_inicio_proceso = None
        self.ultima_actualizacion = 0
        self.estado_valvulas = {elemento: {'estado': 'C', 'tiempo': 0} 
                               for elemento in ['Al', 'As', 'Ga', 'In', 'N', 'Mn', 'Be', 'Mg', 'Si']}
        
        # Configurar interfaz
        self._crear_interfaz()
        
        # Registrar este panel para recibir mensajes seriales
        self.master_panel.registrar_panel_serial("monitoreo", self)
        
        # Iniciar monitoreo
        self.iniciar_monitoreo()

    def _crear_interfaz(self):
        """Crea la interfaz del panel de monitoreo con gráficas de estado y crecimiento"""
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
        
        # Frame para las gráficas
        self.graficas_frame = ctk.CTkFrame(self)
        self.graficas_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.graficas_frame.grid_columnconfigure(0, weight=1)
        self.graficas_frame.grid_rowconfigure(0, weight=1)
        self.graficas_frame.grid_rowconfigure(1, weight=1)
        
        # Gráfica de estados de válvulas
        self.fig_estados = Figure(figsize=(10, 4), dpi=100)
        self.ax_estados = self.fig_estados.add_subplot(111)
        self.canvas_estados = FigureCanvasTkAgg(self.fig_estados, master=self.graficas_frame)
        self.canvas_estados.get_tk_widget().grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        # Gráfica de crecimiento de capas
        self.fig_crecimiento = Figure(figsize=(10, 4), dpi=100)
        self.ax_crecimiento = self.fig_crecimiento.add_subplot(111)
        self.canvas_crecimiento = FigureCanvasTkAgg(self.fig_crecimiento, master=self.graficas_frame)
        self.canvas_crecimiento.get_tk_widget().grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        
        # Configurar gráficas iniciales
        self._configurar_grafica_estados_inicial()
        self._configurar_grafica_crecimiento_inicial()

    def _configurar_grafica_estados_inicial(self):
        """Configura la gráfica de estados con estado inicial"""
        self.ax_estados.clear()
        self.ax_estados.set_title("ESTADO DE VÁLVULAS", pad=10)
        self.ax_estados.set_xlabel("Tiempo (segundos)", labelpad=10)
        self.ax_estados.set_ylabel("Válvula", labelpad=10)
        self.ax_estados.grid(True, linestyle='--', alpha=0.7)
        self.ax_estados.text(0.5, 0.5, 'Seleccione un proceso para monitorear', 
                           horizontalalignment='center',
                           verticalalignment='center',
                           transform=self.ax_estados.transAxes,
                           fontsize=12,
                           color='gray')
        self.canvas_estados.draw()

    def _configurar_grafica_crecimiento_inicial(self):
        """Configura la gráfica de crecimiento con estado inicial"""
        self.ax_crecimiento.clear()
        self.ax_crecimiento.set_title("CRECIMIENTO DE CAPAS", pad=10)
        self.ax_crecimiento.set_xlabel("Tiempo (segundos)", labelpad=10)
        self.ax_crecimiento.set_ylabel("Espesor (u.a.)", labelpad=10)
        self.ax_crecimiento.grid(True, linestyle='--', alpha=0.7)
        
        # Mostrar estructura inicial vacía
        self.ax_crecimiento.set_xlim(0, 100)
        self.ax_crecimiento.set_ylim(0, 10)
        self.ax_crecimiento.text(0.5, 0.5, 'Esperando datos de crecimiento...', 
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
        self.estado_label.configure(text="Estado: Actualizando...", fg_color="#17a2b8")
        procesos = self._obtener_procesos_activos()
        current = self.proceso_combobox.get()
        
        self.proceso_combobox.configure(values=procesos)
        
        if current not in procesos:
            self.proceso_combobox.set(procesos[0] if procesos else "-- Seleccione --")
            self._configurar_grafica_estados_inicial()
            self._configurar_grafica_crecimiento_inicial()
        
        self.estado_label.configure(text="Estado: Listo", fg_color="#28a745")

    def _cambiar_proceso_monitoreado(self, choice):
        """Cambia el proceso que se está monitoreando"""
        if choice in ["-- Seleccione --", "-- Error --"]:
            self._configurar_grafica_estados_inicial()
            self._configurar_grafica_crecimiento_inicial()
            self.estado_label.configure(text="Estado: Inactivo", fg_color="#6c757d")
            return
            
        self.proceso_activo = choice
        self.detener_monitoreo.set()  # Detener cualquier monitoreo previo
        
        # Reiniciar variables de crecimiento
        self.capas_crecimiento = []
        self.tiempo_inicio_proceso = None
        self.ultima_actualizacion = 0
        
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
                
                # Procesar datos y actualizar gráficas
                self.after(0, self._actualizar_grafica, datos)
                time.sleep(0.1)  # Intervalo de actualización
                
            except Exception as e:
                print(f"Error al monitorear: {e}")
                self.after(0, lambda: self.estado_label.configure(
                    text="Estado: Error", 
                    fg_color="#dc3545"
                ))
                time.sleep(0.5)

    def procesar_mensaje(self, mensaje):
        """Procesa un mensaje recibido de la ESP32 para actualizar el estado de las válvulas"""
        # Procesar estado de todas las válvulas en un solo mensaje
        patron = r'M(\d+)([AC])'
        coincidencias = re.findall(patron, mensaje)
        
        if coincidencias:
            # Actualizar estados de válvulas
            for num_valvula, estado in coincidencias:
                    num_valvula = int(num_valvula)
                    if 1 <= num_valvula <= 9:
                        elemento = ['Al', 'As', 'Ga', 'In', 'N', 'Mn', 'Be', 'Mg', 'Si'][num_valvula-1]
                        self.estado_valvulas[elemento]['estado'] = estado
                        
                        # Si está abierta, incrementar tiempo (si ya estaba abierta)
                        if estado == 'A' and self.estado_valvulas[elemento]['estado'] == 'A':
                            self.estado_valvulas[elemento]['tiempo'] += 1
                        else:
                            self.estado_valvulas[elemento]['tiempo'] = 0
            
            # Actualizar animación de crecimiento
            self.actualizar_animacion_crecimiento()

    def actualizar_animacion_crecimiento(self):
        """Actualiza la animación de crecimiento de capas basada en el estado actual de las válvulas"""
        if not self.proceso_activo:
            return
            
        tiempo_actual = time.time()
        
        # Solo actualizar cada segundo para evitar sobrecarga
        if tiempo_actual - self.ultima_actualizacion < 1.0:
            return
            
        self.ultima_actualizacion = tiempo_actual
        
        # Calcular tiempo transcurrido desde el inicio del proceso
        if self.tiempo_inicio_proceso is None:
            self.tiempo_inicio_proceso = tiempo_actual
        tiempo_transcurrido = tiempo_actual - self.tiempo_inicio_proceso
        
        # Determinar qué válvulas están abiertas y su tiempo de apertura
        elementos_activos = [elem for elem, datos in self.estado_valvulas.items() 
                            if datos['estado'] == 'A']
        
        # Simular crecimiento de capas (esto es una simplificación)
        for elemento in elementos_activos:
            # Añadir una nueva capa o aumentar el espesor de la última capa del mismo material
            if not self.capas_crecimiento or self.capas_crecimiento[-1]['elemento'] != elemento:
                # Nueva capa
                self.capas_crecimiento.append({
                    'elemento': elemento,
                    'tiempo_inicio': tiempo_transcurrido,
                    'espesor': 0.1,  # Espesor inicial
                    'color': self._obtener_color_elemento(elemento)
                })
            else:
                # Aumentar espesor de la capa existente
                self.capas_crecimiento[-1]['espesor'] += 0.1
        
        # Dibujar las capas
        self._dibujar_capas_crecimiento(tiempo_transcurrido)

    def _obtener_color_elemento(self, elemento):
        """Devuelve un color único para cada elemento"""
        colores = {
            'Al': 'silver',
            'As': 'darkorange',
            'Ga': 'dodgerblue',
            'In': 'indigo',
            'N': 'limegreen',
            'Mn': 'hotpink',
            'Be': 'teal',
            'Mg': 'gold',
            'Si': 'darkred'
        }
        return colores.get(elemento, 'gray')

    def _dibujar_capas_crecimiento(self, tiempo_transcurrido):
        """Dibuja las capas de crecimiento en la gráfica"""
        self.ax_crecimiento.clear()
        
        # Configuración básica de la gráfica
        self.ax_crecimiento.set_title(f"CRECIMIENTO DE CAPAS: {self.proceso_activo}", pad=10)
        self.ax_crecimiento.set_xlabel("Tiempo (segundos)", labelpad=10)
        self.ax_crecimiento.set_ylabel("Espesor (u.a.)", labelpad=10)
        self.ax_crecimiento.grid(True, linestyle='--', alpha=0.7)
        
        # Ajustar límites
        max_tiempo = max(100, tiempo_transcurrido + 10)  # Mínimo 100 segundos
        max_espesor = sum(capa['espesor'] for capa in self.capas_crecimiento) + 5
        self.ax_crecimiento.set_xlim(0, max_tiempo)
        self.ax_crecimiento.set_ylim(0, max_espesor)
        
        # Dibujar capas
        espesor_acumulado = 0
        for capa in self.capas_crecimiento:
            # Dibujar rectángulo para la capa
            rect = Rectangle((capa['tiempo_inicio'], espesor_acumulado),
                           tiempo_transcurrido - capa['tiempo_inicio'],
                           capa['espesor'],
                           facecolor=capa['color'],
                           edgecolor='black',
                           alpha=0.7)
            self.ax_crecimiento.add_patch(rect)
            
            # Añadir etiqueta
            self.ax_crecimiento.text(capa['tiempo_inicio'] + (tiempo_transcurrido - capa['tiempo_inicio'])/2,
                                   espesor_acumulado + capa['espesor']/2,
                                   capa['elemento'],
                                   ha='center', va='center',
                                   color='black',
                                   fontsize=8)
            
            espesor_acumulado += capa['espesor']
        
        # Dibujar línea de tiempo actual
        self.ax_crecimiento.axvline(x=tiempo_transcurrido, color='red', linestyle='--', alpha=0.5)
        
        # Añadir leyenda de colores
        handles = []
        labels = []
        for elemento, color in {
            'Al': 'silver',
            'As': 'darkorange',
            'Ga': 'dodgerblue',
            'In': 'indigo',
            'N': 'limegreen',
            'Mn': 'hotpink',
            'Be': 'teal',
            'Mg': 'gold',
            'Si': 'darkred'
        }.items():
            handles.append(Rectangle((0, 0), 1, 1, facecolor=color))
            labels.append(elemento)
        
        self.ax_crecimiento.legend(handles, labels, title="Materiales", 
                                 bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.fig_crecimiento.tight_layout()
        self.canvas_crecimiento.draw()

    def _actualizar_grafica(self, datos):
        """Actualiza la gráfica de estados con nuevos datos"""
        try:
            self.ax_estados.clear()
            
            if not datos:
                self.ax_estados.set_title(f"{self.proceso_activo} - Sin datos", pad=10)
                self.ax_estados.text(0.5, 0.5, 'No hay datos para mostrar', 
                                   horizontalalignment='center',
                                   verticalalignment='center',
                                   transform=self.ax_estados.transAxes,
                                   fontsize=12,
                                   color='gray')
                self.canvas_estados.draw()
                return
                
            # Procesamiento de datos
            valvulas = sorted(list(set(d[0] for d in datos)))
            tiempos = [datetime.strptime(d[3], '%Y-%m-%d %H:%M:%S') for d in datos]
            tiempo_inicio = tiempos[0]
            segundos = [(t - tiempo_inicio).total_seconds() for t in tiempos]
            
            # Establecer tiempo de inicio para la animación de crecimiento
            if self.tiempo_inicio_proceso is None:
                self.tiempo_inicio_proceso = time.time()
                self.capas_crecimiento = []  # Reiniciar capas
                self.ultima_actualizacion = 0
            
            # Crear gráfico de estados
            for i, valvula in enumerate(valvulas):
                estados = []
                tiempos_valvula = []
                for d in datos:
                    if d[0] == valvula:
                        estado = 1 if d[1] == 'A' else 0
                        estados.append(estado + i*0.1)  # Desplazamiento vertical
                        tiempos_valvula.append((datetime.strptime(d[3], '%Y-%m-%d %H:%M:%S') - tiempo_inicio).total_seconds())
                
                self.ax_estados.plot(tiempos_valvula, estados, 'o-', label=valvula, markersize=8, linewidth=2)
            
            # Configurar gráfica
            self.ax_estados.set_title(f"ESTADO DE VÁLVULAS: {self.proceso_activo}", pad=10)
            self.ax_estados.set_xlabel("Tiempo transcurrido (segundos)", labelpad=10)
            self.ax_estados.set_ylabel("Estado de válvulas", labelpad=10)
            self.ax_estados.grid(True, linestyle='--', alpha=0.7)
            self.ax_estados.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
            
            # Ajustar límites y ticks
            self.ax_estados.set_yticks([0, 1])
            self.ax_estados.set_yticklabels(["Cerrado", "Abierto"])
            self.ax_estados.set_ylim(-0.5, len(valvulas)*0.1 + 1.5)
            
            self.fig_estados.tight_layout()
            self.canvas_estados.draw()
            
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
            if hasattr(self, 'fig_estados'):
                plt.close(self.fig_estados)
            if hasattr(self, 'fig_crecimiento'):
                plt.close(self.fig_crecimiento)
            # Desregistrar este panel para dejar de recibir mensajes seriales
            if hasattr(self, 'master_panel') and hasattr(self.master_panel, 'desregistrar_panel_serial'):
                self.master_panel.desregistrar_panel_serial("monitoreo")
        except Exception as e:
            print(f"Error en limpieza de Monitoreo: {e}")