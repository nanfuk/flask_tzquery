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
									//$("#dg_otn").datagrid('removeFilterRule');		//先清除过滤器
									var id = node.id+"_"+node.attributes.parent	//id值用于区分不同tabs中不同的表格
									$("#otn_resource_tabs").tabs('add',{
										title:node.text,
										content:'<table id="'+id+'" style="width:100%;height:100%;"></table>',
										closable:true,
										tools:[{
											iconCls:'icon-mini-refresh',
											handler:function(){
												alert('refresh');
											}
										}]
									});
									//rows_index = true;
									$("#"+id).edatagrid({
										//title:'波分端口表',
										//url:'/otn/port',	//post这个地址，在view.py中区分Get与Post，默认post是返回750的数据
										singleSelect:"true",
										nowrap:false,
										fitColumns:true,
										columns:[[
													{field:"no",title:"序号",width:5},
													{field:"anode",title:"本端",width:15},
													{field:"direction",title:"方向",width:15},
													{field:"znode",title:"对端",width:15},
													{field:"route",title:"波道路由",width:25},
													{field:"wavelength",title:"波长编号",width:5},
													{field:"neident",title:"网元标识",width:7},
													{field:"port",title:"支路端口",width:15},
													{field:"index",title:"电路编号",width:20,editor:"text"},
													{field:"remark",title:"备注",width:25,editor:"text"}
												]],
										//toolbar:'#toolbar_otn',
										onRowContextMenu:function(e,index,row){
											e.preventDefault(); //阻止浏览器捕获右键事件
											$(this).datagrid("clearSelections"); //取消所有选中项
											$(this).datagrid("selectRow", index); //根据索引选中该行
											$.data(document.body, "index", row['no']);//将右击选中的某行数据放在缓存中
											$.data(document.body, "jf_name", $("#jf_list").combotree('getText'));//将右击选中的某行数据放在缓存中
											$('#tab1_table_menu').menu('show', {
												//显示右键菜单
								                left: e.pageX,//在鼠标点击处显示菜单
								                top: e.pageY
								            });
										},
										autoSave:'true',			//点击表格外时自动保存，注意是表格外
										updateUrl:"/otn/update",		//跳转到jquery.edatagrid.js的55行onAfterEdit
										onLoadSuccess:function(data){
											if (tname!=$("input[name='jf_name']").val() || vendername!=$("input[name='vender_otn']").val()){
												tname = $("input[name='jf_name']").val();
												vendername = $("input[name='vender_otn']").val();
												//rows = $("#dg_otn").datagrid('getData').rows;
												$("#"+id).datagrid('enableFilter',[{			//加载完数据后再设置行过滤
																		field:"znode",
																		type:"combobox",
																		options:{
																			data:(function(){
																				var o = [];
																				var a = [];
																				var rows = data.rows;
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
																			})(),		//自定义的函数，用于根据列表内容筛选znode单列去重值
																			onSelect:function(rec){
																				//rows_index = false;
																				$("#"+id).datagrid('addFilterRule',{
																					field:"znode",
																					op:"contains",
																					value:rec.value
																				});
																				$("#"+id).datagrid('doFilter');
																			}
																		}
																	}]);
											}
										}
									});		
									$("#"+id).datagrid('loadData',JSON.parse(data));		//需要把json数据转为数组才能使用
								}
							});
						}
			});
	$('#jf_list').combotree('setValue', 750);
	$('input[name=vender_otn]').val("fh300_port");
	
	$("#dg_otn").edatagrid({
		//title:'波分端口表',
		url:'/otn/port', //post这个地址，在view.py中区分Get与Post，默认post是返回750的数据
		singleSelect:"true",
		nowrap:false,
		fitColumns:true,
		columns:[[
					{field:"no",title:"序号",width:5},
					{field:"anode",title:"本端",width:15},
					{field:"direction",title:"方向",width:15},
					{field:"znode",title:"对端",width:15},
					{field:"route",title:"波道路由",width:25},
					{field:"wavelength",title:"波长编号",width:5},
					{field:"neident",title:"网元标识",width:7},
					{field:"port",title:"支路端口",width:15},
					{field:"index",title:"电路编号",width:20,editor:"text"},
					{field:"remark",title:"备注",width:25,editor:"text"}
				]],
		//toolbar:'#toolbar_otn',
		onRowContextMenu:function(e,index,row){
			e.preventDefault(); //阻止浏览器捕获右键事件
			$(this).datagrid("clearSelections"); //取消所有选中项
			$(this).datagrid("selectRow", index); //根据索引选中该行
			$.data(document.body, "index", row['no']);//将右击选中的某行数据放在缓存中
			$.data(document.body, "jf_name", $("#jf_list").combotree('getText'));//将右击选中的某行数据放在缓存中
			$('#tab1_table_menu').menu('show', {
				//显示右键菜单
                left: e.pageX,//在鼠标点击处显示菜单
                top: e.pageY
            });
		},
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
		
	$("#tab2_table").edatagrid({
		singleSelect:"true",
		nowrap:false,
		fitColumns:true,
		columns:[[
					{field:"no",title:"序号",width:5},
					{field:"circuitName",title:"电路编号",width:15},
					{field:"client",title:"客户名称",width:15},
					{field:"detailPath",title:"占用资源情况",width:35},
					{field:"type",title:"电路类型",width:5},
					{field:"requestIndex",title:"需求单号",width:15},
					{field:"dispatchTime",title:"分配日期",width:7},
					{field:"dispatchStaff",title:"分配人员",width:5},
					{field:"remark",title:"备注",width:25,editor:"text"}
		]]

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
	else{
		modifyrecord($.cookie("searchrecord3"));
	}
});

$("#tab1_table_menu").menu({
	onClick:function(item){
        if(item.id=="tab1_table_menu_source"){
        	//$("#atable").textbox("setText",$.data(document.body, "jf_name"));
        	$("#atable").textbox("setValue",$.data(document.body, "jf_name"));
        	$("#ano").textbox("setValue",$.data(document.body, "index"));	//从缓存取值
        	$.data(document.body, "jf_name", "");     //清空缓存
        	$.data(document.body, "index", "");     //清空缓存
        }
        else if(item.id=="tab1_table_menu_dest"){
        	$("#ztable").textbox("setValue",$.data(document.body, "jf_name"));
        	$("#zno").textbox("setValue",$.data(document.body, "index"));	//从缓存取值
        	$.data(document.body, "jf_name", "");     //清空缓存
        	$.data(document.body, "index", "");     //清空缓存
        }
    }
});
		
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