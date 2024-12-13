import librosa
import numpy as np

class AudioPreprocessor:
    @staticmethod
    def preprocess(file_path):
        y, sr = librosa.load(file_path, sr=16000)
        y_trimmed, _ = librosa.effects.trim(y, top_db=20)
        mfcc = librosa.feature.mfcc(y=y_trimmed, sr=sr, n_mfcc=40)
        return np.mean(mfcc.T, axis=0)
