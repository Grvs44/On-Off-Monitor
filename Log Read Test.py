import pickle
from datetime import datetime
class Settings():
    sleeptime= 1
    devices = []
    ledswitch = None
class Device():
    name = ""
    pin = 0
    led = 0
print("Log settings:")
f = open("LogSettings.dat","rb")
settings = pickle.load(f)
f.close()
print(settings.sleeptime)
for device in settings.devices:
    print(device.name+"\t"+str(device.pin)+"\t"+str(device.led))
input("Press RETURN to exit ")
