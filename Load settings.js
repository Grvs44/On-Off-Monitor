let filereader
async function Onload() {
    settingsJSON = await(await fetch("/settings.json")).text()
    settings = JSON.parse(settingsJSON)
    ShowSettings()
    document.forms[0].onsubmit = Form_Submit
    filereader = new FileReader()
    filereader.addEventListener("load",FileLoaded)
}
function LoadFile(){
    filereader.readAsText(document.getElementById("open").files[0])
}
function FileLoaded(){
    settings = JSON.parse(filereader.result)
    /*for(let ul of ["devlist","netlist","pinalist","pinnlist"]){
        ul = document.getElementById(ul)
        while(ul.childElementCount != 0){
            ul.removeChild(ul.firstChild)
        }
    }*/
    document.getElementById("open").value = ""
    ShowSettings()
}