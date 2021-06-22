#From https://raspberrypi.stackexchange.com/questions/34119/gpio-library-on-windows-while-developing
from random import randint as ran
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
def input(pin):
   return ran(0,1) == 1
   #return True
