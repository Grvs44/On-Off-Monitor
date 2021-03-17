import pickle
from time import sleep
from datetime import datetime
class Settings():
    sleeptime = 4
    def __init__(self):
        try:
            f = open("logsettings.dat","rb")
            self = pickle.load(f)
            f.close()
        except FileNotFoundError:
            print("On/Off Monitor Log Setup")
            sleep = input("Wait time after loops (seconds, default is 4): ")
            if sleep == "": self.sleeptime=4
            else: self.sleeptime = int(sleep)
            f = open("logsettings.dat","wb")
            pickle.dump(self,f)
            f.close()
def Add(message):
    logdata.append([datetime.now(),message])
    f = open("locallog.dat","wb")
    pickle.dump(logdata,f)
    f.close()
def Load():
    try:
        f = open("locallog.dat","rb")
        logdata = pickle.load(f)
        f.close()
    except FileNotFoundError:pass
def Log() :
    try:
        while 1:
            print("Log")
            Add("Log")
            sleep(settings.sleeptime)
    except KeyboardInterrupt:
        pass
logdata = []
settings = Settings()
print("On/Off Monitor Log started. Hold Ctrl+C to exit.")
Load()
Log()
print("On/Off Monitor Log finished.")
