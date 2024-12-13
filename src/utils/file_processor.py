import os
import shutil
from .instrument_classifier import InstrumentClassifier

class FileProcessor:
    def __init__(self, classifier):
        self.classifier = classifier
        self.class_counter = {}

    def process(self, file_path, destination):
        predicted_class = self.classifier.predict(file_path)
        ext = os.path.splitext(file_path)[1]

        self.class_counter[predicted_class] = self.class_counter.get(predicted_class, 0) + 1
        count = self.class_counter[predicted_class]
        new_file_name = f"{predicted_class}_{count}{ext}" if count > 1 else f"{predicted_class}{ext}"
        
        new_path = os.path.join(destination, new_file_name)
        shutil.copy(file_path, new_path)
