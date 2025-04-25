import customtkinter as ctk
#PRUEBA 1 (¡NO FUNCIONAL!)
class FormPaneldeControl(ctk.CTkScrollableFrame):
    def __init__(self, panel_principal, predeterminada):
        super().__init__(panel_principal)
        self.predeterminada = predeterminada
        
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        
        self.frame_ciclico = ctk.CTkFrame(self)
        self.frame_ciclico.grid(row=0, column=0, padx=10, pady=(10,5), sticky="nsew")
        
        
        ctk.CTkLabel(self.frame_ciclico, 
                    text="PROCESO CÍCLICO",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,10))
        
        
        self.controles_ciclicos = []
        for i in range(9):  
            frame_control = ctk.CTkFrame(self.frame_ciclico)
            frame_control.pack(fill="x", padx=5, pady=2)
            
            lbl = ctk.CTkLabel(frame_control, text=f"Válvula {i+1}", width=80)
            lbl.pack(side="left", padx=(0,5))
            
            btn = ctk.CTkButton(frame_control, text="OFF", width=60,
                               command=lambda idx=i: self.toggle_button(idx, 'ciclico'))
            btn.pack(side="left", padx=(0,5))
            
            entry = ctk.CTkEntry(frame_control, placeholder_text="Tiempo (s)", width=100)
            entry.pack(side="left")
            
            self.controles_ciclicos.append((btn, entry))

        
        self.frame_puntual = ctk.CTkFrame(self)
        self.frame_puntual.grid(row=1, column=0, padx=10, pady=(5,10), sticky="nsew")
        
        
        ctk.CTkLabel(self.frame_puntual, 
                    text="PROCESO PUNTUAL",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,10))
        
        
        self.controles_puntuales = []
        for i in range(9): 
            frame_control = ctk.CTkFrame(self.frame_puntual)
            frame_control.pack(fill="x", padx=5, pady=2)
            
            lbl = ctk.CTkLabel(frame_control, text=f"Válvula {i+1}", width=80)
            lbl.pack(side="left", padx=(0,5))
            
            btn = ctk.CTkButton(frame_control, text="OFF", width=60,
                              command=lambda idx=i: self.toggle_button(idx, 'puntual'))
            btn.pack(side="left", padx=(0,5))
            
            entry = ctk.CTkEntry(frame_control, placeholder_text="Duración (s)", width=100)
            entry.pack(side="left")
            
            self.controles_puntuales.append((btn, entry))

        
        self.pack(padx=10, pady=10, fill="both", expand=True)

    def toggle_button(self, idx, tipo):
        """Cambia el estado de los botones ON/OFF"""
        if tipo == 'ciclico':
            btn = self.controles_ciclicos[idx][0]
        else:
            btn = self.controles_puntuales[idx][0]
            
        current_text = btn.cget('text')
        new_text = 'ON' if current_text == 'OFF' else 'OFF'
        btn.configure(text=new_text, 
                     fg_color="#06918A" if new_text == 'ON' else "#D3D3D3",
                     text_color="white" if new_text == 'ON' else "black")