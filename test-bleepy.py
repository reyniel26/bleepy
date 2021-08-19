from bleepy import VideoFile, SpeechToText

stt = SpeechToText()
video = VideoFile()

filename = input("What filename? ") #bleepy-test-files/tyler1sample.mp4
video.setFile(filename)


stt.run(video)
