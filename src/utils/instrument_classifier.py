import tensorflow as tf
import numpy as np
from .audio_preprocessor import AudioPreprocessor

class InstrumentClassifier:
    def __init__(self, model_path, class_labels):
        self.model = tf.keras.models.load_model(model_path)
        self.class_labels = class_labels

    def predict(self, file_path):
        features = AudioPreprocessor.preprocess(file_path)
        features = np.expand_dims(features, axis=0)
        prediction = self.model.predict(features)
        return self.class_labels[np.argmax(prediction)]
