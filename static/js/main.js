$(document).ready(function(){
		if ($.cookie("searchrecord3")==null)	
		{
			$.cookie("searchrecord3","",{path:"/",expires:7});
		}
		//else{$.cookie("searchrecord3",null,{path:"/",expires:7});}}); //清空cookie值
		else{modifyrecord($.cookie("searchrecord3"))}});
		
function isEmpty(){
	var searchrecord = $.cookie("searchrecord3");

	inputval = $.trim($("input#box1").val()); //移除字符串两侧的空白字符或其他预定义字符
	areaval = $("select").val()
	areatext = $("option[value="+areaval+"]").text(); //拼凑出来的，不是使用val(),因为得出的是01，02
	//$("input#box1").val("") //更改input框内容
	if (inputval=="")
	{
		alert("输入不能为空！");
		return false;
	}
	else{
		var record = {inputval:inputval, areaval:areaval, areatext:areatext}
		var record_str = JSON.stringify(record);
		searchrecord = searchrecord+"||"+record_str;
		modifyrecord(searchrecord);
		return true;
	}
}
function modifyrecord(searchrecord){
	var rslist = searchrecord.split('||');

	var html = "";
	var forlength = 0;
	var stringcookie = "";
	for (var i=rslist.length-1; i>= 0; i--)
	{
		var textval=rslist[i];

		if ($.trim(textval)!=""&&$.trim(textval)!="null"&&$.trim(textval)!="undefined")
		{
			if (forlength>=10)
			{
				$.cookie("searchrecord3",stringcookie,{expires:7});				
				break;
			}
			else
			{
				jsonval = JSON.parse(textval);
				html += "<li class='lis'><a href=/tzquery?key="+encodeURIComponent(jsonval.inputval)+"&amp;area="+encodeURIComponent(jsonval.areaval)+"&amp;version=1.0 target='_blank'>"+jsonval.inputval+"-->"+jsonval.areatext+"</a></li></br>";
				forlength += 1;
				stringcookie=textval+"||"+stringcookie;
			}
		}
	}
	$.cookie("searchrecord3",stringcookie,{expires:7});		
	//document.getElementById('top10record').innerHTML=html;//这句等效于下句
	$("#top10record").html(html);		
}