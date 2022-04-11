let filereader
async function Onload() {
    settings = await(await fetch("/settings.json")).json();
    ShowSettings();
    document.forms[0].onsubmit = Form_Submit;
    filereader = new FileReader()
    filereader.addEventListener("load",FileLoaded)
}
function LoadFile(){
    filereader.readAsURL(document.getElementById("open").files[0])
}
function FileLoaded(){
    console.log(filereader.result)
    settings = JSON.parse(filereader.result)
    for(let ul of ["devlist","netlist","pinalist","pinnlist"]){
        ul = document.getElementById(ul)
        while(ul.childElementCount != 0){
            ul.removeChild(ul.firstChild)
        }
    }
    document.getElementById("open").value = ""
    ShowSettings()
}
function DownloadFile(){
    open("data:application/json;base64," + btoa(JSON.stringify(settings)))
}