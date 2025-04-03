import customtkinter as ctk
from tkinter import messagebox
from fpdf import FPDF
import pandas as pd
import sys
import tkinter.font as tkFont  

sys.path.append('d:/Python_Proyectos/INTER_C3')
import util.generic as utl


class FormHistorial(ctk.CTkScrollableFrame):
    
    def __init__(self, panel_principal, icono):
        super().__init__()

        try:
            self.title("Generar Reporte")
            self.geometry("300x200")

            # Botón "Generar Reporte"
            self.generate_report_button = ctk.CTkButton(self, text="Generar reporte",
                                                        command=self.generate_report)
            self.generate_report_button.pack(pady=20)

        except Exception as e:
            print(f"Error al inicializar la ventana: {e}")
            messagebox.showerror("Error", "No se pudo abrir la ventana de historial.")

    def generate_report(self):
        try:
            file_format = "PDF"  # Formato de prueba 1

            if file_format == "PDF":
                self.generate_pdf_report()
            elif file_format == "Excel":
                self.generate_excel_report()
            else:
                messagebox.showwarning("Formato no soportado", "Seleccione un formato válido.")

        except Exception as e:
            print(f"Error al generar el reporte: {e}")
            messagebox.showerror("Error", "No se pudo generar el reporte.")

    def generate_pdf_report(self):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Reporte Generado", ln=True, align="C")
            pdf.output("reporte.pdf")
            messagebox.showinfo("Reporte", "PDF generado exitosamente.")

        except Exception as e:
            print(f"Error al generar el PDF: {e}")
            messagebox.showerror("Error", "No se pudo generar el archivo PDF.")

    def generate_excel_report(self):
        try:
            data = {'Columna 1': [1, 2, 3], 'Columna 2': [4, 5, 6]}
            df = pd.DataFrame(data)
            df.to_excel("reporte.xlsx", index=False)
            messagebox.showinfo("Reporte", "Archivo Excel generado exitosamente.")

        except Exception as e:
            print(f"Error al generar el Excel: {e}")
            messagebox.showerror("Error", "No se pudo generar el archivo Excel.")


