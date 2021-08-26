from bleepy import VideoFile, ProfanityExtractor, SpeechToText

stt = SpeechToText()
extractor = ProfanityExtractor()
video = VideoFile()

filename = input("What filename? ") 
video.setFile(filename)

stt.run(video)
print(len(stt.getResults()))
extractor.run(stt.getResults())

profanities = extractor.getProfanities()
print("List of Profanities Detected")
for profanity in profanities:
    print(profanity["word"])