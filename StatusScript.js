var table,refresh,xhr,sortbox;
function Body_Onload(){
    table = document.getElementById("statustable");
    refresh = document.getElementById("statusrefresh");
    sortbox = document.getElementById("sort");
    if (XMLHttpRequest) {xhr = new XMLHttpRequest();}
    else {xhr = new ActiveXObject("Microsoft.XMLHTTP");}
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            if(sortbox.value == "None"){
                var resp = JSON.parse(xhr.responseText);
            }else{
                var resp = SortItems(JSON.parse(xhr.responseText),(sortbox.value == "A-Z" || sortbox.value == "Z-A")?0:1,sortbox.value == "A-Z" || sortbox.value == "Off-On");
            }
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
    return list;
}
function SortCondition(list,key,item,j,ascending){
    if(j<0){return false;}
    else if(ascending){return item[key] < list[j][key];}
    else{return item[key] > list[j][key];}
}
