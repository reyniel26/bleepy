from bleepy import (AudioFile, ProfanityBlocker, ProfanityExtractor,
                    SpeechToText, VideoFile)

stt = SpeechToText()
profanityExtractor = ProfanityExtractor()
profanityBlocker = ProfanityBlocker()
video = VideoFile()
audio = AudioFile()

profanityBlocker.setSaveDirectory("bleeped video")
profanityBlocker.setClipsDirectory("clips")

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