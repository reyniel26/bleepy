"""Run this to try bleepy"""
from bleepy import (AudioFile, ProfanityBlocker, ProfanityExtractor,
                    SpeechToText, VideoFile)

stt = SpeechToText()
profanityExtractor = ProfanityExtractor()
profanityBlocker = ProfanityBlocker()
video = VideoFile()
audio = AudioFile()

profanityBlocker.set_save_directory("bleeped video")
profanityBlocker.set_clips_directory("clips")

video.set_file( input("What video you want to block profanity? ") )
audio.set_file( input("What bleep sound? ") )

stt.run(video)
profanityExtractor.run(stt.get_results())

profanities = profanityExtractor.get_profanities()
profanityBlocker.run(video,audio,profanities)

print("List of Profanities Detected")
for profanity in profanities:
    print(profanity["word"])

print("The Bleeped file saved in: "+profanityBlocker.get_file_location())