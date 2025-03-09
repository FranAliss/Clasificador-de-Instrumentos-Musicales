import os
import shutil
from .instrument_classifier import InstrumentClassifier

class FileProcessor:
    def __init__(self, classifier, config):
        self.classifier = classifier
        self.config = config
        self.class_counter = {}

    def update_config(self, new_config):
        self.config = new_config

    def process(self, file_path, destination, project_name=None):
        predicted_class = self.classifier.predict(file_path)
        ext = os.path.splitext(file_path)[1]

        self.class_counter[predicted_class] = self.class_counter.get(predicted_class, 0) + 1
        count = self.class_counter[predicted_class]

        predicted_class_user_label = self.config["instrument_labels"][predicted_class]
        if project_name:
            new_file_name = project_name + "_" + predicted_class_user_label + "_" + str(count)
        else:
            new_file_name = predicted_class_user_label + "_" + str(count)

        new_path = os.path.join(destination, new_file_name + ext)
        shutil.copy(file_path, new_path)
