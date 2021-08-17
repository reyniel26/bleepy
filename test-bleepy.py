from bleepy import SpeechRecognition

stt = SpeechRecognition()
filename = input("What filename? ")
stt.run(filename)