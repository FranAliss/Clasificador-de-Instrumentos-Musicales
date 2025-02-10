from utils.instrument_classifier import InstrumentClassifier
from gui.gui import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    MODEL_PATH = "models/instrument_classifier_bayesian_2.keras"
    CLASS_LABELS = ["Acoustic Guitar", "Bass", "Drums", "Electric Guitar", "Piano"]

    classifier = InstrumentClassifier(MODEL_PATH, CLASS_LABELS)
    
    app = QApplication(sys.argv)
    window = MainWindow(classifier)
    window.show()
    sys.exit(app.exec_())
