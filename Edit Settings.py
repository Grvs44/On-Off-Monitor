#! /usr/bin/env python3
from settings import *
if os.path.isfile("Settings.dat"):
    f = open("Settings.dat","rb")
    settings = pickle.load(f)
    f.close()
    options = ""
    for key in settings.__dict__:
        options += "\n%s\t%s" % (key,settings.__dict__[key])
    print("----Options----\nATTIRBUTE\tVALUE" + options)
    while True:
        try:
            key = input("Chosen key (or else to save and exit): ")
            if key in settings.__dict__:
                print("Current value: " + str(settings.__dict__[key]))
                if type(settings.__dict__[key]) == list:
                    index = int(input("Enter index to edit: "))
                    settings.__dict__[key][index] = eval(input("New value (enter as Python): "))
                else:
                    settings.__dict__[key] = eval(input("New value (enter as Python): "))
            else:
                if input("Save and exit? ").lower() == "y":
                    f = open("Settings.dat","wb")
                    pickle.dump(settings,f)
                    f.close()
                    break
        except Exception as e:
            print("Error:",e)
else:
    print("No settings file has been created. Start On/Off Monitor to create a new file, or check you are running this script in the correct directory:\n" + __file__)
