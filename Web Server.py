from socket import socket,AF_INET,SOCK_STREAM,SHUT_WR
import pickle
class Settings():
    mainpath = ""
    devices = []
    port = 80
    def __init__(self):#https://www.w3schools.com/python/python_classes.asp
        f = open("ServerSettings.dat","rb")
        self = pickle.load(f)
        f.close()
def CreateServer():
    serversocket = socket(AF_INET, SOCK_STREAM)
    serversocket.bind(('localhost',settings.port))
    serversocket.listen(5)
    shutdown = False
    firstrun = True
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
            data = "" # Stores location for 302s
            contenttype = "text/html"
            httpcode = 200
            if path == "/":
                f = open("HomePage.html",mode='r')
                data=f.read()
                f.close()
            elif path == "/shutdown" and not firstrun:
                data = "<title>Shut down - On/Off Monitor</title><h1 style='font-family:\"Segoe UI\";text-align:center'>The web service has shut down</h1>"
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
                    f = open("log.csv",mode="r")
                    data=f.read()
                    f.close()
                    contenttype="text/csv"
                else : # This device is not the main device
                    data="http://"+settings.mainpath+"/log.csv"
                    httpcode=302 # https://en.wikipedia.org/wiki/HTTP_302
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
def GetData():
    mysock = socket(AF_INET,SOCK_STREAM)
    mysock.connect(('data.pr4e.org', 80))
    cmd = 'GET http://data.pr4e.org/page1.htm HTTP/1.0\r\n\r\n'.encode()
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
#print('Access http://localhost:9000')
logfiles = []
settings = Settings()
GetLogFileList()
CreateServer()
