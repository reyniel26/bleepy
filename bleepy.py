from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import sys
import wave
import subprocess

from profanity_check import predict, predict_prob
import uuid #create unique random id

class File:
    def __init__(self):
        self.__file = "NaN"
        self.__filesize = 0.0
    
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
        self.__setFileSize(file)
    
    def __setFileSize(self,file):
        self.__filesize = os.path.getsize(file)
    
    def getFile(self):
        #Return File
        return self.__file
    
    def getFileSize(self):
        return self.__filesize
    
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
        self.__allowedExtensions = {"mp4","mp3"}
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
                    + " or add extensions by using \'addAllowedExt(str)\' or \'updateAllowedExt(list)\' " )
            exit (1)
    
    def isFileAllowed(self,file):
        #Override
        return super().isFileAllowed(file) and self.isAllowedExt(self.getExtension(file))
    
    def checkIsFileAllowed(self, file):
        #Override
        super().checkIsFileAllowed(file)
        self.checkIsAllowedExt(self.getExtension(file))

    def addAllowedExt(self,extension):
        #Add one allowed Extension
        exts = self.getAllowedExts()
        if extension not in exts:
            exts.add(extension)
            self.setAllowedExts(exts)
    
    def updateAllowedExt(self,extensions):
        #add list allowed extension
        exts = self.getAllowedExts()
        exts.update(extensions)
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
        self.setAllowedExts({"mp4","mpeg","mkv"})

class AudioFile(MediaFile):
    #AudioFile is a mediafile
    def __init__(self):
        super().__init__()
        self.setAllowedExts({"mp3","wav"})

class SpeechToText():
    #SpeechToText or STT
    #model = language-model
    #file = file
    #list of results (txt)

    def __init__(self, model = "model"):
        super().__init__()
        self.checkModelExist(model)
        self.__model = model
        self.__sample_rate=16000
        self.__video = VideoFile()
        self.__results = []

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
    
    def setResults(self,results):
        self.__results = results
    
    def addResult(self,newresult):
        results = self.getResults()
        results.append(newresult)
        self.setResults(results)

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
    
    def getResults(self):
        return self.__results

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
        self.setResults([])
        self.checkModelExist()
        rec = self.getRecognizer()

        process = subprocess.Popen(self.getSttCmd(),stdout=subprocess.PIPE)

        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = rec.Result()
                print(result)
                self.addResult(result)
            else:
                print(rec.PartialResult())

        finalresult = rec.FinalResult()
        print(result)
        self.addResult(finalresult)

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

class ProfanityExtractor():
    # New Process
    # Profanity Extractor should only extract profanity from the list of text results return by STT
    def __init__(self):
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
     
    def run(self,results):
        profanityDetector = ProfanityDetector()
        for result in results:
            self.extendProfanities(profanityDetector.extractListOfProfanity(result))

