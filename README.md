
# Instrument Classifier App

This application allows you to classify audio files by musical instruments using a deep learning model.

## System Requirements
- **Operating System:** Windows, macOS, or Linux
- **Python:** Version 3.8 or higher
- **Dependencies:** Listed in `requirements.txt`

## Installation and Usage

### 1. Clone the Repository
Download or clone this repository:  
```bash
git clone https://github.com/FranAliss/proyecto_de_grado.git
cd InstrumentClassifierApp
```

### 2. Install Dependencies
Install all required Python libraries:  
```bash
pip install -r requirements.txt
```

### 3. Pretrained Model
Ensure the pretrained model file exists in the `models/` directory. The file should be named `instrument_classifier_cross_validated.keras`.

### 4. Run the Application
Run the application from the main file:  
```bash
python main.py
```

## Project Structure
```plaintext
InstrumentClassifierApp/
│
├── models/
│   └── the_model(.keras|.h5)
├── src/
|   ├── main.py
│   ├── gui/
|       └── gui.py
|   └── utils/
|       └── audio_preprocessor.py
|       └── file_processor.py
|       └── instrument_classifier.py
├── requirements.txt
└── README.md
```

## Dependencies
Dependencies are listed in the `requirements.txt` file:  
```plaintext
numpy
librosa
tensorflow
tk
```

## Additional Notes
- Ensure that the audio files to classify are in `.wav` format.
