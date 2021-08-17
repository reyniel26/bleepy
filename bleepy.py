from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import sys
import wave
import subprocess

#SpeechRecognition
#model = language-model
#file = file

class SpeechRecognition:
    def __init__(self):
        self.model = "model"
        self.file = ""
        self.sample_rate=16000
    
    def setModel(self, model):
        self.model = model
    
    def setFile(self, file):
        self.file = file
    
    def setSampleRate(self, sample_rate):
        self.sample_rate = sample_rate
    
    def getModel(self):
        return self.model
    
    def getFile(self):
        return self.file
    
    def getSampleRate(self):
        return self.sample_rate
    
    def isModelNotExist(self):
        if not os.path.exists(self.model):
            print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit (1)

