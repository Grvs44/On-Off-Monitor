#! /usr/bin/env python3
from socket import socket,AF_INET,SOCK_STREAM,SHUT_WR,gethostname
import pickle,json,os
from threading import Thread
from time import sleep
from datetime import datetime
try: import RPi.GPIO as gpio
except ModuleNotFoundError:
    if input("Use GPIOconsole (y) or GPIO_Test (default)? ") == "1": import GPIOconsole as gpio
    else: import GPIO_Test as gpio
import ExtraLogConditions

#OnOffMonitor:
def ListToCsv(header,item):
    csv=header+"\n"
    for i in range(len(item)):
        for j in range(len(item[i])):
            csv+=str(item[i][j])
            if j+1 != len(item[i]): csv+=","
        if i+1 != len(item): csv+="\n"
    return csv

#Log program:
class Settings():
    sleeptime = 1
    devices = []
    logfiles = []
    ledswitch = None
    newthread = False
    outputlog = False
class Device():
    name = ""
    pin = 0
    led = 0
    def __init__(self,name_,pin_,led_):
        self.name = name_
        self.pin = int(pin_)
        self.led = int(led_)
def SaveSettings():
    f = open(os.path.join(Page.folder,"LogSettings.dat"),"wb")
    pickle.dump(settings,f)
    f.close()
def Add(devicename,message):
    log = [datetime.now().strftime("%Y/%m/%d,%H:%M:%S"),devicename,message]
    if settings.outputlog: print(ListToCsv("",[log]),end="")
    logdata.append(log)
def SaveLog():
    f = open(os.path.join(Page.folder,"LocalLog_"+currentlogtime+".dat"),"wb")
    pickle.dump(logdata,f)
    f.close()
def Load():
    global logdata
    try:
        f = open(os.path.join(Page.folder,"LocalLog_"+currentlogtime+".dat"),"rb")
        logdata = pickle.load(f)
        f.close()
        if currentlogtime not in settings.logfiles:
            settings.logfiles.append(currentlogtime)
    except FileNotFoundError:
        g = open(os.path.join(Page.folder,"localLog_"+currentlogtime+".dat"),"wb")
        pickle.dump([],g)
        g.close()
def GetLogFileList():
    global logfiles
    try:
        f = open(os.path.join(Page.folder,"LogFileList.dat"),"rb")
        logfiles = pickle.load(f)
        f.close()
    except FileNotFoundError: pass
def CheckLogName():
    global currentlogtime, logfiles
    now = datetime.now().strftime("%Y%m%d")
    if(now>currentlogtime or currentlogtime == ""):
        currentlogtime = now
        GetLogFileList()
        if now not in logfiles:
            logfiles.append(now)
            f = open(os.path.join(Page.folder,"LogFileList.dat"),"wb")
            pickle.dump(logfiles,f)
            f.close()
        Load()
def OnOrOff(status):
    if status: return "Off"
    else: return "On"
def TryInput(pin):
    if pin == None: return True
    else: return gpio.input(pin)
def SetupGpio():
    gpio.setmode(gpio.BOARD)
    if settings.ledswitch != None: gpio.setup(settings.ledswitch,gpio.IN)
    for device in settings.devices:
        gpio.setup(device.pin,gpio.IN)
        gpio.setup(device.led,gpio.OUT)
        devicestatus.append(True)
def Log() :
    global ledswitchstate,running,serversocket,turnoff
    print("On/Off Monitor Log Started")
    ExtraLogConditions.Setup(settings)
    if settings.outputlog: print("Date,Time,Device,Status",end="")
    while running:
        CheckLogName()
        for i in range(len(devicestatus)):
            state = gpio.input(settings.devices[i].pin)
            if devicestatus[i] != state:
                devicestatus[i] = state
                if settings.ledswitch == None or not TryInput(settings.ledswitch): gpio.output(settings.devices[i].led,not devicestatus[i])
                Add(settings.devices[i].name,OnOrOff(devicestatus[i]))
        if settings.ledswitch != None and ledswitchstate != TryInput(settings.ledswitch):
            ledswitchstate = gpio.input(settings.ledswitch)
            for i in range(len(devicestatus)):
                gpio.output(settings.devices[i].led,(not devicestatus[i] and not gpio.input(settings.ledswitch)))
        ExtraLogConditions.Run(Add,settings,TryInput)
        SaveLog()
        sleep(settings.sleeptime)
    gpio.cleanup()
    serversocket.close() 
    print("\nOn/Off Monitor exited")
    if turnoff: os.system("sudo shutdown -h 0")
    quit()
