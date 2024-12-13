import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from utils.audio_preprocessor import AudioPreprocessor
from utils.file_processor import FileProcessor

class GUI:
    def __init__(self, root, classifier):
        self.root = root
        self.file_paths = []
        self.destination_path = tk.StringVar()
        self.cancel_processing_flag = False
        self.file_processor = FileProcessor(classifier)

        self.loading_label = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Clasificador de instrumentos musicales")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.setup_left_panel()
        self.setup_right_panel()
        self.setup_bottom_panel()

    def setup_left_panel(self):
        left_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_label = tk.Label(left_frame, text="Archivos seleccionados", font=("Yu Gothic UI", 12, "bold"), fg="black")
        left_label.pack()

        self.left_listbox = tk.Listbox(left_frame, selectmode=tk.MULTIPLE, font=("Yu Gothic UI", 10))
        self.left_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_select_files = tk.Button(left_frame, text="Seleccionar Archivos", command=self.select_files, font=("Yu Gothic UI", 10), fg="black")
        btn_select_files.pack(pady=5)

    def setup_right_panel(self):
        right_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN, width=250)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_label = tk.Label(right_frame, text="Destino", font=("Yu Gothic UI", 12, "bold"))
        right_label.pack()

        self.right_listbox = tk.Listbox(right_frame, height=1, font=("Yu Gothic UI", 10))
        self.right_listbox.pack(fill=tk.X, padx=5, pady=5)

        btn_select_destination = tk.Button(right_frame, text="Seleccionar Destino", command=self.select_destination, font=("Yu Gothic UI", 10))
        btn_select_destination.pack(pady=5)

    def setup_bottom_panel(self):
        center_frame = tk.Frame(self.root, width=100)
        center_frame.pack(side=tk.LEFT, fill=tk.NONE)

        btn_rename = tk.Button(center_frame, text="Renombrar y Guardar", command=self.rename_files, font=("Yu Gothic UI", 10, "bold"))
        btn_rename.pack(expand=True)

        btn_cancel = tk.Button(center_frame, text="Cancelar", command=self.cancel_processing, font=("Yu Gothic UI", 10))
        btn_cancel.pack(pady=5)

        self.loading_label = tk.Label(center_frame, text="", font=("Yu Gothic UI", 10, "italic"), fg="blue")
        self.loading_label.pack(pady=5)

    def select_files(self):
        files = filedialog.askopenfilenames(title="Selecciona archivos WAV", filetypes=[("Archivos WAV", "*.wav")])
        if files:
            self.left_listbox.delete(0, tk.END)
            self.file_paths = list(files)
            for file in files:
                self.left_listbox.insert(tk.END, os.path.basename(file))

    def select_destination(self):
        destination = filedialog.askdirectory(title="Selecciona el destino")
        if destination:
            self.right_listbox.delete(0, tk.END)
            self.right_listbox.insert(0, "/" + os.path.basename(destination))
            self.destination_path.set(destination)

    def rename_files(self):
        destination = self.destination_path.get()
        if not destination or not self.file_paths:
            messagebox.showwarning("Advertencia", "Selecciona archivos y destino.")
            return

        self.cancel_processing_flag = False
        self.loading_label.config(text="Analizando...")
        threading.Thread(target=self.process_files, args=(destination,)).start()

    def process_files(self, destination):
        try:
            for file_path in self.file_paths:
                if self.cancel_processing_flag:
                    self.loading_label.config(text="Proceso cancelado.")
                    return
                self.file_processor.process(file_path, destination)
            self.loading_label.config(text="Proceso completado con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar los archivos: {e}")
            self.loading_label.config(text="Error en el proceso.")
        finally:
            self.left_listbox.delete(0, tk.END)
            self.cancel_processing_flag = False

    def cancel_processing(self):
        self.cancel_processing_flag = True
