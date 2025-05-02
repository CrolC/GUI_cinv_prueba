import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import datetime
import traceback
from tkinter import ttk

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
            command=self.generar_reporte,
            fg_color="#06918A",
            width=120
        )
        self.reporte_btn.pack(side="left", padx=5)
        
        
        self.tree_frame = ctk.CTkFrame(self.main_frame)
        self.tree_frame.pack(fill="both", expand=True)
        
        self._configurar_treeview()
        self.cargar_historial()

    def _configurar_treeview(self):
        """Configura el Treeview con las columnas en el orden correcto"""
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
            columns=("fecha_inicio", "hora_instruccion", "fecha_fin",
                    "valvula", "tiempo", "ciclos", "estado"),
            show="headings",
            selectmode="browse"
        )
        
        
        columnas = [
            ("fecha_inicio", "Fecha Inicio", 100),  
            ("hora_instruccion", "Hora Instrucción", 100),
            ("fecha_fin", "Fecha Fin", 100),
            ("valvula", "Válvula", 100),
            ("tiempo", "Tiempo (s)", 80),
            ("ciclos", "Ciclos", 80),
            ("estado", "Estado", 100)
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
        """Carga los datos ordenados según la estructura de la base de datos"""
        try:
            
            self.treeview.delete(*self.treeview.get_children())
            
            
            conn = sqlite3.connect("procesos.db")
            cursor = conn.cursor()
            
            
            cursor.execute("""
                SELECT 
                    fecha_inicio,
                    hora_instruccion,
                    fecha_fin,
                    valvula_activada,
                    tiempo_valvula,
                    ciclos,
                    estado_valvula
                FROM procesos 
                WHERE user_id=? 
                ORDER BY fecha_inicio DESC, hora_instruccion DESC
            """, (self.user_id,))
            
            procesos = cursor.fetchall()
            conn.close()
            
            
            for proceso in procesos:
                # YYYY-MM-DD
                fecha_inicio = proceso[0]
                if fecha_inicio and ' ' in fecha_inicio:
                    fecha_inicio = fecha_inicio.split(' ')[0]
                
                # HH:MM:SS
                hora_instruccion = proceso[1]
                if hora_instruccion and ' ' in hora_instruccion:
                    hora_instruccion = hora_instruccion.split(' ')[1]
                
                # YYYY-MM-DD
                fecha_fin = proceso[2]
                if fecha_fin and ' ' in fecha_fin:
                    fecha_fin = fecha_fin.split(' ')[0]
                
                
                valores = (
                    fecha_inicio,  # solo fecha
                    hora_instruccion,  # solo hora
                    fecha_fin,  # solo fecha
                    proceso[3],  # valvula
                    proceso[4],  # tiempo
                    proceso[5],  # ciclos
                    proceso[6]   # estado
                )
                self.treeview.insert("", "end", values=valores)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial:\n{str(e)}")
            print(f"Error detallado: {traceback.format_exc()}")

    def generar_reporte(self):
        """Genera reporte con los datos en el formato correcto"""
        seleccion = self.treeview.focus()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un proceso del historial")
            return
            
        item = self.treeview.item(seleccion)
        valores = item['values']
        
        try:
           
            nombre_archivo = f"reporte_proceso_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            ruta_archivo = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt")],
                initialfile=nombre_archivo
            )
            
            if not ruta_archivo:
                return
                
            
            contenido = [
                "REPORTE DEL SISTEMA MBE",
                "="*50,
                f"Fecha de generación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "DATOS DEL PROCESO:",
                "-"*50,
                f"Fecha de inicio: {valores[0]}",
                f"Hora de instrucción: {valores[1]}",
                f"Fecha de fin: {valores[2]}",
                f"Válvula activada: {valores[3]}",
                f"Tiempo de activación: {valores[4]} segundos",
                f"Ciclos completados: {valores[5]}",
                f"Estado: {valores[6]}"
            ]
            
           
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write("\n".join(contenido))
                
            messagebox.showinfo("Éxito", f"Reporte generado exitosamente en:\n{ruta_archivo}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte:\n{str(e)}")
            print(f"Error: {traceback.format_exc()}")