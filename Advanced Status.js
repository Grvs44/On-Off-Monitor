var devsadded,refresh,xhr,tries,items,sortbox
function Body_Onload(){
	refresh = document.getElementById("statusrefresh")
	tries = 0;
	items = document.getElementById("items");
        sortbox = document.getElementById("sort");
        sortbox.onchange = Sort;
	if (XMLHttpRequest) {xhr = new XMLHttpRequest();}
	else {xhr = new ActiveXObject("Microsoft.XMLHTTP");}
	xhr.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var resp = JSON.parse(xhr.responseText);
                if(items.children.length){
                    for(var i=0;i<items.children.length;i++){
                        document.getElementById(i).style.backgroundColor = resp[i]?"#25d825":"#e41f1f";
                        document.getElementById(i).on = resp[i];
                    }
                    Sort();
                }else{
                    if(this.responseURL.search("statusnames.json") == 0){
                        if(tries<10){
                            tries+=1;
                            NameRequest();
                        }
                        else{alert("Cannot load device names\nRefresh to try again");}
                    }else{
                        for(var i=0;i<resp.length;i++){
                            var div = document.createElement("div");
                            div.innerText = resp[i];
                            div.id = i;
                            div.style.width = "90%";
                            items.appendChild(div);
                        }
                        StatusRequest();
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
function Sort(){
    console.log("Sort");
    switch(sortbox.value){
        case "None":
            break;
        case "A-Z":
            SortItems(items.children,"value",true);
            break;
        case "Z-A":
            console.log("hi");
            SortItems(items.children,"value",false);
            break;
        case "On-Off":
            SortItems(items.children,"on",false);
            break;
        case "Off-On":
            SortItems(items.children,"on",true);
            break;
        default:
            console.log("Wrong sort type: " + sortbox.value);
            break;
    }
}
function SortItems(list,key,ascending){
    for(var i=1;i<list.length;i++){
        var item = list[i];
        var j = i - 1;
        while(SortCondition(list,key,item,j,ascending)){
            list[j+1] = list[j];
            j -= 1;
        }
        list[j+1] = item;
    }
}
function SortCondition(list,key,item,j,ascending){
    if(j<0){return false}
    else if(ascending){return item[key] < list[j][key]}
    else{return item[key] > list[j][key]}
}
