from utils.instrument_classifier import InstrumentClassifier
from gui.gui import MainWindow

MODEL_PATH = "models/instrument_classifier_bayesian_2.keras"
CLASS_LABELS = ["Acoustic Guitar", "Bass", "Drums", "Electric Guitar", "Piano"]

if __name__ == "__main__":
    classifier = InstrumentClassifier(MODEL_PATH, CLASS_LABELS)
    app = MainWindow(classifier)
    app.mainloop()
