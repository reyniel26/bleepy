from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import sys
import wave
import subprocess


class MediaFile:
    #Abstraction for MediaFile
    def __init__(self):
        self.__file = "NaN"
        self.__allowedExtensions = ["mp4","mp3"]
        self.__extension = ""
        self.__duration = 0.0
    
    def __setFileIfNull(self, file):
        #Private Method that set file default file if null and doesnt alter the file set in the class
        return self.getFile() if file == "" else file
     
    def __safeSetFile(self,file):
        #Private Method use to safe set file, doenst alter the file directly
        file = self.__setFileIfNull(file)
        self.checkIsFileAllowed(file)
        return file

    def setFile(self, file):
        #Set File
        self.__file = self.__safeSetFile(file)
        self.__setFileExtension(file)
        self.__setDuration(file)
    
    def setAllowedExts(self, extensions):
        self.__allowedExtensions = extensions

    def __setFileExtension(self, file):
        #Return File Extension
        self.__extension = self.getExtension(file)
    
    def __setDuration(self, file):
        #Return Full Duration of the Media File
        # #durationcmd = 'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"'+file+'\"'
        durationcmd = ['ffprobe', '-v' ,'error', '-show_entries', 'format=duration', '-of' ,'default=noprint_wrappers=1:nokey=1', file]
        proc = subprocess.Popen(durationcmd, stdout=subprocess.PIPE)
        output = proc.stdout.read()
        output = str(output).replace("\\","")
        for x in ("b","\'","n","r"):
            output = output.strip(x) 
        self.__duration = float(output)

    def getFile(self):
        #Return File
        return self.__file

    def getAllowedExts(self):
        return self.__allowedExtensions

    def getFileExtension(self):
        return self.__extension

    def getExtension(self, file):
        return file.rsplit('.',1)[1]

    def getDuration(self):
        return self.__duration

    def isFileExist(self, file = ""):
        #Return boolean , if file exist
        return os.path.exists(self.__setFileIfNull(file))
     
    def __checkIsFileExist(self, file):
        #Check file exist, if not, print error
        if not self.isFileExist(file):
            print ("Warning: File: ("+file+") not found. Please input or set the correct directory of the file")
            exit (1)
    
    def isAllowedExt(self, extension):
        return extension in self.getAllowedExts()
    
    def __checkIsAllowedExt(self, extension):
        #Check file extension, if not, print error
        if not self.isAllowedExt(extension):
            print ("Warning: File Extension ("+extension+") is not allowed. Please input valid file type "
                    + str(self.getAllowedExts()) 
                    + " or add extensions by using \'addAllowedExt(str)\' or \'extendAllowedExt(list)\' " )
            exit (1)
    
    def isFileAllowed(self,file):
        return self.isFileExist(file) and self.isAllowedExt(self.getExtension(file))
    
    def checkIsFileAllowed(self, file):
        self.__checkIsFileExist(file)
        self.__checkIsAllowedExt(self.getExtension(file))

    def addAllowedExt(self,extension):
        #Add one allowed Extension
        exts = self.getAllowedExts()
        exts.append(extension)
        self.setAllowedExts(exts)
    
    def extendAllowedExt(self,extensions):
        #add list allowed extension
        exts = self.getAllowedExts()
        exts.extend(extensions)
        self.setAllowedExts(exts)
    
    def removeAllowedExt(self,extension):
        #remove one allowed extension
        exts = self.getAllowedExts()
        exts.remove(extension)
        self.setAllowedExts(exts)


class VideoFile(MediaFile):
    #MediaFile is a VideoFile
    def __init__(self):
        super().__init__()
        self.setAllowedExts(["mp4","mpeg","mkv"])

class SpeechToText():
    #SpeechToText or STT
    #model = language-model
    #file = file

    def __init__(self, model = "model"):
        super().__init__()
        self.__model = model
        self.__sample_rate=16000
        self.__video = VideoFile()

        print("Setting up Recognizer for STT...")
        SetLogLevel(0)
        model = Model(self.getModel())
        self.__recognizer = KaldiRecognizer(model, self.getSampleRate())
        self.__recognizer.SetWords(True)

    
    def setModel(self, model="model"):
        self.checkModelExist(model)
        self.__model = model
        self.updateRecognizer()
    
    def setSampleRate(self, sample_rate = 16000):
        self.__sample_rate = sample_rate
        self.updateRecognizer()
    
    def setVideo(self,video):
        self.__video = video
    
    def updateRecognizer(self):
        SetLogLevel(0)
        print("Updating Recognizer for STT...")
        model = Model(self.getModel())
        self.__recognizer = KaldiRecognizer(model, self.getSampleRate())
        self.__recognizer.SetWords(True)
        
    def getModel(self):
        return self.__model
    
    def getVideo(self):
        return self.__video
    
    def getSampleRate(self):
        return self.__sample_rate
    
    def getRecognizer(self):
        return self.__recognizer
    
    def getSttCmd(self):
        #Return FMMPEG Command for STT
        return ['ffmpeg', '-loglevel', 'quiet', '-i',self.getVideo().getFile(), '-ar', str(self.getSampleRate()) , '-ac', '1', '-f', 's16le', '-']
    
    def isModelExist(self, model = ""):
        model = self.getModel() if model == "" else model
        return os.path.exists(model)
    
    def checkModelExist(self, model = ""):
        if not self.isModelExist(model):
            print ("Warning: Model Directory not found ("+model+"). Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit (1)

    def run(self, video):
        self.setVideo(video)
        self.checkModelExist()
        rec = self.getRecognizer()

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




