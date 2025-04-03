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

    def agregar_fase(self, nombre_fase=None):
        """ Agrega una nueva pestaña al Tabview con botones para agregar/eliminar """
        if nombre_fase is None:
            self.fase_contador += 1
            nombre_fase = f"Fase {self.fase_contador}"

        self.tabview.add(nombre_fase)

        # Botón para agregar nueva fase
        boton_agregar = ctk.CTkButton(master=self.tabview.tab(nombre_fase), text="Agregar Fase", fg_color="#06918A", 
                                      command=self.agregar_fase)
        boton_agregar.pack(padx=20, pady=10)

        # Botón para eliminar esta fase
        boton_eliminar = ctk.CTkButton(master=self.tabview.tab(nombre_fase), text="Eliminar Fase", fg_color="#D9534F", 
                                       command=lambda: self.eliminar_fase(nombre_fase))
        boton_eliminar.pack(padx=20, pady=10)

        # Cambiar a la nueva pestaña creada
        self.tabview.set(nombre_fase)

    def eliminar_fase(self, nombre_fase):
        """ Elimina una pestaña si hay más de una """
        if len(self.tabview._name_list) > 1:  # Verifica que no sea la última pestaña
            self.tabview.delete(nombre_fase)
        else:
            print("No puedes eliminar la última fase")
