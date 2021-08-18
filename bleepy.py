from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import sys
import wave
import subprocess

class MediaFile:
    def __init__(self):
        self.file = "NaN"
    
    #Private Method that set file default file if null and doesnt alter the file set in the class
    def __setFileIfNull(self, file):
        return self.getFile() if file == "" else file
    
    #Private Method use to safe set file, doenst alter the file directly
    def __safeSetFile(self,file):
        file = self.__setFileIfNull(file)
        self.checkFileExist(file)
        return file

    #Set File
    def setFile(self, file):
        self.file = self.__safeSetFile(file)
    
    #Return File
    def getFile(self):
        return self.file
    
    #Return boolean , if file exist
    def isFileExist(self, file = ""):
        return os.path.exists(self.__setFileIfNull(file))
    
    #Check file exist, if not, print error
    def checkFileExist(self, file):
        if not self.isFileExist(file):
            print ("Warning: File: ("+file+") not found. Please input or set the correct directory of the file")
            exit (1)
    
    #Return File Extension
    def getFileExtension(self, file = ""):
        file = self.__safeSetFile(file)
        return file.rsplit('.',1)[1]
    
    #Return Full Duration of the Media File
    def getFullDuration(self, file = ""):
        file = file = self.__safeSetFile(file)
        #durationcmd = 'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"'+file+'\"'
        durationcmd = ['ffprobe', '-v' ,'error', '-show_entries', 'format=duration', '-of' ,'default=noprint_wrappers=1:nokey=1', file]
        proc = subprocess.Popen(durationcmd, stdout=subprocess.PIPE)
        output = proc.stdout.read()
        output = str(output).replace("\\","")
        for x in ("b","\'","n","r"):
            output = output.strip(x) 
        return float(output)

#SpeechRecognition
#model = language-model
#file = file

class SpeechToText(MediaFile):
    def __init__(self):
        super().__init__()
        self.model = "model"
        self.sample_rate=16000
    
    def setModel(self, model="model"):
        self.checkModelExist(model)
        self.model = model
    
    def setSampleRate(self, sample_rate = 16000):
        self.sample_rate = sample_rate
    
    def getModel(self):
        return self.model
    
    def getSampleRate(self):
        return self.sample_rate
    
    #Return STT Class ffmpeg command
    def getSttCmd(self):
        return ['ffmpeg', '-loglevel', 'quiet', '-i',self.getFile(), '-ar', str(self.getSampleRate()) , '-ac', '1', '-f', 's16le', '-']
    
    def isModelExist(self, model = ""):
        model = self.getModel() if model == "" else model
        return os.path.exists(model)
    
    def checkModelExist(self, model = ""):
        if not self.isModelExist(model):
            print ("Warning: Model Directory not found ("+model+"). Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit (1)
    
    def run(self, file):
        self.setFile(file)

        self.checkModelExist()

        # SetLogLevel(0)
        model = Model(self.getModel())
        rec = KaldiRecognizer(model, self.getSampleRate())
        #output time and words
        rec.SetWords(True)

        process = subprocess.Popen(self.getSttCmd(),stdout=subprocess.PIPE)

        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                print(rec.Result())
            else:
                print(rec.PartialResult())

        print(rec.FinalResult())

