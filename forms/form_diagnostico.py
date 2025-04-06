import customtkinter as ctk
import sys
import time

class FormDiagnostico(ctk.CTkScrollableFrame):
    def __init__(self, panel_principal, predeterminada):
        super().__init__(panel_principal)
        self.predeterminada = predeterminada

        self.valvulas_activas = {}  # Diccionario para guardar valvulas y sus tiempos

        # FRAME 1: Estado del Sistema
        self.frame_estado = ctk.CTkFrame(self)
        self.frame_estado.pack(pady=10, padx=10, fill='x')

        ctk.CTkLabel(self.frame_estado, text='ESTADO DEL SISTEMA', fg_color='gray', corner_radius=5).pack(fill='x')

        self.estado_micro = ctk.CTkLabel(self.frame_estado, text='FUNCIONAMIENTO ÓPTIMO', fg_color='green', corner_radius=5)
        self.estado_micro.pack(pady=5)

        self.estado_comunicacion = ctk.CTkLabel(self.frame_estado, text='COMUNICACIÓN ESTABLE', fg_color='green', corner_radius=5)
        self.estado_comunicacion.pack(pady=5)

        # FRAME 2: Válvulas Activas
        self.frame_valvulas = ctk.CTkFrame(self)
        self.frame_valvulas.pack(pady=10, padx=10, fill='both', expand=True)

        ctk.CTkLabel(self.frame_valvulas, text='VÁLVULAS ACTIVAS', fg_color='gray', corner_radius=5).pack(fill='x')

        self.valvula_widgets = {}  # Almacena widgets por válvula

        # Iniciar actualización del contador
        self.actualizar_tiempos()

    def agregar_valvula_activa(self, nombre_valvula):
        if nombre_valvula not in self.valvulas_activas:
            self.valvulas_activas[nombre_valvula] = time.time()

            frame = ctk.CTkFrame(self.frame_valvulas)
            frame.pack(fill='x', padx=5, pady=2)

            lbl_nombre = ctk.CTkLabel(frame, text=nombre_valvula, width=100)
            lbl_nombre.pack(side='left', padx=5)

            lbl_estado = ctk.CTkLabel(frame, text='ACTIVA', fg_color='green', corner_radius=5, width=100)
            lbl_estado.pack(side='left', padx=5)

            lbl_tiempo = ctk.CTkLabel(frame, text='00:00', width=100)
            lbl_tiempo.pack(side='left', padx=5)

            self.valvula_widgets[nombre_valvula] = lbl_tiempo

    def actualizar_tiempos(self):
        now = time.time()
        for nombre, inicio in self.valvulas_activas.items():
            tiempo_segundos = int(now - inicio)
            minutos = tiempo_segundos // 60
            segundos = tiempo_segundos % 60
            tiempo_str = f"{minutos:02}:{segundos:02}"
            if nombre in self.valvula_widgets:
                self.valvula_widgets[nombre].configure(text=tiempo_str)

        self.after(1000, self.actualizar_tiempos)

    def actualizar_estado_micro(self, texto, color="green"):
        self.estado_micro.configure(text=texto, fg_color=color)

    def actualizar_estado_comunicacion(self, texto, color="green"):
        self.estado_comunicacion.configure(text=texto, fg_color=color)
