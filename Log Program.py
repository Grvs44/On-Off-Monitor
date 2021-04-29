import pickle
from time import sleep
from datetime import datetime
from OnOffMonitor import *
import RPi.GPIO as gpio
from atexit import register
class Settings():
    sleeptime = 1
    devices = []
    logfiles = []
    ledswitch = None
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
    log = [datetime.now().strftime("%Y/%m/%d,%H:%M:%S"),devicename,message]
    print(ListToCsv("",[log]),end="")
    logdata.append(log)
    f = open("LocalLog_"+currentlogtime+".dat","wb")
    pickle.dump(logdata,f)
    f.close()
def Load():
    global logdata
    try:
        f = open("LocalLog_"+currentlogtime+".dat","rb")
        logdata = pickle.load(f)
        f.close()
        if currentlogtime not in settings.logfiles:
            settings.logfiles.append(currentlogtime)
    except FileNotFoundError: pass
def GetLogFileList():
    global logfiles
    try:
        f = open("LogFileList.dat","rb")
        logfiles = pickle.load(f)
        f.close()
    except FileNotFoundError: pass
def CheckLogName():
    global currentlogtime, logfiles
    now = datetime.now().strftime("%Y%m%d")
    if(now>currentlogtime or currentlogtime == ""):
        currentlogtime = now
        GetLogFileList()
        if now not in logfiles:
            logfiles.append(now)
            f = open("LogFileList.dat","wb")
            pickle.dump(logfiles,f)
            f.close()
        Load()
def OnOrOff(status):
    if status: return "Off"
    else: return "On"
def TryInput(pin):
    if pin == None: return True
    else: return gpio.input(pin)
def SetupGpio():
    gpio.setmode(gpio.BOARD)
    print(settings.ledswitch)
    if settings.ledswitch != None: gpio.setup(settings.ledswitch,gpio.IN)
    for device in settings.devices:
        gpio.setup(device.pin,gpio.IN)
        gpio.setup(device.led,gpio.OUT)
        devicestatus.append(True)
def Log() :
    global ledswitchstate
    print("Date,Time,Device,Status",end="")
    while 1:
        CheckLogName()
        for i in range(len(devicestatus)):
            if devicestatus[i] != gpio.input(settings.devices[i].pin):
                devicestatus[i] = gpio.input(settings.devices[i].pin)
                if settings.ledswitch == None or not TryInput(settings.ledswitch): gpio.output(settings.devices[i].led,not devicestatus[i])
                Add(settings.devices[i].name,OnOrOff(devicestatus[i]))
        if settings.ledswitch != None and ledswitchstate != TryInput(settings.ledswitch):
            ledswitchstate = gpio.input(settings.ledswitch)
            for i in range(len(devicestatus)):
                gpio.output(settings.devices[i].led,(not devicestatus[i] and not gpio.input(settings.ledswitch)))
        sleep(settings.sleeptime)
def GetSettings(file):
    try:
        f = open(file,"rb")
        self = pickle.load(f)
        f.close()
    except FileNotFoundError:
        print("On/Off Monitor Log Setup")
        sleep = input("Wait time after loops (seconds, default is 1): ")
        self = Settings()
        if sleep != "": self.sleeptime = int(sleep)
        leds = input("Input pin number for LED panel switch (leave blank if there is no switch): ")
        if leds != "": self.ledswitch = int(leds)
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
register(gpio.cleanup)
currentlogtime = ""
logdata = []
devicestatus = []
ledswitchstate = False
logfiles = []
settings = GetSettings("LogSettings.dat")
print("On/Off Monitor Log started. Hold Ctrl+C to exit.")
try:
    CheckLogName()
    SetupGpio()
    Log()
except KeyboardInterrupt:
    print("\nOn/Off Monitor Log exited.")