def GetSettings(file):
    try:
        f = open(os.path.join(Page.folder,file),"rb")
        self = pickle.load(f)
        f.close()
    except FileNotFoundError:
        print("On/Off Monitor Log Setup")
        sleep = input("Wait time after loops (seconds, default is 1): ")
        self = Settings()
        if sleep != "": self.sleeptime = int(sleep)
        leds = input("Input pin number for LED panel switch (leave blank if there is no switch): ")
        if leds != "": self.ledswitch = int(leds)
        self.newthread = "y" in input("Start a new thread for log program (y/n) - allows the program to run in the background fully: ").lower()
        self.outputlog = "y" in input("Output log (y/n) - not recommended if log has a new thread: ").lower()
        self.devices = []
        setup = False
        if "y" in input("Set up device name/input/output list with CSV file? (y/n) ").lower():
            csvpath = input("Please enter the path of the CSV file: ")
            try:
                csvfile = open(csvpath,"r")
                csvdata = csvfile.read()
                csvfile.close()
                if csvdata != "":
                    for line in csvdata.split("\n"): self.devices.append(Device(*line.split(",")[:3]))
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
                    self.devices.append(Device(newname,newpin,newled))
            except KeyboardInterrupt: pass
            except ValueError: pass
        g = open(os.path.join(Page.folder,file),"wb")
        pickle.dump(self,g)
        g.close()
    return self

#Web server:
class ServerSettings():
    devices = []
    port = 80
class Page:
    folder = os.path.dirname(__file__)
    contenttypes = {"html":"text/html","js":"application/javascript","hta":"text/html"}
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
    def load(this):
        """Returns the contents of the file"""
        if not this.loaded:
            f = open(os.path.join(this.folder,this.path),mode='r')
            this._data=f.read()
            f.close()
            this.loaded = True
        return this._data
    def loadct(this):
        """Returns the contents of the file and its content type in the format (contents,contenttype)"""
        return this.load(),this.contenttype
    def reset(this):
        """Resets the cache, so that changes to the file are applied"""
        this.loaded = False
        this._data = ""
def Server():
    global running,turnoff,serversocket,pagecache
    print("On/Off Monitor Web Started\n")
    pagecache = {"/":Page("HomePage.html"),"/status/status.js":Page("StatusScript.js"),"/status":Page("StatusPage.html"),"/status/reduced.js":Page("Reduced Status.js"),"/status/reduced":Page("Reduced Status.html"),"/app":Page("AppPage.html")}
    ipaddress = gethostname()
    serversocket.bind((ipaddress,serversettings.port))
    serversocket.listen(5)
    while running:
        try:
            req = serversocket.accept()
            Thread(target=ServerRespond,args=req).start()
        except OSError: break
