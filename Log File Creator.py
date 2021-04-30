from pickle import dump,load
def AddData():
    logdata = []
    fields = ["Date,Time","Device","Status"]
    while True:
        logitem = []
        for field in fields:
            logfield = input(field + ": ")
            if logfield == "": return logdata
            else: logitem.append(logfield)
        logdata.append(logitem)

while True:
    name = input("Enter name (without extension): LocalLog_")
    print("Enter file contents, leave a field blank to discard that record and save to file")
    f = open("LocalLog_"+name+".dat","wb")
    dump(AddData(),f)
    f.close()
    f = open("LogFileList.dat","rb")
    logfiles = load(f)
    f.close()
    logfiles.append(name)
    f = open("LogFileList.dat","wb")
    dump(logfiles,f)
    f.close()
    try: input("File saved and added to log file list. Press RETURN to continue or Ctrl + C to exit")
    except KeyboardInterrupt: break
