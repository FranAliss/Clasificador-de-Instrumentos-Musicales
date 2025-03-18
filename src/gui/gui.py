import os
import re
import time
from pygame import mixer
import threading
import json
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage
from utils.file_processor import FileProcessor
from PIL import Image
from playsound import playsound
from tkinterdnd2 import DND_FILES

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
        self.geometry("740x525")
        self.minsize(710, 525)
        self.maxsize(750,580)
        self.configure(bg=PRIMARY_COLOR)
        self.file_paths = []
        self.destination_path = None
        self.load_config()
        self.processor = FileProcessor(classifier, self.config)
        self.init_ui()
        mixer.init()
        self.mark = 0

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
            self.config = {"instrument_labels":{"Acoustic Guitar":"Acoustic Guitar", 
                                                "Bass":"Bass", 
                                                "Drums":"Drums", 
                                                "Electric Guitar":"Electric Guitar", 
                                                "Piano":"Piano"}}
            self.save_config()
    
    def save_config(self):
        with open(CONFIG_FILE, "w") as file:
            json.dump(self.config, file)
    
    def init_ui(self):
        self.tabs = ctk.CTkTabview(self, width=680, height=515)
        self.tabs.pack(pady=10, padx=10, fill="both")
        
        self.main_tab = self.tabs.add("Main")
        self.settings_tab = self.tabs.add("Settings")
        self.about_tab = self.tabs.add("About")
        
        self.create_main_tab()
        self.create_settings_tab()
        self.create_about_tab()
    
    def add_file_to_ui(self, file_path):
        file_frame = ctk.CTkFrame(self.file_scroll_frame)
        file_frame.pack(fill="x", pady=2, padx=2)

        file_label = ctk.CTkLabel(file_frame, text=os.path.basename(file_path), anchor="w", width=150, wraplength=195)
        file_label.pack(side="left", padx=(5, 0))

        delete_button = ctk.CTkButton(file_frame, text="", image=self.iconDelete, width=5, fg_color="transparent",hover_color="black",
                                    command=lambda: self.delete_file_entry(file_frame, file_path))
        delete_button.pack(side="right", padx=1)
        
        forward_button = ctk.CTkButton(file_frame, text="", image=self.iconForward, width=5, fg_color="transparent",hover_color="black",
                                    command=lambda: self.skip_30s())
        forward_button.pack(side="right", padx=1)

        play_button = ctk.CTkButton(file_frame, text="", image=self.iconPlay, width=5, fg_color="transparent", hover_color="black",
                                    command=lambda: self.toggle_audio(play_button, file_path))
        play_button.pack(side="right", padx=1)

    def toggle_audio(self, play_button, file_path):
        if mixer.music.get_busy():
            self.stop_audio()
            play_button.configure(image=self.iconPlay, command=lambda: self.toggle_audio(play_button, file_path))
        else:
            self.play_audio(file_path)
            play_button.configure(image=self.iconStop, command=lambda: self.toggle_audio(play_button, file_path))

    def play_audio(self, file_path):
        if not mixer.music.get_busy():
            mixer.music.load(file_path)
            mixer.music.play()
            self.mark = 0
        else:
            self.stop_audio()
            mixer.music.load(file_path)
            mixer.music.play()
            self.mark = 0

    def stop_audio(self):
        if mixer.music.get_busy():
            mixer.music.stop()

    def skip_30s(self):
        if mixer.music.get_busy():
            mixer.music.set_pos(self.mark)
            self.mark = self.mark + 20

    def delete_file_entry(self, frame, file_path):
        frame.destroy()
        self.file_paths.remove(file_path)
        self.stop_audio()

    def create_main_tab(self):
        if getattr(sys, 'frozen', False):
            BASE_DIR = sys._MEIPASS
        else:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        ICON_DIR = os.path.join(BASE_DIR, "btn_icons")
        iconAI = PhotoImage(file=os.path.join(ICON_DIR, "ai.png")).subsample(16, 16)
        iconUpload = PhotoImage(file=os.path.join(ICON_DIR, "upload.png")).subsample(16, 16)
        iconTrash = PhotoImage(file=os.path.join(ICON_DIR, "delete.png")).subsample(24, 24)
        iconFolder = PhotoImage(file=os.path.join(ICON_DIR, "folder.png")).subsample(18, 18)
        iconPlay = PhotoImage(file=os.path.join(ICON_DIR, "play.png")).subsample(24, 24)
        iconStop = PhotoImage(file=os.path.join(ICON_DIR, "stop.png")).subsample(30, 30)
        iconForward = PhotoImage(file=os.path.join(ICON_DIR, "forward.png")).subsample(32, 32)
        iconDelete = PhotoImage(file=os.path.join(ICON_DIR, "delete_small.png")).subsample(32, 32)

        frame_left = ctk.CTkFrame(self.main_tab, border_width=2, border_color="LightSkyBlue4")
        frame_left.pack(side="left", fill="both", expand=True, padx=5, pady=10)

        label_top = ctk.CTkLabel(frame_left, text="1. Selecciona los archivos", font=("@MicrosoftJhengHeiUI", 16, "bold"))
        label_top.pack(pady=5, padx=5, fill="x")

        self.file_scroll_frame = ctk.CTkScrollableFrame(frame_left, width=300, height=320, border_width=0.5, border_color="LightSkyBlue4")
        self.file_scroll_frame.pack(pady=5,padx=8, fill="both", expand=True)

        self.btn_select_files = ctk.CTkButton(frame_left, text="Upload Files",font=("@MicrosoftJhengHeiUI",14), command=self.select_files, image=iconUpload, compound="left")
        self.btn_select_files.pack(pady=5, padx=5, side="left")

        self.btn_clear_files = ctk.CTkButton(frame_left, text="Clean Files", text_color="gray1", font=("@MicrosoftJhengHeiUI",14),command=self.clear_file_list, state="disabled", fg_color="snow4", image=iconTrash, compound="left")
        self.btn_clear_files.pack(pady=5, padx=5, side="right")

        frame_right = ctk.CTkFrame(self.main_tab, border_width=2, border_color="LightSkyBlue4")
        frame_right.pack(side="right", fill="both", expand=True, padx=5, pady=10)

        frame_destination = ctk.CTkFrame(frame_right, fg_color="gray20", width=100, border_width=0.5, border_color="LightSkyBlue4")
        frame_destination.pack(fill="x", padx=10, pady=5)

        self.btn_select_destination = ctk.CTkButton(frame_destination, text="Pick Destination",font=("@MicrosoftJhengHeiUI",14), command=self.select_destination, image=iconFolder, compound="left")
        self.btn_select_destination.pack(pady=5)
        self.destination_label = ctk.CTkLabel(frame_destination, text="", text_color="white", font=("@MicrosoftJhengHeiUI", 12, "italic"))

        frame_project = ctk.CTkFrame(frame_right, fg_color="gray20", width=100, border_width=0.5, border_color="LightSkyBlue4")
        frame_project.pack(fill="both", padx=10, pady=10)

        self.project_entry_label = ctk.CTkLabel(frame_project, text="Prefix (Song name):")
        self.project_entry_label.pack(pady=(5, 2))
        self.project_entry = ctk.CTkEntry(frame_project, width=150)
        self.project_entry.pack(pady=(2, 10))
        self.project_entry.bind("<KeyRelease>", lambda event: self.update_filename_preview())

        frame_process = ctk.CTkFrame(frame_right, fg_color="gray20", width=100, height=100, border_width=0.5, border_color="LightSkyBlue4")
        frame_process.pack(fill="both", padx=10, pady=10, side="bottom")

        self.filename_preview_label = ctk.CTkLabel(
            frame_project,
            text="Preview: <instrument>_1.wav",
            font=("@MicrosoftJhengHeiUI", 12, "italic"),
            wraplength=200,
            justify="left")
        self.filename_preview_label.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(frame_process, width=250)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        self.btn_process = ctk.CTkButton(frame_process, text="AI Classify", font=("@MicrosoftJhengHeiUI",18, "bold"), state="disabled", height=80, width=220, 
                                        command=self.start_processing, fg_color='cyan3', image=iconAI, compound="left")
        self.btn_process.pack(pady=10)

        self.canvas = ctk.CTkCanvas(frame_process, width=25, height=25, highlightthickness=0, bg="gray20")       
        self.canvas.pack()

        self.iconPlay = iconPlay
        self.iconStop = iconStop
        self.iconForward = iconForward
        self.iconDelete = iconDelete

    def create_settings_tab(self):
        frame_settings = ctk.CTkFrame(self.settings_tab)
        frame_settings.pack(fill="both", expand=True, padx=10, pady=8)

        self.naming_label = ctk.CTkLabel(frame_settings, text="Change instrument tags", text_color=TEXT_COLOR)
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

        self.btn_save_settings = ctk.CTkButton(frame_settings, text="Save Settings", command=self.update_naming_pattern)
        self.btn_save_settings.pack(pady=5)

        self.btn_reset_settings = ctk.CTkButton(frame_settings, text="Reset Settings", command=self.reset_naming_pattern)
        self.btn_reset_settings.pack(pady=5)
    
    def update_filename_preview(self):
        project_name = self.project_entry.get().strip()
        filename = f"{project_name}_<instrumento>_1.wav" if project_name else f"<instrumento>_1.wav"
        self.filename_preview_label.configure(text=f"Preview: {filename}")

    def update_naming_pattern(self):
        for key, entry in self.naming_entries.items():
            self.config["instrument_labels"][key] = entry.get()

        with open(CONFIG_FILE, "w") as config_file:
            json.dump(self.config, config_file, indent=4)
    
    def reset_naming_pattern(self):
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
        self.processor.update_config(self.config)
        self.update_naming_pattern()

    def create_about_tab(self):
        frame_about = ctk.CTkScrollableFrame(self.about_tab)
        frame_about.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Sección 1: Tutorial de Usuario ---
        frame_tutorial = ctk.CTkFrame(frame_about, fg_color="gray20")
        frame_tutorial.pack(fill="x", pady=10, padx=5)

        label_tutorial = ctk.CTkLabel(frame_tutorial, text="📖 Tutorial de Usuario", font=("Arial", 14, "bold"))
        label_tutorial.pack(pady=5)

        if getattr(sys, 'frozen', False):
            BASE_DIR = sys._MEIPASS
        else:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        IMG_DIR = os.path.join(BASE_DIR, "img")

        tutorial_steps = [
            ("1. Selecciona los archivos de audio.", os.path.join(IMG_DIR, "step1.png")),
            ("2. Especifica la carpeta de destino.", os.path.join(IMG_DIR, "step2.png")),
            ("3. Ingresa el nombre del proyecto (opcional).", os.path.join(IMG_DIR, "step3.png")),
            ("4. Presiona 'Renombrar y Guardar'.", os.path.join(IMG_DIR, "step4.png"))
        ]

        for step_text, image_file in tutorial_steps:
            label_step = ctk.CTkLabel(frame_tutorial, text=step_text, justify="left", wraplength=400)
            label_step.pack(pady=2)
            img = ctk.CTkImage(light_image=Image.open(image_file), size=(500, 300))
            img_label = ctk.CTkLabel(frame_tutorial, image=img, text="")
            img_label.pack(pady=5)

        # --- Sección 2: Información sobre el Modelo ---
        frame_model_info = ctk.CTkFrame(frame_about, fg_color="gray20")
        frame_model_info.pack(fill="x", pady=10, padx=5)

        label_model = ctk.CTkLabel(frame_model_info, text="🎵 Información del Modelo", font=("Arial", 14, "bold"))
        label_model.pack(pady=5)

        results_text = """El modelo cuenta con una precisión del 98% (promedio aritmético y ponderado):"""
        label_model_results = ctk.CTkLabel(frame_model_info, text=results_text, justify="left", wraplength=400)
        label_model_results.pack(pady=5)
        model_image_results = ctk.CTkImage(light_image=Image.open(os.path.join(IMG_DIR, "results.png")), size=(300, 175))
        results_img_label = ctk.CTkLabel(frame_model_info, image=model_image_results, text="")
        results_img_label.pack(pady=5)

        confusion_text = """Matriz de confusión de la clasificación del modelo con datos nuevos:"""
        label_model_confusion = ctk.CTkLabel(frame_model_info, text=confusion_text, justify="left", wraplength=400)
        label_model_confusion.pack(pady=5)
        model_image_confusion = ctk.CTkImage(light_image=Image.open(os.path.join(IMG_DIR, "confusion.png")), size=(400, 350))
        confusion_img_label = ctk.CTkLabel(frame_model_info, image=model_image_confusion, text="")
        confusion_img_label.pack(pady=5)

        train_text = """Gráficas del entrenamiento del modelo:"""
        label_model_train = ctk.CTkLabel(frame_model_info, text=train_text, justify="left", wraplength=400)
        label_model_train.pack(pady=5)
        model_image_train = ctk.CTkImage(light_image=Image.open(os.path.join(IMG_DIR, "train.png")), size=(500, 250))
        train_img_label = ctk.CTkLabel(frame_model_info, image=model_image_train, text="")
        train_img_label.pack(pady=5)

        info_text = """El modelo utilizado en la aplicación cuenta con un elevado porcentaje de precisión. La matriz de confusión muestra el desempeño del modelo para cada instrumento y las gráficas de entrenamiento muestran convergencia y ausencia de sobre-entrenamiento. Aún así, es importante recalcar que el modelo no es perfecto y puede fallar en ocasiones."""
        label_model_info = ctk.CTkLabel(frame_model_info, text=info_text, justify="left", wraplength=400)
        label_model_info.pack(pady=5)
        # --- Sección 3: Información General y Enlaces ---
        frame_general_info = ctk.CTkFrame(frame_about, fg_color="gray20")
        frame_general_info.pack(fill="x", pady=10, padx=5)

        label_general = ctk.CTkLabel(frame_general_info, text="ℹ️ Información General", font=("Arial", 14, "bold"))
        label_general.pack(pady=5)

        general_text = """Desarrollado por Francisco Gabriel Aliss Arteaga.\nContacto: franalissar@gmail.com"""
        
        label_general_text = ctk.CTkLabel(frame_general_info, text=general_text, justify="left", wraplength=400)
        label_general_text.pack(pady=5)

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Archivos WAV", "*.wav")])
        if files:
            self.file_paths.extend(files)
            for file in files:
                self.add_file_to_ui(file) 
    
    def clear_file_list(self):
        self.btn_clear_files.configure(state="disabled")
    
    def select_destination(self):
        destination = filedialog.askdirectory()
        if destination:
            short_path = re.split(r'[/\\]', destination)[-1]
            self.destination_label.configure(text=f"Destination: {short_path}")
            self.destination_label.pack(pady=3)
            self.destination_path = destination
            self.btn_process.configure(state="normal")
    
    def start_processing(self):
        if not self.file_paths or not self.destination_path:
            messagebox.showwarning("Warning", "Upload files and set a destination folder.")
            return
        self.progress_bar.set(0)
        self.process_thread = threading.Thread(target=self.process_files)
        self.process_thread.start()
    
    def process_files(self):
        total_files = len(self.file_paths)
        # ---------- Deshabilitar botones ----------------
        self.btn_select_destination.configure(state='disabled')
        self.btn_select_files.configure(state='disabled')
        self.btn_reset_settings.configure(state='disabled')
        self.btn_save_settings.configure(state='disabled')
        self.btn_clear_files.configure(state='disabled')
        self.btn_process.configure(state='disabled')
        # -----------------------------------------------
        self.create_circular_loader()
        # --------------- progress bar y model -----------
        for i, file_path in enumerate(self.file_paths, start=1):
            self.processor.process(file_path, self.destination_path, self.project_entry.get())
            progress = i / total_files
            
            for _ in range(10):
                # time.sleep(0.1)
                self.progress_bar.set(progress - 0.1 + (_ * 0.01))
        
        self.stop_circular_loader()
        self.progress_bar.set(1)
        messagebox.showinfo("Processing", "AI processing finished.")

        # ------------ Habilitar botones -------------------------
        self.btn_select_destination.configure(state='normal')
        self.btn_select_files.configure(state='normal')
        self.btn_reset_settings.configure(state='normal')
        self.btn_save_settings.configure(state='normal')
        self.btn_process.configure(state='normal')
        # --------------------------------------------------------

        # self.file_list.configure(state="normal")
        # self.file_list.delete("1.0", "end")
        # self.file_list.configure(state="disabled")
        self.file_paths.clear()
        os.startfile(self.destination_path)
        self.progress_bar.set(0)
        self.btn_process.configure(state="disabled")
        self.btn_clear_files.configure(state="disabled")