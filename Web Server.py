from socket import *
mainpath = ""
def createServer():
    serversocket = socket(AF_INET, SOCK_STREAM)
    try :
        serversocket.bind(('localhost',9000))
        serversocket.listen(5)
        shutdown = True
        while(1):
                (clientsocket, address) = serversocket.accept()
                rd = clientsocket.recv(5000).decode()
                pieces = rd.split("\n")
                path = ""
                if ( len(pieces) > 0 ) :
                    print(pieces[0])
                    path = pieces[0].split(" ")[1].lower()
                print(path)
                #data = "HTTP/1.1 200 OK\r\n"
                #data += "Content-Type: text/html; charset=utf-8\r\n"
                #data += "\r\n"
                data = ""
                contenttype = "text/html"
                if(path == "/shutdown" and shutdown == False):
                    data = "<title>Shut down</title><p>The device has shut down</p>"
                    shutdown = True
                elif path == "/localdata":
                    f=open("locallog.dgl",mode="r")
                    data = f.read()
                    f.close()
                elif path == "/log.csv":
                    if mainpath == "" :
                        #data+="<p>Logfile from this device</p>"
                        f = open("log.csv",mode="r")
                        data+=f.read()
                        f.close()
                        contenttype="text/csv"
                    else :
                        data="<p>Logfile from the main device</p>"
                else:
                    f = open("HomePage.html",mode='r')
                    data=f.read()
                    f.close()
                    shutdown = False
                #data += "\r\n\r\n"
                clientsocket.sendall(("HTTP/1.1 200 OK\r\nContent-Type: "+contenttype+"; charset=utf-8\r\n\r\n"+data+"\r\n\r\n").encode())
                clientsocket.shutdown(SHUT_WR)
                if(shutdown):break
    except KeyboardInterrupt :
        print("\nShutting down...\n")
    serversocket.close()
def GetData():
    mysock = socket(socket.AF_INET, socket.SOCK_STREAM)
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
print('Access http://localhost:9000')
createServer()
