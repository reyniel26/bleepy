from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import sys
import wave
import subprocess

from profanity_check import predict, predict_prob

class File:
    def __init__(self):
        self.__file = "NaN"
    
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
    
    def getFile(self):
        #Return File
        return self.__file
    
    def isFileExist(self, file = ""):
        #Return boolean , if file exist
        return os.path.exists(self.__setFileIfNull(file))
     
    def checkIsFileExist(self, file):
        #Check file exist, if not, print error
        if not self.isFileExist(file):
            print ("Warning: File: ("+file+") not found. Please input or set the correct directory of the file")
            exit (1)

    def isFileAllowed(self,file):
        return self.isFileExist(file)

    def checkIsFileAllowed(self, file):
        self.checkIsFileExist(file)
    
class MediaFile(File):
    #Abstraction for MediaFile
    def __init__(self):
        super().__init__()
        self.__allowedExtensions = ["mp4","mp3"]
        self.__extension = ""
        self.__duration = 0.0
    
    def setFile(self, file):
        #Set File , Override
        super().setFile(file)
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

    def getAllowedExts(self):
        return self.__allowedExtensions

    def getFileExtension(self):
        return self.__extension

    def getExtension(self, file):
        return file.rsplit('.',1)[1]

    def getDuration(self):
        return self.__duration
    
    def isAllowedExt(self, extension):
        return extension in self.getAllowedExts()
    
    def checkIsAllowedExt(self, extension):
        #Check file extension, if not, print error
        if not self.isAllowedExt(extension):
            print ("Warning: File Extension ("+extension+") is not allowed. Please input valid file type "
                    + str(self.getAllowedExts()) 
                    + " or add extensions by using \'addAllowedExt(str)\' or \'extendAllowedExt(list)\' " )
            exit (1)
    
    def isFileAllowed(self,file):
        #Override
        return super().isFileAllowed() and self.isAllowedExt(self.getExtension(file))
    
    def checkIsFileAllowed(self, file):
        #Override
        super().checkIsFileAllowed(file)
        self.checkIsAllowedExt(self.getExtension(file))

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
    #Video file is a MediaFile
    def __init__(self):
        super().__init__()
        self.setAllowedExts(["mp4","mpeg","mkv"])

class AudioFile(MediaFile):
    #AudioFile is a mediafile
    def __init__(self):
        super().__init__()
        self.setAllowedExts(["mp3","wav"])

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

class ProfanityDetector:

    def extractListOfResults(self,txt): 
        #Make List of Results
        #Vosk, KaldiRecognizer obj.Result() and obj.FinalResult() return txt
        a = txt.split('[')#Split the Result str in open bracket
        b = a[1].split(']') #Get the 2nd half then Split in Closing Bracket
        c = b[0].split(', ') #Get the 1st half then Split in comma and space
        for i in range(len(c)):
            c[i] = c[i].strip("{}") #remove brackets
            c[i] = c[i].replace('\n','') #replace newline
            c[i] = c[i].replace('\"','') #replace "
        return c #return list of Results

    def extractListOfWords(self,txt): 
        #Make List of Words, extracted from the list of Results
        words = [] #create new list
        if "result" in txt: #Check if there is result or words
            for item in self.extractListOfResults(txt):
                attrs= item.split(',') #Split the items into attributes in comma
                tempdict = {} #create temp dict
                for attr in attrs:
                    data = attr.split(':')#Then Split the attributes in : separating the key and value
                    tempdict[data[0].strip()] = data[1].strip()#data[0] is the key, data[1] is the value
                words.append(tempdict)
        #To output this, you can use for loop
        #another example: print(extractListOfWords(txt)[0]["word"])
        return words #return this list of words (dict)

    def extractListOfProfanity(self,txt):
        words = self.extractListOfWords(txt)
        profanity = []
        for word in words:
            if bool(predict([word["word"]])):
                profanity.append(word)
        return profanity #list of dictionaries 

class ProfanityExtractor(SpeechToText):
    #ProfanityExtractor is STT with ProfanityDetector
    def __init__(self, model = "model"):
        super().__init__(model)
        self.__profanities = []
    
    def setProfanities(self,profanities):
        self.__profanities = profanities
    
    def getProfanities(self):
        return self.__profanities
    
    def addProfanity(self, newprofanity):
        profanities = self.getProfanities()
        profanities.append(newprofanity)
        self.setProfanities(profanities)
    
    def extendProfanities(self, newprofanities):
        profanities = self.getProfanities()
        profanities.extend(newprofanities)
        self.setProfanities(profanities)
    
    def run(self, video):
        self.setVideo(video)
        self.checkModelExist()
        rec = self.getRecognizer()
        profanityDetector = ProfanityDetector()

        process = subprocess.Popen(self.getSttCmd(),stdout=subprocess.PIPE)

        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                txt = rec.Result()
                print(txt)
                self.extendProfanities(profanityDetector.extractListOfProfanity(txt))
            else:
                print(rec.PartialResult())

        txt = rec.FinalResult()
        print(txt)
        self.extendProfanities(profanityDetector.extractListOfProfanity(txt))

class ProfanityBlocker:
    def __init__(self):
        self.__video = VideoFile()
        self.__audio = AudioFile()
        self.__profanities = []
    
    def setVideo(self, video):
        self.__video = video
    
    def setAudio(self, audio):
        self.__audio = audio
    
    def setProfanities(self, profanities):
        self.__profanities = profanities
    
    def getVideo(self):
        return self.__video
    
    def getAudio(self):
        return self.__audio
    
    def getProfanities(self):
        return self.__profanities
    
    def run(self, video, audio, profanities):
        self.setVideo(video)
        self.setAudio(audio)
        self.setProfanities(profanities)