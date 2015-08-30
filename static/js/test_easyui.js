function transparam(param){
	list_param = JSON.parse(param);	//在函数内没加var定义的变量均是全局变量
	//{'searchword':searchword,'area':area,'index':index}
}

$(function(){
	$.ajax({
		type:'POST',
		url:'/tzquery',
		data:list_param,	//传的就是js的列表，这是一个全局变量
		dataType:'json',
		success:function(data){	//这个data已经是js的列表格式了，自动进行json转换的
			//alert(data);
			process_data(data);
		}
	});
});

function process_data(data){
	//data_tmp = JSON.parse(data);
	//alert(data["index"]);
	$("#test").datagrid({
				//width:800,
				title:"测试",
				iconCls:"icon-search",
				nowrap:false,	//定义为可以换行
				fitColumns:true,
			    columns:data["columns"],
			    data:data["datas"],
			    //fitColumns:true,		//自动适应列宽
			    autoRowHeight: true,	//根据内容自动调整行高,默认false,节省性能
				rownumbers:true,
			});
	//$("#test").datagrid(autoSizeColumn,"D");
}

/*
$("table").datagrid({
	//width:800,
	title:"测试",
	iconCls:"icon-search",
	
    columns:[[	//两个方括号，因为可以合并单元格的
    		{field:'code',title:'Code',width:100},	//field是数据库中的体现
    		{field:'name',title:'Name',width:100},
    		{field:'price',title:'Price',width:100,align:'right'}
    ]],
    
    //fitColumns:true,		//自动适应列宽
    autoRowHeight: true,	//根据内容自动调整行高,默认false,节省性能
	rownumbers:true,
});
*/
/*
$(function(){
	$.ajax({url:'test',dataType:'json',success:function(data){
		console.log(data),
		data1 = [[{field:'Category',title:'Category'}]],
		console.log(data1),
	    $('#show').datagrid({ 
	        title:'Stores sales quantity performance',
	        //url: 'get_salesquantityper.php',
	        width: 1000,
	        singleSelect: true,
	        rownumbers:true,
	        //frozenColumns:[[{field:'Category',title:'Category'}]],
	        columns:data,///xxxxxx那个页面输出column需要的内容
	        }); 
 
	},error:function(xhr){
  		alert('动态页有问题或者返回了不标准的JSON字符串\n'+xhr.responseText);
	}})
});
*/