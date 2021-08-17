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
    
    def isModelExist(self):
        return os.path.exists(self.model)
    
    def isModelNotExist(self):
        if not self.isModelExist():
            print ("Warning: Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit (1)
    
    def isFileExist(self):
        return os.path.exists(self.file)
    
    def isFileNotExist(self):
        if not self.isFileExist():
            print ("Warning: File: ("+self.getFile()+") not exist. Please input the directory of the file")
            exit (1)
    
    def checkImportantFiles(self):
        self.isModelNotExist()
        self.isFileNotExist()
    
    def run(self, file):
        self.setFile(file)

        SetLogLevel(0)

        self.checkImportantFiles()
    
        model = Model(self.getModel())
        rec = KaldiRecognizer(model, self.getSampleRate())

        process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                    self.getFile(),
                                    '-ar', str(self.getSampleRate()) , '-ac', '1', '-f', 's16le', '-'],
                                    stdout=subprocess.PIPE)

        #output time and words
        rec.SetWords(True)

        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                print(rec.Result())
            else:
                print(rec.PartialResult())

        print(rec.FinalResult())

