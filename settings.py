import os,pickle,json
from server import *
def ListToCsv(header,item):
    csv=header+"\n"
    for i in range(len(item)):
        for j in range(len(item[i])):
            csv+=str(item[i][j])
            if j+1 != len(item[i]): csv+=","
        if i+1 != len(item): csv+="\n"
    return csv
class Settings:
    def __init__(this):
        this.sleeptime = 1
        this.logfiles = []
        this.ledswitch = None
        this.networkdevices = {}
        this.port = 80 # server
        this.pinaccess = {}
        this.pinnames = {}
        this.deviceid = None
        this.shutdownpin = None
        this.dataled = None
        this.extralogconditions = None
        this.newthread = False
        this.outputlog = False
        this.devices = []
        this.console = False        

        if "y" in input("Set up with JSON file? (y/n) ").lower():
            try:
                f = open(input("Path of JSON file: "),"r")
                this.updatefromjson(f.read(),True)
                f.close()
            except FileNotFoundError:
                print("File not found, set up with questions:")
                this._initcli()
            except json.JSONDecodeError:
                print("Error with decoding JSON file, set up with questions:")
                this._initcli()
            #except Exception as e:
            #    print("Error",e,"Set up with questions",sep="\n")
            #    this._initcli()
        else: this._initcli()
    def _initcli(this):
        print("On/Off Monitor Log Setup")
        sleep = input("Wait time after loops (seconds, default is 1): ")
        if sleep != "": this.sleeptime = int(sleep)
        leds = input("Input pin number for LED panel switch (leave blank if there is no switch): ")
        if leds != "": this.ledswitch = int(leds)
        this.shutdownpin = IntValOrNone(input("Shutdown button pin (leave blank if there is no button): "))
        this.dataled = IntValOrNone(input("Data LED pin (leave blank if there is no LED): "))
        this.extralogconditions = input("Extra log conditions script (*.py,*.pyw,*.pyc file) path (leave blank if there isn't a script): ")
        while this.extralogconditions != "" and not os.path.isfile(os.path.abspath(this.extralogconditions)):
            this.extralogconditions = input("Please enter a valid path: ")
        if this.extralogconditions != "":
            this.extralogconditions = list(os.path.split(os.path.splitext(this.extralogconditions)[0]))
        this.newthread = "y" in input("Start a new thread for log program (y/n) - allows the program to run in the background fully: ").lower()
        this.outputlog = "y" in input("Output log (y/n) - not recommended if log has a new thread: ").lower()
        this.console = "y" in input("Access console remotely (y/n): ").lower()
        setup = False
        if "y" in input("Set up device name/input/output list with CSV file? (y/n) ").lower():
            csvpath = input("Please enter the path of the CSV file: ")
            try:
                csvfile = open(csvpath,"r")
                csvdata = csvfile.read()
                csvfile.close()
                if csvdata != "":
                    for line in csvdata.split(""): this.devices.append(Device(*line.split(",")[:3]))
                setup = True
            except FileNotFoundError: print("Not a valid file path")
        if not setup:
            print("Other devices connected to this device (press Ctrl+C or leave blank after adding all devices):")
            try:
                while 1:
                    newname = input("Name: ")
                    if newname == "" : break
                    newpin = int(input("GPIO pin number of device input: "))
                    newled = int(input("GPIO pin number of status LED: "))
                    this.devices.append(Device(newname,newpin,newled))
            except KeyboardInterrupt: pass
            except ValueError: pass

        print("On/Off Monitor Web Setup")
        setup = False
        port = input("Port number (default is 80): ")
        if port != "" : this.port = int(port)
        if "y" in input("Set up device IP address list with CSV file? (y/n) ").lower():
            csvpath = input("Please enter the path of the CSV file: ")
            try:
                csvfile = open(os.path.join(Page.folder,csvpath),"r")
                csvdata = csvfile.read()
                csvfile.close()
                if csvdata != "":
                    for line in csvdata.split(""): this.networkdevices[line.split(",")[0]] = int(line.split(",")[1])
                setup = True
            except FileNotFoundError: print("Not a valid file path")
        if not setup:
            print("Other device's IP addresses, including port number if necessary (press Ctrl+C or leave blank after adding all devices):")
            try:
                while True:
                    newip = input("> ")
                    if newip == "" : break
                    else:
                        this.networkdevices[newip] = IntValOrNone(input("Status LED for this device (leave blank if none): "))
            except KeyboardInterrupt: pass
        if len(this.networkdevices) != 0:
            print("Other device access IDs, for pin access on this device (press Ctrl+C or leave blank after adding all IDs:")
            while True:
                try:
                    id = input("Device ID: ")
                    if id == "":
                        break
                    else:
                        this.pinaccess[id] = []
                        print("Enter pins for this device (integers/blank only):")
                        try:
                            while True:
                                name = input("Pin name: ")
                                if name == "":
                                    break
                                else:
                                    if name not in this.pinnames:
                                        pin = IntValOrNone(input("Pin number corresponding to this name: "))
                                        if pin == None:
                                            break
                                        else:
                                            this.pinaccess[id].append(name)
                                            this.pinnames[name] = pin
                        except KeyboardInterrupt:
                            break
                except KeyboardInterrupt:
                    break
            deviceid = input("This device's ID (leave blank if not accessing pins on other devices): ")
            if deviceid != "": this.deviceid = deviceid
        this.save()
    def save(this):
        f = open(os.path.join(Page.folder,"Settings.dat"),"wb")
        pickle.dump(this,f)
        f.close()
    def sendpinrequest(this,device,pinname,state):
        """device: the address of the device
        pinname: the name of the pin, entered when setting up the device
        state: True for off, False for on"""
        try:
            if type(device) == int: device = this.networkdevices[device]
            return GetData(device,"/pinaccess",[["pin",pinname],["state","1" if state else "0"],["id",this.deviceid]]).split("\r\n\r\n")[1] == "1"
        except KeyError as e:
            raise KeyError("Device or pin name doesn't exist") from e
    def updatefromjson(this,data,ask=False):
        """data: a JSON string"""
        data = json.loads(data)
        if "sleeptime" in data: this.sleeptime = int(data["sleeptime"])
        if "ledswitch" in data: this.ledswitch = IntValOrNone(data["ledswitch"])
        if "shutdownpin" in data: this.shutdownpin = IntValOrNone(data["shutdownpin"])
        if "dataled" in data: this.dataled = IntValOrNone(data["dataled"])
        if "newthread" in data: this.newthread = bool(data["newthread"])
        if "outputlog" in data: this.outputlog = bool(data["outputlog"])
        if "port" in data: this.port = int(data["port"])
        if "deviceid" in data: this.deviceid = data["deviceid"]
        if "extralogconditions" in data:
            if type(data["extralogconditions"]) == list and len(data["extralogconditions"]) >= 2:
                this.extralogconditions = data["extralogconditions"][:2]
            elif type(data["extralogconditions"]) == str:
                this.extralogconditions = list(os.path.split(os.path.splitext(data["extralogconditions"])[0]))
        if "pinaccess" in data and type(data["pinaccess"]) == dict:
            this.pinaccess = data["pinaccess"]
        if "pinnames" in data and type(data["pinnames"]) == dict:
            this.pinnames = data["pinnames"]
        if "devices" in data and type(data["devices"]) == list:
            for device in data["devices"]:
                if type(device) == list and len(device) >= 3:
                    this.devices.append(Device(*device[:3]))
        if "networkdevices" in data and type(data["networkdevices"]) == dict:
            this.networkdevices = data["networkdevices"]
        if ask:
            this.console = "y" in input("Setting not in JSON file:\nAccess console remotely (y/n): ").lower()
        this.save()
    def tojson(this):
        data = {"sleeptime":this.sleeptime,"ledswitch":this.ledswitch,"shutdownpin":this.shutdownpin,"dataled":this.dataled,"newthread":this.newthread,"outputlog":this.outputlog,"port":this.port,"deviceid":this.deviceid,"extralogconditions":this.extralogconditions,"pinaccess":this.pinaccess,"pinnames":this.pinnames,"devices":[],"networkdevices":this.networkdevices}
        for device in this.devices:
            data["devices"].append(device.tolist())
        return json.dumps(data)
    @staticmethod
    def fromfile(path):
        try:
            f = open(path,"rb")
            settings = pickle.load(f)
            f.close()
            attributes = {"sleeptime":1,"logfiles":[],"ledswitch":None,"networkdevices":{},"port":80,"pinaccess":{},"pinnames":{},"deviceid":None,"shutdownpin":None,"dataled":None,"extralogconditions":None,"newthread":False,"outputlog":False,"devices":[],"console":False}
            for attribute in attributes:
                if not hasattr(settings,attribute) or type(settings.__dict__[attribute]) != type(attributes[attribute]):
                    settings.__dict__[attribute] = attributes[attribute]
            return settings
        except FileNotFoundError:
            return Settings()

