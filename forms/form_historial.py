import customtkinter as ctk
import sys
sys.path.append('d:/Python_Proyectos/INTER_C3')


class FormHistorial(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        # Create the CTkOptionMenu
        self.optionmenu = ctk.CTkOptionMenu(self, values=["option 1", "option 2"],
                                            command=self.optionmenu_callback)
        self.optionmenu.set("option 2")  # Set the default value
        self.optionmenu.pack(padx=20, pady=20)  # Pack the widget into the window

    def optionmenu_callback(self, choice):
        print("OptionMenu dropdown clicked:", choice)

