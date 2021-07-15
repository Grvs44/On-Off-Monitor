import pickle
class ServerSettings():
    devices = []
    port = 80
f = open("ServerSettings.dat","rb")
settings = pickle.load(f)
f.close()
print(settings.devices)
print(settings.port)
input("Press RETURN to exit ")
