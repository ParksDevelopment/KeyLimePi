import threading
import yaml

timers = {}
Config = []

def init():
    with open('exampleConfig/Config.yml', 'r') as file:
        Config = yaml.safe_load(file)

def keyChange(queue):
    while True:
        event = queue.get()
        interpret(event)
        queue.task_done()

def interpret(keyData):
    print(keyData)
    key = (keyData[1], keyData[2])
    if keyData[0]:
        timer = threading.Timer(.2, keyHeld, args=(key,))
        timers[key] = timer
        timer.start()
    else:
        if key in timers:
            timers[key].cancel()
            del timers[key]
            keyPressed(key)

def keyHeld(key):
    del timers[key]
    print("held")
    print(key)

def keyPressed(key):
    print("pressed")
    print(key)