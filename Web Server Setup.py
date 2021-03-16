import pickle
class Settings():
    mainpath = ""
    devices = []
    port = 80
print("On/Off Monitor setup\nMake sure you are using Python 3 for the On/Off Monitor")
settings = Settings()
settings.devices = []
settings.port = 80
port = input("Port number (default is 80): ")
if port != "" : settings.port = int(port)
settings.mainpath = input("IP address of the main device (leave blank if this is the main device): ")
if settings.mainpath == "":
    print("Other device's IP addresses (press Ctrl+C or leave blank after adding all devices):")
    try:
        while True:
            newip = input("> ")
            if newip == "" : break
            else: settings.devices.append(newip)
    except KeyboardInterrupt: pass
print(settings.mainpath)
print(settings.devices)
print(settings.port)
f = open("Web Server Settings.dat","wb")
pickle.dump(settings,f)
f.close()
print("Setup complete")
