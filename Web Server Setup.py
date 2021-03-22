import pickle
class Settings():
    #mainpath = ""
    devices = []
    port = 80
    def __init__(self):
        self.devices = []
        self.port = 80
        port = input("Port number (default is 80): ")
        if port != "" : self.port = int(port)
        #self.mainpath = input("IP address of the main device (leave blank if this is the main device): ")
        #if self.mainpath == "":
        print("Other device's IP addresses, including port number (press Ctrl+C or leave blank after adding all devices):")
        try:
            while True:
                newip = input("> ")
                if newip == "" : break
                else: self.devices.append(newip)
        except KeyboardInterrupt: pass
print("On/Off Monitor setup\nMake sure you are using Python 3 for the On/Off Monitor")
settings = Settings()

#print(settings.mainpath)
print("Devices: " + str(settings.devices))
print("Port: " + str(settings.port))
f = open("ServerSettings.dat","wb")
pickle.dump(settings,f)
f.close()
print("Setup complete")
input("Press RETURN to exit ")
