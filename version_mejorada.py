import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import xml.etree.ElementTree as ET
import os
from pathlib import Path


class XMLProcessorApp:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.configuracion_ventana()
        self.estilos()
        self.widgets()
        self.procesar_archivos = []

    def configuracion_ventana(self):
        """Configuración inicial de la ventana"""
        self.root.title("Procesador de XML - Agregar Folio")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        self.root.configure(bg='#f0f0f0')

        self.center_window()

    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def estilos(self):
        """Crear estilos personalizados"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('Main.TFrame', background='#f0f0f0')

        self.style.configure('Action.TButton',
                             font=('Segoe UI', 10, 'bold'),
                             padding=(20, 10))

        self.style.configure('Title.TLabel',
                             font=('Segoe UI', 16, 'bold'),
                             background='#f0f0f0',
                             foreground='#2c3e50')

        self.style.configure('Subtitle.TLabel',
                             font=('Segoe UI', 10),
                             background='#f0f0f0',
                             foreground='#7f8c8d')

    def widgets(self):
        """Crear todos los widgets de la interfaz"""
        main_frame = ttk.Frame(self.root, style='Main.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame,
                                text="Procesador de XML",
                                style='Title.TLabel')
        title_label.pack(pady=(0, 5))

        subtitle_label = ttk.Label(main_frame,
                                   text="Agrega automáticamente el folio basado en el UUID",
                                   style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 30))

        self.drop_frame = tk.Frame(main_frame,
                                   bg='#ecf0f1',
                                   relief='solid',
                                   borderwidth=2,
                                   highlightbackground='#3498db',
                                   highlightthickness=0)
        self.drop_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.drop_label = tk.Label(self.drop_frame,
                                   text="🗂️\n\nArrastra solo un archivo XML aqui\n o haz clic para seleccionarlo",
                                   font=('Segoe UI', 14),
                                   bg='#ecf0f1',
                                   fg='#7f8c8d',
                                   cursor='hand2')
        self.drop_label.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_label.bind('<Button-1>', self.select_file)

        button_frame = ttk.Frame(main_frame, style='Main.TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 20))


        self.select_btn = ttk.Button(button_frame,
                                     text="📁 Seleccionar Archivo",
                                     style='Action.TButton',
                                     command=self.select_file)
        self.select_btn.pack(side=tk.LEFT, padx=(0, 10))


        self.clear_btn = ttk.Button(button_frame,
                                    text="🗑️ Limpiar Historial",
                                    command=self.clear_history)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.help_btn = ttk.Button(button_frame,
                                   text="❓ Ayuda",
                                   command=self.show_help)
        self.help_btn.pack(side=tk.RIGHT)

        history_frame = ttk.LabelFrame(main_frame, text="Historial de Archivos Procesados", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)

        # Crear Treeview para el historial
        columns = ('archivo', 'folio', 'estado')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=6)

        # Configurar columnas
        self.history_tree.heading('archivo', text='Archivo')
        self.history_tree.heading('folio', text='Folio Agregado')
        self.history_tree.heading('estado', text='Estado')

        self.history_tree.column('archivo', width=300)
        self.history_tree.column('folio', width=100, anchor='center')
        self.history_tree.column('estado', width=100, anchor='center')

        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # Empaquetar treeview y scrollbar
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo para procesar archivos XML")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W, padding="5")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def agregar_folio(self, ruta_xml):
        """Función para agregar folio con manejo de errores"""
        try:
            tree = ET.parse(ruta_xml)
            root = tree.getroot()
            namespaces = {
                'cfdi': 'http://www.sat.gob.mx/cfd/4',
                'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
            }

            uuid_elem = root.find('.//tfd:TimbreFiscalDigital', namespaces)
            if uuid_elem is None:
                raise Exception("No se encontró el nodo TimbreFiscalDigital")

            uuid = uuid_elem.attrib.get('UUID')
            if not uuid:
                raise Exception("El nodo TimbreFiscalDigital no tiene atributo UUID")

            folio = uuid[-6:]
            folio = "M" + folio

            comprobante = root

            if 'Folio' in comprobante.attrib:

                return "N/A", "Ya tenía folio"

            # Convertimos atributos a lista y los reordenamos con Folio antes de Sello
            atributos = list(comprobante.attrib.items())
            nuevos_atributos = []
            insertado = False

            for clave, valor in atributos:
                if not insertado and clave == 'Sello':
                    nuevos_atributos.append(('Folio', folio))
                    insertado = True
                nuevos_atributos.append((clave, valor))

            # Limpiar y reasignar atributos
            comprobante.attrib.clear()
            comprobante.attrib.update(dict(nuevos_atributos))

            # Guardar el XML modificado
            tree.write(ruta_xml, encoding='utf-8', xml_declaration=True)

            return folio, "Procesado exitosamente"

        except Exception as e:
            raise Exception(f"Error al procesar el archivo: {str(e)}")

    def on_drop(self, event):
        data = event.data
        files = self.root.tk.splitlist(data)
        if len(files) > 1:
            self.show_error("❌ Arrastra solo un archivo a la vez")
            return
        self.process_file(files[0])

    def select_file(self, event=None):
        """Abrir diálogo para seleccionar archivo"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo XML",
            filetypes=[("Archivos XML", "*.xml"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.process_file(filepath)

    def process_file(self, filepath):
        """Procesar un archivo XML"""
        if not filepath.lower().endswith('.xml'):
            self.show_error("❌ Solo se permiten archivos .xml")
            return

        if not os.path.exists(filepath):
            self.show_error("❌ El archivo no existe")
            return

        try:
            # Actualizar estado
            self.status_var.set(f"Procesando: {os.path.basename(filepath)}...")
            self.root.update()

            # Procesar archivo
            folio, estado = self.agregar_folio(filepath)

            # Agregar al historial
            filename = os.path.basename(filepath)
            self.history_tree.insert('', 0, values=(filename, f'{folio}', estado))

            # Actualizar zona de drop
            self.update_drop_zone(f"✅ Archivo procesado exitosamente\n{filename}\nFolio agregado: {folio}",
                                  success=True)

            # Actualizar estado
            self.status_var.set(f"Archivo procesado exitosamente - Folio: {folio}")

            # Mostrar mensaje de éxito
            if estado != "Ya tenía folio":
                messagebox.showinfo("Éxito", f"Folio {folio} agregado correctamente al archivo:\n{filename}")
            else:
                messagebox.showinfo("Info", f"el archivo:\n{filename} ya cuenta con folio, por lo cual no se realizo ninguna alteracion")


        except Exception as e:
            self.show_error(f"❌ Error: {str(e)}")
            # Agregar al historial como error
            filename = os.path.basename(filepath)
            self.history_tree.insert('', 0, values=(filename, "N/A", "Error"))

    def update_drop_zone(self, text, success=False):
        """Actualizar el texto de la zona de drop"""
        color = '#27ae60' if success else '#e74c3c'
        bg_color = '#d5f4e6' if success else '#fadbd8'

        self.drop_label.config(text=text, fg=color)
        self.drop_frame.config(bg=bg_color)
        self.drop_label.config(bg=bg_color)

        # Restaurar después de 3 segundos
        self.root.after(3000, self.restore_drop_zone)

    def restore_drop_zone(self):
        """Restaurar la zona de drop al estado original"""
        self.drop_label.config(text="🗂️\n\nArrastra tu archivo XML aquí\no haz clic para seleccionar",
                               fg='#7f8c8d')
        self.drop_frame.config(bg='#ecf0f1')
        self.drop_label.config(bg='#ecf0f1')

    def show_error(self, message):
        """Mostrar mensaje de error"""
        self.update_drop_zone(message, success=False)
        self.status_var.set("Error en el procesamiento")
        messagebox.showerror("Error", message)

    def clear_history(self):
        """Limpiar el historial"""
        if messagebox.askyesno("Confirmar", "¿Deseas limpiar todo el historial?"):
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            self.status_var.set("Historial limpiado")

    def show_help(self):
        """Mostrar ventana de ayuda"""
        help_text = """
Procesador de XML CFDI - Ayuda

Esta aplicación agrega automáticamente un folio a los archivos XML de CFDI basado en los ultimos caracteres del UUID del TimbreFiscalDigital.

Cómo usar:
1. Arrastra un solo archivo XML a la zona indicada, o
2. Haz clic en "Seleccionar Archivo" para elegir un archivo
3. El folio se generará automáticamente usando los últimos 6 caracteres del UUID
4. El folio se agregará con el prefijo "M" (manual) antes del atributo "Sello"

Nota: Solo se procesan archivos .xml válidos con estructura CFDI.
        """

        help_window = tk.Toplevel(self.root)
        help_window.title("Ayuda")
        help_window.geometry("500x400")
        help_window.resizable(False, False)

        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

        # Centrar ventana de ayuda
        help_window.transient(self.root)
        help_window.grab_set()

    def run(self):
        """Iniciar la aplicación"""
        self.root.mainloop()


# Ejecutar la aplicación
if __name__ == "__main__":
    app = XMLProcessorApp()
    app.run()
