import pickle
class Settings():
    sleeptime=1
f = open("LogSettings.dat","rb")
settings = pickle.load(f)
f.close()
print(settings.sleeptime)
f  = open("LocalLog.dat","rb")
logdata = pickle.load(f)
f.close()
print(logdata)
input("Press RETURN to exit ")
