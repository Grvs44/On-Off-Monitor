function Save(){
    let form = document.forms[0]
    for(let field of ["sleeptime","port"]){
        settings[field] = Number(form[field].value)
    }
    for(let field of ["ledswitch","shutdownpin","dataled"]){
        if(form[field+"c"].checked) settings[field] = Number(form[field].value)
        else settings[field] = null
    }
    for(let field of ["outputlog","newthread"]){
        settings[field] = form[field].checked
    }
    settings.deviceid = form.deviceid.value
}
async function Form_Submit(e){
    e.preventDefault()
    if(Save()){
        let response = await(await fetch("/settings.json/set",{"method":"POST"})).text()
        if(response == "") alert("Settings saved")
        else alert(response)
    }
}