def ServerRespond(clientsocket,other):
    global running,turnoff,pagecache
    pieces = clientsocket.recv(5000).decode().split("\n")
    path = ""
    if len(pieces) > 0:
        try: path = pieces[0].split(" ")[1].lower()
        except IndexError : pass
    #data = ""
    contenttype = "text/html"
    httpcode = 200
    if path in pagecache: data,contenttype = pagecache[path].loadct()
    elif path == "/status/status.json":
        contenttype = "application/json"
        data = []
        for device in settings.devices: data.append([device.name,tern(gpio.input(device.pin),"Off","On")])
        data = json.dumps(data)
    elif path == "/status/reducedstatus.json":
        contenttype = "application/json"
        data = []
        for device in settings.devices: data.append(gpio.input(device.pin))
        data = json.dumps(data)
    elif path == "/status/statusnames.json":
        contenttype = "application/json"
        data = []
        for device in settings.devices: data.append(device.name)
        data = json.dumps(data)
    elif path == "/status.hta":
        data = pagecache["/status"].load().replace('<script type="application/javascript" src="/status/status.js"></script>',"<script>" + pagecache["/status/status.js"].load() + "</script>")
    elif path == "/status/reduced.hta":
        data = pagecache["/status/reduced"].load().replace('<script type="application/javascript" src="/status/reduced.js"></script>',"<script>" + pagecache["/status/reduced.js"].load() + "</script>")
    elif path == "/shutdown":
        post = GetPostData(pieces,{"devices":"this","web":"web","app":"0"})
        if post["devices"] == "all":
            for device in serversettings.devices:
                GetData(device,"/shutdown",postlist=[["web","web"],["app","1"]])
            data="Shut down requested for all devices"
        else:
            data="Shut down"
        if post["app"]=="0":
            data = "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><title>Shut down - On/Off Monitor</title><h1 style='font-family:\"Segoe UI\";text-align:center'>" + data + "</h1>"
        if post["web"] == "all":
            turnoff = True
        running = False
    elif path == "/resetcache":
        for key in pagecache:
            pagecache[key].reset()
        data = "Page cache reset"
        contenttype = "text/plain"
    elif "/localdata" in path:
        try:
            item = 1
            if "?" in path:
                item = int(path.split("?")[1])
            if item > len(logfiles): data=json.dumps([])
            else:
                f=open("LocalLog_"+logfiles[len(logfiles)-item]+".dat",mode="r")
                data = json.dumps(pickle.load(f))
                f.close()
        except IndexError: pass
    elif path == "/log.csv":
        post = GetPostData(pieces,{"lognum":0,"fileage":"new"})
        post["lognum"] = int(post["lognum"])
        if post["lognum"] < 1: post["lognum"] = 1
        elif post["lognum"] > len(logfiles): post["lognum"] = len(logfiles)
        if post["fileage"]=="new": logfilein = range(len(logfiles)-1,len(logfiles)-post["lognum"]-1,-1)
        else: logfilein = range(post["lognum"])
        print(list(logfilein))
        filedata = []
        for i in logfilein:
            f = open("LocalLog_"+logfiles[i]+".dat","rb")
            filedata.extend(pickle.load(f))
            f.close()
            for device in serversettings.devices: filedata.extend(json.loads(GetData(device,"/localdata?"+str(i)).split("\r\n")[3]))
        filedata.sort(reverse=True)
        data = ListToCsv("Date,Time,Device,Status",filedata)
        contenttype="text/csv"
    elif path == "/deletelocallogs":
        post = GetPostData(pieces,{"lognum":0,"fileage":"new"})
        post["lognum"] = int(post["lognum"])
        data = str(DeleteLogFiles(post["lognum"],(post["fileage"]=="new")))
    elif path == "/deletelogs":
        post = GetPostData(pieces,{"lognum":0,"fileage":"new","app":"0"})
        post["lognum"]=int(post["lognum"])
        deletedfiles = 0
        if len(logfiles)>0:
            deletedfiles+=DeleteLogFiles(post["lognum"],(post["fileage"]=="new"))
        for device in serversettings.devices: deletedfiles+=int(GetData(device,"/deletelocallogs",postlist=pathdata).split("\r\n")[3])
        if post["app"]=="1":
            data = str(deletedfiles) + " files were deleted"
        else:
            data = "/deleted" + str(deletedfiles)
            httpcode = 302
    elif path == "/logfilelist":
        data = GetPostData(pieces,{"app":"0"})
        if data["app"]=="1": data = json.dumps(logfiles)
        else: httpcode = 404
    elif path == "/deletelocallog":
        lognum = int(GetPostData(pieces,{"lognum":0})["lognum"])
        if app:
            item = logfiles.pop(lognum)
            data = item[:4] + "/" + item[4:6] + "/" + item[6:8]
            try:
                os.unlink("LocalLog_"+item+".dat")
                data += " was deleted"
            except FileNotFoundError: data += " was not found"
            SaveLogFileList()
        else: httpcode = 404
    elif path == "/logfile":
        post = GetPostData(pieces,{"lognum":0,"app":"0"})
        post["lognum"]=int(post["lognum"])
        if post["app"]=="1":
            print("lognum: ",post["lognum"])
            if post["lognum"] < len(logfiles):
                f = open("LocalLog_"+logfiles[post["lognum"]]+".dat","rb")
                data = json.dumps(pickle.load(f))
                f.close()
            else: data = "[]"
        else: httpcode = 404
    elif "/deleted" in path:
        try: deleteditems = path.split("deleted")[1]
        except IndexError: deleteditems = "0"
        data = "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><title>Delete Log Files - On/Off Monitor</title><div style=\"font-family:'Segoe UI';text-align:center\"><h1>" + deleteditems + " files were deleted</h1><a href='/'>Click here</a> to return to the home page</div>"
    else: httpcode = 404
    if httpcode == 200: clientsocket.sendall(("HTTP/1.1 200 OK\r\nContent-Type: "+contenttype+"; charset=utf-8\r\n\r\n"+data+"\r\n\r\n").encode())
    elif httpcode == 404: clientsocket.sendall("HTTP/1.1 404 NOT FOUND\r\n\r\n<title>Not found</title><h1>Not found</h1><p><a href='/'>Return to On/Off Monitor</a></p>\r\n\r\n".encode())
    elif httpcode == 302: clientsocket.sendall(("HTTP/1.1 302 FOUND\r\nLocation: "+data+"\r\n\r\n").encode())
    clientsocket.shutdown(SHUT_WR)

