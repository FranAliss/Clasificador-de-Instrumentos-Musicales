from utils.instrument_classifier import InstrumentClassifier
from gui.gui import GUI
import tkinter as tk


if __name__ == "__main__":
    MODEL_PATH = "models/instrument_classifier_cross_validated.keras"
    CLASS_LABELS = ["Acoustic Guitar", "Bass", "Drums", "Electric Guitar", "Piano"]

    classifier = InstrumentClassifier(MODEL_PATH, CLASS_LABELS)
    root = tk.Tk()
    app = GUI(root, classifier)
    root.mainloop()
