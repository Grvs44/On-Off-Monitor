let list
function Onload(){
    list = document.getElementById("list")
    document.forms[0]["c"].placeholder = "Enter commands here\nThe console instance is closed after each set of commands is sent"
    document.forms[0].addEventListener("submit",SubmitCommand)
}
async function SubmitCommand(e){
    e.preventDefault()
    e.submitter.disabled = true
    let li = document.createElement("li")
    let cmd = document.createElement("b")
    cmd.innerText = e.target["c"].value
    let res = document.createElement("code")
    res.innerText = await(await fetch("/console/run",{"method":"POST","body":"c="+JSON.stringify(e.target["c"].value.split("\n"))})).text()
    e.submitter.disabled = false
    li.append(cmd,document.createElement("br"),res)
    list.appendChild(li)
    li.scrollIntoView()
}
function Clear(){
    list.innerHTML = ""
}