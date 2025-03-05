import os
import re
import threading
import time
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage
from utils.file_processor import FileProcessor

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

PRIMARY_COLOR = "#000000"
TEXT_COLOR = "#E5E7EB"

APPDATA_PATH = os.path.join(os.getenv("APPDATA"), "ClasificadorInstrumentos")

os.makedirs(APPDATA_PATH, exist_ok=True)

CONFIG_FILE = os.path.join(APPDATA_PATH, "config.json")

class MainWindow(ctk.CTk):
    def __init__(self, classifier):
        super().__init__()
        self.title("Clasificador de instrumentos musicales")
        self.geometry("700x430")
        self.minsize(650, 420)
        self.maxsize(800,500)
        self.configure(bg=PRIMARY_COLOR)

        self.file_paths = []
        self.destination_path = None
        self.load_config()
        self.processor = FileProcessor(classifier, self.config)
        self.init_ui()
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                self.config = json.load(file)
        else:
            self.config = {"instrument_labels":
                                    {"Acoustic Guitar":"Acoustic Guitar", 
                                    "Bass":"Bass", 
                                    "Drums":"Drums", 
                                    "Electric Guitar":"Electric Guitar", 
                                    "Piano":"Piano"}}
            with open(CONFIG_FILE, "w") as file:
                json.dump(self.config, file, indent=4)

    def create_circular_loader(self):
        def animate():
            if self.loader_running:
                self.angle = (self.angle + 10) % 360
                self.canvas.itemconfig(self.loader_arc, start=self.angle)
                self.after(30, animate)

        if self.canvas:
            self.canvas.delete("all")

        self.angle = 0
        self.loader_running = True
        self.loader_arc = self.canvas.create_arc(
            2.5, 2.5, 22.5, 22.5,
            start=self.angle, extent=90,
            outline="cyan", width=5, style="arc"
        )

        animate()

    def stop_circular_loader(self):
        self.loader_running = False
        self.canvas.delete("all")
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                self.config = json.load(file)
        else:
            self.config = {"project_name": "",
                           "instrument_labels":{"Acoustic Guitar":"Acoustic Guitar", 
                                                "Bass":"Bass", 
                                                "Drums":"Drums", 
                                                "Electric Guitar":"Electric Guitar", 
                                                "Piano":"Piano"}}
    
    def save_config(self):
        with open(CONFIG_FILE, "w") as file:
            json.dump(self.config, file)
    
    def init_ui(self):
        self.tabs = ctk.CTkTabview(self, width=680, height=480)
        self.tabs.pack(pady=10, padx=10)
        
        self.main_tab = self.tabs.add("Principal")
        self.settings_tab = self.tabs.add("Configuración")
        self.about_tab = self.tabs.add("Acerca de")
        
        self.create_main_tab()
        self.create_settings_tab()
        self.create_about_tab()
    
    def create_main_tab(self):
        frame_left = ctk.CTkFrame(self.main_tab)
        frame_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        btn_select_files = ctk.CTkButton(frame_left, text="Seleccionar Archivos", command=self.select_files)
        btn_select_files.pack(pady=5)

        self.file_list = ctk.CTkTextbox(frame_left, height=200, width=300, state="disabled")
        self.file_list.pack(pady=10)
        
        self.btn_clear_files = ctk.CTkButton(frame_left, text="Limpiar Lista", command=self.clear_file_list, state="disabled", fg_color="snow4")
        self.btn_clear_files.pack(pady=5)
        
        # --- FRAME DERECHO ---
        frame_right = ctk.CTkFrame(self.main_tab)
        frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # --- Sección de destino ---
        frame_destination = ctk.CTkFrame(frame_right, fg_color="gray20", width=100)
        frame_destination.pack(fill="x", padx=5, pady=5)

        self.destination_label = ctk.CTkLabel(frame_destination, text="Destino: No seleccionado", text_color="white", font=("Arial", 12, "italic"))
        self.destination_label.pack(pady=5)

        btn_select_destination = ctk.CTkButton(frame_destination, text="Seleccionar Destino", command=self.select_destination)
        btn_select_destination.pack(pady=5)

        # --- Sección de Nombre del Proyecto ---
        frame_project = ctk.CTkFrame(frame_right, fg_color="gray20", width=100)
        frame_project.pack(fill="x", padx=5, pady=10)

        self.project_entry_label = ctk.CTkLabel(frame_project, text="Nombre del Proyecto:")
        self.project_entry_label.pack(pady=(5, 2))
        self.project_entry = ctk.CTkEntry(frame_project, width=150)
        self.project_entry.pack(pady=(2, 10))
        self.project_entry.bind("<KeyRelease>", lambda event: self.update_filename_preview())

        # --- Sección Final: Procesamiento y progreso ---
        frame_process = ctk.CTkFrame(frame_right, fg_color="gray20", width=100, height=100)
        frame_process.pack(fill="both", padx=5, pady=10, side="bottom")

        self.filename_preview_label = ctk.CTkLabel(
        frame_process, 
        text="Preview: <instrumento>_1.wav", 
        font=("Arial", 12, "italic"), 
        wraplength=200,
        justify="left")
        self.filename_preview_label.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(frame_process, width=250)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        self.btn_process = ctk.CTkButton(frame_process, text="Renombrar y Guardar", state="disabled", command=self.start_processing, fg_color='navy')
        self.btn_process.pack(pady=10)

        self.canvas = ctk.CTkCanvas(frame_process, width=25, height=25, highlightthickness=0, bg="gray20")       
        self.canvas.pack()

    def create_settings_tab(self):
        frame_settings = ctk.CTkFrame(self.settings_tab)
        frame_settings.pack(fill="both", expand=True, padx=10, pady=8)

        self.naming_label = ctk.CTkLabel(frame_settings, text="Ajustar nombres de instrumentos", text_color=TEXT_COLOR)
        self.naming_label.pack(pady=2)

        self.naming_entries = {}

        for key, label_text in self.config["instrument_labels"].items():
            frame = ctk.CTkFrame(frame_settings)
            frame.pack(fill="x", pady=2)

            label = ctk.CTkLabel(frame, text=f"{key}:")
            label.pack(side="left", padx=3)

            self.entry = ctk.CTkEntry(frame, width=250)
            self.entry.insert(0, label_text)
            self.entry.pack(side="right", padx=5)
            self.naming_entries[key] = self.entry

        btn_save_settings = ctk.CTkButton(frame_settings, text="Guardar Configuración", command=self.update_naming_pattern)
        btn_save_settings.pack(pady=5)

        btn_reset_settings = ctk.CTkButton(frame_settings, text="Restablecer Configuración", command=self.reset_naming_pattern)
        btn_reset_settings.pack(pady=5)
    
    def update_filename_preview(self):
        project_name = self.project_entry.get().strip()
        filename = f"{project_name}_<instrumento>_1.wav" if project_name else f"<instrumento>_1.wav"
        self.filename_preview_label.configure(text=f"Preview: {filename}")

    def update_naming_pattern(self):
        for key, entry in self.naming_entries.items():
            self.config["instrument_labels"][key] = entry.get()

        with open("config.json", "w") as config_file:
            json.dump(self.config, config_file, indent=4)
    
    def reset_naming_pattern(self):
        # Restore default config values
        self.config["instrument_labels"] = {
            "Acoustic Guitar": "Acoustic Guitar",
            "Bass": "Bass",
            "Drums": "Drums",
            "Electric Guitar": "Electric Guitar",
            "Piano": "Piano"
        }
        for key, label_text in self.config["instrument_labels"].items():
            if key in self.naming_entries:
                self.naming_entries[key].delete(0, "end")
                self.naming_entries[key].insert(0, label_text)
        self.save_config()
        self.processor.update_config(self.config)
        self.update_naming_pattern()

    
    def create_about_tab(self):
        frame_about = ctk.CTkFrame(self.about_tab)
        frame_about.pack(fill="both", expand=True, padx=10, pady=10)
        
        about_text = """Clasificador de Instrumentos Musicales\n\nEsta aplicación utiliza un modelo de IA para identificar \ndiferentes instrumentos en archivos de audio y \nrenombrarlos automáticamente."""
        
        label_about = ctk.CTkLabel(frame_about, text=about_text, text_color=TEXT_COLOR)
        label_about.pack(pady=10)
    
    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Archivos WAV", "*.wav")])
        if files:
            self.file_paths.extend(files)
            self.file_list.configure(state="normal")
            self.file_list.insert("end", "\n".join(os.path.basename(f) for f in files) + "\n")
            self.file_list.configure(state="disabled")
            self.btn_clear_files.configure(state="normal")
    
    def clear_file_list(self):
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")
        self.file_list.configure(state="disabled")
        self.file_paths.clear()
        self.btn_clear_files.configure(state="disabled")
    
    def select_destination(self):
        destination = filedialog.askdirectory()
        if destination:
            short_path = re.split(r'[/\\]', destination)[-1]
            self.destination_label.configure(text=f"Destino: {short_path}")
            self.destination_path = destination
            self.btn_process.configure(state="normal")
    
    def start_processing(self):
        if not self.file_paths or not self.destination_path:
            messagebox.showwarning("Advertencia", "No hay archivos seleccionados.")
            return
        
        self.progress_bar.set(0)
        self.process_thread = threading.Thread(target=self.process_files)
        self.process_thread.start()
    
    def process_files(self):
        total_files = len(self.file_paths)
        self.create_circular_loader()
        
        for i, file_path in enumerate(self.file_paths, start=1):
            new_name = self.processor.process(file_path, self.destination_path, self.project_entry.get())
            progress = i / total_files
            
            for _ in range(10):
                time.sleep(0.1)
                self.progress_bar.set(progress - 0.1 + (_ * 0.01))
                self.update_idletasks()
            
        self.stop_circular_loader()
        
        self.progress_bar.set(1)
        messagebox.showinfo("Procesamiento", "Proceso completado.")
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")
        self.file_list.configure(state="disabled")
        self.file_paths.clear()
        os.startfile(self.destination_path)
        self.progress_bar.set(0)
        self.btn_process.configure(state="disabled")
        self.btn_clear_files.configure(state="disabled")