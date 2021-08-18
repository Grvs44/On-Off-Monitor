var table,refresh,xhr
function Body_Onload(){
	table = document.getElementById("statustable")
	refresh = document.getElementById("statusrefresh")
	if (XMLHttpRequest) {xhr = new XMLHttpRequest();}
	else {xhr = new ActiveXObject("Microsoft.XMLHTTP");}
	xhr.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
			var resp = JSON.parse(xhr.responseText);
			var tabletext = "<tr><th>Name</th><th>Status</th></tr>";
			for(var i=0;i<resp.length;i++){
				tabletext += "<tr><td>" + resp[i].join("</td><td>") + "</td></tr>";
			}
			table.innerHTML = tabletext;
		}
	};
	Request();
}
function Request(){
	xhr.open("GET","/status/status.json",true);
	xhr.setRequestHeader("Pragma", "no-cache");
	xhr.send();
	var number = Number(refresh.value);
	if(isNaN(number) || number < 0.05){number = 10;}
	setTimeout(Request,number*1000);
}