"""Bleepy file"""
import os
import subprocess
import sys
import uuid  # create unique random id
import wave

from profanity_check import predict, predict_prob
from vosk import KaldiRecognizer, Model, SetLogLevel


class File:
    """Abstraction for file"""

    def __init__(self):
        """Init file"""
        self.__file = "NaN"
        self.__filesize = 0.0

    def __set_file_if_null(self, file):
        """
        Private Method that set file default file if null
        and doesnt alter the file set in the class
        """
        return self.get_file() if file == "" else file

    def __safe_set_file(self,file):
        """Private Method use to safe set file,
        doenst alter the file directly"""
        file = self.__set_file_if_null(file)
        self.check_is_file_allowed(file)
        return file

    def set_file(self, file):
        """Set File"""
        self.__file = self.__safe_set_file(file)
        self.__set_file_size(file)

    def __set_file_size(self,file):
        """Set the filesize from os.path.getsize function"""
        self.__filesize = os.path.getsize(file)

    def get_file(self) -> str:
        """Return File, file name to be exact"""
        return self.__file

    def get_file_size(self):
        """Return File size"""
        return self.__filesize

    def is_file_exist(self, file = ""):
        """Return boolean , if file exist"""
        return os.path.exists(self.__set_file_if_null(file))

    def check_is_file_exist(self, file):
        """Check file exist, if not, print error"""
        if not self.is_file_exist(file):
            print (
                f"Warning: File: ({file}) not found."+
                "Please input or set the correct directory of the file")
            sys.exit()

    def is_file_allowed(self,file):
        """Return if the file is allowed by checking it if it exist"""
        return self.is_file_exist(file)

    def check_is_file_allowed(self, file):
        """check if the file is allowed"""
        self.check_is_file_exist(file)

class MediaFile(File):
    """Abstraction for MediaFile"""

    def __init__(self):
        """Init Media File"""
        super().__init__()
        self.__allowed_extensions = {"mp4","mp3"}
        self.__extension = ""
        self.__duration = 0.0

    def set_file(self, file):
        """Set File , Override"""
        super().set_file(file)
        self.__set_file_extension(file)
        self.__set_duration(file)

    def set_allowed_exts(self, extensions):
        """
        Set list or any iteratable
        allowed extension, can be used to
        set custom allowed extensions.
        """
        self.__allowed_extensions = set(extensions)

    def __set_file_extension(self, file):
        """Set File Extension"""
        self.__extension = self.get_extension(file)

    def __set_duration(self, file):
        """
        Return Full Duration of the Media File

        ```
        durationcmd = (
            f"ffprobe -v error -show_entries format=duration"+
            f"-of default=noprint_wrappers=1:nokey=1 \"'{file}\""
            )
        ```

        """
        durationcmd = [
            'ffprobe', '-v' ,'error', '-show_entries',
            'format=duration', '-of' ,'default=noprint_wrappers=1:nokey=1', file]
        proc = subprocess.Popen(durationcmd, stdout=subprocess.PIPE)
        output = proc.stdout.read()
        output = str(output).replace("\\","")
        for char in ("b","\'","n","r"):
            output = output.strip(char)
        self.__duration = float(output)

    def get_allowed_exts(self) -> set:
        """Get allowed extension"""
        return self.__allowed_extensions

    def get_file_extension(self):
        """Get File extension"""
        return self.__extension

    def get_extension(self, file):
        """Get the extension from file name"""
        return file.rsplit('.',1)[1]

    def get_duration(self):
        """Get the duration"""
        return self.__duration

    def is_allowed_ext(self, extension):
        """Return boolen if extension is allowed"""
        return extension in self.get_allowed_exts()

    def check_is_allowed_ext(self, extension):
        """Check file extension, if not, print error"""
        if not self.is_allowed_ext(extension):
            print (f"Warning: File Extension ({extension}) is not allowed."
            + f" Please input valid file type {self.get_allowed_exts()} or add extensions"+
            " by using \'add_allowed_ext(str)\' or \'update_allowed_ext(list)\' " )
            sys.exit()

    def is_file_allowed(self,file):
        """
        Return if file is allowed by
        - checking it if it exist
        - and if its file type is allowed
        """
        return super().is_file_allowed(file) and self.is_allowed_ext(self.get_extension(file))

    def check_is_file_allowed(self, file):
        """
        Check if the file is allowed by
        - checking it if it exist
        - and if its file type is allowed
        """
        super().check_is_file_allowed(file)
        self.check_is_allowed_ext(self.get_extension(file))

    def add_allowed_ext(self,extension):
        """Add one allowed Extension"""
        exts = self.get_allowed_exts()
        if extension not in exts:
            exts.add(extension)
            self.set_allowed_exts(exts)

    def update_allowed_ext(self,extensions):
        """add list or any iteratable of allowed extensions"""
        exts = self.get_allowed_exts()
        exts.update(extensions)
        self.set_allowed_exts(exts)

    def remove_allowed_ext(self,extension):
        """remove one allowed extension"""
        exts = self.get_allowed_exts()
        exts.remove(extension)
        self.set_allowed_exts(exts)

