import customtkinter as ctk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from datetime import datetime
from matplotlib.patches import Rectangle
import re

class FormMonitoreo(ctk.CTkFrame):
    def __init__(self, panel_principal, user_id):
        super().__init__(panel_principal)
        self.user_id = user_id
        self.master_panel = panel_principal.master
        self.configure(fg_color="#f4f8f7")
        
        # Variables de estado
        self.proceso_activo = None
        self.detener_monitoreo = threading.Event()
        self._hilo_monitoreo = None
        
        # Variables para la animación
        self.fases_crecimiento = {}
        self.tiempo_inicio_proceso = None
        self.ultima_actualizacion = 0
        self.proceso_finalizado = False
        
        # Configurar interfaz
        self._crear_interfaz()
        
        # Registrar este panel para recibir mensajes seriales
        self.master_panel.registrar_panel_serial("monitoreo", self)
        
        # Iniciar monitoreo
        self.iniciar_monitoreo()

    def _crear_interfaz(self):
        """Crea la interfaz simplificada del panel de monitoreo"""
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Frame para controles
        self.controles_frame = ctk.CTkFrame(self)
        self.controles_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Título
        ctk.CTkLabel(
            self.controles_frame,
            text="ANIMACIÓN DE CRECIMIENTO POR FASES",
            font=ctk.CTkFont(size=14, weight="bold")
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
        
        # Frame para la gráfica
        self.grafica_frame = ctk.CTkFrame(self)
        self.grafica_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Gráfica de crecimiento
        self.fig_crecimiento = Figure(figsize=(10, 6), dpi=100)
        self.ax_crecimiento = self.fig_crecimiento.add_subplot(111)
        self.canvas_crecimiento = FigureCanvasTkAgg(self.fig_crecimiento, master=self.grafica_frame)
        self.canvas_crecimiento.get_tk_widget().pack(fill="both", expand=True)
        
        # Configurar gráfica inicial
        self._configurar_grafica_inicial()

    def _configurar_grafica_inicial(self):
        """Configura la gráfica con estado inicial"""
        self.ax_crecimiento.clear()
        self.ax_crecimiento.set_title("CRECIMIENTO POR FASES", pad=10, fontsize=14, weight='bold')
        self.ax_crecimiento.set_xlabel("Tiempo (segundos)", labelpad=10)
        self.ax_crecimiento.set_ylabel("Espesor (u.a.)", labelpad=10)
        self.ax_crecimiento.grid(True, linestyle='--', alpha=0.7)
        
        # Mostrar mensaje inicial
        self.ax_crecimiento.text(0.5, 0.5, 'Seleccione un proceso para comenzar', 
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
                WHERE user_id=? 
                ORDER BY fecha_inicio DESC
                LIMIT 10
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

    def _cambiar_proceso_monitoreado(self, choice):
        """Cambia el proceso que se está monitoreando"""
        if choice in ["-- Seleccione --", "-- Error --"]:
            self._configurar_grafica_inicial()
            return
            
        self.proceso_activo = choice
        self.detener_monitoreo.set()  # Detener cualquier monitoreo previo
        
        # Reiniciar variables
        self.fases_crecimiento = {}
        self.tiempo_inicio_proceso = None
        self.ultima_actualizacion = 0
        self.proceso_finalizado = False
        
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
        """Monitorea el proceso seleccionado y actualiza la animación"""
        while not self.detener_monitoreo.is_set() and self.proceso_activo:
            try:
                conn = sqlite3.connect("procesos.db")
                cursor = conn.cursor()
                
                # Obtener todos los registros del proceso ordenados por tiempo
                cursor.execute("""
                    SELECT 
                        valvula_activada, 
                        estado_valvula, 
                        tiempo_valvula,
                        hora_instruccion,
                        tipo_proceso,
                        fase,
                        ciclos,
                        fecha_fin
                    FROM procesos 
                    WHERE proceso_id=?
                    ORDER BY hora_instruccion ASC
                """, (self.proceso_activo,))
                
                registros = cursor.fetchall()
                conn.close()
                
                # Verificar si el proceso ha finalizado
                proceso_finalizado = any(reg[7] != '' for reg in registros if reg[7] is not None)
                
                if proceso_finalizado and not self.proceso_finalizado:
                    self.proceso_finalizado = True
                    self.after(0, self.agregar_notificacion, "Proceso finalizado detectado")
                
                # Procesar datos y actualizar animación
                self.after(0, self._procesar_datos_animacion, registros)
                
                # Diferentes intervalos según si el proceso está activo o finalizado
                time.sleep(0.5 if not self.proceso_finalizado else 2)
                
            except Exception as e:
                print(f"Error al monitorear: {e}")
                time.sleep(2)

    def _procesar_datos_animacion(self, registros):
        """Procesa los datos del proceso para la animación"""
        if not registros:
            return
            
        # Obtener tiempo de inicio del proceso
        tiempo_inicio_proceso = datetime.strptime(registros[0][3], '%Y-%m-%d %H:%M:%S')
        
        # Inicializar estructura de fases
        fases = {}
        for reg in registros:
            fase_num = reg[5]  # Número de fase
            if fase_num not in fases:
                fases[fase_num] = {
                    'valvulas': {},
                    'inicio': None,
                    'fin': None,
                    'tiempo_total': 0,
                    'elementos': set()
                }
            
            # Extraer elemento de "Válvula X"
            valvula_nombre = reg[0]
            elemento = valvula_nombre.replace("Válvula ", "").strip() if "Válvula" in valvula_nombre else valvula_nombre
            
            # Calcular tiempo de apertura total (tiempo * ciclos)
            tiempo_valvula = reg[2] if reg[2] is not None else 0
            ciclos = reg[6] if reg[6] is not None else 1
            tiempo_total = tiempo_valvula * ciclos
            
            # Actualizar información de la fase
            fases[fase_num]['elementos'].add(elemento)
            fases[fase_num]['tiempo_total'] += tiempo_total
            
            # Registrar válvula
            if elemento not in fases[fase_num]['valvulas']:
                fases[fase_num]['valvulas'][elemento] = {
                    'tiempo': tiempo_valvula,
                    'ciclos': ciclos,
                    'estado': reg[1],
                    'tiempo_total': tiempo_total
                }
            
            # Actualizar tiempos de inicio/fin de fase
            hora_instruccion = datetime.strptime(reg[3], '%Y-%m-%d %H:%M:%S')
            tiempo_relativo = (hora_instruccion - tiempo_inicio_proceso).total_seconds()
            
            if fases[fase_num]['inicio'] is None or tiempo_relativo < fases[fase_num]['inicio']:
                fases[fase_num]['inicio'] = tiempo_relativo
                
            if reg[1] == 'C' or reg[7] != '':  # Si está cerrado o proceso finalizado
                if fases[fase_num]['fin'] is None or tiempo_relativo > fases[fase_num]['fin']:
                    fases[fase_num]['fin'] = tiempo_relativo
        
        # Calcular espesor proporcional al tiempo total de la fase
        tiempo_max_fase = max(fase['tiempo_total'] for fase in fases.values()) if fases else 1
        
        # Actualizar datos para la animación
        for fase_num, fase_data in fases.items():
            if fase_num not in self.fases_crecimiento:
                # Calcular espesor proporcional al tiempo total
                espesor = max(0.5, (fase_data['tiempo_total'] / tiempo_max_fase) * 3)
                
                self.fases_crecimiento[fase_num] = {
                    'elementos': list(fase_data['elementos']),
                    'valvulas': fase_data['valvulas'],
                    'tiempo_inicio': fase_data['inicio'],
                    'tiempo_fin': fase_data['fin'],
                    'tiempo_total': fase_data['tiempo_total'],
                    'espesor': espesor,
                    'color': self._obtener_color_fase(fase_num)
                }
        
        # Calcular tiempo transcurrido
        if self.tiempo_inicio_proceso is None:
            self.tiempo_inicio_proceso = time.time()
            
        tiempo_transcurrido = 0
        if not self.proceso_finalizado:
            tiempo_transcurrido = time.time() - self.tiempo_inicio_proceso
        else:
            # Usar el tiempo final del proceso si ha terminado
            tiempo_transcurrido = max(fase['tiempo_fin'] for fase in self.fases_crecimiento.values() if fase['tiempo_fin'] is not None)
        
        # Actualizar animación
        if time.time() - self.ultima_actualizacion >= 0.5:  # Actualizar cada 0.5 segundos
            self._dibujar_animacion(tiempo_transcurrido)
            self.ultima_actualizacion = time.time()

    def _obtener_color_fase(self, fase_num):
        """Devuelve un color único para cada fase"""
        colores = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
            '#c49c94', '#f7b6d2', '#dbdb8d', '#9edae5', '#393b79'
        ]
        return colores[(int(fase_num) - 1) % len(colores)]

    def _dibujar_animacion(self, tiempo_transcurrido):
        """Dibuja la animación de crecimiento por fases"""
        self.ax_crecimiento.clear()
        
        # Configuración básica de la gráfica
        self.ax_crecimiento.set_title(f"CRECIMIENTO: {self.proceso_activo}", pad=10, fontsize=14, weight='bold')
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
        max_tiempo = max([fase['tiempo_inicio'] + fase['tiempo_total'] + 10 for fase in self.fases_crecimiento.values()] + [tiempo_transcurrido + 10])
        max_espesor = sum(fase['espesor'] for fase in self.fases_crecimiento.values()) + 1
        self.ax_crecimiento.set_xlim(0, max_tiempo)
        self.ax_crecimiento.set_ylim(0, max_espesor)
        
        # Dibujar cada fase
        espesor_acumulado = 0
        for fase_num, fase_data in sorted(self.fases_crecimiento.items(), key=lambda x: int(x[0])):
            # Determinar estado de la fase
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
                
                # Dibujar la fase principal
                rect = Rectangle((fase_data['tiempo_inicio'], espesor_acumulado),
                               tiempo_fin_dibujo - fase_data['tiempo_inicio'],
                               fase_data['espesor'],
                               facecolor=fase_data['color'],
                               edgecolor='black',
                               alpha=alpha)
                self.ax_crecimiento.add_patch(rect)
                
                # Dibujar subdivisiones por ciclos si existen
                for elemento, valvula in fase_data['valvulas'].items():
                    if valvula['ciclos'] > 1:
                        for ciclo in range(valvula['ciclos']):
                            ciclo_inicio = fase_data['tiempo_inicio'] + ciclo * valvula['tiempo']
                            ciclo_fin = min(ciclo_inicio + valvula['tiempo'], tiempo_fin_dibujo)
                            
                            if ciclo_fin > ciclo_inicio:
                                # Dibujar subdivisión
                                self.ax_crecimiento.axvline(x=ciclo_inicio, color='white', linestyle=':', alpha=0.5)
                                
                                # Etiqueta de ciclo
                                if ciclo % 2 == 0:  # Mostrar solo ciclos pares para evitar saturación
                                    self.ax_crecimiento.text(
                                        ciclo_inicio + (ciclo_fin - ciclo_inicio)/2,
                                        espesor_acumulado + fase_data['espesor']/2,
                                        f"C{ciclo+1}",
                                        ha='center', va='center',
                                        color='black',
                                        fontsize=6,
                                        bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
                                    )
                
                # Etiqueta de fase
                texto = f"Fase {fase_num}\n({', '.join(fase_data['elementos'])})\n{int(fase_data['tiempo_total'])}s"
                self.ax_crecimiento.text(
                    fase_data['tiempo_inicio'] + (tiempo_fin_dibujo - fase_data['tiempo_inicio'])/2,
                    espesor_acumulado + fase_data['espesor']/2,
                    texto,
                    ha='center', va='center',
                    color='black',
                    fontsize=8,
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
                )
                
                espesor_acumulado += fase_data['espesor']
        
        # Dibujar línea de tiempo actual (solo si el proceso no ha finalizado)
        if not self.proceso_finalizado:
            self.ax_crecimiento.axvline(x=tiempo_transcurrido, color='red', linestyle='--', alpha=0.7, linewidth=2)
        
        # Añadir leyenda
        handles = []
        labels = []
        for fase_num, fase_data in sorted(self.fases_crecimiento.items(), key=lambda x: int(x[0])):
            handles.append(Rectangle((0, 0), 1, 1, facecolor=fase_data['color']))
            labels.append(f"Fase {fase_num} ({', '.join(fase_data['elementos'])}) - {int(fase_data['tiempo_total'])}s")
        
        self.ax_crecimiento.legend(handles, labels, title="Fases", 
                                 bbox_to_anchor=(1.05, 1), loc='upper left',
                                 fontsize=8)
        
        self.fig_crecimiento.tight_layout()
        self.canvas_crecimiento.draw()

    def agregar_notificacion(self, mensaje):
        """Agrega un mensaje al área de notificaciones (si existe)"""
        if hasattr(self, 'notificaciones_text'):
            self.notificaciones_text.configure(state="normal")
            self.notificaciones_text.insert("end", f"- {mensaje}\n")
            self.notificaciones_text.configure(state="disabled")
            self.notificaciones_text.see("end")

    def procesar_mensaje(self, mensaje):
        """Procesa mensajes seriales (opcional para actualizaciones en tiempo real)"""
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
            if hasattr(self, 'master_panel') and hasattr(self.master_panel, 'desregistrar_panel_serial'):
                self.master_panel.desregistrar_panel_serial("monitoreo")
        except Exception as e:
            print(f"Error en limpieza de Monitoreo: {e}")