from socket import socket,AF_INET,SOCK_STREAM,SHUT_WR,gethostname,gethostbyname
import pickle,json
from os import unlink, system
from OnOffMonitor import ListToCsv
class Settings():
    devices = []
    port = 80
def Server():
    ipaddress = "localhost"#gethostbyname(gethostname())#"localhost"
    serversocket = socket(AF_INET, SOCK_STREAM)
    serversocket.bind((ipaddress,settings.port))
    serversocket.listen(5)
    shutdown = False
    turnoff = False
    while(1):
            #(clientsocket,address) = serversocket.accept()
            clientsocket = serversocket.accept()[0]
            rd = clientsocket.recv(5000).decode()
            pieces = rd.split("\n")
            path = ""
            if ( len(pieces) > 0 ) :
                try: path = pieces[0].split(" ")[1].lower()
                except IndexError : pass
            data = ""
            contenttype = "text/html"
            httpcode = 200
            if path == "/":
                f = open("HomePage.html",mode='r')
                data=f.read()
                f.close()
            elif path == "/shutdown":
                pathdata = pieces[len(pieces)-1].split("&")
                devices = "this"
                web = "web"
                for i in range(len(pathdata)):
                    pathdata[i] = pathdata[i].split("=")
                    if pathdata[i][0] == "devices":
                        devices = pathdata[i][1]
                    elif pathdata[i][0] == "web":
                        web = pathdata[i][1]
                    elif pathdata[i][0] == "app":
                        app = (pathdata[i][1]=="1")
                if devices == "all":
                    for device in settings.devices:
                        GetData(device,"/shutdown",postlist=[["web",web]])
                    data="Shut down requested for all devices"
                else:
                    data="Shut down"
                if not app:
                    data = "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><title>Shut down - On/Off Monitor</title><h1 style='font-family:\"Segoe UI\";text-align:center'>" + data + "</h1>"
                if web == "all":
                    turnoff = True
                shutdown = True
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
                lognun,fileage,app = SplitPostData(pieces)
                if lognum < 1: lognum = 1
                elif lognum > len(logfiles): lognum = len(logfiles)
                filedata = []
                for i in range(lognum):
                    f = open("LocalLog_"+logfiles[len(logfiles)-lognum]+".dat","rb")
                    filedata.extend(pickle.load(f))
                    f.close()
                    for device in settings.devices:
                        filedata.extend(json.loads(GetData(device,"/localdata?"+str(lognum)).split("\r\n")[3]))
                filedata.sort(reverse=True)
                data = ListToCsv("Date,Time,Device,Status",filedata)
                contenttype="text/csv"
            elif path == "/deletelocallogs":
                lognum,fileage,app = SplitPostData(pieces)
                if len(logfiles)<lognum: lognum = len(logfiles)
                data = str(DeleteLogFiles(lognum,(fileage=="new")))
            elif path == "/deletelogs":
                lognum,fileage,app = SplitPostData(pieces)
                deletedfiles = 0
                if len(logfiles)>0:
                    deletedfiles+=DeleteLogFiles(lognum,(fileage=="new"))
                for device in settings.devices: deletedfiles+=int(GetData(device,"/deletelocallogs",postlist=pathdata).split("\r\n")[3])
                if app:
                    data = str(deletedfiles) + " files were deleted"
                else:
                    data = "/deleted?" + str(deletedfiles)
                    httpcode = 302
            elif path == "/logfilelist":
                lognum,fileage,app = SplitPostData(pieces)
                if app: data = json.dumps(logfiles)
                else: httpcode = 301
            elif path == "/deletelocallog":
                lognum,fileage,app = SplitPostData(pieces)
                if app:
                    unlink("LocalLog_"+logfiles.pop(lognum)+".dat")
                    data = "Log file deleted"
                else: httpcode = 301
            elif path == "/logfile":
                lognum,fileage,app = SplitPostData(pieces)
                if app:
                    print("lognum: "+str(lognum))
                    if lognum < len(logfiles):
                        f = open("LocalLog_"+logfiles[lognum]+".dat","rb")
                        data = json.dumps(pickle.load(f))
                        f.close()
                    else: data = "[]"
                else: httpcode = 301
            elif "/deleted" in path:
                deleteditems = "0"
                if "?" in path: deleteditems = path.split("?")[1]
                data = "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><title>Delete Log Files - On/Off Monitor</title><div style=\"font-family:'Segoe UI';text-align:center\"><h1>" + deleteditems + " files were deleted</h1><a href='/'>Click here</a> to return to the home page</div>"
            else:
                data = "/"
                httpcode = 301
            if httpcode == 200:clientsocket.sendall(("HTTP/1.1 200 OK\r\nContent-Type: "+contenttype+"; charset=utf-8\r\n\r\n"+data+"\r\n\r\n").encode())
            elif httpcode == 301: clientsocket.sendall(("HTTP/1.1 301 MOVED\r\nLocation: "+data+"\r\n\r\n").encode())
            elif httpcode == 302: clientsocket.sendall(("HTTP/1.1 302 FOUND\r\nLocation: "+data+"\r\n\r\n").encode())
            clientsocket.shutdown(SHUT_WR)
            if(shutdown):break
    serversocket.close()
    if turnoff: system("sudo shutdown -h 0")
def SplitPostData(pieces):
    fileage = "new"
    lognum = 1
    app = False
    pathdata = pieces[len(pieces)-1].split("&")
    print(pathdata)
    for i in range(len(pathdata)):
        pathdata[i] = pathdata[i].split("=")
        if pathdata[i][0] == "lognum":
            lognum = int(pathdata[i][1])
        elif pathdata[i][0] == "fileage":
            fileage = pathdata[i][1]
        elif pathdata[i][0] == "app":
            app = (pathdata[i][1]=="1")
    print(lognum)
    return (lognum,fileage,app)
def DeleteLogFiles(lognum,keepmode):#keepmode: False = delete lognum old, True = keep lognum new
    deleteindexes = []
    if keepmode:
        deleteindexes = range(len(logfiles)-lognum)
    else:
        deleteindexes = range(lognum)
    for i in deleteindexes: unlink("LocalLog_"+logfiles.pop(0)+".dat")
    SaveLogFileList()
    return len(deleteindexes)
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
    g = open("LogFileList.dat","wb")
    pickle.dump(logfiles,g)
    g.close()
def GetLogFileList():
    global logfiles
    try:
        g = open("LogFileList.dat","rb")
        logfiles = pickle.load(g)
        g.close()
    except FileNotFoundError: pass
def GetSettings(file):
    try:
        f = open(file,"rb")
        self = pickle.load(f)
        f.close()
    except FileNotFoundError:
        g = open(file,"wb")
        self = Settings()
        pickle.dump(self,g)
        g.close()
    return self
logfiles = []
settings = GetSettings("ServerSettings.dat")
GetLogFileList()
Server()
