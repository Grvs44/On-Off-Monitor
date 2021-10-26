BOARD = 1
OUT = 1
IN = 1
def setmode(a):
   print ("setmode:",a)
def setup(a, b):
   print ("setup:",a,b)
def output(a, b):
   print ("output:",a,b)
def cleanup():
   print ("cleanup")
def setwarnings(flag):
   print ("setwarnings:",flag)
try:
   f = open("GPIOtest.json","r")
   import json
   gpiotest = json.load(f)
   f.close()
   def input(pin):
      return gpiotest[str(pin)]
except FileNotFoundError:
   from random import randint as ran
   def input(pin):
      return ran(0,1) == 1
