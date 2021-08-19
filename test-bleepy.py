from bleepy import VideoFile, ProfanityExtractor

bleepy = ProfanityExtractor()
video = VideoFile()

filename = input("What filename? ")
video.setFile(filename)

bleepy.run(video)
profanities = bleepy.getProfanities()
print("List of Profanities Detected")
for profanity in profanities:
    print(profanity["word"])