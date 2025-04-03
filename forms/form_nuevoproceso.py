import customtkinter as ctk
import sys
sys.path.append('d:/Python_Proyectos/INTER_C3')
import util.generic as utl

COLOR_CUERPO_PRINCIPAL = "#f4f8f7"

class FormNuevoProceso(ctk.CTk):
    
    def __init__(self, panel_principal, logo):
        super().__init__()

        self.fase_contador = 1  # Inicia con solo una fase

        # Frame scrolleable
        self.scrollable_frame = ctk.CTkScrollableFrame(panel_principal)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabview con solo una pestaña inicial
        self.tabview = ctk.CTkTabview(master=self.scrollable_frame)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.agregar_fase("Fase 1")  # Inicia con la primera fase

        # Contenedor para los botones generales (Ejecutar, Pausar, Reiniciar)
        self.botones_generales_frame = ctk.CTkFrame(panel_principal)
        self.botones_generales_frame.pack(fill="x", padx=10, pady=10)

        self.ejecutar_btn = ctk.CTkButton(self.botones_generales_frame, text="Ejecutar Rutina", fg_color="#06918A")
        self.ejecutar_btn.pack(side="right", padx=5, pady=5)

        self.pausar_btn = ctk.CTkButton(self.botones_generales_frame, text="Pausar Rutina", fg_color="#F0AD4E")
        self.pausar_btn.pack(side="right", padx=5, pady=5)

        self.reiniciar_btn = ctk.CTkButton(self.botones_generales_frame, text="Reiniciar Rutina", fg_color="#D9534F")
        self.reiniciar_btn.pack(side="right", padx=5, pady=5)

    def agregar_fase(self, nombre_fase=None):
        """ Agrega una nueva pestaña al Tabview """
        if nombre_fase is None:
            self.fase_contador += 1
            nombre_fase = f"Fase {self.fase_contador}"

        self.tabview.add(nombre_fase)

        frame_fase = ctk.CTkFrame(self.tabview.tab(nombre_fase))
        frame_fase.pack(fill="both", expand=True, padx=10, pady=10)

        for i in range(1, 10):  # Crear 9 válvulas
            fila = ctk.CTkFrame(frame_fase)
            fila.pack(fill="x", padx=5, pady=2)

            switch = ctk.CTkSwitch(fila, text=str(i))
            switch.pack(side="left", padx=5)

            for _ in range(3):  # Campos de apertura, cierre y ciclos deseados
                entry = ctk.CTkEntry(fila, width=50, placeholder_text="####")
                entry.pack(side="left", padx=5)

        # Frame de botones de fase
        botones_frame = ctk.CTkFrame(self.tabview.tab(nombre_fase))
        botones_frame.pack(side="bottom", pady=10)

        boton_agregar = ctk.CTkButton(botones_frame, text="Agregar Fase", fg_color="#06918A", command=self.agregar_fase)
        boton_agregar.pack(side="right", padx=5)

        boton_eliminar = ctk.CTkButton(botones_frame, text="Eliminar Fase", fg_color="#D9534F", 
                                       command=lambda: self.eliminar_fase(nombre_fase))
        boton_eliminar.pack(side="right", padx=5)

        self.tabview.set(nombre_fase)

    def eliminar_fase(self, nombre_fase):
        """ Elimina una pestaña si hay más de una """
        if len(self.tabview._name_list) > 1:
            self.tabview.delete(nombre_fase)
        else:
            print("No puedes eliminar la última fase")
