import customtkinter as ctk
from tkinter import messagebox, filedialog
import sqlite3
import datetime
import traceback
from tkinter import ttk

class FormHistorial(ctk.CTkFrame):
    def __init__(self, master, logo):
        super().__init__(master)
        self.master = master
        self.logo = logo
        
        # Configuración principal del frame
        self.configure(fg_color="#f4f8f7")  # Color de fondo del frame
        self.pack(fill="both", expand=True, padx=10, pady=10)  # Expandir completamente
        
        # Frame contenedor principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Historial de Procesos", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=(0, 20))
        
        # Frame para botones
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", pady=(0, 10))
        
        # Botón de actualizar
        self.actualizar_btn = ctk.CTkButton(
            self.button_frame, 
            text="Actualizar", 
            command=self.cargar_historial,
            fg_color="#06918A",
            width=120
        )
        self.actualizar_btn.pack(side="left", padx=5)
        
        # Botón de generar reporte
        self.reporte_btn = ctk.CTkButton(
            self.button_frame, 
            text="Generar Reporte", 
            command=self.generar_reporte,
            fg_color="#06918A",
            width=120
        )
        self.reporte_btn.pack(side="left", padx=5)
        
        # Frame para el Treeview
        self.tree_frame = ctk.CTkFrame(self.main_frame)
        self.tree_frame.pack(fill="both", expand=True)
        
        # Configurar el Treeview
        self._configurar_treeview()
        
        # Cargar datos iniciales
        self.cargar_historial()
        
        # Forzar actualización de la interfaz
        self.update()
        self.update_idletasks()

    def _configurar_treeview(self):
        """Configura el Treeview y su scrollbar"""
        # Configurar estilo
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
        
        # Crear Treeview
        self.treeview = ttk.Treeview(
            self.tree_frame,
            columns=("fecha_inicio", "fecha_fin", "hora_instruccion", 
                    "valvula", "tiempo", "ciclos", "estado"),
            show="headings",
            selectmode="browse"
        )
        
        # Configurar columnas
        columnas = [
            ("fecha_inicio", "Fecha Inicio", 120),
            ("fecha_fin", "Fecha Fin", 120),
            ("hora_instruccion", "Hora Instrucción", 150),
            ("valvula", "Válvula", 100),
            ("tiempo", "Tiempo (s)", 80),
            ("ciclos", "Ciclos", 80),
            ("estado", "Estado", 100)
        ]
        
        for col, text, width in columnas:
            self.treeview.heading(col, text=text, anchor="w")
            self.treeview.column(col, width=width, anchor="w", stretch=False)
        
        # Añadir scrollbar
        self.scrollbar = ctk.CTkScrollbar(
            self.tree_frame,
            orientation="vertical",
            command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        
        # Empaquetar widgets
        self.treeview.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def cargar_historial(self):
        """Carga los datos desde la base de datos"""
        try:
            # Limpiar Treeview
            for item in self.treeview.get_children():
                self.treeview.delete(item)
            
            # Conectar a la base de datos
            conn = sqlite3.connect("procesos.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM procesos ORDER BY id DESC")
            procesos = cursor.fetchall()
            conn.close()
            
            # Insertar datos
            for proceso in procesos:
                self.treeview.insert("", "end", values=proceso[1:8])
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial:\n{str(e)}")
            print(f"Error: {traceback.format_exc()}")

    def generar_reporte(self):
        """Genera un reporte con los datos seleccionados"""
        seleccion = self.treeview.focus()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un proceso del historial")
            return
            
        item = self.treeview.item(seleccion)
        
        try:
            # Configurar diálogo de guardado
            nombre_archivo = f"reporte_proceso_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            ruta_archivo = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt")],
                initialfile=nombre_archivo
            )
            
            if not ruta_archivo:
                return
                
            # Generar contenido
            contenido = [
                "REPORTE DEL SISTEMA MBE",
                "="*50,
                f"Fecha de generación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "DATOS DEL PROCESO:",
                "-"*50,
                f"Fecha de inicio: {item['values'][0]}",
                f"Fecha de fin: {item['values'][1]}",
                f"Hora de instrucción: {item['values'][2]}",
                f"Válvula activada: {item['values'][3]}",
                f"Tiempo de activación: {item['values'][4]} segundos",
                f"Ciclos completados: {item['values'][5]}",
                f"Estado: {item['values'][6]}"
            ]
            
            # Guardar archivo
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write("\n".join(contenido))
                
            messagebox.showinfo("Éxito", f"Reporte generado exitosamente en:\n{ruta_archivo}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte:\n{str(e)}")
            print(f"Error: {traceback.format_exc()}")