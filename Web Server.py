from socket import socket,AF_INET,SOCK_STREAM,SHUT_WR
import pickle
class Settings():
    mainpath = ""
    devices = []
    port = 80
    def __init__(self):
        self.devices = []
        f = open("ServerSettings.dat","rb")
        self = pickle.load(f)
        f.close()
def Server():
    serversocket = socket(AF_INET, SOCK_STREAM)
    serversocket.bind(('localhost',settings.port))
    serversocket.listen(5)
    shutdown = False
    firstrun = True
    turnoff = False
    while(1):
            (clientsocket, address) = serversocket.accept()
            rd = clientsocket.recv(5000).decode()
            pieces = rd.split("\n")
            path = ""
            if ( len(pieces) > 0 ) :
                print(pieces[0])
                try: path = pieces[0].split(" ")[1].lower()
                except IndexError : pass
            print(path)
            data = ""
            contenttype = "text/html"
            httpcode = 200
            if path == "/":
                f = open("HomePage.html",mode='r')
                data=f.read()
                f.close()
            elif path == "/shutdown" and not firstrun:
                pathdata = pieces[len(pieces)-1].split("&")
                devices = "this"
                web = "web"
                data = "<title>Shut down - On/Off Monitor</title><h1 style='font-family:\"Segoe UI\";text-align:center'>"
                for i in range(len(pathdata)):
                    pathdata[i] = pathdata[i].split("=")
                    if pathdata[i][0] == "devices":
                        devices = pathdata[i][1]
                    elif pathdata[i][0] == "web":
                        web = pathdata[i][1]
                if devices == "all":
                    if settings.mainpath == "":
                        print(settings.devices)
                        for device in settings.devices:
                            GetData(device,"/shutdown",postlist=["web",web])
                            print("a")
                    else: GetData(settings.mainpath,"/shutdown",postlist=[["devices",devices],["web",web]])
                    data+="Shut down requested for all devices</h1>"
                else:
                    data+="Shut down</h1>"
                if web == "all":
                    turnoff = True
                shutdown = True
            elif "/localdata" in path:
                try:
                    item = 1
                    if "?" in path:
                        item = int(path.split("?")[1])
                    f=open("LocalLog_"+settings.logfiles[len(setings.logfiles)-item]+".dat",mode="r")
                    data = f.read()
                    f.close()
                except IndexError: pass
            elif path == "/log.csv":
                if settings.mainpath == "" : # This device is the main device
                    filedata = []
                    for i in range(lognum):
                        for device in devices:
                            data.append(pickle.load(GetData(device,"/localdata?"+str(lognum)))) ##
                    
                    contenttype="text/csv"
                else : # This device is not the main device
                    data="http://"+settings.mainpath+"/log.csv"
                    httpcode=302
            else:
                data = "/"
                if path == "/shutdown" : httpcode = 302
                else : httpcode = 301
            if httpcode == 200:clientsocket.sendall(("HTTP/1.1 200 OK\r\nContent-Type: "+contenttype+"; charset=utf-8\r\n\r\n"+data+"\r\n\r\n").encode())
            elif httpcode == 301: clientsocket.sendall(("HTTP/1.1 301 MOVED\r\nLocation: "+data+"\r\n\r\n").encode())
            elif httpcode == 302: clientsocket.sendall(("HTTP/1.1 302 FOUND\r\nLocation: "+data+"\r\n\r\n").encode())
            clientsocket.shutdown(SHUT_WR)
            if(shutdown):break
            firstrun = False
    serversocket.close()
    if turnoff: print("Turned off")
def GetData(address,path,postlist=[]):
    post = ""
    for i in range(len(postlist)):
        post+=postlist[i][0]+"="+postlist[i][1]
        if i+1 != len(postlist): post+="&"
    mysock = socket(AF_INET,SOCK_STREAM)
    mysock.connect((address, 80))
    cmd = ('GET http://'+address+path+' HTTP/1.0\r\n\r\n'+post).encode()
    mysock.send(cmd)
    iterations = 0
    while True:
        data = mysock.recv(512)
        if len(data) < 1:
            break
        print(data.decode(),end='')
        iterations +=1
    mysock.close()
    print(iterations)
def GetLogFileList():
    global logfiles
    try:
        g = open("LogFileList.dat","rb")
        logfiles = pickle.load(g)
        g.close()
    except FileNotFoundError: print("FNF")
logfiles = []
settings = Settings()
GetLogFileList()
Server()