class VideoFile(MediaFile):
    """Video file is a MediaFile"""
    def __init__(self):
        """Init Video file"""
        super().__init__()
        self.set_allowed_exts({"mp4","mpeg","mkv"})

class AudioFile(MediaFile):
    """AudioFile is a mediafile"""
    def __init__(self):
        """Init Audio file"""
        super().__init__()
        self.set_allowed_exts({"mp3","wav"})

class SpeechToText():
    """
    SpeechToText or STT

    model = language-model

    file = file

    list of results (txt)
    """

    def __init__(self, model = "model"):
        """Init speech to text"""
        super().__init__()
        self.check_model_exist(model)
        self.__model = model
        self.__sample_rate=16000
        self.__video = VideoFile()
        self.__results = []

        print("Setting up Recognizer for STT...")
        SetLogLevel(0)
        model = Model(self.get_model())
        self.__recognizer = KaldiRecognizer(model, self.get_sample_rate())
        self.__recognizer.SetWords(True)

    def set_model(self, model="model"):
        """Set language model"""
        self.check_model_exist(model)
        self.__model = model
        self.update_recognizer()

    def set_sample_rate(self, sample_rate = 16000):
        """Set sample rate"""
        self.__sample_rate = sample_rate
        self.update_recognizer()

    def set_video(self,video:VideoFile):
        """Set video file """
        self.__video = video

    def set_results(self,results):
        """set list of  results"""
        self.__results = list(results)

    def add_result(self,newresult):
        """Add result"""
        results = self.get_results()
        results.append(newresult)
        self.set_results(results)

    def update_recognizer(self):
        """Update recognizer"""
        SetLogLevel(0)
        print("Updating Recognizer for STT...")
        model = Model(self.get_model())
        self.__recognizer = KaldiRecognizer(model, self.get_sample_rate())
        self.__recognizer.SetWords(True)

    def get_model(self):
        """Return model"""
        return self.__model

    def get_video(self):
        """Return video"""
        return self.__video

    def get_sample_rate(self):
        """Get sample rate"""
        return self.__sample_rate

    def get_results(self):
        """Get results"""
        return self.__results

    def get_recognizer(self):
        """Get recognizer"""
        return self.__recognizer

    def get_stt_cmd(self):
        """Return FMMPEG Command for STT"""
        return ['ffmpeg', '-loglevel', 'quiet', '-i',
                self.get_video().get_file(), '-ar', str(self.get_sample_rate()) ,
                '-ac', '1', '-f', 's16le', '-']

    def is_model_exist(self, model = ""):
        """Return boolean if model exist"""
        model = self.get_model() if model == "" else model
        return os.path.exists(model)

    def check_model_exist(self, model = ""):
        """Check model if exist"""
        if not self.is_model_exist(model):
            print (
                f"Warning: Model Directory not found ({model})."+
                " Please download the model from https://alphacephei.com/vosk/models"+
                " and unpack as 'model' in the current folder."
                )
            sys.exit()

    def run(self, video):
        """Run Speech to text"""
        self.set_video(video)
        self.set_results([])
        self.check_model_exist()
        rec = self.get_recognizer()

        process = subprocess.Popen(self.get_stt_cmd(),stdout=subprocess.PIPE)

        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = rec.Result()
                print(result)
                self.add_result(result)
            else:
                print(rec.PartialResult())

        finalresult = rec.FinalResult()
        print(finalresult)
        self.add_result(finalresult)

