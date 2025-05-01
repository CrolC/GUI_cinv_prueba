import customtkinter as ctk
import sys
sys.path.append('d:/Python_Proyectos/INTER_C3')
import util.generic as utl

#EN CONSTRUCCIÓN#
class FormMonitoreo(ctk.CTkFrame):
    def __init__(self, panel_principal, user_id):
        super().__init__(panel_principal, fg_color="#f4f8f7")  
        self.user_id = user_id
  
        self.grid_rowconfigure(0, weight=1) 
        self.grid_columnconfigure(0, weight=1)
        
        self.frame_construccion = ctk.CTkFrame(self, width=400, height=200) 
        self.frame_construccion.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  
        
        self.label_construccion = ctk.CTkLabel(self.frame_construccion, 
                                                text='Panel en construcción', 
                                                font=ctk.CTkFont(size=20, weight="bold"))
        self.label_construccion.pack(fill='x', padx=5, pady=20)

        self.grid(row=0, column=0, sticky="nsew")  

