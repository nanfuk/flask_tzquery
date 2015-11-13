var tname = undefined;
var vendername = undefined;
//var rows = undefined;
//var editIndex = undefined;
$(document).ready(function(){
		$("#tab-tools").tabs({			//生成选项卡
			tabPosition:"left",
			fit:"true"
		});

		$(".radioItem").change(function(){		//点击radio按键触发的事件处理方法
			var selectedValue = $("input[name='vender']:checked").val();
			/*if (selectedValue=='fh'){
				$("#dg").datagrid('load',{
					vender:"fh"
				})
			}
			else if(selectedValue=='hw'){
				$("#dg").datagrid('load',{
					vender:"hw"
				})
			}
			else if(selectedValue=='zx'){
				$("#dg").datagrid('load',{
					vender:"zx"
				})
			}*/
			$("#dg").datagrid('load',{
					vender:selectedValue
				})
		});

		$("#dg").datagrid({
			title:'波分环路表',
			columns:[[
						//{field:'no',title:"序号",width:10},
						{field:'ring_index',title:"环路编号",width:20},
						{field:'equiptype',title:'设备类型',width:20},
						{field:'node', title:'环上节点', width:60},
						{field:'remark', title:'备注', width:50}
					]],
			url:'/otn/get_data',
			toolbar:'#toolbar',
			rownumbers:'true',
			fitColumns:'true',		//加了这个参数，列才不会堆在一起
			singleSelect:'true',
			//onClickCell: onClickCell,	//点击单元格时间触发的方法
			queryParams:{vender:'fhr'},		//首次打开，请求远程数据时，发送的参数
			//autoSave:'true',			//点击表格外时自动保存，注意是表格外
			//saveUrl:"/otn/save",
			//updateUrl:"/otn/save"
		});

		$("#jf_list").combotree({
							url:'/otn/get_tree_json',
							method:'get',
							onClick:function(node){			//事件处理函数，不能使用onSelect事件
								$('input[name=vender_otn]').val(node.attributes.parent);	//设置value值的方法，别使用value="xx"
								//为了能得到combotree选取值的父节点，加了attributes属性，使用方法:node.attributes.parent
								//提交form前设置隐藏框的value值,把父节点值赋给这个隐藏框
								$('#otn_form').form('submit',{
									url:'otn/port',
									onSubmit:function(){
										return $(this).form('enableValidation').form('validate');	// return false will stop the form submission
									},
									success:function(data){
										$("#dg_otn").datagrid('removeFilterRule');		//先清除过滤器
										//rows_index = true;
										$('#dg_otn').datagrid('loadData',JSON.parse(data));		//需要把json数据转为数组才能使用
									}
								});
							}
				});
				$('#jf_list').combotree('setValue', 750);
				$('input[name=vender_otn]').val("fh300_port");
		
		$("#dg_otn").edatagrid({
			title:'波分端口表',
			url:'/otn/port',
			singleSelect:"true",
			nowrap:false,
			fitColumns:true,
			columns:[[
						{field:"no",title:"序号",width:5},
						{field:"anode",title:"本端",width:20},
						{field:"direction",title:"方向",width:20},
						{field:"znode",title:"对端",width:20},
						{field:"route",title:"波道路由",width:20},
						{field:"wavelength",title:"波长编号",width:8},
						{field:"index",title:"电路编号",width:20,editor:"text"},
						{field:"remark",title:"备注",width:20,editor:"text"}
					]],
			fitColumns:'true',
			toolbar:'#toolbar_otn',
			autoSave:'true',			//点击表格外时自动保存，注意是表格外
			updateUrl:"/otn/update",		//跳转到jquery.edatagrid.js的55行onAfterEdit
			onLoadSuccess:function(data){
				if (tname!=$("input[name='jf_name']").val() || vendername!=$("input[name='vender_otn']").val()){
					tname = $("input[name='jf_name']").val();
					vendername = $("input[name='vender_otn']").val();
					//rows = $("#dg_otn").datagrid('getData').rows;
					$("#dg_otn").datagrid('enableFilter',[{			//加载完数据后再设置行过滤
											field:"znode",
											type:"combobox",
											options:{
												data:get_list(),		//自定义的函数，用于根据列表内容筛选znode单列去重值
												onSelect:function(rec){
													//rows_index = false;
													$("#dg_otn").datagrid('addFilterRule',{
														field:"znode",
														op:"contains",
														value:rec.value
													});
													$("#dg_otn").datagrid('doFilter');
												}
											}
										}]);
				}
			}
		});		
				

		var dg = $("#client-210").datagrid({
			singleSelect:true,
			url:"client_names",
			method:"get",
			collapsible:true, //可折叠
			closable:true,	//可关闭，继承panel面板属性
			nowrap:false,
		});
		dg.datagrid('enableFilter',[{
			field:"itemid",
			type:"numberbox",
			op:['equal','notequal','less','greater']
		}]);
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

function get_list(){	//test
	var o = [];
	var a = [];
	var rows = $("#dg_otn").datagrid('getData').rows;
	for (var i = 0; i < rows.length; i++) {
		o.push(rows[i].znode);
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