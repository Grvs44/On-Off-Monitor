import pickle
from datetime import datetime
class Settings():
    sleeptime= 1
    devices = []
    ledswitch = None
    newthread = False
    outputlog = False
class Device():
    name = ""
    pin = 0
    led = 0
print("Log settings:")
f = open("LogSettings.dat","rb")
settings = pickle.load(f)
f.close()
print("Sleep time: %i\nLED switch: %s\nNew thread for log: %s\nOutput log: %s"%(settings.sleeptime,settings.ledswitch,settings.newthread,settings.outputlog))
for device in settings.devices: print("%s\t%i\t%i"%(device.name,device.pin,device.led))
input("Press RETURN to exit ")
