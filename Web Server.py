from socket import socket,AF_INET,SOCK_STREAM,SHUT_WR,gethostname,gethostbyname
import pickle,json
from os import unlink, system
from OnOffMonitor import ListToCsv
class Settings():
    devices = []
    port = 80
def Server():
    ipaddress = gethostbyname(gethostname())#"localhost"
    serversocket = socket(AF_INET, SOCK_STREAM)
    serversocket.bind((ipaddress,settings.port))
    serversocket.listen(5)
    shutdown = False
    turnoff = False
    while(1):
            clientsocket = serversocket.accept()[0]
            pieces = clientsocket.recv(5000).decode().split("\n")
            path = ""
            if ( len(pieces) > 0 ) :
                try: path = pieces[0].split(" ")[1].lower()
                except IndexError : pass
            data = ""
            contenttype = "text/html"
            httpcode = 200
            if "log" in path: GetLogFileList() #To keep logfiles up to date
            if path == "/":
                f = open("HomePage.html",mode='r')
                data=f.read()
                f.close()
            elif path == "/shutdown":
                post = GetPostData(pieces,{"devices":"this","web":"web","app":"0"})
                if post["devices"] == "all":
                    for device in settings.devices:
                        GetData(device,"/shutdown",postlist=[["web",web]])
                    data="Shut down requested for all devices"
                else:
                    data="Shut down"
                if post["app"]=="0":
                    data = "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><title>Shut down - On/Off Monitor</title><h1 style='font-family:\"Segoe UI\";text-align:center'>" + data + "</h1>"
                if post["web"] == "all":
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
                    for device in settings.devices: filedata.extend(json.loads(GetData(device,"/localdata?"+str(i)).split("\r\n")[3]))
                filedata.sort(reverse=True)
                data = ListToCsv("Date,Time,Device,Status",filedata)
                contenttype="text/csv"
            elif path == "/deletelocallogs":
                post = GetPostData(pieces,{"lognum":0,"fileage":"new"})
                post["lognum"] = int(post["lognum"])
                #if len(logfiles)<post["lognum"]: data="No file deleted"#post["lognum"] = len(logfiles)
                data = str(DeleteLogFiles(post["lognum"],(post["fileage"]=="new")))
            elif path == "/deletelogs":
                post = GetPostData(pieces,{"lognum":0,"fileage":"new","app":"0"})
                post["lognum"]=int(post["lognum"])
                deletedfiles = 0
                if len(logfiles)>0:
                    deletedfiles+=DeleteLogFiles(post["lognum"],(post["fileage"]=="new"))
                for device in settings.devices: deletedfiles+=int(GetData(device,"/deletelocallogs",postlist=pathdata).split("\r\n")[3])
                if post["app"]=="1":
                    data = str(deletedfiles) + " files were deleted"
                else:
                    data = "/deleted" + str(deletedfiles)
                    httpcode = 302
            elif path == "/logfilelist":
                data = GetPostData(pieces,{"app":"0"})
                if data["app"]=="1": data = json.dumps(logfiles)
                else: httpcode = 301
            elif path == "/deletelocallog":
                lognum = int(GetPostData(pieces,{"lognum":0})["lognum"])
                if app:
                    item = logfiles.pop(lognum)
                    data = item[:4] + "/" + item[4:6] + "/" + item[6:8]
                    try:
                        unlink("LocalLog_"+item+".dat")
                        data += " was deleted"
                    except FileNotFoundError: data += " was not found"
                    SaveLogFileList()
                else: httpcode = 301
            elif path == "/logfile":
                post = GetPostData(pieces,{"lognum":0,"app":"0"})
                post["lognum"]==int(post["lognum"])
                if post["app"]=="1":
                    print("lognum: "+str(lognum))
                    if post["lognum"] < len(logfiles):
                        f = open("LocalLog_"+logfiles[post["lognum"]]+".dat","rb")
                        data = json.dumps(pickle.load(f))
                        f.close()
                    else: data = "[]"
                else: httpcode = 301
            elif "/deleted" in path:
                try: deleteditems = path.split("deleted")[1]
                except IndexError: deleteditems = "0"
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
    for i in deleteindexes: unlink("LocalLog_"+logfiles.pop(0)+".dat")
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
Server()
