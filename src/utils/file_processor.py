import os
import shutil
from .instrument_classifier import InstrumentClassifier

class FileProcessor:
    def __init__(self, classifier, config):
        self.classifier = classifier
        self.config = config
        self.class_counter = {}

    def update_config(self, new_config):
        """Actualizar configuración de nombres."""
        self.config = new_config

    def process(self, file_path, destination):
        predicted_class = self.classifier.predict(file_path)
        ext = os.path.splitext(file_path)[1]

        self.class_counter[predicted_class] = self.class_counter.get(predicted_class, 0) + 1
        count = self.class_counter[predicted_class]

        naming_pattern = self.config.get("naming_pattern", "instrumento_#")
        new_file_name = naming_pattern.replace("#", str(count)).replace("instrumento", predicted_class)

        new_path = os.path.join(destination, new_file_name + ext)
        shutil.copy(file_path, new_path)
        return new_file_name + ext
