import pickle
from time import sleep
from datetime import datetime
class Settings():
    sleeptime = 1
    def __init__(self):
        try:
            f = open("LogSettings.dat","rb")
            self = pickle.load(f)
            f.close()
        except FileNotFoundError:
            print("On/Off Monitor Log Setup")
            sleep = input("Wait time after loops (seconds, default is 1): ")
            if sleep != "": self.sleeptime = int(sleep)
            else: self.sleeptime=1
            g = open("LogSettings.dat","wb")
            pickle.dump(self,g)
            g.close()
def Add(message):
    logdata.append([datetime.now(),message])
    f = open("LocalLog.dat","wb")
    pickle.dump(logdata,f)
    f.close()
def Load():
    try:
        f = open("LocalLog.dat","rb")
        logdata = pickle.load(f)
        f.close()
    except FileNotFoundError:pass
def Log() :
    while 1:
        print("Log")
        Add("Log")
        sleep(settings.sleeptime)
logdata = []
settings = Settings()
print("On/Off Monitor Log started. Hold Ctrl+C to exit.")
try:
    Load()
    Log()
except KeyboardInterrupt:
    print("On/Off Monitor Log exited.")
