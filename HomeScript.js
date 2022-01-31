function ChangeDeleteLabels(entry){
	document.getElementById("deletelabel1").innerText = document.getElementById("deletelabel2").innerText = entry.value
	let dbtn = document.getElementById("deletebutton")
	dbtn.disabled  = (entry.value=="")
	dbtn.value = "Delete"
	document.getElementById("confirmdeletebutton").style.display = "none"
}
function ConfirmDelete(){
	let btn = document.getElementById("deletebutton")
	btn.value = btn.value=="Delete"?"Decline delete":"Delete"
	let sub = document.getElementById("confirmdeletebutton")
	sub.style.display=sub.style.display=="inline"?"none":"inline"
}
function ConfirmShutdown(){
	let btn = document.getElementById("sdownbutton")
	btn.value=btn.value=="Shut down"?"Decline shut down":"Shut down"
	let sub = document.getElementById("confirmsdownbutton")
	sub.style.display=btn.value=="Shut down"?"none":"inline"
}
async function ResetCache(){
	alert(await(await fetch("/resetcache")).text())
}