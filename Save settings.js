function SaveToJson(){
    let form = document.forms[0]
    let inputs,lis,values
    for(let field of ["sleeptime","port"]){
        settings[field] = Number(form[field].value)
    }
    for(let field of ["ledswitch","shutdownpin","dataled","deviceid"]){
        if(form[field+"c"].checked) settings[field] = Number(form[field].value)
        else settings[field] = null
    }
    for(let field of ["outputlog","newthread"]){
        settings[field] = form[field].checked
    }
    if(form["elc"].checked) settings["extralogconditions"] = [form["elc0"].value,form["elc1"].value]
    else settings["extralogconditions"] = null
    settings["devices"] = []
    for(let li of document.getElementById("devlist").children){
        let inputs = li.getElementsByTagName("input")
        settings["devices"].push([inputs[1].value,inputs[2].value,inputs[3].value])
    }
    settings.networkdevices = {}
    settings.pinaccess = {}
    settings.pinnames = {}
    for(let list of [["netlist","networkdevices"],["pinnlist","pinnames"]]){
        lis = document.getElementById(list[0]).children
        for(let li of lis){
            inputs = li.getElementsByTagName("input")
            settings[list[1]][inputs[1].value] = inputs[2].value
        }
    }
    for(let li of document.getElementById("pinalist").children){
        values = []
        for(let entry of li.getElementsByClassName("e")) values.push(entry.value)
        settings.pinaccess[li.getElementsByTagName("input")[1].value] = values
    }
    settingsJSON = JSON.stringify(settings)
    changes = false
}
async function Form_Submit(e){
    e.preventDefault()
    if(changes) SaveToJson()
    if(e.submitter.id == "local") saveAs(new File([settingsJSON],"settings.json",{type:"application/json;charset=utf-8"}))
    else{
        let response = await(await fetch("/settings.json/set",{"method":"POST","body":"d="+encodeURI(settingsJSON)})).text()
        if(response.trim() == "") alert("Settings saved")
        else alert(response)
    }
}