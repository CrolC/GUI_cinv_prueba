import customtkinter as ctk


class FormPaneldeControl(ctk.CTkFrame):
    def __init__(self, panel_principal, predeterminada):
        super().__init__(panel_principal)
        self.predeterminada = predeterminada
        
        # Frame 1
        self.frame1 = ctk.CTkFrame(self)
        self.frame1.pack(side='top', padx=10, pady=10, fill='both', expand=True)
        
        self.buttons1 = []
        self.entries1 = []
        for i in range(9):
            button = ctk.CTkButton(self.frame1, text=f'ON/OFF {i+1}', command=lambda idx=i: self.toggle_button(idx, 'frame1'))
            button.grid(row=i, column=0, padx=5, pady=5)
            entry = ctk.CTkEntry(self.frame1, placeholder_text=f'Input {i+1}')
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.buttons1.append(button)
            self.entries1.append(entry)

        # Frame 2: 9 botones (ON/OFF) con campos de entrada
        self.frame2 = ctk.CTkFrame(self)
        self.frame2.pack(side='top', padx=10, pady=10, fill='both', expand=True)

        self.buttons2 = []
        self.entries2 = []
        for i in range(9):
            button = ctk.CTkButton(self.frame2, text=f'ON/OFF {i+1}', command=lambda idx=i: self.toggle_button(idx, 'frame2'))
            button.grid(row=i, column=0, padx=5, pady=5)
            entry = ctk.CTkEntry(self.frame2, placeholder_text=f'Input {i+1}')
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.buttons2.append(button)
            self.entries2.append(entry)

        # Frame 3: 9 indicadores LED que reflejan el estado de los botones de los frames anteriores
        self.frame3 = ctk.CTkFrame(self)
        self.frame3.pack(side='top', padx=10, pady=10, fill='both', expand=True)
        
        self.leds1 = []
        for i in range(9):
            led = ctk.CTkLabel(self.frame3, text="OFF", fg_color="red", width=50)
            led.grid(row=i, column=0, padx=5, pady=5)
            self.leds1.append(led)

        # Frame 4: 3 indicadores LED y un slider para selección de modo
        self.frame4 = ctk.CTkFrame(self)
        self.frame4.pack(side='top', padx=10, pady=10, fill='both', expand=True)

        self.mode_leds = []
        for i in range(3):
            led = ctk.CTkLabel(self.frame4, text="OFF", fg_color="red", width=50)
            led.grid(row=i, column=0, padx=5, pady=5)
            self.mode_leds.append(led)
        
        self.slider_mode = ctk.CTkSlider(self.frame4, from_=0, to=2, command=self.update_mode)
        self.slider_mode.grid(row=3, column=0, padx=5, pady=5)

        self.pack(padx=10, pady=10, fill='both', expand=True)

    def toggle_button(self, idx, frame):
        if frame == 'frame1':
            current_text = self.buttons1[idx].cget('text')
            new_text = 'OFF' if current_text == 'ON' else 'ON'
            self.buttons1[idx].configure(text=new_text)
            self.leds1[idx].configure(text=new_text, fg_color='green' if new_text == 'ON' else 'red')
        elif frame == 'frame2':
            current_text = self.buttons2[idx].cget('text')
            new_text = 'OFF' if current_text == 'ON' else 'ON'
            self.buttons2[idx].configure(text=new_text)
            self.leds1[idx].configure(text=new_text, fg_color='green' if new_text == 'ON' else 'red')

    def update_mode(self, value):
        mode_idx = int(value)
        for i, led in enumerate(self.mode_leds):
            if i == mode_idx:
                led.configure(text='ON', fg_color='green')
            else:
                led.configure(text='OFF', fg_color='red')
