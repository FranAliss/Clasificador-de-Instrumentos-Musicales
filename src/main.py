import sys
import os
from utils.instrument_classifier import InstrumentClassifier
from gui.gui import MainWindow

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

MODEL_PATH = os.path.join(base_path, "models", "instrument_classifier_bayesian_4.keras")
CLASS_LABELS = ["Acoustic Guitar", "Bass", "Drums", "Electric Guitar", "Piano"]
ICON_PATH = os.path.join(base_path, "guitar_28109.ico")

if __name__ == "__main__":
    classifier = InstrumentClassifier(MODEL_PATH, CLASS_LABELS)
    app = MainWindow(classifier)
    app.iconbitmap(ICON_PATH)
    app.mainloop()