class Device:
    def __init__(self,name,pin,led):
        self.name = name
        self.pin = int(pin)
        self.led = int(led)
    def __str__(self):
        return "%s (Pin: %i, LED: %i)" % (self.name,self.pin,self.led)
    def tolist(self):
        return [self.name,self.pin,self.led]

def IntValOrNone(value):
    try:
        return int(value)
    except (ValueError,TypeError):
        return None

class Page:
    folder = os.path.dirname(__file__)
    contenttypes = {"html":"text/html","js":"application/javascript","css":"text/css"}
    """__init__
    Caches the contents of a file, so the file is only read once
    path: the path of the file"""
    def __init__(this,path):
        this.path = path
        this.loaded = False
        filetype = path.split(".")
        filetype = filetype[len(filetype)-1]
        if filetype in this.contenttypes: this.contenttype = this.contenttypes[filetype]
        else: this.contenttype = "text/plain"
        if filetype == "js" or filetype == "css": this.cachecontrol = "max-age=31536000, immutable"
        else: this.cachecontrol = "no-cache"
    def load(this):
        """Returns the contents of the file"""
        if not this.loaded:
            f = open(os.path.join(this.folder,this.path),mode='r')
            this._data=f.read()
            f.close()
            this.loaded = True
        return this._data
    def loadh(this):
        """Returns the contents of the file and its content type in the format (contents,contenttype)"""
        return this.load(),this.contenttype,this.cachecontrol
    def reset(this):
        """Resets the cache, so that changes to the file are applied"""
        this.loaded = False
        this._data = ""
