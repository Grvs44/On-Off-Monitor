overrun = False
def Setup(settings):
    global pump,othersrange
    pump,index = DeviceSearch(settings,37)
    othersrange = list(range(len(settings.devices)))
    othersrange.pop(index)
    print(index,othersrange)
def Run(Add,settings,TryInput):
    #overrun = pump is on and rest are off
    global overrun
    if not overrun and not TryInput(pump.pin) and OthersOff(settings,TryInput):
        overrun = True
        Add("Pump","Overrun started")
    elif overrun and TryInput(pump.pin) and not OthersOff(settings,TryInput):
        overrun = False
        Add("Pump","Overrun ended")
def DeviceSearch(settings,inpin):
    index = 0
    min = 0
    max = len(settings.devices)-1
    while min <= max:
            index = int((min+max)/2)
            if settings.devices[index].pin == inpin: return settings.devices[index],index
            elif settings.devices[index].pin < inpin: min = index+1
            else: max = index-1
    raise Exception("Input pin not in device list")
def OthersOff(settings,TryInput):
    for i in othersrange:
        if not TryInput(settings.devices[i].pin): return False
    return True
