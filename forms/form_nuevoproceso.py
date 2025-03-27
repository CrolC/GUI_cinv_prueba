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

        # Título de la ventana
        #self.labelTitulo = ctk.CTkLabel(self.barra_superior, text="En construcción", text_color="black", font=ctk.CTkFont(family="Roboto", size=15))
        #self.labelTitulo.pack(side=ctk.TOP, pady=10)

        # Imagen en la parte inferior
        #self.label_imagen = ctk.CTkLabel(self.barra_inferior, image=logo, text="")
        #self.label_imagen.place(x=0, y=0, relwidth=1, relheight=1)
        #self.label_imagen.config(bg=COLOR_CUERPO_PRINCIPAL)

        tabview = ctk.CTkTabview(master=self.barra_superior)#FormNuevoProceso)
        tabview.pack(padx=20, pady=20)

        tabview.add("Fase 1")  # add tab at the end
        tabview.add("Fase 2")  # add tab at the end
        tabview.set("Fase 2")  # set currently visible tab

        botonA = ctk.CTkButton(master=tabview.tab("Fase 1") )
        botonA.pack(padx=20, pady=20)
        botonA.configure(text="Nueva Fase", fg_color="#06918A")

        botonC = ctk.CTkButton(master=tabview.tab("Fase 1") )
        botonC.pack(padx=20, pady=20)
        botonC.configure(text="Fase 2", fg_color="#06918A")
        
        botonB = ctk.CTkButton(master=tabview.tab("Fase 2"))
        botonB.pack(padx=20, pady=20)
        botonB.configure(text="Fase 1", fg_color="#06918A")


    