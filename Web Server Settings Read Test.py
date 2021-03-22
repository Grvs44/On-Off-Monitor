import pickle
class Settings():
    mainpath = ""
    devices = []
    port = 0
f = open("ServerSettings.dat","rb")
settings = pickle.load(f)
f.close()
print(settings.mainpath)
print(settings.devices)
print(settings.port)
input("Press RETURN to exit ")
