# bleepy
Bleepy is a Python program that can block Tagalog and English profanity in audio and videos.

## Requirements
The following are the Python modules and software that are needed to run this program.

### FFMPEG
Note: FFMPEG is also needed to be installed to run this program.

### Python modules
1. vosk-api
   - Offline speech recognition
   - https://pypi.org/project/vosk/
   - https://github.com/alphacep/vosk-api
   - Language Model: https://alphacephei.com/vosk/models

2. bleepy-profanity-check
   - Profanity checker in string that uses machine learning
   - https://pypi.org/project/bleepy-profanity-check/
   - https://github.com/dimitrismistriotis/profanity-check

## Development

### Installation

1. Clone this repository.
2. Install Python 3.
   - Download [here](https://www.python.org/downloads/)
   - Python version 3.9 or above
   - Create a virtual environment by running python -m venv venv
   - Activate the virtual environment by running .\venv\Scripts\Activate.ps1
   - Check if you have the right python version: python --version should output 3.9.0 or higher

3. Install FFMPEG.
   - Easy Installation tutorial for [FFMPEG](https://www.wikihow.com/Install-FFmpeg-on-Windows)
   - If you install VLC Media Player, you already have FFMPEG

4. Install Packages. You can easily install packages by running `python -m pip install -r requirements.txt`
   - Install vosk.
      - `pip install vosk`
      - pip for [vosk](https://pypi.org/project/vosk/)
      - [Documentation](https://github.com/alphacep/vosk-api)
      - Tutorial to use [vosk](https://www.youtube.com/watch?v=Itic1lFc4Gg)
   - Install bleepy-profanity-check.
      - `pip install bleepy-profanity-check`
      - pip for [bleepy-profanity-check](https://pypi.org/project/bleepy-profanity-check/)
      - [Documentation](https://github.com/reyniel26/bleepy-profanity-check)

5. Set up the language model (follow the instructions).
   - Download the language model for vosk from [models page](https://alphacephei.com/vosk/models). My suggested model is [vosk-model-en-us-aspire-0.2](https://alphacephei.com/vosk/models/vosk-model-en-us-aspire-0.2.zip).
   - Paste it inside bleepy directory or folder. Make sure the file is inside the bleepy folder.
   - Extract it.
   - Rename it to model.
6. Try to run test_bleepy.py.

## Testing and linting

1. `pip install pylint`
2. `pip install pytest`
3. `pylint bleepy`