class ProfanityBlocker:
    def __init__(self):
        self.__video = VideoFile()
        self.__audio = AudioFile()
        self.__clips = []
        self.__trashclips = []
        self.__clipsDirectory = ""
        self.__saveDirectory = ""
    
    def setVideo(self, video):
        self.__video = video
    
    def setAudio(self, audio):
        self.__audio = audio
    
    def setClips(self, clips):
        self.__clips = clips
    
    def setTrashClips(self,trashclips):
        self.__trashclips = trashclips
    
    def setClipsDirectory(self,directory):
        self.__clipsDirectory = self.validDir(directory)
    
    def setSaveDirectory(self,directory):
        self.__saveDirectory = self.validDir(directory)
    
    def validDir(self,directory):
        directory = directory.replace("\\","/")
        return directory if "/" == directory[-1] or directory == "" else directory+"/"
    
    def getVideo(self):
        return self.__video
    
    def getAudio(self):
        return self.__audio
    
    def getClips(self):
        return self.__clips
    
    def getTrashClips(self):
        return self.__trashclips
    
    def getClipsDirectory(self):
        return self.__clipsDirectory
    
    def getSaveDirectory(self):
        return self.__saveDirectory
    
    def getClipDirForConcat(self):
        return "../" * self.getClipsDirectory().count("/")
    
    def getClipDuration(self,end,start):
        return float(end) - float(start)
    
    def runSubprocess(self,process):
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
    
    def split(self,profanities):
        clips = self.getClips()

        videoduration = self.getVideo().getDuration()
        fileExt = self.getVideo().getFileExtension()
        fileLocation = self.getVideo().getFile()

        laststart = 0.0
        print("SPLIT")
        for word in profanities:
            print(word["word"])
            wordduration = self.getClipDuration(word["start"],laststart)
            profanityduration = self.getClipDuration(word["end"],word["start"])

            clipinfo = {}

            if float(word["start"]) != float(laststart):

                clipinfo = {
                    "name":self.getClipsDirectory()+"not"+str(uuid.uuid4())+"."+fileExt,
                    "isProfanity":False
                }

                txtnoprofanity = "ffmpeg -i \"{}\" -ss {} -t {} -c:v h264_nvenc {}"
                txtnoprofanity = txtnoprofanity.format(fileLocation,laststart, wordduration,clipinfo["name"])
                
                vidprocess = subprocess.Popen(txtnoprofanity, stdout=subprocess.PIPE)

                self.runSubprocess(vidprocess)

                if os.path.exists(clipinfo["name"]):
                    print(txtnoprofanity)
                    clips.append(clipinfo)

            clipinfo = {
                "name":self.getClipsDirectory()+"profanity"+str(uuid.uuid4())+"."+fileExt,
                "isProfanity":True
            }

            txtprofanity = "ffmpeg -i \"{}\" -ss {} -t {} -c:v h264_nvenc {}"
            txtprofanity = txtprofanity.format(fileLocation,word["start"], profanityduration,clipinfo["name"])

            vidprocess = subprocess.Popen(txtprofanity, stdout=subprocess.PIPE)
            self.runSubprocess(vidprocess)

            if os.path.exists(clipinfo["name"]):
                print(txtprofanity)
                clips.append(clipinfo)
            laststart = float(word["end"])

        if(float(laststart) != float(videoduration)):

            clipinfo = {
                "name":self.getClipsDirectory()+"last"+str(uuid.uuid4())+"."+fileExt,
                "isProfanity":False
            }
            lastclip = "ffmpeg -i \"{}\" -ss {} -t {} -c:v h264_nvenc {}"
            lastclip = lastclip.format(fileLocation,laststart, (videoduration-laststart),clipinfo["name"])
            
            vidprocess = subprocess.Popen(lastclip, stdout=subprocess.PIPE)
            self.runSubprocess(vidprocess)

            print(lastclip)
            clips.append(clipinfo)
        
        self.setClips(clips)
        self.setTrashClips(self.getClips().copy())

    def replace(self):
        fileExt = self.getVideo().getFileExtension()

        # trashclips = clips.copy()
        clips = self.getClips()
        trashclips = self.getTrashClips()

        print("Replace")
        audioFileLocation = self.getAudio().getFile()

        for i in range(len(clips)):
            clip=clips[i].copy()
            if clip["isProfanity"]:
                trashclips.append(clip)

                #ready to be replace
                replacename = self.getClipsDirectory()+"replaced"+str(uuid.uuid4())+"."+fileExt
                
                txtreplaced = "ffmpeg -i {} -i \"{}\" -map 0:v -map 1:a -c:v copy -shortest {}"
                txtreplaced = txtreplaced.format(clip["name"],audioFileLocation,replacename)
                
                vidprocess = subprocess.Popen(txtreplaced, stdout=subprocess.PIPE)
                self.runSubprocess(vidprocess)

                print(txtreplaced)
                clip["name"] = replacename
                clips[i] = clip
        
        self.setClips(clips)
        self.setTrashClips(trashclips)

    def concat(self):
        fileExt = self.getVideo().getFileExtension()
        clips = self.getClips()
        trashclips = self.getTrashClips()

        print("Concat")
        txtfilename = self.getClipsDirectory()+"listofclips"+str(uuid.uuid4())+".txt"

        for clip in clips:
            try:
                f = open(txtfilename, "a")
                f.write("file "+self.getClipDirForConcat()+clip["name"]+"\n")
            finally:
                f.close()
                print(clip["name"])
                

        #concat
        print("\nFFMPEG CONCAT FINAL:----")

        blockfilename = self.getSaveDirectory()+"blocked"+str(uuid.uuid4())+"."+fileExt

        txtconcat = "ffmpeg -safe 0 -f concat -i {} -c copy {}"

        txtconcat = txtconcat.format(txtfilename,blockfilename)

        vidprocess = subprocess.Popen(txtconcat, stdout=subprocess.PIPE)
        self.runSubprocess(vidprocess)

        print(txtconcat)
        
        f = open(txtfilename, "a")
        f.write("\n\nDeleting Clips... \n\n")
        f.close()

        for trashclip in trashclips:
            try:
                f = open(txtfilename, "a")
                
                if os.path.exists(trashclip["name"]):
                    os.remove(trashclip["name"])
                    f.write("deleted clip "+trashclip["name"]+"\n")
                else:
                    f.write("not_deleted clip "+trashclip["name"]+"\n")
            finally:
                f.close()

        print("The profanities are now block")

    def run(self, video, audio, profanities):
        self.setVideo(video)
        self.setAudio(audio)

        self.split(profanities)
        self.replace()
        self.concat()

        
