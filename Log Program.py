import pickle
from time import sleep
from datetime import datetime
#import RPi.GPIO as gpio
#import atexit
class Settings():
    sleeptime = 1
    devices = []
    logfiles = []
class Device():
    name = ""
    pin = 0
    led = 0
    def __init__(self,name_,pin_,led_):
        self.name = name_
        self.pin = pin_
        self.led = led_
def SaveSettings():
    f = open("LogSettings.dat","wb")
    pickle.dump(settings,f)
    f.close()
def Add(devicename,message):
    log = [datetime.now(),devicename,message]
    print(log)
    logdata.append(log)#.strftime("%Y%m%d%H%M%S")
    f = open("LocalLog_"+currentlogtime+".dat","wb")
    pickle.dump(logdata,f)
    f.close()
def Load():
    global logdata
    print(currentlogtime)
    try:
        f = open("LocalLog_"+currentlogtime+".dat","rb")
        logdata = pickle.load(f)
        f.close()
        if currentlogtime not in settings.logfiles:
            settings.logfiles.append(currentlogtime)
    except FileNotFoundError:print("FNF")
def GetLogFileList():
    global logfiles
    try:
        f = open("LogFileList.dat","rb")
        logfiles = pickle.load(f)
        f.close()
    except FileNotFoundError: pass
def CheckLogName():
    global currentlogtime, logfiles
    now = datetime.now().strftime("%Y%m%d")# https://www.w3schools.com/python/python_datetime.asp
    if(now>currentlogtime or currentlogtime == ""):
        currentlogtime = now
        if now not in logfiles:
            logfiles.append(now)
            f = open("LogFileList.dat","wb")
            pickle.dump(logfiles,f)
            f.close()
        Load()
def OnOrOff(status):
    if status: return "off"
    else: return "on"
def Log() :
    for device in settings.devices:
        #gpio.setMode(device.pin,IN)
        devicestatus.append(True)
    while 1:
        CheckLogName()
        for i in range(len(devicestatus)):
            if devicestatus[i]:##
                devicestatus[i] = not devicestatus[i]##
                Add(settings.devices[i].name,settings.devices[i].name + " turned " + OnOrOff(settings.devices[i].pin))
        sleep(settings.sleeptime)
def GetSettings(file):
    try:
        f = open(file,"rb")
        self = pickle.load(f)
        f.close()
    except FileNotFoundError:
        print("On/Off Monitor Log Setup")
        sleep = input("Wait time after loops (seconds, default is 1): ")
        if sleep != "": self.sleeptime = int(sleep)
        #else: self.sleeptime=1
        self.devices = []
        print("Other devices connected to this device (press Ctrl+C or leave blank after adding all devices):")
        try:
            while 1:
                newname = input("Name: ")
                if newname == "" : break
                newpin = int(input("GPIO pin number of device input: "))
                newled = int(input("GPIO pin number of status LED: "))
                self.devices.append(Device(newname,newpin,newled))
        except KeyboardInterrupt: pass
        except ValueError: pass
        g = open(file,"wb")
        pickle.dump(self,g)
        g.close()
    return self
#atexit.register(gpio.cleanup)
currentlogtime = ""
logdata = []
devicestatus = []
logfiles = []
settings = GetSettings("LogSettings.dat")
print("On/Off Monitor Log started. Hold Ctrl+C to exit.")
try:
    GetLogFileList()
    CheckLogName()
    Log()
except KeyboardInterrupt:
    print("On/Off Monitor Log exited.")
