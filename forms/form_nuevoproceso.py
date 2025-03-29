import customtkinter as ctk
import sys
sys.path.append('d:/Python_Proyectos/INTER_C3')
import util.generic as utl

COLOR_CUERPO_PRINCIPAL = "#f4f8f7"

class FormNuevoProceso(ctk.CTk):
    
    def __init__(self, panel_principal, logo):
        super().__init__()

        # Subdivisión de la ventana
        self.barra_superior = ctk.CTkFrame(panel_principal)
        self.barra_superior.pack(side=ctk.TOP, fill=ctk.X, expand=False)

        self.barra_inferior = ctk.CTkFrame(panel_principal)
        self.barra_inferior.pack(side=ctk.BOTTOM, fill='both', expand=True)

        tabview = ctk.CTkTabview(master=self.barra_superior)
        tabview.pack(padx=20, pady=20)

        tabview.add("Fase 1")  
        tabview.add("Fase 2") 
        tabview.set("Fase 2")  

        botonA = ctk.CTkButton(master=tabview.tab("Fase 1") )
        botonA.pack(padx=20, pady=20)
        botonA.configure(text="Nueva Fase", fg_color="#06918A")

        botonC = ctk.CTkButton(master=tabview.tab("Fase 1") )
        botonC.pack(padx=20, pady=20)
        botonC.configure(text="Fase 2", fg_color="#06918A")
        
        botonB = ctk.CTkButton(master=tabview.tab("Fase 2"))
        botonB.pack(padx=20, pady=20)
        botonB.configure(text="Fase 1", fg_color="#06918A")


    