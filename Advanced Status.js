var devsadded,refresh,xhr
function Body_Onload(){
	refresh = document.getElementById("statusrefresh")
	devsadded = false;
	if (XMLHttpRequest) {xhr = new XMLHttpRequest();}
	else {xhr = new ActiveXObject("Microsoft.XMLHTTP");}
	xhr.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
			var resp = JSON.parse(xhr.responseText);
			if(devsadded){
				for(var i=0;resp.length;i++){
					div = document.getElementById(i);
					div.style.backgroundColor = resp[i]?"green":"red";
				}
				devsadded = true;
			}
			else{
				for(var i=0;i<resp.length;i++){
					var div = document.createElement("div");
					div.innerText = resp[i];
					div.id = i
					document.body.addChild(div);
				}
			}
		}
	};
	xhr.open("GET","/status/statusnames.json",true);
	Request();
	StatusRequest();
}
function Request(){
	xhr.setRequestHeader("Pragma", "no-cache");
	xhr.send();
}
function StatusRequest(){
	xhr.open("GET","/status/advancedstatus.json",true);
	Request();
	var number = Number(refresh.value);
	if(isNaN(number) || number < 0.05){number = 10;}
	setTimeout(Request,number*1000);
}