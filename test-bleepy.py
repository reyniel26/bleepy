from bleepy import VideoFile, AudioFile, ProfanityExtractor, SpeechToText, ProfanityBlocker

stt = SpeechToText()
profanityExtractor = ProfanityExtractor()
profanityBlocker = ProfanityBlocker()
video = VideoFile()
audio = AudioFile()


video.setFile( input("What video you want to block profanity? ") ) 
audio.setFile( input("What bleep sound? ") )

stt.run(video)
profanityExtractor.run(stt.getResults())

profanities = profanityExtractor.getProfanities()
profanityBlocker.run(video,audio,profanities)

print("List of Profanities Detected")
for profanity in profanities:
    print(profanity["word"])

print("The Bleeped file saved in: "+profanityBlocker.getFileLocation())