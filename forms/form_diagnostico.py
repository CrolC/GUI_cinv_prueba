import customtkinter as ctk
import sys
from PIL import Image, ImageTk
sys.path.append('d:/Python_Proyectos/INTER_C3')
import util.generic as utl

class FormDiagnostico(ctk.CTk):
    
    def __init__(self, panel_principal, icono):
        super().__init__()

        self.title("Página en desarrollo")
        self.geometry("1024x600")
        
        # Crear un Frame principal dentro de la ventana
        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.pack(fill="both", expand=True)
        
        # Mensaje en pantalla
        self.label_mensaje = ctk.CTkLabel(self.frame_principal, text="Panel en desarrollo", font=("Arial", 24))
        self.label_mensaje.pack(pady=20)
        
        # Cargar imagen
        try:
            imagen = utl.leer_imagen("D:\Python_Proyectos\INTER_C3\imagenes\MBE_blender_camaracrecimiento.png", size=(300, 100))
            self.label_imagen = ctk.CTkLabel(self.frame_principal, image=imagen, text="")
            self.label_imagen.pack(pady=10)
        except Exception as e:
            print(f"Error cargando la imagen: {e}")


