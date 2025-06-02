import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import datetime
import traceback
from tkinter import ttk
from fpdf import FPDF
import os

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
        """Genera reporte PDF con formato profesional incluyendo marca de agua"""
        seleccion = self.treeview.focus()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro del historial")
            return
            
        item = self.treeview.item(seleccion)
        valores = item['values']
        proceso_id = valores[7]
        
        if not self.nombre_crecimiento_entry.get() or not self.responsables_entry.get() or not self.sustrato_entry.get():
            messagebox.showwarning("Advertencia", "Por favor complete todos los campos del reporte")
            return
            
        try:
            conn = sqlite3.connect("procesos.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    fecha_inicio,
                    CASE WHEN fecha_fin = '' THEN 'En progreso' ELSE fecha_fin END as fecha_fin,
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
            
            # Procesamiento de datos
            fecha_inicio_proceso = min(det[0] for det in detalles)
            fecha_fin_proceso = max(det[1] for det in detalles if det[1] != 'En progreso') if any(det[1] != 'En progreso' for det in detalles) else 'En progreso'
            
            # Calcular duración total del proceso
            duracion_total = "En progreso"
            if fecha_fin_proceso != 'En progreso':
                try:
                    inicio = datetime.datetime.strptime(fecha_inicio_proceso, "%Y-%m-%d %H:%M:%S")
                    fin = datetime.datetime.strptime(fecha_fin_proceso, "%Y-%m-%d %H:%M:%S")
                    duracion_total = str(fin - inicio)
                except ValueError:
                    duracion_total = "No disponible"
            
            # Agrupar por fases
            fases = {}
            for detalle in detalles:
                fase = str(detalle[5])
                if fase not in fases:
                    fases[fase] = []
                fases[fase].append(detalle)
            
            # Calcular duración por fase
            for fase, registros in fases.items():
                inicio_fase = min(reg[0] for reg in registros)
                fin_fase = max(reg[1] for reg in registros if reg[1] != 'En progreso') if any(reg[1] != 'En progreso' for reg in registros) else 'En progreso'
                
                if fin_fase != 'En progreso':
                    try:
                        inicio = datetime.datetime.strptime(inicio_fase, "%Y-%m-%d %H:%M:%S")
                        fin = datetime.datetime.strptime(fin_fase, "%Y-%m-%d %H:%M:%S")
                        fases[fase] = {
                            'registros': registros,
                            'duracion': str(fin - inicio),
                            'inicio': inicio_fase,
                            'fin': fin_fase
                        }
                    except ValueError:
                        fases[fase] = {
                            'registros': registros,
                            'duracion': "No disponible",
                            'inicio': inicio_fase,
                            'fin': fin_fase
                        }
                else:
                    fases[fase] = {
                        'registros': registros,
                        'duracion': "En progreso",
                        'inicio': inicio_fase,
                        'fin': fin_fase
                    }
            
            # Separar flashes (tiempo total <60s)
            fases_normales = {}
            flashes = []
            
            for fase, datos in fases.items():
                for reg in datos['registros']:
                    if (reg[3] or 0) < 60:  # Solo tiempo total <60s
                        flashes.append(reg)
                
                # Quitar los flashes de la fase normal
                registros_normales = [reg for reg in datos['registros'] if (reg[3] or 0) >= 60]
                
                if registros_normales:
                    fases_normales[fase] = {
                        'registros': registros_normales,
                        'duracion': datos['duracion'],
                        'inicio': datos['inicio'],
                        'fin': datos['fin']
                    }
            
            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            
            # 1. Agregar marca de agua (fondo)
            watermark_path = r"D:\Python_Proyectos\INTER_C3\imagenes\marcadeagua.png"
            if os.path.exists(watermark_path):
                try:
                    # Configurar transparencia
                    if hasattr(pdf, 'set_alpha'):
                        pdf.set_alpha(0.05)  # 95% transparencia
                    
                    # Centrar la marca de agua
                    pdf.image(watermark_path, x=30, y=50, w=150)
                    
                    if hasattr(pdf, 'set_alpha'):
                        pdf.set_alpha(1)  # Restablecer opacidad normal
                except Exception as e:
                    print(f"Error al agregar marca de agua: {str(e)}")
            
            # Configuración principal
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            
            # Logo principal
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
            pdf.cell(0, 10, f"Nombre: {self.nombre_crecimiento_entry.get()}", 0, 1)
            pdf.cell(0, 10, f"Responsables: {self.responsables_entry.get()}", 0, 1)
            pdf.cell(0, 10, f"Inicio: {fecha_inicio_proceso}", 0, 1)
            pdf.cell(0, 10, f"Fin: {fecha_fin_proceso}", 0, 1)
            pdf.cell(0, 10, f"Duración: {duracion_total}", 0, 1)
            pdf.ln(10)
            
            # Configuración de columnas (angostas y centradas)
            headers = ["Elemento", "Tiempo", "Ciclos", "Hora inicio", "Hora fin"]
            col_widths = [35, 30, 25, 35, 30]  # Total: 155mm
            total_width = sum(col_widths)
            left_margin = (210 - total_width) / 2  # Centrar en página A4

            
            # Crear tabla unificada centrada
            pdf.set_left_margin(left_margin)
            pdf.set_font("Arial", size=10)
            
            # 1. FASE
            if fases_normales:
                for fase, datos in fases_normales.items():
                    # Encabezado de fase (azul claro)
                    pdf.set_fill_color(200, 220, 255)
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(total_width, 10, f"FASE {fase} (Duración: {datos['duracion']})", 1, 1, 'C', 1)
                    
                    # Encabezados de columnas (gris)
                    pdf.set_fill_color(220, 220, 220)
                    
                    for i, header in enumerate(headers):
                        pdf.cell(col_widths[i], 10, header, 1, 0, 'C', 1)
                    pdf.ln()
                    
                    # Contenido de la fase
                    pdf.set_font("Arial", size=10)
                    for reg in datos['registros']:
                        tiempo_total = reg[3] or 0
                        ciclos = reg[4] or 0
                        inicio = reg[0][11:19] if len(reg[0]) > 10 else reg[0]
                        fin = reg[1][11:19] if reg[1] != 'En progreso' and len(reg[1]) > 10 else reg[1]
                        
                        pdf.cell(col_widths[0], 8, reg[2], 1, 0)
                        pdf.cell(col_widths[1], 8, f"{tiempo_total}s", 1, 0, 'C')
                        pdf.cell(col_widths[2], 8, str(ciclos) if ciclos > 0 else "Puntual", 1, 0, 'C')
                        pdf.cell(col_widths[3], 8, inicio, 1, 0, 'C')
                        pdf.cell(col_widths[4], 8, fin, 1, 1, 'C')
            
            # 2. FLASHES (verde oscuro y filas delgadas)
            if flashes:
                pdf.set_font("Arial", 'B', 12)
                pdf.set_fill_color(0, 100, 0)  # Verde oscuro
                pdf.cell(total_width, 10, "FLASHES", 1, 1, 'C', 1)
                
                # Encabezados de columnas (gris)
                pdf.set_fill_color(220, 220, 220)
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, header, 1, 0, 'C', 1)
                pdf.ln()
                
                # Contenido de flashes (filas delgadas)
                pdf.set_font("Arial", size=8)
                for flash in flashes:
                    tiempo_total = flash[3] or 0
                    ciclos = flash[4] or 0
                    inicio = flash[0][11:19] if len(flash[0]) > 10 else flash[0]
                    fin = flash[1][11:19] if flash[1] != 'En progreso' and len(flash[1]) > 10 else flash[1]
                    
                    pdf.cell(col_widths[0], 6, flash[2], 1, 0)
                    pdf.cell(col_widths[1], 6, f"{tiempo_total}s", 1, 0, 'C')
                    pdf.cell(col_widths[2], 6, str(ciclos) if ciclos > 0 else "Puntual", 1, 0, 'C')
                    pdf.cell(col_widths[3], 6, inicio, 1, 0, 'C')
                    pdf.cell(col_widths[4], 6, fin, 1, 1, 'C')
            
            # 3. SUSTRATO (amarillo)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_fill_color(255, 255, 0)  # Amarillo
            pdf.cell(total_width, 10, "SUSTRATO", 1, 1, 'C', 1)
            pdf.set_font("Arial", size=10)
            pdf.set_fill_color(255, 255, 255)
            pdf.cell(total_width, 10, self.sustrato_entry.get(), 1, 1, 'C')
            
            # Restablecer margen
            pdf.set_left_margin(10)
            
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