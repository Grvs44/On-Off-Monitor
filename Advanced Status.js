var devsadded,refresh,xhr,tries,items
function Body_Onload(){
	refresh = document.getElementById("statusrefresh")
	tries = 0;
	items = [];
	if (XMLHttpRequest) {xhr = new XMLHttpRequest();}
	else {xhr = new ActiveXObject("Microsoft.XMLHTTP");}
	xhr.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
			var resp = JSON.parse(xhr.responseText);
			if(items.length){
				for(var i=0;i<items.length;i++){
					items[i].style.backgroundColor = resp[i]?"#25d825":"#e41f1f";
				}
			}
			else{
				if(this.responseURL.search("statusnames.json") == 0){
					for(var i=0;i<resp.length;i++){
						var div = document.createElement("div");
						div.innerText = resp[i];
						div.id = i;
						div.style.width = resp[i].length + "em";
						document.body.appendChild(div);
						items.push(div);
					}
					StatusRequest();
				}else{
					if(tries<10){
						tries+=1;
						NameRequest();
					}
					else{alert("Cannot load device names\nRefresh to try again");}
				}
			}
		}
	};
	NameRequest();
}
function Request(){
	xhr.setRequestHeader("Pragma", "no-cache");
	xhr.send();
}
function NameRequest(){
	xhr.open("GET","/status/statusnames.json",true);
	Request();
}
function StatusRequest(){
	xhr.open("GET","/status/advancedstatus.json",true);
	Request();
	var number = Number(refresh.value);
	if(isNaN(number) || number < 0.05){number = 10;}
	setTimeout(StatusRequest,number*1000);
}