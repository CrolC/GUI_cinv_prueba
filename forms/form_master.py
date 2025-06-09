import customtkinter as ctk
from PIL import Image
import sys
import threading
from tkinter import messagebox
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
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self._imagenes = []
        self.paneles_activos = {}  # Diccionario para mantener los paneles
        self.lock = threading.Lock()  # Para sincronización de threads
        self.panel_actual = None  # Referencia al panel actualmente visible
        self.bloqueo_activo = False  # Nuevo estado para rastrear bloqueo por hardware
        self.panel_con_bloqueo = None  # Panel que activó el bloqueo
        
        self.config_window()
        self.logo = self.leer_imagen("d:/Python_Proyectos/INTER_C3/imagenes/logocinves_predeterm.png", (400, 136))
        self.perfil = self.leer_imagen("d:/Python_Proyectos/INTER_C3/imagenes/Perfil.png", (100, 100))
        self.predeterminada = self.leer_imagen("d:/Python_Proyectos/INTER_C3/imagenes/predeterm.png", (300, 100))
        
        self.paneles()
        self.controles_barra_superior()
        self.controles_menu_lateral()
        self.controles_cuerpo()

    def on_close(self):
        """Maneja el cierre seguro de la ventana"""
        try:
            # Cancelar eventos pendientes
            for id in self.tk.eval('after info').split():
                try:
                    self.after_cancel(id)
                except:
                    pass
        
            # Limpiar todos los paneles activos
            for nombre, panel in self.paneles_activos.items():
                if hasattr(panel, '__del__'):
                    panel.__del__()
                if hasattr(panel, 'destroy'):
                    panel.destroy()
            
            # Liberar recursos
            if hasattr(self, '_imagenes'):
                del self._imagenes
        
            # Cierre en orden
            self.quit()
            self.destroy()
        except Exception as e:
            print(f"Error durante el cierre: {e}")
            import os
            os._exit(0)

    def leer_imagen(self, path, size): 
        try:
            pil_image = Image.open(path)
            pil_image = pil_image.resize(size, Image.LANCZOS)
            image = ctk.CTkImage(pil_image, size=size)
            # Imagen como atributo
            if not hasattr(self, '_imagenes'):
                self._imagenes = []
            self._imagenes.append(image)
            return image
        except Exception as e:
            print(f"Error al cargar la imagen {path}: {e}")
            # Crea una imagen de placeholder
            placeholder = ctk.CTkImage(Image.new('RGB', size, (200, 200, 200)), size=size)
            if not hasattr(self, '_imagenes'):
                self._imagenes = []
            self._imagenes.append(placeholder)
            return placeholder

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
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def paneles(self):        
        # FRAMES PRINCIPALES: barra superior, menú lateral y cuerpo principal
        self.barra_superior = ctk.CTkFrame(self, fg_color=COLOR_BARRA_SUPERIOR, height=50)
        self.barra_superior.pack(side=ctk.TOP, fill='both')
        
        self.menu_lateral = ctk.CTkFrame(self, fg_color=COLOR_MENU_LATERAL, width=150)
        self.menu_lateral.pack(side=ctk.LEFT, fill='both', expand=False)
        
        self.cuerpo_principal = ctk.CTkFrame(self, fg_color=COLOR_CUERPO_PRINCIPAL)
        self.cuerpo_principal.pack(side=ctk.RIGHT, fill='both', expand=True)
        self.cuerpo_principal.grid_rowconfigure(0, weight=1)
        self.cuerpo_principal.grid_columnconfigure(0, weight=1)
    
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
            if hasattr(self, 'perfil') and self.perfil:
                self.labelPerfil = ctk.CTkLabel(self.menu_lateral, image=self.perfil, text="", fg_color=COLOR_MENU_LATERAL)
            else:
                self.labelPerfil = ctk.CTkLabel(self.menu_lateral, text="Perfil", fg_color=COLOR_MENU_LATERAL)
            self.labelPerfil.pack(side=ctk.TOP, pady=10)
        except Exception as e:
            print(f"Error al crear label de perfil: {e}")
            self.labelPerfil = ctk.CTkLabel(self.menu_lateral, text="Perfil", fg_color=COLOR_MENU_LATERAL)
            self.labelPerfil.pack(side=ctk.TOP, pady=10)
        
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
        """Muestra el panel inicial (logo) sin destruir otros"""
        if not hasattr(self, 'panel_inicial'):
            try:
                if hasattr(self, 'logo') and self.logo:
                    self.panel_inicial = ctk.CTkLabel(self.cuerpo_principal, image=self.logo, text="", fg_color=COLOR_CUERPO_PRINCIPAL)
                else:
                    self.panel_inicial = ctk.CTkLabel(self.cuerpo_principal, text="Bienvenido al Sistema MBE", font=ctk.CTkFont(size=20), fg_color=COLOR_CUERPO_PRINCIPAL)
                
                self.panel_inicial.pack(fill="both", expand=True)
                self.panel_actual = self.panel_inicial
            except Exception as e:
                print(f"Error al crear el cuerpo principal: {e}")

    def verificar_ejecucion(self, nombre_panel):
        """Verifica si se puede enviar comandos a las válvulas."""
        with self.lock:
            if self.bloqueo_activo and self.panel_con_bloqueo != nombre_panel:
                messagebox.showwarning(
                    "Hardware ocupado",
                    f"No se pueden enviar comandos. El panel {self.panel_con_bloqueo} está controlando las válvulas."
                )
                return False
            return True

    def activar_bloqueo_hardware(self, nombre_panel):
        """Activa el bloqueo al enviar comandos a las válvulas."""
        with self.lock:
            self.bloqueo_activo = True
            self.panel_con_bloqueo = nombre_panel

    def liberar_bloqueo_hardware(self):
        """Libera el bloqueo al pausar/detener/terminar procesos."""
        with self.lock:
            self.bloqueo_activo = False
            self.panel_con_bloqueo = None

    def mostrar_panel(self, nombre):
        """Muestra un panel existente o crea uno nuevo sin destruir los existentes"""
        # Ocultar el panel actual si existe
        if self.panel_actual and self.panel_actual.winfo_exists():
            self.panel_actual.pack_forget()
        
        # Verificar si el panel ya existe y no ha sido destruido
        if nombre in self.paneles_activos and self.paneles_activos[nombre].winfo_exists():
            panel = self.paneles_activos[nombre]
        else:
            # Crear nuevo panel según el tipo solicitado
            if nombre == "nuevoproceso":
                panel = FormNuevoProceso(self.cuerpo_principal, self.user_id)
            elif nombre == "paneldecontrol":
                panel = FormPaneldeControl(self.cuerpo_principal, self.user_id)
            elif nombre == "historial":
                panel = FormHistorial(self.cuerpo_principal, self.user_id)
            elif nombre == "diagnostico":
                panel = FormDiagnostico(self.cuerpo_principal, self.user_id)
            elif nombre == "monitoreo":
                panel = FormMonitoreo(self.cuerpo_principal, self.user_id)
            else:
                return
                
            self.paneles_activos[nombre] = panel
        
        # Mostrar el panel
        panel.pack(fill="both", expand=True)
        self.panel_actual = panel

    def toggle_panel(self):
        if self.menu_lateral.winfo_ismapped():
            self.menu_lateral.pack_forget()
        else:
            self.menu_lateral.pack(side=ctk.LEFT, fill='both', expand=False)  

    def abrir_nuevoproceso(self):
        self.mostrar_panel("nuevoproceso")

    def abrir_paneldecontrol(self):
        self.mostrar_panel("paneldecontrol")

    def abrir_historial(self):
        self.mostrar_panel("historial")

    def abrir_diagnostico(self):
        self.mostrar_panel("diagnostico")

    def abrir_monitoreo(self):
        self.mostrar_panel("monitoreo")

    def __del__(self):
        """Asegurar limpieza adecuada al cerrar"""
        for nombre, panel in self.paneles_activos.items():
            if hasattr(panel, '__del__'):
                panel.__del__()

if __name__ == "__main__":
    app = MasterPanel()  
    app.mainloop()