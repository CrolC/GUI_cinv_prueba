import customtkinter as ctk
import sys
sys.path.append('d:/Python_Proyectos/INTER_C3')
import util.generic as utl

COLOR_CUERPO_PRINCIPAL = "#f4f8f7"

class FormNuevoProceso(ctk.CTk):

    def __init__(self, panel_principal, logo):
        super().__init__()

        self.fase_contador = 1
        self.fases_datos = {}

        self.scrollable_frame = ctk.CTkScrollableFrame(panel_principal)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview = ctk.CTkTabview(master=self.scrollable_frame)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.agregar_fase("Fase 1")

        self.botones_generales_frame = ctk.CTkFrame(panel_principal)
        self.botones_generales_frame.pack(fill="x", padx=10, pady=10)

        self.ejecutar_btn = ctk.CTkButton(self.botones_generales_frame, text="Ejecutar Rutina", fg_color="#06918A", command=self.enviar_cadena)
        self.ejecutar_btn.pack(side="right", padx=5, pady=5)

        self.pausar_btn = ctk.CTkButton(self.botones_generales_frame, text="Pausar Rutina", fg_color="#F0AD4E")
        self.pausar_btn.pack(side="right", padx=5, pady=5)

        self.reiniciar_btn = ctk.CTkButton(self.botones_generales_frame, text="Reiniciar Rutina", fg_color="#D9534F")
        self.reiniciar_btn.pack(side="right", padx=5, pady=5)

    def validar_entrada(self, text, entry_widget):
        if text.isdigit():
            try:
                val = int(text)
                if val <= 9999:
                    entry_widget.configure(border_color="gray")
                    return True
                else:
                    entry_widget.configure(border_color="red")
                    return False
            except:
                entry_widget.configure(border_color="red")
                return False
        else:
            entry_widget.configure(border_color="red")
            return False
        return True

    def validar_tiempo(self, entry, unidad_menu):
        try:
            valor = float(entry.get()) if entry.get() else 0
            unidad = unidad_menu.get()
            segundos = self.convertir_a_segundos(valor, unidad)

            if segundos > 9999:
                entry.configure(border_color="red")
            else:
                entry.configure(border_color="gray")
        except:
            entry.configure(border_color="red")

    def seleccionar_direccion(self, dir_var, btn_izq, btn_der, seleccion):
        dir_var.set(seleccion)
        btn_izq.configure(fg_color="#06918A" if seleccion == "I" else "#D3D3D3")
        btn_der.configure(fg_color="#06918A" if seleccion == "D" else "#D3D3D3")

    def convertir_a_segundos(self, valor, unidad):
        try:
            valor = float(valor)
            if unidad == "min":
                return int(valor * 60)
            elif unidad == "h":
                return int(valor * 3600)
            else:
                return int(valor)
        except:
            return 0

    def agregar_fase(self, nombre_fase=None):
        if nombre_fase is None:
            self.fase_contador += 1
            nombre_fase = f"Fase {self.fase_contador}"

        self.tabview.add(nombre_fase)

        frame_fase = ctk.CTkFrame(self.tabview.tab(nombre_fase))
        frame_fase.pack(fill="both", expand=True, padx=10, pady=10)

        validar_cmd = self.register(self.validar_entrada)

        elementos = ["Al", "As", "Ga", "I", "N", "Mn", "Be", "Mg", "Si"]
        self.fases_datos[nombre_fase] = []

        header = ctk.CTkFrame(frame_fase)
        header.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(header, text="Válvula", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Apertura", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Cierre", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Ciclos", width=60).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Dirección", width=100).pack(side="left", padx=5)

        for i, elemento in enumerate(elementos):
            fila = ctk.CTkFrame(frame_fase)
            fila.pack(fill="x", padx=5, pady=5)

            switch = ctk.CTkSwitch(fila, text=elemento)
            switch.pack(side="left", padx=5)

            # Apertura
            apertura_frame = ctk.CTkFrame(fila)
            apertura_frame.pack(side="left", padx=5)
            apertura = ctk.CTkEntry(apertura_frame, width=50, validate="key", validatecommand=(validar_cmd, "%P"))
            apertura.pack(side="left")
            apertura_unidad = ctk.CTkOptionMenu(apertura_frame, values=["s", "min", "h"], width=50)
            apertura_unidad.set("s")
            apertura_unidad.pack(side="left", padx=5)
            apertura.bind("<KeyRelease>", lambda e, ent=apertura, unidad=apertura_unidad: self.validar_tiempo(ent, unidad))
            apertura_unidad.configure(command=lambda v, ent=apertura, unidad=apertura_unidad: self.validar_tiempo(ent, unidad))

            # Cierre
            cierre_frame = ctk.CTkFrame(fila)
            cierre_frame.pack(side="left", padx=5)
            cierre = ctk.CTkEntry(cierre_frame, width=50, validate="key", validatecommand=(validar_cmd, "%P"))
            cierre.pack(side="left")
            cierre_unidad = ctk.CTkOptionMenu(cierre_frame, values=["s", "min", "h"], width=50)
            cierre_unidad.set("s")
            cierre_unidad.pack(side="left", padx=5)
            cierre.bind("<KeyRelease>", lambda e, ent=cierre, unidad=cierre_unidad: self.validar_tiempo(ent, unidad))
            cierre_unidad.configure(command=lambda v, ent=cierre, unidad=cierre_unidad: self.validar_tiempo(ent, unidad))

            # Ciclos
            ciclos = ctk.CTkEntry(fila, width=60, validate="key", validatecommand=(validar_cmd, "%P"))
            ciclos.pack(side="left", padx=5)

            # Dirección
            dir_var = ctk.StringVar(value="N")
            btn_izq = ctk.CTkButton(fila, text="I", width=40, command=lambda v=dir_var, b1=None, b2=None: self.seleccionar_direccion(v, btn_izq, btn_der, "I"))
            btn_der = ctk.CTkButton(fila, text="D", width=40, command=lambda v=dir_var, b1=None, b2=None: self.seleccionar_direccion(v, btn_izq, btn_der, "D"))
            btn_izq.pack(side="left", padx=5)
            btn_der.pack(side="left", padx=5)

            self.fases_datos[nombre_fase].append((switch, dir_var, apertura, apertura_unidad, cierre, cierre_unidad, ciclos))

        botones_frame = ctk.CTkFrame(self.tabview.tab(nombre_fase))
        botones_frame.pack(side="bottom", pady=10)

        boton_agregar = ctk.CTkButton(botones_frame, text="Agregar Fase", fg_color="#06918A", command=self.agregar_fase)
        boton_agregar.pack(side="right", padx=5)

        boton_eliminar = ctk.CTkButton(botones_frame, text="Eliminar Fase", fg_color="#D9534F", command=lambda: self.eliminar_fase(nombre_fase))
        boton_eliminar.pack(side="right", padx=5)

        self.tabview.set(nombre_fase)

    def eliminar_fase(self, nombre_fase):
        if len(self.tabview._name_list) > 1:
            self.tabview.delete(nombre_fase)
        else:
            print("No puedes eliminar la última fase")

    def enviar_cadena(self):
        try:
            cadenas_fases = []
            for fase, valvulas in self.fases_datos.items():
                cadenas = []
                for i, (switch, dir_var, apertura, apertura_unidad, cierre, cierre_unidad, ciclos) in enumerate(valvulas, start=1):
                    estado = switch.get()
                    if estado:
                        motor = f"M{i}"
                        direccion = dir_var.get()

                        ciclos_val = ciclos.get()
                        ciclos_val = ciclos_val.zfill(4) if ciclos_val else "0000"

                        apertura_val = self.convertir_a_segundos(apertura.get(), apertura_unidad.get())
                        cierre_val = self.convertir_a_segundos(cierre.get(), cierre_unidad.get())

                        apertura_str = str(min(apertura_val, 9999)).zfill(4)
                        cierre_str = str(min(cierre_val, 9999)).zfill(4)

                        if int(ciclos_val) > 0:
                            tarea = "B"
                        elif apertura_val > 0 and cierre_val > 0:
                            tarea = "C"
                        elif apertura_val > 0:
                            tarea = "A"
                        else:
                            tarea = "E"

                        cadena = f"{motor}{tarea}{direccion}{ciclos_val}{apertura_str}{cierre_str}"
                        cadenas.append(cadena)

                if cadenas:
                    cadenas_fases.append("&".join(cadenas))

            cadena_final = "&".join(cadenas_fases) if cadenas_fases else "(Ninguna válvula activa)"
            print(f"Cadena enviada a ESP32: {cadena_final}")

        except Exception as e:
            print(f"Error al generar la cadena: {e}")
