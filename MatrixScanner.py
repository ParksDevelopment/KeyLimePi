import yaml
import RPi.GPIO as GPIO
import time
import threading
import queue

import Interpreter

rows = 0
columns = 0
senders = []
recievers = []
currentMatrix = []
debounceMatrix = []
event_queue = queue.Queue()

debounceMaximum = 5
debounceMinimum = 0
pollingRate = .005

def inputOutputSetup():
    for i in senders:
        GPIO.setup(i, GPIO.OUT)
    for j in recievers:
        GPIO.setup(j, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    

def matrixScan():
    tempMatrix = [ [0]*len(recievers) for i in range(len(senders))]
    for i in range(len(senders)):
        GPIO.output(senders[i], GPIO.HIGH)
        for j in range(len(recievers)):
            if GPIO.input(recievers[j]):
                tempMatrix[i][j] = 1
            else:
                tempMatrix[i][j] = 0
        GPIO.output(senders[i], GPIO.LOW) 
    debounce(tempMatrix)

def debounce(tempMatrix):
    for i in range(len(debounceMatrix)):
        for j in range(len(debounceMatrix[0])):
            if (debounceMatrix[i][j] > 0) and (tempMatrix[i][j] == 0):
                debounceMatrix[i][j] -= 1
            elif debounceMatrix[i][j] < debounceMaximum:
                debounceMatrix[i][j] += tempMatrix[i][j]
            if (debounceMatrix[i][j] == debounceMinimum) and (currentMatrix[i][j] == 1):
                currentMatrix[i][j] = 0
                event_queue.put([0,i,j])
            elif (debounceMatrix[i][j] == debounceMaximum) and (currentMatrix[i][j] == 0):
                currentMatrix[i][j] = 1
                event_queue.put([1,i,j])
    
threading.Thread(target=Interpreter.keyChange, args=(event_queue,), daemon=True).start()

with open('exampleConfig/Config.yml', 'r') as file:
    Config = yaml.safe_load(file)
GPIO.setmode(GPIO.BCM)
columns = Config['columns']['count']
rows = Config['rows']['count']

if Config['matrixDirection'] == 'col2row':
    senders = Config['columns']['pins']
    recievers = Config['rows']['pins']
elif Config['matrixDirection'] == 'row2col':
    recievers = Config['columns']['pins']
    senders = Config['rows']['pins']
else:
    print("invalid direction")
currentMatrix = [ [0]*len(recievers) for i in range(len(senders))]
debounceMatrix = [ [0]*len(recievers) for i in range(len(senders))]
Interpreter.init()
inputOutputSetup()
try:
    while True:
        matrixScan()
        time.sleep(pollingRate)

except KeyboardInterrupt:
    # Clean up the GPIO pins on exit
    GPIO.cleanup()
    print("Program exited cleanly")