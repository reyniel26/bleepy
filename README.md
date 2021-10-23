# bleepy
Bleepy is a python program can block tagalog and english profanity audio in videos.

## Requirements
The following are the Python modules and software that are needed to run this program.

### FFMPEG
Note: FFMPEG is also needed to be installed to run this program.

### Python modules 
1. vosk-api
   - v 0.3.30 to latest
   - Offline speech recognition 
   - https://pypi.org/project/vosk/
   - https://github.com/alphacep/vosk-api
   - Language Model: https://alphacephei.com/vosk/models

2. alt-profanity-check
   - v 0.24.2 to latest
   - Profanity checker in string that uses machine learning
   - https://pypi.org/project/alt-profanity-check/
   - https://github.com/dimitrismistriotis/profanity-check


## Installation

1. Clone this repository
2. Install Python 3 
   - Download [here](https://www.python.org/downloads/)
3. Install FFMPEG
   - Easy Installation tutorial for [FFMPEG](https://www.wikihow.com/Install-FFmpeg-on-Windows)
4. pip install vosk
   - pip for [vosk](https://pypi.org/project/vosk/)
   - [Documentation](https://github.com/alphacep/vosk-api)
   - Tutorial to use [vosk](https://www.youtube.com/watch?v=Itic1lFc4Gg)
5. pip install alt-profanity-check
   - pip for [alt-profanity-check](https://pypi.org/project/alt-profanity-check/)
   - [Documentation](https://github.com/dimitrismistriotis/profanity-check)
6. Set up language model (follow the instruction)
   - Download language model for vosk from [models page](https://alphacephei.com/vosk/models). My suggested model is [vosk-model-en-us-aspire-0.2](https://alphacephei.com/vosk/models/vosk-model-en-us-aspire-0.2.zip)
   - Paste it inside bleepy directory or folder. Make sure the file is inside of the bleepy folder
   - Extract it
   - Rename it to model
 7. Try to run test_bleepy.py




