let settings = {}
let settingsJSON
let changes
async function ShowSettings(){
    for (let a of ["sleeptime","port"]) {
        document.getElementById(a).value = settings[a]
    }
    for (let a of ["newthread", "outputlog"]) {
        document.getElementById(a).checked = settings[a]
    }
    for (let a of ["shutdownpin", "ledswitch", "dataled","deviceid"]) {
        if (settings[a] == null) {
            document.getElementById(a).disabled = true
            document.getElementById(a).checked = false
        } else {
            document.getElementById(a).disabled = false
            document.getElementById(a).checked = true
            document.getElementById(a).value = settings[a]
        }
        document.getElementById(a+"c").onchange = Checkbox_Change
    }
    if(settings.extralogconditions == null){
        document.getElementById("elc").checked = false
        document.getElementById("elc0").disabled = document.getElementById("elc1").disabled = true
    }else{
        document.getElementById("elc").checked = true
        document.getElementById("elc0").disabled = document.getElementById("elc1").disabled = false
        document.getElementById("elc0").value = settings.extralogconditions[0]
        document.getElementById("elc1").value = settings.extralogconditions[1]
    }
    document.getElementById("elc").onchange = e => {
        let group = e.target.parentElement.children
        group[4].disabled = group[7].disabled = !e.target.checked
    }
    document.getElementById("devlist").innerHTML = document.getElementById("netlist").innerHTML = document.getElementById("pinalist").innerHTML = document.getElementById("pinnlist").innerHTML = ""
    for(let device of settings.devices) AddDev(device)
    for(let key of Object.keys(settings.networkdevices)) AddNet(key)
    for(let key of Object.keys(settings.pinaccess)) AddPinADev(key)
    for(let key of Object.keys(settings.pinnames)) AddPinName(key)
    changes = true
}
function Checkbox_Change(e){
    e.target.parentElement.children[4].disabled = !e.target.checked
}
function AddDev(values=null){
    let li = document.createElement("li")
    let l1 = document.createElement("label")
    let l2 = document.createElement("label")
    let l3 = document.createElement("label")
    let e1 = document.createElement("input")
    let e2 = document.createElement("input")
    let e3 = document.createElement("input")
    let btn = document.createElement("input")
    e1.type = "text"
    e2.type = "number"
    e3.type = "number"
    btn.type = "button"
    l1.innerText = "Device name"
    l2.innerText = "Input pin number"
    l3.innerText = "LED pin number"
    l1.htmlFor = e1
    l2.htmlFor = e2
    l3.htmlFor = e3
    e1.required = e2.required = e3.required = true
    btn.value = "X"
    btn.className = "delete"
    btn.onclick = Del
    if(values != null){
        e1.value = values[0]
        e2.value = values[1]
        e3.value = values[2]
    }
    li.append(btn,l1,e1,l2,e2,l3,e3)
    document.getElementById("devlist").appendChild(li)
}
function AddNet(key=null){
    let li = document.createElement("li")
    let l1 = document.createElement("label")
    let l2 = document.createElement("label")
    let e1 = document.createElement("input")
    let e2 = document.createElement("input")
    let btn = document.createElement("input")
    l1.innerText = "Device IP address"
    l2.innerText = "Device status LED pin"
    l1.for = e1
    l2.for = e2
    e1.type = "text"
    e2.type = "number"
    e1.required = true
    e2.placeholder = "None"
    btn.type = "button"
    btn.value = "X"
    btn.className = "delete"
    btn.onclick = Del
    if(key != null){
        e1.value = key
        e2.value = settings.networkdevices[key]
    }
    li.append(btn,l1,e1,l2,e2)
    document.getElementById("netlist").appendChild(li)
}
function AddPinADev(key=null){
    let li = document.createElement("li")
    let ul = document.createElement("ul")
    let l1 = document.createElement("label")
    let e1 = document.createElement("input")
    let delbtn = document.createElement("input")
    let addbtn = document.createElement("input")
    l1.innerText = "Device IP address"
    ul.id = key
    l1.for = e1
    e1.type = "text"
    e1.required = true
    delbtn.type = addbtn.type = "button"
    delbtn.value = "X"
    delbtn.className = "delete"
    delbtn.onclick = Del
    addbtn.value = "Add"
    addbtn.onclick = e => AddPinAPin(key)
    li.append(delbtn,l1,e1,addbtn,ul)
    document.getElementById("pinalist").appendChild(li)
    if(key != null){
        e1.value = key
        for(let pin of settings.pinaccess[key]) AddPinAPin(key,pin)
    }
}
function AddPinAPin(key,pin=null){
    let li = document.createElement("li")
    let l1 = document.createElement("label")
    let e1 = document.createElement("input")
    let btn = document.createElement("input")
    l1.innerText = "Pin name"
    l1.for = e1
    e1.type = "text"
    e1.required = true
    e1.className = "e"
    btn.type = "button"
    btn.value = "X"
    btn.className = "delete"
    btn.onclick = Del
    if(key != null) e1.value = pin
    li.append(btn,l1,e1)
    document.getElementById(key).appendChild(li)
}
function AddPinName(key=null){
    let li = document.createElement("li")
    let l1 = document.createElement("label")
    let l2 = document.createElement("label")
    let e1 = document.createElement("input")
    let e2 = document.createElement("input")
    let btn = document.createElement("input")
    l1.innerText = "Pin name"
    l2.innerText = "Pin number"
    l1.for = e1
    l2.for = e2
    e1.type = "text"
    e2.type = "number"
    e1.required = e2.required = true
    btn.type = "button"
    btn.value = "X"
    btn.className = "delete"
    btn.onclick = Del
    if(key != null){
        e1.value = key
        e2.value = settings.pinnames[key]
    }
    li.append(btn,l1,e1,l2,e2)
    document.getElementById("pinnlist").appendChild(li)
}
function Del(e){
    e.target.parentElement.remove()
}