import pickle
class Settings():
    mainpath = ""
    devices = []
    port = 0
f = open("Web Server Settings.dat","rb")
settings = pickle.load(f)
f.close()
print(settings.mainpath)
print(settings.devices)
print(settings.port)
