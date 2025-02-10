import os
import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QLabel, QFileDialog, QMessageBox,
    QProgressBar, QTabWidget, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QDragEnterEvent, QDropEvent
from utils.file_processor import FileProcessor

PRIMARY_COLOR = "#1F1F1F"
SECONDARY_COLOR = "#2C2C2C"
ACCENT_COLOR = "#3A99D9"
TEXT_COLOR = "#FFFFFF"
BUTTON_COLOR = "#444444"
HIGHLIGHT_COLOR = "#555555"
TAB_ACTIVE_COLOR = "#3A99D9"
TAB_INACTIVE_COLOR = "#2C2C2C"

class FileProcessorThread(QThread):
    progress = pyqtSignal(int)
    completed = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, file_paths, destination, processor):
        super().__init__()
        self.file_paths = file_paths
        self.destination = destination
        self.processor = processor
        self.cancel_flag = False

    def run(self):
        try:
            total_files = len(self.file_paths)
            for i, file_path in enumerate(self.file_paths):
                if self.cancel_flag:
                    return
                self.processor.process(file_path, self.destination)
                self.progress.emit(int(((i + 1) / total_files) * 100))
            self.completed.emit()
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self.cancel_flag = True


class MainWindow(QMainWindow):
    def __init__(self, classifier):
        super().__init__()
        self.file_paths = []
        self.processor = FileProcessor(classifier)
        self.thread = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Clasificador de Instrumentos Musicales")
        self.setFixedSize(520, 450)
        self.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR};")
        self.setWindowIcon(QIcon('icon.ico'))

        self.setAcceptDrops(True)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"QTabBar::tab {{ background: {TAB_INACTIVE_COLOR}; color: {TEXT_COLOR}; padding: 10px; }} QTabBar::tab:selected {{ background: {TAB_ACTIVE_COLOR}; }}")
        self.setCentralWidget(self.tabs)

        self.main_tab = QWidget()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.main_tab, "Principal")
        self.tabs.addTab(self.settings_tab, "Configuración")

        self.create_main_tab()
        self.create_settings_tab()

    def create_main_tab(self):
        layout = QHBoxLayout()

        self.file_list = QListWidget()
        self.file_list.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: {TEXT_COLOR};")
        self.file_list.setFixedSize(260, 330)

        btn_select_files = QPushButton("Seleccionar Archivos")
        btn_select_files.clicked.connect(self.select_files)
        btn_select_files.setStyleSheet(f"QPushButton {{ background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; }} QPushButton:hover {{ background-color: {HIGHLIGHT_COLOR}; }}")

        self.destination_label = QLabel("Destino: No seleccionado")
        btn_select_destination = QPushButton("Seleccionar Destino")
        btn_select_destination.clicked.connect(self.select_destination)
        btn_select_destination.setStyleSheet(f"QPushButton {{ background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; }} QPushButton:hover {{ background-color: {HIGHLIGHT_COLOR}; }}")

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"QProgressBar {{ text-align: center; color: black; }} QProgressBar::chunk {{ background-color: {ACCENT_COLOR}; }}")
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

        btn_process = QPushButton("Renombrar y Guardar")
        btn_process.clicked.connect(self.start_processing)
        btn_process.setStyleSheet(f"QPushButton {{ background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; }} QPushButton:hover {{ background-color: {HIGHLIGHT_COLOR}; }}")

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.cancel_processing)
        self.btn_cancel.setStyleSheet(f"QPushButton {{ background-color: {BUTTON_COLOR}; color: {TEXT_COLOR}; }} QPushButton:hover {{ background-color: {HIGHLIGHT_COLOR}; }}")
        self.btn_cancel.hide()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Archivos seleccionados:"))
        left_layout.addWidget(self.file_list)
        left_layout.addWidget(btn_select_files)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.destination_label)
        right_layout.addWidget(btn_select_destination)
        right_layout.addWidget(btn_process)
        right_layout.addWidget(self.progress_bar)
        right_layout.addWidget(self.btn_cancel)

        layout.addLayout(left_layout, 2)
        layout.addLayout(right_layout, 1)

        self.main_tab.setLayout(layout)

    def create_settings_tab(self):
        layout = QVBoxLayout()
        label = QLabel("Configuración")
        label.setStyleSheet(f"font-size: 18px; font-weight: bold; background-color: {PRIMARY_COLOR}; color: {TEXT_COLOR};")
        layout.addWidget(label)
        self.settings_tab.setLayout(layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".wav"):
                self.file_list.addItem(os.path.basename(path))
                self.file_paths.append(path)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Selecciona archivos WAV", "", "Archivos WAV (*.wav)")
        if files:
            self.file_list.addItems([os.path.basename(f) for f in files])
            self.file_paths.extend(files)

    def select_destination(self):
        destination = QFileDialog.getExistingDirectory(self, "Selecciona el destino")
        if destination:
            short_path = re.split(r'[/\\]', destination)[-1]
            self.destination_label.setText(f"Destino: ../{short_path}")
            self.destination_path = destination

    def start_processing(self):
        if not self.file_paths or not hasattr(self, 'destination_path'):
            QMessageBox.warning(self, "Advertencia", "Selecciona archivos y destino.")
            return

        self.progress_bar.show()
        self.btn_cancel.show()
        self.thread = FileProcessorThread(self.file_paths, self.destination_path, self.processor)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.completed.connect(self.processing_completed)
        self.thread.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.thread.start()

    def processing_completed(self):
        os.startfile(self.destination_path)
        self.progress_bar.hide()
        self.btn_cancel.hide()
        self.file_list.clear()

    def cancel_processing(self):
        if self.thread:
            self.thread.cancel()
            QMessageBox.information(self, "Cancelado", "El proceso ha sido cancelado.")
            self.progress_bar.hide()
            self.btn_cancel.hide()