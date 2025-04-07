import customtkinter as ctk
from tkinter import messagebox
import sys
import tkinter.font as tkFont
sys.path.append('d:/Python_Proyectos/INTER_C3')
#import util.generic as utl


class FormHistorial(ctk.CTkScrollableFrame):
    def __init__(self, panel_principal, predeterminada):
        super().__init__(panel_principal)
        self.predeterminada = predeterminada

       
        self.frame_construccion = ctk.CTkFrame(self)
        self.frame_construccion.pack(pady=10, padx=10, fill='both', expand=True)

        ctk.CTkLabel(self.frame_construccion, text='Panel en construcción', font=ctk.CTkFont(size=20, weight="bold")).pack(fill='x', padx=5, pady=20)
