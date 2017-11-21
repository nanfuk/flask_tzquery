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

function get_list(){	//test
	var o = [];
	var a = [];
	var rows = $("#dg_otn").datagrid('getData').rows;
	for (var i = 0; i < rows.length; i++) {
		if(rows[i].znode!=null){	//避免出现空内容的空格时，下拉框筛选框会有一小行空白
			o.push(rows[i].znode);
		}
		
		//o.push({value:rows[i].znode,text:rows[i].znode}); 	//必须得加value才能选中这个选项
	}
	o = _.uniq(o);		//特定引入的用于数组去重的。

	for (var i = 0; i< o.length; i++) {
		a.push({value:o[i],text:o[i]}); 	//构建combobox的data,必须得加value才能选中这个选项
	}
	return a;					
}

$.extend($.fn.datagrid.methods, {
    editCell: function(jq, param) {
        return jq.each(function() {
            var opts = $(this).datagrid('options');
            var fields = $(this).datagrid('getColumnFields', true).concat($(this).datagrid('getColumnFields'));
            //concat,连接数组。datagrid('getColumnFields', true)表示获取冻结的列，datagrid('getColumnFields')指获取的未冻结列
            for (var i = 0; i < fields.length; i++) {
                var col = $(this).datagrid('getColumnOption', fields[i]);
                col.editor1 = col.editor;
                if (fields[i] != param.field) {
                    col.editor = null;
                }
            }
            $(this).datagrid('beginEdit', param.index);
            for (var i = 0; i < fields.length; i++) {
                var col = $(this).datagrid('getColumnOption', fields[i]);
                col.editor = col.editor1;
            }
        });
    }
});

var editIndex = undefined;
function endEditing() {
    if (editIndex == undefined) {
        return true
    }
    if ($('#dg').datagrid('validateRow', editIndex)) {
        $('#dg').datagrid('endEdit', editIndex);
        editIndex = undefined;
        return true;
    } else {
        return false;
    }
}
function onClickCell(index, field) {
    if (endEditing()) {
        $('#dg').datagrid('selectRow', index).datagrid('editCell', {
            index: index,
            field: field
        });
        editIndex = index;
    }
}