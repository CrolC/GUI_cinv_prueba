import customtkinter as ctk
from PIL import Image
import sys
from tkinter import font
sys.path.append('d:/Python_Proyectos/INTER_C3')
from forms.form_nuevoproceso import FormNuevoProceso
from forms.form_paneldecontrol import FormPaneldeControl
from forms.form_historial import FormHistorial
from forms.form_monitoreo import FormMonitoreo
from forms.form_diagnostico import FormDiagnostico

COLOR_BARRA_SUPERIOR = "#1a1e23"
COLOR_MENU_LATERAL = "#1f3334"
COLOR_CUERPO_PRINCIPAL = "#f4f8f7"
COLOR_MENU_CURSOR_ENCIMA = "#18a9b1"

class MasterPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config_window()
        
        self.logo = self.leer_imagen("d:/Python_Proyectos/INTER_C3/imagenes/logocinves_predeterm.png", (400, 136))
        self.perfil = self.leer_imagen("d:/Python_Proyectos/INTER_C3/imagenes/Perfil.png", (100, 100))
        self.predeterminada = self.leer_imagen("d:/Python_Proyectos/INTER_C3/imagenes/predeterm.png", (300, 100))
        
        self.paneles()
        self.controles_barra_superior()
        self.controles_menu_lateral()
        self.controles_cuerpo()

    def leer_imagen(self, path, size): 
        try:
            pil_image = Image.open(path)
            pil_image = pil_image.resize(size, Image.LANCZOS)
            return ctk.CTkImage(pil_image, size=size)
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
            return None
    
    def centrar_ventana(self, aplicacion_ancho, aplicacion_largo):
        pantall_ancho = self.winfo_screenwidth()
        pantall_largo = self.winfo_screenheight()
        x = int((pantall_ancho / 2) - (aplicacion_ancho / 2))
        y = int((pantall_largo / 2) - (aplicacion_largo / 2))
        self.geometry(f"{aplicacion_ancho}x{aplicacion_largo}+{x}+{y}")

    def config_window(self):
        self.title('Cinvestav')
        try:
            self.iconbitmap("d:/Python_Proyectos/INTER_C3/imagenes/logo.ico")
        except Exception as e:
            print(f"Error al cargar el ícono: {e}")
        self.centrar_ventana(1024, 600)
    
    def paneles(self):        
        # FRAMES PRINCIPALES: barra superior, menú lateral y cuerpo principal
        self.barra_superior = ctk.CTkFrame(self, fg_color=COLOR_BARRA_SUPERIOR, height=50)
        self.barra_superior.pack(side=ctk.TOP, fill='both')
        
        self.menu_lateral = ctk.CTkFrame(self, fg_color=COLOR_MENU_LATERAL, width=150)
        self.menu_lateral.pack(side=ctk.LEFT, fill='both', expand=False)
        
        self.cuerpo_principal = ctk.CTkFrame(self, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.cuerpo_principal.pack(side=ctk.RIGHT, fill='both', expand=True)
    
    def controles_barra_superior(self):
        font_awesome = ctk.CTkFont(family="FontAwesome", size=12)
        
        self.labelTitulo = ctk.CTkLabel(self.barra_superior, text="Sistema MBE", text_color="white", font=ctk.CTkFont(family="Roboto", size=15))
        self.labelTitulo.pack(side=ctk.LEFT, padx=10, pady=10)
        
        self.buttonMenuLateral = ctk.CTkButton(self.barra_superior, text="\uf022", font=font_awesome, command=self.toggle_panel, fg_color=COLOR_BARRA_SUPERIOR, text_color="white")
        self.buttonMenuLateral.pack(side=ctk.LEFT, padx=5)
        
        self.labelInfo = ctk.CTkLabel(self.barra_superior, text="Crecimiento por Epitaxia de Haces Moleculares", text_color="white", font=ctk.CTkFont(family="Roboto", size=10))
        self.labelInfo.pack(side=ctk.RIGHT, padx=10, pady=10)
    
    def controles_menu_lateral(self):
        ancho_menu = 20
        alto_menu = 2

        font_awesome = ctk.CTkFont(family="FontAwesome", size=15)
        
        try:
            self.labelPerfil = ctk.CTkLabel(self.menu_lateral, image=self.perfil, text="", fg_color=COLOR_MENU_LATERAL) if self.perfil else ctk.CTkLabel(self.menu_lateral, text="Perfil", fg_color=COLOR_MENU_LATERAL)
            self.labelPerfil.pack(side=ctk.TOP, pady=10)
        except Exception as e:
            print(f"Error al crear label de perfil: {e}")
        
        buttons_info = [ 
            ("Nuevo proceso", "\uf144", self.abrir_nuevoproceso),  
            ("Historial", "\uf07c", self.abrir_historial), 
            ("Diagnóstico", "\uf044", self.abrir_diagnostico), 
            ("Panel de Control", "\uf080", self.abrir_paneldecontrol), 
            ("Monitoreo del Proceso", "\uf017", self.abrir_monitoreo) 
        ]
        
        for text, icon, command in buttons_info:  
            try:
                button = ctk.CTkButton(self.menu_lateral, text=f"  {icon}    {text}", font=font_awesome, anchor="w", fg_color=COLOR_MENU_LATERAL, text_color="white", hover_color=COLOR_MENU_CURSOR_ENCIMA, command=command)
                button.pack(side=ctk.TOP, fill="x", padx=5, pady=5)
            except Exception as e:
                print(f"Error al crear botón {text}: {e}")
    
    def controles_cuerpo(self):
        try:
            label = ctk.CTkLabel(self.cuerpo_principal, image=self.logo, text="", fg_color=COLOR_CUERPO_PRINCIPAL)
            label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error al crear el cuerpo principal: {e}")

    def toggle_panel(self):
        if self.menu_lateral.winfo_ismapped():
            self.menu_lateral.pack_forget()
        else:
            self.menu_lateral.pack(side=ctk.LEFT, fill='both', expand=False)  

    
    def abrir_nuevoproceso(self):
        self.limpiar_panel(self.cuerpo_principal)
        FormNuevoProceso(self.cuerpo_principal, self.predeterminada)
    
    def abrir_paneldecontrol(self):
        self.limpiar_panel(self.cuerpo_principal)
        FormPaneldeControl(self.cuerpo_principal, self.predeterminada)
    
    def abrir_historial(self):
        self.limpiar_panel(self.cuerpo_principal)
        FormHistorial(self.cuerpo_principal, self.predeterminada)

    #P Monitoreo del proceso
    def abrir_monitoreo(self):
        self.limpiar_panel(self.cuerpo_principal)
        FormMonitoreo(self.cuerpo_principal, self.predeterminada)

    #P Diagnostico
    def abrir_diagnostico(self):
        self.limpiar_panel(self.cuerpo_principal)
        FormDiagnostico(self.cuerpo_principal, self.predeterminada)
    
    def limpiar_panel(self, panel):
        for widget in panel.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = MasterPanel()
    app.mainloop()
