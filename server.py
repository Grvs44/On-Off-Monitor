from socket import socket,AF_INET,SOCK_STREAM,SHUT_WR,gethostname
def GetPostData(data,post):
    data = data[len(data)-1].split("&")
    for item in data:
        item = item.split("=")
        if item[0] in post:
            post[item[0]]=item[1].replace("+"," ")
    return post
def GetData(address,path,postlist=[],binary=False):
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
    clientsocket.send((method+" "+path+" HTTP/1.1\r\n\r\n"+post).encode())
    data = b""
    while True:
        newdata = clientsocket.recv(512)
        data += newdata
        if len(newdata) < 1:
            break
    clientsocket.close()
    if binary: return data
    else: return data.decode()
