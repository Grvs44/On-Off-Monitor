import pickle
def ListToCsv(header,item):
    csv=header+"\n"
    for i in range(len(item)):
        for j in range(len(item[i])):
            csv+=str(item[i][j])
            if j+1 != len(item[i]): csv+=","
        if i+1 != len(item): csv+="\n"
    return csv
f = open("LogFileList.dat","rb")
logfiles = pickle.load(f)
f.close()
print(logfiles)
try:
	item = int(input("Which item would you like to open? (starting from 1): "))-1
	if item in range(len(logfiles)):
	    f = open("LocalLog_"+logfiles[item]+".dat","rb")
	    print(ListToCsv("Date,Time,Device,Status",pickle.load(f)))
	    f.close()
	else: print("File not found")
except ValueError: print("File not found")
input("Press RETURN to exit ")