class ProfanityDetector():
    """Profanity Detector"""
    def __init__(self,lang="english"):
        """Init profanity detector"""
        self.__lang = lang

    def get_lang(self):
        """Get language"""
        return self.__lang

    def extract_list_of_results(self,txt):
        """
        Extract the list of results

        Make List of Results
        """
        #Vosk, KaldiRecognizer obj.Result() and obj.FinalResult() return txt
        a_char = txt.split('[')#Split the Result str in open bracket
        b_char = a_char[1].split(']') #Get the 2nd half then Split in Closing Bracket
        c_char = b_char[0].split(', ') #Get the 1st half then Split in comma and space
        for i, item in enumerate(c_char):
            item
            c_char[i] = c_char[i].strip("{}") #remove brackets
            c_char[i] = c_char[i].replace('\n','') #replace newline
            c_char[i] = c_char[i].replace('\"','') #replace "
        return c_char #return list of Results

    def extract_list_of_words(self,txt):
        """Make List of Words, extracted from the list of Results"""
        words = [] #create new list
        if "result" in txt: #Check if there is result or words
            for item in self.extract_list_of_results(txt):
                attrs= item.split(',') #Split the items into attributes in comma
                tempdict = {} #create temp dict
                for attr in attrs:
                    #Then Split the attributes in : separating the key and value
                    data = attr.split(':')
                    #data[0] is the key, data[1] is the value
                    tempdict[data[0].strip()] = data[1].strip()
                words.append(tempdict)
        #To output this, you can use for loop
        #another example: print(extract_list_of_words(txt)[0]["word"])
        return words #return this list of words (dict)

    def extract_list_of_profanity(self,txt):
        """Make a list of profanity"""
        words = self.extract_list_of_words(txt)
        profanity = []
        for word in words:
            if bool(predict([word["word"]]) if self.get_lang() == "english"
                    else predict([word["word"]], self.get_lang()) ):
                word["lang"] = self.get_lang()
                word["predict_prob"] = ( predict_prob([word["word"]])[0]
                                            if self.get_lang() == "english"
                                            else predict_prob([word["word"]], self.get_lang())[0])
                profanity.append(word)
        return profanity #list of dictionaries

class ProfanityExtractor():
    """
    New Process

    Profanity Extractor should only extract profanity
    from the list of text results return by STT
    """
    def __init__(self, lang="english"):
        """Init profanity extractor"""
        self.__profanities = []
        self.__lang = lang

    def set_profanities(self,profanities):
        """ Set profanities """
        self.__profanities = profanities

    def get_profanities(self):
        """Get profanities"""
        return self.__profanities

    def get_lang(self):
        """Get language"""
        return self.__lang

    def add_profanity(self, newprofanity):
        """Add profanity"""
        profanities = self.get_profanities()
        profanities.append(newprofanity)
        self.set_profanities(profanities)

    def extend_profanities(self, newprofanities):
        """Extend profanities by adding list of profanity"""
        profanities = self.get_profanities()
        profanities.extend(newprofanities)
        self.set_profanities(profanities)

    def run(self,results):
        """Run profanity extractor"""
        profanity_detector = ProfanityDetector(self.get_lang())
        for result in results:
            self.extend_profanities(
                profanity_detector.extract_list_of_profanity(result)
                )

