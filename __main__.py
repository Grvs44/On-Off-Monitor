#! /usr/bin/env python3
from settings import *
from threading import Thread
from time import sleep
from datetime import datetime
try: import RPi.GPIO as gpio
except ModuleNotFoundError:
    if input("Use GPIOconsole (y) or GPIO_Test (default)? ") == "y": import GPIOconsole as gpio
    else: import GPIO_Test as gpio

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
    if settings.dataled != None: gpio.setup(settings.dataled,gpio.OUT)
    for device in settings.devices:
        gpio.setup(device.pin,gpio.IN)
        gpio.setup(device.led,gpio.OUT)
        devicestatus.append(True)
    for name in settings.pinnames:
        gpio.setup(settings.pinnames[name],gpio.OUT)
    for device in settings.networkdevices:
        if settings.networkdevices[device] != None:
            gpio.setup(settings.networkdevices[device],gpio.OUT)
def Log() :
    global ledswitchstate,running,serversocket,turnoff
    print("On/Off Monitor Log Started")
    if settings.extralogconditions != None: ExtraLogConditions.Setup(settings,gpio)
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
        if settings.extralogconditions: ExtraLogConditions.Run(Add,settings,TryInput)
        SaveLog()
        if not TryInput(settings.shutdownpin):
            break
        sleep(settings.sleeptime)
    gpio.cleanup()
    serversocket.close() 
    print("On/Off Monitor exited")
    if turnoff: os.system("sudo shutdown -h 0")
    quit()
def GetSettings():
    global ExtraLogConditions
    try:
        f = open(os.path.join(Page.folder,"Settings.dat"),"rb")
        settings = pickle.load(f)
        f.close()
    except FileNotFoundError:
        settings = Settings()
    if settings.extralogconditions:
        from sys import path
        path.append(settings.extralogconditions[0])
        ExtraLogConditions = __import__(settings.extralogconditions[1])
    return settings

def Server():
    global running,turnoff,serversocket,pagecache,ipaddress
    print("On/Off Monitor Web Started")
    pagecache = {"/":Page("HomePage.html"),"/styles.css":Page("Styles.css"),"/script.js":Page("HomeScript.js"),"/status/status.js":Page("StatusScript.js"),"/status":Page("StatusPage.html"),"/status/reduced.js":Page("Reduced Status.js"),"/status/reduced":Page("Reduced Status.html"),"/app":Page("AppPage.html"),"/settings":Page("SettingsPage.html"),"/settings.js":Page("Settings.js"),"/settings1.js":Page("Load settings.js"),"/settings2.js":Page("Save settings.js"),"/settings.css":Page("Settings.css")}
    ipaddress = gethostname()
    serversocket.bind((ipaddress,settings.port))
    serversocket.listen(5)
    while running:
        try:
            req = serversocket.accept()
            Thread(target=ServerRespond,args=req).start()
        except OSError: break
def ServerRespond(clientsocket,other):
    global running,turnoff,pagecache
    if settings.dataled:
        gpio.output(settings.dataled,True)
    pieces = clientsocket.recv(5000).decode().split("\n")
    path = ""
    if len(pieces) > 0:
        try: path = pieces[0].split(" ")[1].lower()
        except IndexError : pass
    contenttype = "text/html"
    httpcode = 200
    cachecontrol = "no-cache"
    if path in pagecache: data,contenttype,cachecontrol = pagecache[path].loadh()
    elif path == "/status/status.json":
        contenttype = "application/json"
        data = []
        for device in settings.devices: data.append([device.name,"Off" if gpio.input(device.pin) else "On"])
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
    elif path == "/pinaccess":
        post = GetPostData(pieces,{"pin":None,"state":True,"id":""})
        post["pin"] = post["pin"]
        post["state"] = post["state"] == "1"
        if post["id"] in settings.pinaccess and post["pin"] in settings.pinaccess[post["id"]]:
            gpio.output(settings.pinnames[post["pin"]],post["state"])
            data = "1"
        else: data = "0"
    elif path == "/netdevicestatus":
        post = GetPostData(pieces,{"ipaddress":"","state":"0"})
        if post["ipaddress"] in settings.networkdevices:
            gpio.output(settings.networkdevices[post["ipaddress"]],post["state"] == "1")
            data = "1"
        else: data = "0"
    elif path == "/pinnames":
        id = GetPostData(pieces,{"id":""})["id"]
        if id in settings.pinaccess:
            data = json.dumps(settings.pinaccess[id])
        else:
            data = "[]"
    elif path == "/shutdown":
        post = GetPostData(pieces,{"devices":"this","web":"web","app":"0"})
        if post["devices"] == "all":
            for device in settings.networkdevices:
                GetData(device,"/shutdown",postlist=[["web","web"],["app","1"]])
            data="Shut down requested for all devices"
        else:
            data="Shut down"
        if post["app"]=="0":
            data = "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><title>Shut down - On/Off Monitor</title><h1 style='font-family:\"Segoe UI\";text-align:center'>" + data + "</h1>"
        if post["web"] == "all":
            turnoff = True
        running = False
    elif path == "/settings.json":
        data = settings.tojson()
        contenttype = "application/json"
    elif path == "/settings.json/save":
        settings.updatefromjson()
        data = ""
        contenttype = "text/plain"
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
            for device in settings.networkdevices: filedata.extend(json.loads(GetData(device,"/localdata?"+str(i)).split("")[3]))
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
        for device in settings.networkdevices: deletedfiles+=int(GetData(device,"/deletelocallogs",postlist=[["lognum",post["lognum"]],["fileage",post["fileage"]],["app","1"]]).split("")[3])
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
        post = GetPostData(pieces,{"lognum":"0","app":"0"})
        if post["app"] == "1":
            item = logfiles.pop(int(post["lognum"]))
            data = item[:4] + "/" + item[4:6] + "/" + item[6:8]
            try:
                os.unlink("LocalLog_"+item+".dat")
                data += " was deleted"
            except (FileNotFoundError,ValueError): data += " was not found"
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
    if httpcode == 200: clientsocket.sendall(("HTTP/1.1 200 OK\r\nContent-Type: "+contenttype+"; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\nCache-Control: " + cachecontrol + "\r\n\r\n"+data+"\r\n\r\n").encode())
    elif httpcode == 404: clientsocket.sendall("HTTP/1.1 404 NOT FOUND\r\n\r\n<title>Not found</title><h1>Not found</h1><p><a href='/'>Return to On/Off Monitor</a></p>\r\n\r\n".encode())
    elif httpcode == 302: clientsocket.sendall(("HTTP/1.1 302 FOUND\r\nLocation: "+data+"\r\n\r\n").encode())
    clientsocket.shutdown(SHUT_WR)
    if settings.dataled:
        gpio.output(settings.dataled,False)

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
def SaveLogFileList():
    g = open(os.path.join(Page.folder,"LogFileList.dat"),"wb")
    pickle.dump(logfiles,g)
    g.close()

currentlogtime = ""
logdata = []
devicestatus = []
ledswitchstate = False
logfiles = []
running = True
turnoff = False
settings = GetSettings()
SetupGpio()
serversocket = socket(AF_INET, SOCK_STREAM)
Thread(target=Server).start()
if settings.newthread: Thread(target=Log).start()
else: Log()
