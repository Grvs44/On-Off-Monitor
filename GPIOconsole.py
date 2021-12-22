BOARD = "Board"
BCM = "BCM"
IN = "input"
OUT = "output"
outputs = []
inputs = []
raw_input = input
filetext = ["----RESTART----"]
def setmode(mode):
    _out("GPIO Console: setmode",str(mode))
def setup(pin,mode):
    _out("GPIO Console: setup",str(pin),str(mode))
def cleanup():
    _out("GPIO Console: cleanup")
    print("\n".join(filetext))
def input(pin):
    entry = raw_input("GPIO Console: State of pin " + str(pin) + " (on:1/off:0): ")
    filetext.append("GPIO Console: State of pin " + str(pin) + " (on:1/off:0): " + entry)
    return entry == "0"
def output(pin,state):
    if state:
        _out("GPIO Console: set",str(pin),"on")
    else:
        _out("GPIO Console: set",str(pin),"off")
def _out(*text):
    filetext.append(" ".join(text))
    print(*text)
