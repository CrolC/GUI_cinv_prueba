import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import datetime
import traceback
from tkinter import ttk
from fpdf import FPDF
import os
#NOTAS:
#Checar error de run: pip uninstall --yes pypdf && pip install --upgrade fpdf2
#Modificar para que detecte flashes ciclicos de menos de 60 segundos y los muestre en el reporte
#Ajuste de diseño (agregar columna ciclos)

class FormHistorial(ctk.CTkFrame):
    def __init__(self, panel_principal, user_id):  
        super().__init__(panel_principal)
        self.user_id = user_id
        self.configure(fg_color="#f4f8f7")  
        self.pack(fill="both", expand=True, padx=10, pady=10)  
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Historial de Procesos", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=(0, 20))
        
        # Frame para los campos de entrada del reporte
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(fill="x", pady=(0, 10))
        
        # Campos de entrada para el reporte
        self.nombre_crecimiento_label = ctk.CTkLabel(self.input_frame, text="Nombre del crecimiento:")
        self.nombre_crecimiento_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nombre_crecimiento_entry = ctk.CTkEntry(self.input_frame, width=200)
        self.nombre_crecimiento_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.responsables_label = ctk.CTkLabel(self.input_frame, text="Responsables:")
        self.responsables_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.responsables_entry = ctk.CTkEntry(self.input_frame, width=200)
        self.responsables_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.sustrato_label = ctk.CTkLabel(self.input_frame, text="Sustrato:")
        self.sustrato_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.sustrato_entry = ctk.CTkEntry(self.input_frame, width=200)
        self.sustrato_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", pady=(0, 10))
        
        self.actualizar_btn = ctk.CTkButton(
            self.button_frame, 
            text="Actualizar", 
            command=self.cargar_historial,
            fg_color="#06918A",
            width=120
        )
        self.actualizar_btn.pack(side="left", padx=5)
        
        self.reporte_btn = ctk.CTkButton(
            self.button_frame, 
            text="Generar Reporte", 
            command=self.generar_reporte_pdf,
            fg_color="#06918A",
            width=120
        )
        self.reporte_btn.pack(side="left", padx=5)
        
        self.tree_frame = ctk.CTkFrame(self.main_frame)
        self.tree_frame.pack(fill="both", expand=True)
        
        self._configurar_treeview()
        self.cargar_historial()

    def _configurar_treeview(self):
        """Configura el Treeview con las columnas solicitadas"""
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                       background="#ffffff",
                       foreground="black",
                       rowheight=25,
                       fieldbackground="#ffffff",
                       font=('Arial', 10),
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background="#06918A",
                       foreground="white",
                       font=('Arial', 11, 'bold'),
                       padding=5)
        style.map("Treeview",
                 background=[('selected', '#007bff')],
                 foreground=[('selected', 'white')])
        
        self.treeview = ttk.Treeview(
            self.tree_frame,
            columns=("fecha_inicio", "hora_inicio", "hora_fin", 
                    "valvula", "ciclos", "fase", "tipo_proceso", "proceso_id"),
            show="headings",
            selectmode="browse"
        )
        
        columnas = [
            ("fecha_inicio", "Fecha Inicio", 100),
            ("hora_inicio", "Hora Inicio", 100),
            ("hora_fin", "Hora Fin", 100),
            ("valvula", "Válvula", 120),
            ("ciclos", "Ciclos", 80),
            ("fase", "Fase", 60),
            ("tipo_proceso", "Tipo Proceso", 120),
            ("proceso_id", "ID Proceso", 80)
        ]
        
        for col, text, width in columnas:
            self.treeview.heading(col, text=text, anchor="w")
            self.treeview.column(col, width=width, anchor="w", stretch=False)
        
        self.scrollbar = ctk.CTkScrollbar(
            self.tree_frame,
            orientation="vertical",
            command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        
        self.treeview.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def cargar_historial(self):
        """Carga los datos con los campos solicitados y formato específico"""
        try:
            self.treeview.delete(*self.treeview.get_children())
            
            conn = sqlite3.connect("procesos.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    substr(fecha_inicio, 1, 10) as fecha_inicio,
                    substr(hora_instruccion, 12, 8) as hora_inicio,
                    CASE 
                        WHEN fecha_fin = '' THEN 'En progreso'
                        ELSE substr(fecha_fin, 12, 8)
                    END as hora_fin,
                    valvula_activada as valvula,
                    ciclos,
                    fase,
                    tipo_proceso,
                    proceso_id
                FROM procesos 
                WHERE user_id=?
                ORDER BY fecha_inicio DESC, hora_instruccion DESC
            """, (self.user_id,))
            
            registros = cursor.fetchall()
            conn.close()
            
            for registro in registros:
                self.treeview.insert("", "end", values=registro)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial:\n{str(e)}")
            print(f"Error detallado: {traceback.format_exc()}")

    def generar_reporte_pdf(self):
        """Genera reporte PDF con todos los datos de un proceso completo"""
        seleccion = self.treeview.focus()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro del historial")
            return
            
        item = self.treeview.item(seleccion)
        valores = item['values']
        proceso_id = valores[7]  # El proceso_id está en la columna 7
        
        # Verificar campos obligatorios
        if not self.nombre_crecimiento_entry.get() or not self.responsables_entry.get() or not self.sustrato_entry.get():
            messagebox.showwarning("Advertencia", "Por favor complete todos los campos del reporte")
            return
            
        try:
            # Obtener todos los registros del proceso seleccionado
            conn = sqlite3.connect("procesos.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    fecha_inicio,
                    CASE 
                        WHEN fecha_fin = '' THEN 'En progreso'
                        ELSE fecha_fin
                    END as fecha_fin,
                    valvula_activada,
                    tiempo_valvula,
                    ciclos,
                    fase,
                    tipo_proceso,
                    estado_valvula,
                    hora_instruccion
                FROM procesos 
                WHERE user_id=? AND proceso_id=?
                ORDER BY hora_instruccion ASC
            """, (self.user_id, proceso_id))
            
            detalles = cursor.fetchall()
            
            if not detalles:
                messagebox.showwarning("Advertencia", "No se encontraron detalles para este registro")
                return
            
            # Obtener fechas de inicio y fin del proceso completo
            fecha_inicio_proceso = detalles[0][0]
            fecha_fin_proceso = detalles[-1][1] if detalles[-1][1] != 'En progreso' else 'En progreso'
            
            # Calcular duración total del proceso
            duracion_total = "En progreso"
            if fecha_fin_proceso != 'En progreso':
                try:
                    inicio = datetime.datetime.strptime(fecha_inicio_proceso, "%Y-%m-%d %H:%M:%S")
                    fin = datetime.datetime.strptime(fecha_fin_proceso, "%Y-%m-%d %H:%M:%S")
                    duracion_total = str(fin - inicio)
                except ValueError:
                    duracion_total = "No disponible"
            
            # Agrupar por fases y calcular tiempos
            fases = {}
            
            for detalle in detalles:
                fase = str(detalle[5])  # Convertir fase a string
                tiempo_valvula = detalle[3] or 0  # Tiempo de la válvula
                
                if fase not in fases:
                    fases[fase] = {
                        'registros': [],
                        'inicio': detalle[0],
                        'fin': detalle[1]
                    }
                else:
                    # Actualizar hora fin de la fase (será la de la última válvula)
                    fases[fase]['fin'] = detalle[1]
                
                fases[fase]['registros'].append(detalle)
            
            # Calcular duración de cada fase
            for fase, datos in fases.items():
                if datos['fin'] != 'En progreso':
                    try:
                        inicio_fase = datetime.datetime.strptime(datos['inicio'], "%Y-%m-%d %H:%M:%S")
                        fin_fase = datetime.datetime.strptime(datos['fin'], "%Y-%m-%d %H:%M:%S")
                        datos['duracion'] = str(fin_fase - inicio_fase)
                    except ValueError:
                        datos['duracion'] = "No disponible"
                else:
                    datos['duracion'] = "En progreso"
            
            # Separar flashes (eventos < 60 segundos)
            fases_ordenadas = []
            flashes = []
            
            for fase, datos in fases.items():
                # Verificar si es flash (todos los registros < 60s)
                es_flash = all((reg[3] or 0) < 60 for reg in datos['registros'])
                
                if es_flash:
                    flashes.extend(datos['registros'])
                else:
                    fases_ordenadas.append((fase, datos))
            
            # Ordenar fases por tiempo (última primero)
            fases_ordenadas.sort(key=lambda x: x[1]['inicio'], reverse=True)
            
            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Configurar fuente
            pdf.set_font("Arial", size=12)
            
            # Agregar logo (si existe)
            logo_path = r"D:\Python_Proyectos\INTER_C3\imagenes\logocinves_predeterm.png"
            if os.path.exists(logo_path):
                try:
                    pdf.image(logo_path, x=170, y=10, w=30)
                except:
                    pass
            
            # Título
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Reporte del Sistema MBE", 0, 1, 'C')
            pdf.ln(5)
            
            # Información básica
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Nombre del crecimiento: {self.nombre_crecimiento_entry.get()}", 0, 1)
            pdf.cell(0, 10, f"Responsables: {self.responsables_entry.get()}", 0, 1)
            pdf.cell(0, 10, f"Fecha y hora de INICIO: {fecha_inicio_proceso}", 0, 1)
            pdf.cell(0, 10, f"Fecha y hora de FIN: {fecha_fin_proceso}", 0, 1)
            pdf.cell(0, 10, f"Duración total del crecimiento: {duracion_total}", 0, 1)
            pdf.ln(10)
            
            # Tabla de fases
            if fases_ordenadas:
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "DETALLES DE FASES:", 0, 1)
                pdf.ln(5)
                
                for fase, datos in fases_ordenadas:
                    # Encabezado de fase
                    pdf.set_fill_color(200, 220, 255)
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(0, 10, f"Fase: {fase} (Duración total: {datos['duracion']})", 1, 1, 'C', 1)
                    
                    # Detalles de cada válvula en la fase
                    pdf.set_font("Arial", size=10)
                    for reg in datos['registros']:
                        tiempo_valvula = reg[3] or 0
                        elementos = [
                            f"{reg[2]}", # Válvula activada
                            f"Tiempo: {tiempo_valvula}s",
                            f"Ciclos: {reg[4]}",
                            f"Inicio: {reg[0]}",
                            f"Fin: {reg[1]}"
                        ]
                        pdf.cell(0, 8, " | ".join(elementos), 1, 1)
                    
                    pdf.ln(3)
            
            # Sección de flashes
            if flashes:
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "FLASHES (Eventos menores a 60 segundos):", 0, 1)
                pdf.ln(5)
                
                pdf.set_fill_color(220, 220, 220)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Eventos puntuales", 1, 1, 'C', 1)
                
                pdf.set_font("Arial", size=10)
                for flash in flashes:
                    tiempo_flash = flash[3] or 0
                    elementos = [
                        f"{flash[2]}", # Válvula activada
                        f"Tiempo: {tiempo_flash}s",
                        f"Inicio: {flash[0]}"
                    ]
                    pdf.cell(0, 8, " | ".join(elementos), 1, 1)
                
                pdf.ln(3)
            
            # Sección de sustrato
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "SUSTRATO:", 0, 1)
            pdf.ln(5)
            
            pdf.set_fill_color(200, 220, 255)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Sustrato utilizado: {self.sustrato_entry.get()}", 1, 1, 'C', 1)
            
            # Guardar PDF
            nombre_archivo = f"reporte_{valores[0]}_{valores[1].replace(':', '')}.pdf"
            ruta_archivo = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")],
                initialfile=nombre_archivo
            )
            
            if ruta_archivo:
                pdf.output(ruta_archivo)
                messagebox.showinfo("Éxito", f"Reporte generado exitosamente en:\n{ruta_archivo}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte:\n{str(e)}")
            print(f"Error: {traceback.format_exc()}")
        finally:
            conn.close()