import customtkinter as ctk
import sys
from PIL import Image, ImageTk
sys.path.append('d:/Python_Proyectos/INTER_C3')
import util.generic as utl

class FormDiagnostico(ctk.CTkScrollableFrame):
    def __init__(self, panel_principal, predeterminada):
        super().__init__(panel_principal)
        self.predeterminada = predeterminada

        # Elementos para el estado de las válvulas
        frame_valvulas = ctk.CTkFrame(self)
        frame_valvulas.pack(pady=10, padx=10, fill='both', expand=True)
        ctk.CTkLabel(frame_valvulas, text='ESTADO DE LAS VÁLVULAS', fg_color='gray', corner_radius=5).pack(fill='x')

        elementos = ["Al", "As", "Ga", "I", "N", "Mn", "Be", "Mg", "Si"]

        for i, elemento in enumerate(elementos):
            fila = ctk.CTkFrame(frame_valvulas)
            fila.pack(fill='x', padx=5, pady=2)

            ctk.CTkLabel(fila, text=elemento, width=50).pack(side='left', padx=5)
            entry = ctk.CTkEntry(fila, width=50, placeholder_text='####')
            entry.pack(side='left', padx=5)
            
            indicador_activo = ctk.CTkLabel(fila, text='●', fg_color='green', width=20)
            indicador_activo.pack(side='left', padx=5)
            indicador_inactivo = ctk.CTkLabel(fila, text='●', fg_color='gray', width=20)
            indicador_inactivo.pack(side='left', padx=5)

        # Estado del Microcontrolador
        frame_micro = ctk.CTkFrame(self)
        frame_micro.pack(pady=10, padx=10, fill='both', expand=True)
        ctk.CTkLabel(frame_micro, text='ESTADO DEL MICROCONTROLADOR', fg_color='gray', corner_radius=5).pack(fill='x')
        
        self.estado_micro = ctk.CTkLabel(frame_micro, text='FUNCIONAMIENTO ÓPTIMO', fg_color='green', corner_radius=5)
        self.estado_micro.pack(pady=5)

        # Semáforo del microcontrolador
        self.semaforo_micro = ctk.CTkLabel(frame_micro, text='●', fg_color='green', width=20)
        self.semaforo_micro.pack()

        # Estado del Proceso
        frame_proceso = ctk.CTkFrame(self)
        frame_proceso.pack(pady=10, padx=10, fill='both', expand=True)
        ctk.CTkLabel(frame_proceso, text='ESTADO DEL PROCESO', fg_color='gray', corner_radius=5).pack(fill='x')
        
        self.estado_proceso = ctk.CTkLabel(frame_proceso, text='🟡 ESPERANDO EJECUCIÓN DE RUTINA...', fg_color='yellow', corner_radius=5)
        self.estado_proceso.pack(pady=5)
        
        self.modo_label = ctk.CTkLabel(frame_proceso, text='MODO: AUTOMÁTICO')
        self.modo_label.pack()
        
        self.semaforo_proceso = ctk.CTkLabel(frame_proceso, text='●', fg_color='yellow', width=20)
        self.semaforo_proceso.pack()

    def actualizar_estado_micro(self, estado):
        estados = {
            "optimo": ("FUNCIONAMIENTO ÓPTIMO", "green"),
            "falla_com": ("FALLA DE COMUNICACIÓN", "yellow"),
            "falla_micro": ("FALLA EN MICROCONTROLADOR", "red")
        }
        if estado in estados:
            texto, color = estados[estado]
            self.estado_micro.configure(text=texto, fg_color=color)
            self.semaforo_micro.configure(fg_color=color)
    
    def actualizar_estado_proceso(self, modo, estado):
        modos = {"manual": "MODO: MANUAL", "automatico": "MODO: AUTOMÁTICO"}
        estados = {
            "espera": ("🟡 ESPERANDO EJECUCIÓN DE RUTINA...", "yellow"),
            "ejecucion": ("🟢 RUTINA EN EJECUCIÓN", "green"),
            "finalizado": ("🔴 RUTINA FINALIZADA", "red")
        }
        
        if modo in modos:
            self.modo_label.configure(text=modos[modo])
        if estado in estados:
            texto, color = estados[estado]
            self.estado_proceso.configure(text=texto, fg_color=color)
            self.semaforo_proceso.configure(fg_color=color)
