import pickle
class Settings():
    sleeptime=1
f = open("logsettings.dat","rb")
settings = pickle.load(f)
f.close()
print(settings.sleeptime)
f  = open("locallog.dat","rb")
logdata = pickle.load(f)
f.close()
print(logdata)