class ProfanityBlocker:
    """Profanity Blocker"""
    def __init__(self):
        """Init profanity blocker"""
        self.__video = VideoFile()
        self.__audio = AudioFile()
        self.__clips = []
        self.__trashclips = []
        self.__clips_directory = ""
        self.__save_directory = ""
        self.__filelocation = ""

    def set_video(self, video):
        """Set video"""
        self.__video = video

    def set_audio(self, audio):
        """Set audio"""
        self.__audio = audio

    def set_clips(self, clips):
        """Set clips"""
        self.__clips = clips

    def set_trash_clips(self,trashclips):
        """Set trash clips"""
        self.__trashclips = trashclips

    def set_clips_directory(self,directory):
        """Set clips directory name, if not exist, create it"""
        self.__clips_directory = self.decorate_dir_name(directory)
        if not os.path.exists(self.__clips_directory):
            os.makedirs(self.__clips_directory)

    def set_save_directory(self,directory):
        """Set save directory name, if not exist, create it"""
        self.__save_directory = self.decorate_dir_name(directory)
        if not os.path.exists(self.__save_directory):
            os.makedirs(self.__save_directory)

    def set_file_location(self,filelocation):
        """Set file location"""
        self.__filelocation = filelocation

    def decorate_dir_name(self,directory):
        """Decorate directory name """
        directory = directory.replace("\\","/")
        return directory if "/" == directory[-1] or directory == "" else directory+"/"

    def get_video(self):
        """Get video"""
        return self.__video

    def get_audio(self):
        """Get audio"""
        return self.__audio

    def get_clips(self):
        """Get clips"""
        return self.__clips

    def get_trash_clips(self):
        """Get trash clips"""
        return self.__trashclips

    def get_clips_directory(self):
        """Get clips directory"""
        return self.__clips_directory

    def get_save_directory(self):
        """Get save directory"""
        return self.__save_directory

    def get_file_location(self):
        """Get file location"""
        return self.__filelocation

    def get_clip_dir_for_concat(self):
        """Get directory for concat"""
        return "../" * self.get_clips_directory().count("/")

    def get_clip_duration(self,end,start):
        """Get clip duration"""
        return float(end) - float(start)

    def run_subprocess(self,process):
        """Run subprocess"""
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break

    def split(self,profanities):
        """Do split"""
        clips = self.get_clips()

        videoduration = self.get_video().get_duration()
        file_ext = self.get_video().get_file_extension()
        fileLocation = self.get_video().get_file()

        laststart = 0.0
        print("SPLIT")
        for word in profanities:
            print(word["word"])
            word["start"] = round(float(word["start"]),2)
            word["end"] = round(float(word["end"]),2)
            wordduration = round(self.get_clip_duration(word["start"],laststart),2)
            profanityduration = round(self.get_clip_duration(word["end"],word["start"]),2)

            clipinfo = {}

            if float(word["start"]) != float(laststart):
                if wordduration > 1:
                    clipinfo = {
                        # "name":self.get_clips_directory()+"not"+str(uuid.uuid4())+"."+file_ext,
                        "name":f"{self.get_clips_directory()}not{uuid.uuid4()}.{file_ext}",
                        "isProfanity":False
                    }

                    txtnoprofanity = (
                        f"ffmpeg -i \"{fileLocation}\" -ss {laststart}"+
                        f" -t {wordduration} -c:v h264_nvenc {clipinfo['name']}")

                    vidprocess = subprocess.Popen(txtnoprofanity, stdout=subprocess.PIPE)

                    self.run_subprocess(vidprocess)

                    if os.path.exists(clipinfo["name"]):
                        print(txtnoprofanity)
                        clips.append(clipinfo)

            clipinfo = {
                "name":f"{self.get_clips_directory()}profanity{uuid.uuid4()}.{file_ext}",
                "isProfanity":True
            }

            txtprofanity = "ffmpeg -i \"{}\" -ss {} -t {} -c:v h264_nvenc {}"

            templaststart = float(word["end"])
            if (videoduration - templaststart) < 1:
                # If the last clip is not long enough,
                # it will be attach already from the previous clip
                duration = round(profanityduration+(videoduration - templaststart),2)
                txtprofanity = txtprofanity.format(
                    fileLocation,word["start"], duration,clipinfo["name"]
                    )
                laststart = videoduration
            elif wordduration < 1:
                #If the no profanity clip is less than 1
                duration = round(profanityduration+wordduration,2)
                txtprofanity = txtprofanity.format(
                    fileLocation,laststart, duration,clipinfo["name"]
                    )
                laststart = float(word["end"])
            else:
                txtprofanity = txtprofanity.format(
                    fileLocation,word["start"], profanityduration,clipinfo["name"]
                    )
                laststart = float(word["end"])

            vidprocess = subprocess.Popen(txtprofanity, stdout=subprocess.PIPE)
            self.run_subprocess(vidprocess)

            if os.path.exists(clipinfo["name"]):
                print(txtprofanity)
                clips.append(clipinfo)


        if float(laststart) != float(videoduration):

            clipinfo = {
                "name":self.get_clips_directory()+"last"+str(uuid.uuid4())+"."+file_ext,
                "isProfanity":False
            }
            duration = round((videoduration-laststart),2)
            lastclip = (
                f"ffmpeg -i \"{fileLocation}\" -ss {laststart}"+
                f" -t {duration} -c:v h264_nvenc {clipinfo['name']}")

            vidprocess = subprocess.Popen(lastclip, stdout=subprocess.PIPE)
            self.run_subprocess(vidprocess)

            if os.path.exists(clipinfo["name"]):
                print(lastclip)
                clips.append(clipinfo)

        self.set_clips(clips)
        self.set_trash_clips(self.get_clips().copy())

    def replace(self):
        file_ext = self.get_video().get_file_extension()

        # trashclips = clips.copy()
        clips = self.get_clips()
        trashclips = self.get_trash_clips()

        print("Replace")
        audio_file_location = self.get_audio().get_file()

        for i in range(len(clips)):
            clip=clips[i].copy()
            if clip["isProfanity"]:
                trashclips.append(clip)

                #ready to be replace
                replacename = f"{self.get_clips_directory()}replaced{uuid.uuid4()}.{file_ext}"
                txtreplaced = (
                    f"ffmpeg -i {clip['name']} -i \"{audio_file_location}\""+
                    f" -map 0:v -map 1:a -c:v copy -shortest {replacename}")


                vidprocess = subprocess.Popen(txtreplaced, stdout=subprocess.PIPE)
                self.run_subprocess(vidprocess)

                print(txtreplaced)
                clip["name"] = replacename
                clips[i] = clip

        self.set_clips(clips)
        self.set_trash_clips(trashclips)

    def concat(self):
        file_ext = self.get_video().get_file_extension()
        clips = self.get_clips()
        trashclips = self.get_trash_clips()

        print("Concat")
        txtfilename = f"{self.get_clips_directory()}listofclips{uuid.uuid4}.txt"

        for clip in clips:
            try:
                f = open(txtfilename, "a")
                f.write(f"file {self.get_clip_dir_for_concat()}{clip['name']}\n")
            finally:
                f.close()
                print(clip["name"])


        #concat
        print("\nFFMPEG CONCAT FINAL:----")

        blockfilename = f"{self.get_save_directory()}blocked{uuid.uuid4()}.{file_ext}"

        txtconcat = f"ffmpeg -safe 0 -f concat -i \"{txtfilename}\" -c copy \"{blockfilename}\""

        vidprocess = subprocess.Popen(txtconcat, stdout=subprocess.PIPE)
        self.run_subprocess(vidprocess)

        print(txtconcat)

        f = open(txtfilename, "a")
        f.write("\n\nDeleting Clips... \n\n")
        f.close()

        for trashclip in trashclips:
            try:
                f = open(txtfilename, "a")

                if os.path.exists(trashclip["name"]):
                    os.remove(trashclip["name"])
                    f.write(f"deleted clip {trashclip['name']}\n")
                else:
                    f.write(f"not_deleted clip {trashclip['name']}\n")
            finally:
                f.close()

        try:
            f = open(txtfilename, "a")
            f.write("\n\nThe Bleeped file saved in: "+blockfilename)
        finally:
            f.close()

        self.set_file_location(blockfilename)
        print("The profanities are now block")

    def run(self, video:VideoFile, audio:AudioFile, profanities:list):
        """Run Profanity Blocker"""
        self.set_video(video)
        self.set_audio(audio)

        self.split(profanities)
        self.replace()
        self.concat()
