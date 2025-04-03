import customtkinter as ctk
import sys
from PIL import Image, ImageTk
sys.path.append('d:/Python_Proyectos/INTER_C3')
import util.generic as utl

class FormDiagnostico(ctk.CTkScrollableFrame):
    def __init__(self, panel_principal, predeterminada):
        super().__init__(panel_principal)
        self.predeterminada = predeterminada
        self.configurar_interfaz()
    
    def configurar_interfaz(self):
        try:
            self.columnconfigure((0, 1, 2, 3, 4), weight=1)
            self.rowconfigure(tuple(range(10)), weight=1)

            # Encabezados
            ctk.CTkLabel(self, text="VÁLVULA ACTIVA").grid(row=0, column=0, padx=5, pady=5)
            ctk.CTkLabel(self, text="APERTURA").grid(row=0, column=1, padx=5, pady=5)
            ctk.CTkLabel(self, text="CIERRE").grid(row=0, column=2, padx=5, pady=5)
            ctk.CTkLabel(self, text="CICLOS DESEADOS").grid(row=0, column=3, padx=5, pady=5)

            # Elementos de la tabla
            self.switches = []
            self.entries = []
            for i in range(1, 10):
                try:
                    switch = ctk.CTkSwitch(self, text=str(i))
                    switch.grid(row=i, column=0, padx=5, pady=5)
                    self.switches.append(switch)

                    entry_apertura = ctk.CTkEntry(self, width=50)
                    entry_apertura.grid(row=i, column=1, padx=5, pady=5)
                    entry_cierre = ctk.CTkEntry(self, width=50)
                    entry_cierre.grid(row=i, column=2, padx=5, pady=5)
                    entry_ciclos = ctk.CTkEntry(self, width=50)
                    entry_ciclos.grid(row=i, column=3, padx=5, pady=5)
                    
                    self.entries.append((entry_apertura, entry_cierre, entry_ciclos))
                except Exception as e:
                    print(f"Error al crear elementos de la fila {i}: {e}")

            # Botones de control
            try:
                self.ejecutar_btn = ctk.CTkButton(self, text="EJECUTAR RUTINA")
                self.ejecutar_btn.grid(row=10, column=0, columnspan=2, padx=5, pady=10)

                self.pausar_btn = ctk.CTkButton(self, text="PAUSAR RUTINA")
                self.pausar_btn.grid(row=10, column=2, padx=5, pady=10)

                self.reiniciar_btn = ctk.CTkButton(self, text="REINICIAR RUTINA")
                self.reiniciar_btn.grid(row=10, column=3, padx=5, pady=10)
            except Exception as e:
                print(f"Error al crear los botones de control: {e}")
        except Exception as e:
            print(f"Error al configurar la interfaz: {e}")


