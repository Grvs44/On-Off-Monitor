#! /usr/bin/env python3
from os.path import isfile
class Settings():
    sleeptime = 1
    devices = []
    logfiles = []
    ledswitch = None
    newthread = False
    outputlog = False
class Device():
    name = ""
    pin = 0
    led = 0
    def __init__(self,name_,pin_,led_):
        self.name = name_
        self.pin = int(pin_)
        self.led = int(led_)
if isfile("LogSettings.dat"):
    import pickle
    f = open("LogSettings.dat","rb")
    settings = pickle.load(f)
    f.close()
    options = ""
    for key in settings.__dict__:
        options += "\n%s\t%s" % (key,settings.__dict__[key])
    print("----Options----\nATTIRBUTE\tVALUE" + options)
    while True:
        key = input("Chosen key (or else to save and exit): ")
        if key in settings.__dict__:
            print("Current value: " + str(settings.__dict__[key]))
            settings.__dict__[key] = eval(input("New value (enter as Python): "))
        else:
            f = open("LogSettings.dat","wb")
            pickle.dump(settings,f)
            f.close()
            break
else:
    print("No settings file has been created. Start On/Off Monitor to create a new file, or check you are running this script in the correct directory:\n" + __file__)
