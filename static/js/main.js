$(document).ready(function(){
		if ($.cookie("searchrecord2")==null)	
		{
			$.cookie("searchrecord2","",{path:"/",expires:7});
		}
		//else{$.cookie("searchrecord",null,{path:"/",expires:7});}}); //清空cookie值
		else{modifyrecord($.cookie("searchrecord2"))}});
		
function isEmpty(){
	var searchrecord = $.cookie("searchrecord2");

	inputval = $.trim($("input#box1").val()); //移除字符串两侧的空白字符或其他预定义字符
	areaval = $("select").val();
	//$("input#box1").val("") //更改input框内容
	if (inputval=="")
	{
		alert("输入不能为空！");
		return false;
	}
	else{
		var record = {inputval:inputval, areaval:areaval}
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
				$.cookie("searchrecord2",stringcookie,{expires:7});				
				break;
			}
			else
			{
				jsonval = JSON.parse(textval);
				html += "<li class='lis'><a href=/tzquery?key="+encodeURIComponent(jsonval.inputval)+"&amp;area="+encodeURIComponent(jsonval.areaval)+" target='_blank'>"+jsonval.inputval+"-->"+jsonval.areaval+"</a></li></br>";
				forlength += 1;
				stringcookie=textval+"||"+stringcookie;
			}
		}
	}
	$.cookie("searchrecord2",stringcookie,{expires:7});		
	//document.getElementById('top10record').innerHTML=html;//这句等效于下句
	$("#top10record").html(html);		
}