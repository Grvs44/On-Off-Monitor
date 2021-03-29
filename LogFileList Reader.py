import pickle
f = open("LogFileList.dat","rb")
logfiles = pickle.load(f)
f.close()
print(logfiles)
item = int(input("Which item would you like to open? (starting from 1): "))-1
if item in range(len(logfiles)):
    from OnOffMonitor import ListToCsv
    f = open("LocalLog_"+logfiles[item]+".dat","rb")
    print(ListToCsv("Date,Time,Device,Message",pickle.load(f)))
    f.close()
else: print("File not found")
input("Press RETURN to exit ")
