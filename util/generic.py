import customtkinter as ctk
from PIL import Image
import tkinter as tk

def leer_imagen(path, size): 
    try:
        pil_image = Image.open(path)
        pil_image = pil_image.resize(size, Image.LANCZOS)
        return ctk.CTkImage(pil_image, size=size)
    except Exception as e:
        print(f"Error al cargar la imagen: {e}")
        return None  


# Para definir el centro de la ventana
def centrar_ventana(ventana, aplicacion_ancho, aplicacion_largo):    
    pantall_ancho = ventana.winfo_screenwidth()
    pantall_largo = ventana.winfo_screenheight()
    x = int((pantall_ancho / 2) - (aplicacion_ancho / 2))
    y = int((pantall_largo / 2) - (aplicacion_largo / 2))
    return ventana.geometry(f"{aplicacion_ancho}x{aplicacion_largo}+{x}+{y}")
