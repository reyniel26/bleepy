from vosk import Model, KaldiRecognizer, SetLogLevel
import os
import sys
import wave
import subprocess


#ASK FILE NAME
filename = input("What filename? ")

SetLogLevel(0)

if not os.path.exists("model"):
    print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit (1)

sample_rate=16000
model = Model("model")
rec = KaldiRecognizer(model, sample_rate)


process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                            filename,
                            '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                            stdout=subprocess.PIPE)

#output time and words
rec.SetWords(True)

while True:
    data = process.stdout.read(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        print(rec.Result())
    else:
        print(rec.PartialResult())

print(rec.FinalResult())