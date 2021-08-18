from bleepy import SpeechToText

stt = SpeechToText()
filename = input("What filename? ")
stt.run(filename)