let settings = {};
async function load(){
    settings = await (await fetch("/settings.json")).json()
    for (let a of ["sleeptime","port","deviceid"]) {
        document.getElementById(a).value = settings[a]
    }
    for (let a of ["newthread", "outputlog"]) {
        document.getElementById(a).checked = settings[a]
    }
    for (let a of ["shutdownpin", "ledswitch", "dataled"]) {
        if (settings[a] == null) {
            document.getElementById(a).disabled = true
            document.getElementById(a).checked = false
        } else {
            document.getElementById(a).disabled = false
            document.getElementById(a).checked = true
            document.getElementById(a).value = settings[a]
        }
    }
    document.forms[0].onsubmit = async function (e) {
        e.preventDefault()
    }
}