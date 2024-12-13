
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
git clone <URL_OF_REPOSITORY>
cd InstrumentClassifierApp
```

### 2. Set Up Virtual Environment
Create and activate a virtual environment to avoid dependency conflicts:  
```bash
python -m venv env
source env/bin/activate  # On Linux/MacOS
env\Scripts\activate   # On Windows
```

### 3. Install Dependencies
Install all required Python libraries:  
```bash
pip install -r requirements.txt
```

### 4. Pretrained Model
Ensure the pretrained model file exists in the `models/` directory. The file should be named `instrument_classifier_cross_validated.keras`.

### 5. Run the Application
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
|   ├── utils/
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
- The application will create a destination folder where the classified files will be renamed and organized.