def GetPostData(data,post):
    data = data[len(data)-1].split("&")
    for item in data:
        item = item.split("=")
        if item[0] in post:
            post[item[0]]=item[1].replace("+"," ")
    return post
def DeleteLogFiles(lognum,keepmode):#keepmode: False = delete lognum old, True = keep lognum new
    if lognum >= len(logfiles): lognum = len(logfiles)
    if keepmode:
        deleteindexes = range(len(logfiles)-lognum)
    else:
        deleteindexes = range(lognum)
    print(list(deleteindexes))
    for i in deleteindexes: os.unlink("LocalLog_"+logfiles.pop(0)+".dat")
    SaveLogFileList()
    return lognum
def GetData(address,path,postlist=[]):
    method = "GET"
    if len(postlist)>0: method = "POST"
    post = ""
    for i in range(len(postlist)):
        post+=str(postlist[i][0])+"="+str(postlist[i][1])
        if i+1 != len(postlist): post+="&"
    addressparts = address.split(":")
    if len(addressparts) == 1: addressparts.append(80)
    clientsocket = socket(AF_INET,SOCK_STREAM)
    clientsocket.connect((addressparts[0], int(addressparts[1])))
    cmd = (method+' '+path+' HTTP/1.1\r\n\r\n'+post).encode()
    clientsocket.send(cmd)
    data = "".encode()
    while True:
        newdata = clientsocket.recv(512)
        data += newdata
        if len(newdata) < 1:
            break
    clientsocket.close()
    return data.decode()
def SaveLogFileList():
    g = open(os.path.join(Page.folder,"LogFileList.dat"),"wb")
    pickle.dump(logfiles,g)
    g.close()
def GetServerSettings(file):
    try:
        f = open(os.path.join(Page.folder,file),"rb")
        self = pickle.load(f)
        f.close()
    except FileNotFoundError:
        setup = False
        print("On/Off Monitor Web Setup")
        self = ServerSettings()
        port = input("Port number (default is 80): ")
        if port != "" : self.port = int(port)
        if "y" in input("Set up device IP address list with CSV file? (y/n) ").lower():
            csvpath = input("Please enter the path of the CSV file: ")
            try:
                csvfile = open(os.path.join(Page.folder,csvpath),"r")
                csvdata = csvfile.read()
                csvfile.close()
                if csvdata != "":
                    for line in csvdata.split("\n"): self.devices.append(line.split(",")[0])
                setup = True
            except FileNotFoundError: print("Not a valid file path")
        if not setup:
            print("Other device's IP addresses, including port number if necessary (press Ctrl+C or leave blank after adding all devices):")
            try:
                while True:
                    newip = input("> ")
                    if newip == "" : break
                    else: self.devices.append(newip)
            except KeyboardInterrupt: pass
        g = open(file,"wb")
        pickle.dump(self,g)
        g.close()
    return self
def tern(condition,truevalue,falsevalue):
    if condition: return truevalue
    else: return falsevalue

#Global variables:
currentlogtime = ""
logdata = []
devicestatus = []
ledswitchstate = False
logfiles = []
running = True
turnoff = False
settings = GetSettings("LogSettings.dat")
serversettings = GetServerSettings("ServerSettings.dat")
SetupGpio()
serversocket = socket(AF_INET, SOCK_STREAM)
Thread(target=Server).start()
if settings.newthread: Thread(target=Log).start()
else: Log()
