import customtkinter as ctk
import sys
sys.path.append('d:/Python_Proyectos/INTER_C3')
import util.generic as utl

COLOR_CUERPO_PRINCIPAL = "#f4f8f7"

class FormNuevoProceso(ctk.CTk):
    
    def __init__(self, panel_principal, logo):
        super().__init__()

        self.fase_contador = 1  # Inicia con solo una fase
        self.fases_datos = {}

        # Frame scrolleable
        self.scrollable_frame = ctk.CTkScrollableFrame(panel_principal)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabview con solo una pestaña inicial
        self.tabview = ctk.CTkTabview(master=self.scrollable_frame)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.agregar_fase("Fase 1")  # Inicia con la primera fase

        # Contenedor para los botones generales (Ejecutar, Pausar, Reiniciar)
        self.botones_generales_frame = ctk.CTkFrame(panel_principal)
        self.botones_generales_frame.pack(fill="x", padx=10, pady=10)

        self.ejecutar_btn = ctk.CTkButton(self.botones_generales_frame, text="Ejecutar Rutina", fg_color="#06918A", command=self.enviar_cadena)
        self.ejecutar_btn.pack(side="right", padx=5, pady=5)

        self.pausar_btn = ctk.CTkButton(self.botones_generales_frame, text="Pausar Rutina", fg_color="#F0AD4E")
        self.pausar_btn.pack(side="right", padx=5, pady=5)

        self.reiniciar_btn = ctk.CTkButton(self.botones_generales_frame, text="Reiniciar Rutina", fg_color="#D9534F")
        self.reiniciar_btn.pack(side="right", padx=5, pady=5)

    def validar_entrada(self, text):
        return text.isdigit() and len(text) <= 4

    def seleccionar_direccion(self, dir_var, botones, seleccion):
        dir_var.set(seleccion)
        for btn in botones:
            if btn.cget("text") == seleccion:
                btn.configure(fg_color="#06918A")  # Color del botón seleccionado
            else:
                btn.configure(fg_color="#D3D3D3")  # Color de los botones no seleccionados

    def agregar_fase(self, nombre_fase=None):
        """ Agrega una nueva pestaña al Tabview """
        if nombre_fase is None:
            self.fase_contador += 1
            nombre_fase = f"Fase {self.fase_contador}"

        self.tabview.add(nombre_fase)

        frame_fase = ctk.CTkFrame(self.tabview.tab(nombre_fase))
        frame_fase.pack(fill="both", expand=True, padx=10, pady=10)

        validar_cmd = self.register(self.validar_entrada)

        elementos = ["Al", "As", "Ga", "I", "N", "Mn", "Be", "Mg", "Si"]
        self.fases_datos[nombre_fase] = []

        # Encabezados de las columnas
        header = ctk.CTkFrame(frame_fase)
        header.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(header, text="Válvula", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Apertura", width=50).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Cierre", width=50).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Ciclos", width=50).pack(side="left", padx=5)

        # Crear las filas con los elementos
        for i, elemento in enumerate(elementos):
            fila = ctk.CTkFrame(frame_fase)
            fila.pack(fill="x", padx=5, pady=2)

            switch = ctk.CTkSwitch(fila, text=elemento)
            switch.pack(side="left", padx=5)

            # Definir las direcciones
            dir_var = ctk.StringVar(value="N")
            btn_izq = ctk.CTkButton(fila, text="I", width=20, command=lambda v=dir_var: self.seleccionar_direccion(v, [btn_izq, btn_neu, btn_der], "I"))
            btn_neu = ctk.CTkButton(fila, text="N", width=20, command=lambda v=dir_var: self.seleccionar_direccion(v, [btn_izq, btn_neu, btn_der], "N"))
            btn_der = ctk.CTkButton(fila, text="D", width=20, command=lambda v=dir_var: self.seleccionar_direccion(v, [btn_izq, btn_neu, btn_der], "D"))

            btn_izq.pack(side="left", padx=2)
            btn_neu.pack(side="left", padx=2)
            btn_der.pack(side="left", padx=2)

            # Campos de entrada
            apertura = ctk.CTkEntry(fila, width=50, validate="key", validatecommand=(validar_cmd, "%P"))
            cierre = ctk.CTkEntry(fila, width=50, validate="key", validatecommand=(validar_cmd, "%P"))
            ciclos = ctk.CTkEntry(fila, width=50, validate="key", validatecommand=(validar_cmd, "%P"))

            apertura.pack(side="left", padx=5)
            cierre.pack(side="left", padx=5)
            ciclos.pack(side="left", padx=5)

            self.fases_datos[nombre_fase].append((switch, dir_var, apertura, cierre, ciclos))

        # Frame de botones de fase
        botones_frame = ctk.CTkFrame(self.tabview.tab(nombre_fase))
        botones_frame.pack(side="bottom", pady=10)

        boton_agregar = ctk.CTkButton(botones_frame, text="Agregar Fase", fg_color="#06918A", command=self.agregar_fase)
        boton_agregar.pack(side="right", padx=5)

        boton_eliminar = ctk.CTkButton(botones_frame, text="Eliminar Fase", fg_color="#D9534F", command=lambda: self.eliminar_fase(nombre_fase))
        boton_eliminar.pack(side="right", padx=5)

        self.tabview.set(nombre_fase)

    def eliminar_fase(self, nombre_fase):
        """ Elimina una pestaña si hay más de una """
        if len(self.tabview._name_list) > 1:
            self.tabview.delete(nombre_fase)
        else:
            print("No puedes eliminar la última fase")

    def enviar_cadena(self):
        cadenas_fases = []
        for fase, valvulas in self.fases_datos.items():
            cadenas = []
            for i, (switch, dir_var, apertura, cierre, ciclos) in enumerate(valvulas, start=1):
                if switch.get() == "on":
                    motor = f"M{i}"  # Cada válvula tiene un número único
                    direccion = dir_var.get()
                    ciclos_val = ciclos.get().zfill(4) if ciclos.get() else "0000"
                    apertura_val = apertura.get().zfill(4) if apertura.get() else "0000"
                    cierre_val = cierre.get().zfill(4) if cierre.get() else "0000"
                    tarea = "B" if int(ciclos_val) > 0 else "C" if int(apertura_val) > 0 and int(cierre_val) > 0 else "A" if int(apertura_val) > 0 else "E"
                    cadena = f"{motor}#{tarea}{direccion}{ciclos_val}{apertura_val}{cierre_val}"
                    cadenas.append(cadena)
            if cadenas:
                cadenas_fases.append("&".join(cadenas))
        cadena_final = "&".join(cadenas_fases) if cadenas_fases else "(Ninguna válvula activa)"
        print(f"Cadena enviada a ESP32: {cadena_final}")
