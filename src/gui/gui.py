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

CONFIG_FILE = os.path.join(os.getenv("APPDATA"), "instrument_classifier", "config.json")

class MainWindow(ctk.CTk):
    def __init__(self, classifier):
        super().__init__()
        self.title("Clasificador de instrumentos musicales")
        self.geometry("600x430")
        self.minsize(530, 400)
        self.configure(bg=PRIMARY_COLOR)

        self.file_paths = []
        self.destination_path = None
        self.load_config()
        self.processor = FileProcessor(classifier, self.config)
        self.init_ui()

    def create_circular_loader(self):
        """Creates and starts a circular loader animation"""
        def animate():
            if self.loader_running:
                self.angle = (self.angle + 10) % 360
                self.canvas.itemconfig(self.loader_arc, start=self.angle)
                self.after(30, animate)  # Schedule next frame

        self.canvas.delete("all")

        self.angle = 0
        self.loader_running = True
        self.loader_arc = self.canvas.create_arc(
            5, 5, 45, 45,
            start=self.angle, extent=90,
            outline="cyan", width=5, style="arc"
        )

        animate()

    def stop_circular_loader(self):
        """Stops the circular loader animation"""
        self.loader_running = False
        self.canvas.delete("all")
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                self.config = json.load(file)
        else:
            self.config = {"naming_pattern": "instrumento_#"}
    
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
        
        self.file_list = ctk.CTkTextbox(frame_left, height=200, width=300)
        self.file_list.pack(pady=10)
        
        btn_select_files = ctk.CTkButton(frame_left, text="Seleccionar Archivos", command=self.select_files)
        btn_select_files.pack(pady=5)
        
        btn_clear_files = ctk.CTkButton(frame_left, text="Limpiar Lista", command=self.clear_file_list)
        btn_clear_files.pack(pady=5)
        
        frame_right = ctk.CTkFrame(self.main_tab)
        frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.destination_label = ctk.CTkLabel(frame_right, text="Destino: No seleccionado", text_color=TEXT_COLOR)
        self.destination_label.pack(pady=5)
        
        btn_select_destination = ctk.CTkButton(frame_right, text="Seleccionar Destino", command=self.select_destination)
        btn_select_destination.pack(pady=5)
        
        btn_process = ctk.CTkButton(frame_right, text="Renombrar y Guardar", command=self.start_processing)
        btn_process.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(frame_right, width=250)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        
        self.canvas = ctk.CTkCanvas(frame_right, width=50, height=50, highlightthickness=0, bg=self.main_tab._fg_color)
        self.canvas.pack(pady=5)        
        self.canvas.pack()
    
    def create_settings_tab(self):
        frame_settings = ctk.CTkFrame(self.settings_tab)
        frame_settings.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.naming_label = ctk.CTkLabel(frame_settings, text="Formato de nombres:", text_color=TEXT_COLOR)
        self.naming_label.pack(pady=5)
        
        self.naming_entry = ctk.CTkEntry(frame_settings, width=250)
        self.naming_entry.insert(0, self.config["naming_pattern"])
        self.naming_entry.pack(pady=5)
        
        btn_save_settings = ctk.CTkButton(frame_settings, text="Guardar Configuración", command=self.update_naming_pattern)
        btn_save_settings.pack(pady=5)
        
        btn_reset_settings = ctk.CTkButton(frame_settings, text="Restablecer Configuración", command=self.reset_naming_pattern)
        btn_reset_settings.pack(pady=5)
    
    def update_naming_pattern(self):
        self.config["naming_pattern"] = self.naming_entry.get()
        self.save_config()
        self.processor.update_config(self.config)
    
    def reset_naming_pattern(self):
        self.config["naming_pattern"] = "instrumento_#"
        self.naming_entry.delete(0, "end")
        self.naming_entry.insert(0, self.config["naming_pattern"])
        self.save_config()
        self.processor.update_config(self.config)
    
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
            self.file_list.insert("end", "\n".join(os.path.basename(f) for f in files) + "\n")
    
    def clear_file_list(self):
        self.file_list.delete("1.0", "end")
        self.file_paths.clear()
    
    def select_destination(self):
        destination = filedialog.askdirectory()
        if destination:
            short_path = re.split(r'[/\\]', destination)[-1]
            self.destination_label.configure(text=f"Destino: {short_path}")
            self.destination_path = destination
    
    def start_processing(self):
        if not self.file_paths or not self.destination_path:
            messagebox.showwarning("Advertencia", "Selecciona archivos y destino.")
            return
        
        self.progress_bar.set(0)
        self.process_thread = threading.Thread(target=self.process_files)
        self.process_thread.start()
    
    def process_files(self):
        total_files = len(self.file_paths)
        self.create_circular_loader()
        
        for i, file_path in enumerate(self.file_paths, start=1):
            new_name = self.processor.process(file_path, self.destination_path)
            progress = i / total_files
            
            for _ in range(10):
                time.sleep(0.1)
                self.progress_bar.set(progress - 0.1 + (_ * 0.01))
                self.update_idletasks()
            
        self.stop_circular_loader()
        
        self.progress_bar.set(1)
        messagebox.showinfo("Procesamiento", "Proceso completado.")
        self.file_list.delete("1.0", "end")
        self.file_paths.clear()
        os.startfile(self.destination_path)
        self.progress_bar.set(0)