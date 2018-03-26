// var tname = undefined;
// var vendername = undefined;

$("#otnDispatchTab").data("portTabs", {});

$(document).ready(function(){
    
    $("#tzqueryUpdateTable").datagrid({
        columns:[[
            {field:"cb", checkbox:true},
            {field:"wbName", title:"文件名", width:200},
            {field:"updateTime", title:"导入时间", width:90},
            {field:"lastModified", title:"修改时间", width:90},
            {field:"size", title:"文件大小", width:60},
            {field:"wbIndex", title:"专业分类", width:60}
        ]],
        url:"/managedb",
        method:"get",
        toolbar:"#tzqueryUpdateTableToolBar",
        rownumbers:true,
        fit:true
    });

    $("#tzqueryUpdateTableToolBar > #addWb").linkbutton({
        disabled:true,
        onClick:function(){
            $('#tzqueryUpdateDlg').dialog('open');
        }
    });

    $("#tzqueryUpdateTableToolBar > #delWb").linkbutton({
        disabled:true,
        onClick:function(){
            var checkedRows = $("#tzqueryUpdateTable").datagrid("getChecked");
            if(checkedRows.length==0){
                alert("请选择需要移除的EXCEL文件！");
                return;
            }
            $("body").showLoading();
            var wbIndexList = [];
            $.each(checkedRows, function(i){
                wbIndexList.push(checkedRows[i].wbIndex);
            });
            $.ajax({
                url:"/managedb",
                method:"post",
                data:{action:"del",wbIndexList:wbIndexList},
                success:function(returndata){
                    $("#tzqueryUpdateTable").datagrid("reload");
                    $("body").hideLoading();
                },
                error:function(returndata){
                    $("body").hideLoading();
                    alert("移除失败！");
                }
            });
        }
    });

    $("#tzqueryUpdateTableToolBar > #reloadWb").linkbutton({
        onClick:function(){
            $("#tzqueryUpdateTable").datagrid("reload");
        }
    });

    $("#tzqueryUpdateDlg").dialog({
        title:"导入更新",
        width:500,
        height:500,
        closed:true,
        modal:true
    });

    $("#tzqueryUpdateForm").form({
        url:"managedb",
    });

    $("#tzqueryUpdateForm > input").filebox({
        multiple:true,
        accept:"xls",
        buttonText:"选择文件",
        buttonAlign:"left"
    });

    $("#tzqueryUpdateForm > select").combo({
        required:true,
        editable:false
    });
    $("#classifiedSelectOption").appendTo($("#tzqueryUpdateForm > select").combo("panel"));
    $("#classifiedSelectOption input").click(function(){
        var v = $(this).val();
        var s = $(this).next("span").text();
        $("#tzqueryUpdateForm > select").combo("setValue", v).combo("setText", s).combo("hidePanel");
    });

    $("#tzqueryUpdateForm > .easyui-linkbutton").linkbutton({
        iconCls: "icon-ok",
        onClick:function(){
            var formData = new FormData();
            var files = $("#tzqueryUpdateForm > input").filebox("files"); // 更新到1.5.4才有的方法
            if(files.length==0){
                alert("请指定需要加入数据库的EXCEL文件！");
                return;
            }
            if($("#tzqueryUpdateForm").form("validate")==false){
                alert("请选择特定的分类！");
                return
            }
            $('#tzqueryUpdateDlg').dialog('close');
            $("body").showLoading();
            $.each(files, function(i){
                formData.append(i, files[i]);
                formData.append("lastModified"+i,files[i]["lastModified"]);
                formData.append("size"+i,files[i]["size"]);
            });
            var classified = $("#tzqueryUpdateForm > select").combo("getValue");
            formData.append("classified", classified);
            formData.append("action", "add");
            $.ajax({
                url:"managedb",
                type:"POST",
                data:formData,
                contentType:false,
                processData:false,
                success:function(returndata){
                    $("#tzqueryUpdateTable").datagrid("reload");
                    $("#tzqueryUpdateForm").form("clear"); //清空表单
                    $("body").hideLoading();
                },
                error:function(returndata){
                    $("body").hideLoading();
                    $("#tzqueryUpdateForm").form("clear"); //清空表单
                    alert("添加EXCEL失败！");
                }
            });
        }
    });

    $("#tab-tools").tabs({          //生成选项卡
        tabPosition:"left",
        fit:"true"
    });

    $('#circuitName').textbox({
    buttonText:'电路编号',
    width:250,
    iconCls:'icon-man',
    required:true,
    missingMessage:'核心局房优先顺序：太阳城--夏茅--科学城--云景--新时空--750--七所--工业园--中侨--远东--东兴--化龙。汇聚机房优先顺序：按首字母',
    //iconAlign:'left',
    tipPosition: "top", //在输入框上面显示提示信息
    onClickButton:function(){
        $('#circuitNameDialog').dialog('open')
        }
    });

    $('#circuitNameDialog').dialog({
        modal:true,
        title:'电路编号',
        width:400,
        height:200,
        closed:true
    });

    $(".radioItem").change(function(){      //点击radio按键触发的事件处理方法
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
        fitColumns:'true',      //加了这个参数，列才不会堆在一起
        singleSelect:'true',
        //onClickCell: onClickCell, //点击单元格时间触发的方法
        queryParams:{vender:'fhr'},     //首次打开，请求远程数据时，发送的参数
        //autoSave:'true',          //点击表格外时自动保存，注意是表格外
        //saveUrl:"/otn/save",
        //updateUrl:"/otn/save"
        view:detailview,
        detailFormatter: function(rowIndex, rowData){
            return '<div style="padding:2px"><table style="height:150px" id="ddv-' + rowIndex + '"></table></div>'
        },
        onExpandRow:function(rowIndex, rowData){
            $.data(document.body, "dgTableRowIndex", rowIndex);
            $('#ddv-'+rowIndex).datagrid({
                url:'/otn/getWaves',
                queryParams:{ring_index:rowData.ring_index, nodes:rowData.node},
                columns:[[
                            {field:"index",title:"编号"},
                            {field:"link",title:"对接方向"},
                            {
                                field:"nums",
                                title:"波道数量",
                                formatter: function(value,row,index){
                                    var content = [
                                        '<a data-dgtablerowindex=',$.data(document.body, "dgTableRowIndex"),
                                        ' data-ddvtablerowindex=',index,
                                        ' onClick="popDetailRoute(this)">',
                                        value,
                                        '</a>'
                                        ]
                                    return content.join("")
                                }
                            }
                        ]],
            });
            
        }
    });

    $("#disDetailRouteTable").datagrid({
        remoteSort:false,   // 默认是true，必须设为false才能在本地列排序
        // title:"详细波道信息",
        fitColumns:true,
        columns:[[
                {field:'route',title:"路由信息", width:300},
                {
                    field:'wl',
                    title:'占用波道',
                    width:100,
                    sortable:true,
                    sorter:function(a,b){
                        return parseInt(a)>parseInt(b)?1:-1
                    }
                },
            ]],
    });

    $("#otn_resource_tabs").tabs({  //tabs构建
        fit:true,
        onSelect:function(title,index){
            var tab = $(this).tabs('getSelected');
            tableObject = tab.find(".tabs_table");
            if(tableObject.length>0){
                var id = tableObject[0].id;
                $.data(document.body, "db_table", [id,title])
            }
        },
        onContextMenu:function(e,title,index){
            e.preventDefault(); //阻止浏览器捕获右键事件
            var tab_title_array = new Array();
            var tabs = $("#otn_resource_tabs").tabs('tabs');
            for (var i = 0; i < tabs.length; i++) {
                var tab_title = tabs[i].panel('options')['title'];
                if (tab_title!=title && tab_title!="路由显示"){
                    tab_title_array.push(tab_title)
                }
            }
            $("#otn_resource_tabs_contextmenu").data("tab_title",{"selected":title,"unselected":tab_title_array}); //把tab_title字典存入右键菜单的缓存
            $('#otn_resource_tabs_contextmenu').menu('show', {
                //显示右键菜单
                left: e.pageX,//在鼠标点击处显示菜单
                top: e.pageY
            });
        }
    });



    $("#jf_list").combotree({
        url:'/otn/get_tree_json',
        method:'get',
        lines:true,
        onClick:function(node){         //事件处理函数，不能使用onSelect事件
            var id = node.id+"___"+node.attributes.parent;  //id值用于区分不同tabs中不同的表格
            var table_name = node.text; //选取combotree的项名称，例如白云厅
            var db_name = node.attributes.parentname; //选取combotree的父名称，例如烽火3000
            var title = table_name+"_"+db_name;
            if($("#otn_resource_tabs").tabs('exists',title)){
                $('#otn_resource_tabs').tabs('select', title);
            } else {
                $('input[name=vender_otn]').val(node.attributes.parent);    //设置value值的方法，别使用value="xx"
                //为了能得到combotree选取值的父节点，加了attributes属性，使用方法:node.attributes.parent
                //提交form前设置隐藏框的value值,把父节点值赋给这个隐藏框
                $("#otn_form").form("submit", {
                    url:"otn/port", //在html定义form时默认是get请求的，参数就是form中的标签值
                    success:function(data){
                        $("#otn_resource_tabs").tabs('add',{
                            title:title, //显示新时空_烽火3000
                            content:'<table class="tabs_table" id="'+id+'" style="width:100%;height:100%;"></table>',
                            closable:true,
                            tools:[{
                                iconCls:'icon-mini-refresh',
                                handler: function(){
                                    var jfname = id.split("___")[0];
                                    var vender = id.split("___")[1];
                                    refreshPortDg(vender, jfname); //更新端口表
                                }
                            }]
                        });
                        generatePortDg(id, title, data); 
                        //自定义的函数用于创建edategrid并加载数据
                    },
                    onLoadError:function(data){
                        alert("获取数据失败！");
                    },
                    onBeforeLoad:function(){
                        alert('obBeforeLoad')
                    }
                });
            }
        },
        onLoadSuccess:function(){
            var tree = $('#jf_list').combotree('tree');
            tree.tree("collapseAll");
        }
    });
    
    // $('#jf_list').combotree('setValue', 750);
    // $('input[name=vender_otn]').val("fh3000_port");
        
    $("#tab2_table").datagrid({
        singleSelect:"true",
        nowrap:false,
        fitColumns:true,
        columns:[[
                    {field:"oldIndex",title:"旧电路编号",width:10,editor:"text"},
                    {field:"Index",title:"规范电路编号",width:10,editor:"text"},
                    {field:"project",title:"项目",width:12,editor:"text"},
                    {field:"requestNo",title:"需求编号",width:5,editor:"text"},
                    {field:"dispatchNo",title:"调度单号",width:10,editor:"text"},
                    {field:"band",title:"带宽",width:15,editor:"text"},
                    {field:"AIndex",title:"局向A",width:5,editor:"text"},
                    {field:"ZIndex",title:"局向Z",width:5,editor:"text"},
                    {field:"usage",title:"用途",width:10,editor:"textbox"},
                    {field:"route",title:"路由",width:30,editor:"textarea"},
                    {field:"remark",title:"备注",width:10,editor:"textarea"},
        ]],
        editorHeight: 96,   //设置编辑器的高度
        onRowContextMenu:function(e,index,row){ //datagrid中的右键事件
            e.preventDefault(); //阻止浏览器捕获右键事件
            $(this).datagrid("clearSelections"); //取消所有选中项
            $(this).datagrid("selectRow", index); //根据索引选中该行
            $('#tab1_dispatch_table_menu').menu('show', {
                //显示右键菜单
                left: e.pageX,//在鼠标点击处显示菜单
                top: e.pageY
            });
        },
        onDblClickRow:edit
    }); 

    var dg = $("#client-210").datagrid({
        singleSelect:true,
        url:"client_names",
        method:"get",
        collapsible:true, //可折叠
        closable:true,  //可关闭，继承panel面板属性
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


function popDetailRoute(el){
    var dgTableRowIndex = $(el).data("dgtablerowindex");
    var ddvTableRowIndex = $(el).data("ddvtablerowindex");
    var content = $("#ddv-"+dgTableRowIndex).datagrid('getData').rows[ddvTableRowIndex].content;
    $("#disDetailRouteWin").window('open');
    $("#disDetailRouteTable").datagrid('loadData',content);
}



// 生成端口表
function generatePortDg(id, tableName, data){
    /*
    $.extend($.fn.datagrid.defaults, {
        filterMenuIconCls: 'icon-ok',
        filterBtnIconCls: 'icon-filter',
        filterBtnPosition: 'right',
        filterPosition: 'bottom',
        remoteFilter: false,
        filterDelay: 400,
        filterRules: [],
        filterStringify: function(data){
            return JSON.stringify(data);
        }
    });*/
    // $.extend($.fn.datagrid.defaults,{filterRules:[]});   //加载了新表格，得设filterRules为空，不然共享filterRules
    var portTabs = $.data($("#otnDispatchTab")[0], "portTabs");
    var el = $("#"+id);
    portTabs[id]={'el':el, 'tableName':tableName};

    el.datagrid({
        singleSelect:"true",
        nowrap:false,
        // fitColumns:true,
        columns:[[
                    {field:"no",title:"序号",width:30},
                    {field:"anode",title:"本端",width:120},
                    {field:"direction",title:"方向",width:80,editor:"text"},
                    {field:"znode",title:"对端",width:80,editor:"text"},
                    {field:"route",title:"波道路由",width:180,editor:"text"},
                    {field:"wavelength",title:"波长",width:50,editor:"text"},
                    {field:"neident",title:"网元标识",width:60,editor:"text"},
                    {field:"lineport",title:"线路端口",width:80,editor:"text"},
                    {field:"port",title:"支路端口",width:80,editor:"text"},
                    {field:"linetype",title:"速率",width:40,editor:"text"},
                    {field:"index",title:"电路编号",width:150,editor:"text"},
                    {field:"remark",title:"备注",width:180,editor:"text"},
                    {field:"odf",title:"ODF",width:120,editor:"text"},
                    {field:"system",title:"所属系统",width:80,editor:"text",hidden:true},
                    {field:"jijiano",title:"机架编号",width:60,editor:"text",hidden:true},
                    {field:"kuangno",title:"框编号",width:60,editor:"text",hidden:true},
                    {field:"boardname",title:"单板名称",width:60,editor:"text",hidden:true},
                    {field:"portindex",title:"端口编号",width:60,editor:"text",hidden:true},
                    {field:"rtx",title:"收/发",width:50,editor:"text",hidden:true}
                ]],
        onDblClickRow: edit,
        onRowContextMenu:function(e,index,row){ //datagrid页面中右键触发，不是tab标题
            e.preventDefault(); //阻止浏览器捕获右键事件
            $(this).datagrid("clearSelections"); //取消所有选中项
            $(this).datagrid("selectRow", index); //根据索引选中该行

            $.data(document.body, "row", row);  //将右键选中的行加入全局缓存
            $('#tab1_port_table_menu').menu('show', {
                //显示右键菜单
                left: e.pageX,//在鼠标点击处显示菜单
                top: e.pageY
            });
        },
        onHeaderContextMenu: function(e, field){
            e.preventDefault();
            if (!$cmenu){
                createColumnMenu(el);    // el是对应的datagrid的选择器
            }
            $cmenu.menu('show', {
                left:e.pageX,
                top:e.pageY
            });
        }
    });

    var $cmenu;     // 端口表列名右键菜单
    function createColumnMenu(el){  // el是对应的datagrid的选择器
        $cmenu = $('<div/>').appendTo('body');
        $cmenu.menu({
            onClick: function(item){
                if (item.iconCls == 'icon-ok'){
                    el.datagrid('hideColumn', item.name);
                    $cmenu.menu('setIcon', {
                        target: item.target,
                        iconCls: 'icon-empty'
                    });
                } else {
                    el.datagrid('showColumn', item.name);
                    $cmenu.menu('setIcon', {
                        target: item.target,
                        iconCls: 'icon-ok'
                    });
                }
                // el.datagrid("fitColumns");
            }
        });
        var fields = el.datagrid('getColumnFields');
        for(var i=0; i<fields.length; i++){
            var field = fields[i];
            var col = el.datagrid('getColumnOption', field);
            if(col.hidden){
                $cmenu.menu('appendItem', {
                    text: col.title,
                    name: field,
                });
            } else {
                $cmenu.menu('appendItem', {
                text: col.title,
                name: field,
                iconCls: 'icon-ok'
                });
            }
        }
    }
    
    el.datagrid('loadData',JSON.parse(data));       //需要把json数据转为数组才能使用,必须在加载过滤器前加载表格数据

    el.datagrid('enableFilter', [{          //加载完数据后再设置行过滤
        field:"znode",
        type:"combobox",
        options:{
            data:(function(){
                var o = [];
                var a = [{value:'',text:'ALL'}];
                var rows = JSON.parse(data);
                for (var i = 0; i < rows.length; i++) {
                    if(rows[i].znode!=null){    //避免出现空内容的空格时，下拉框筛选框会有一小行空白
                        o.push(rows[i].znode);
                    }
                }
                o = _.uniq(o);      //特定引入的用于数组去重的。

                for (var i = 0; i< o.length; i++) {
                    a.push({value:o[i],text:o[i]});     //构建combobox的data,必须得加value才能选中这个选项
                }
                return a;                   
            })(),       //自定义的函数，用于根据列表内容筛选znode单列去重值
            onChange:function(value){
                if(value==''){
                    el.datagrid('removeFilterRule', 'znode');
                } else {
                    el.datagrid('addFilterRule',{
                        field:"znode",
                        op:"contains",
                        value:value
                    });
                }
                el.datagrid('doFilter');
                storeAllChangedRows();  // 过滤后会把编辑行的颜色复原，这里再次渲染编辑的行。
            }
        }
    }]);
}

// 更新端口表，传入端口表的id值
function refreshPortDg(vender, jfname){
    $.ajax({
        url:"otn/port",
        data: {vender_otn:vender, jf_name:jfname},
        async: false,   // 使用同步请求，来解决多表同时刷新时不能正常反应的情况
        type: "GET",
        success:function(data){
            $("#"+jfname+"___"+vender).datagrid('loadData',JSON.parse(data));
        }
    });
}

// 端口表Tab选项卡右键菜单
$("#otn_resource_tabs_contextmenu").menu({
    onClick:function(item){
        if(item.id=="otn_resource_tabs_contextmenu_refresh"){
            alert("刷新");
        }
        else if(item.id=="otn_resource_tabs_contextmenu_closeother"){
            var unselected_tab_title_array = $(this).data("tab_title")["unselected"];
            var selected_tab_title = $(this).data("tab_title")["selected"];
            var $otn_resource_tabs = $("#otn_resource_tabs");
            alert(unselected_tab_title_array);
            for(var i=unselected_tab_title_array.length-1;i>=0;i--){
                var tab = $otn_resource_tabs.tabs("close",unselected_tab_title_array[i]);
            }
            $otn_resource_tabs.tabs('select',selected_tab_title);
        }  
    }
})

// 端口表右键菜单
$("#tab1_port_table_menu").menu({
    onClick:function(item){
        var id = item.id;
        var db_table = $.data(document.body, "db_table");
        
        var table = db_table[0].split("___")[0];
        var db = db_table[0].split("___")[1];

        var tablename = db_table[1].split("_")[0];
        var dbname = db_table[1].split("_")[1];

        var row = $.data(document.body, "row");
        if(id=="tab1_table_menu_edit"){
            $("#port_table_edit_window > form").form('load', row);
            $("#port_table_edit_window").panel("open");
        }
        else if(id=="tab1_table_menu_insert"){
            alert("插入一行");
        }
        else if(id="tab1_table_menu_del"){
            alert("删除该行");
        }
        else if(id=="tab1_table_menu_source"){
            $("#atable").textbox("setValue", tablename);
            $("#ano").textbox("setValue", row['no']);
            $("#avender").textbox('setValue', dbname);
            $("#vender").textbox('setValue',db);   //vender是hidden的input框
            $.data(document.body, "source", {vender:db,tablename:table,rows:[row]});    //otn/update需求的数据格式
        }
        else if(id=="tab1_table_menu_dest"){
            $("#ztable").textbox("setValue", tablename);
            $("#zno").textbox("setValue", row['no']);
            $("#zvender").textbox('setText', dbname);
            $.data(document.body, "dest", {vender:db,tablename:table,rows:[row]});
        }
    }
});

// 路由分配表的右键菜单
$("#tab1_dispatch_table_menu").menu({
    onClick: function(item){
        if(item.id=="tab1_dispatch_table_menu_exportall"){
            var rows = $("#tab2_table").datagrid("getRows");
            var columns = ["oldIndex","Index","project","requestNo","dispatchNo",
                            "band","AIndex","ZIndex","usage","route","remark"];
            var x = [];
            for(var i=0; i<=rows.length-1; i++){
                var y = [];
                for(var j=0; j<=columns.length-1; j++){
                    y.push(rows[i][columns[j]]);
                }
                x.push(y);
            }   // 把表格转换为[[a1,b1,c2],[a2,b2,c3]]格式
            var content = JSON.stringify(x);
            content = content.replace(/"/g,"&quot;");   //把双引号转义为&quot;
            DownLoadFile({
                        url:"otn/export_dispatch_excel",
                        data: {content:content},
                        method:"post"
                    });
            return;
        }
        else if(item.id=="tab1_dispatch_table_menu_deleterow"){
            var rows = $("#tab2_table").datagrid("getSelections");
        }
        else if(item.id=="tab1_dispatch_table_menu_deleteallrows"){
            var rows = $("#tab2_table").datagrid("getRows");
        }
        for (var i = rows.length - 1; i >= 0; i--) {
            var rowIndex = $("#tab2_table").datagrid("getRowIndex",rows[i]);
            $("#tab2_table").datagrid("deleteRow",rowIndex);
        }
    }
});

// 弹出资源分配框
$("#dispatchDialog").dialog({"onBeforeOpen":function(){
    var route = $("#output-box").textbox("getText");
    var source = $.data(document.body,"source");
    if(source&&route){
        var remark = source["rows"][0]["remark"];
    }else{
        alert('还未指定路由！');
        return false
    }
    $("#dispatchRoute").textbox("setText",route);
    $("#remarkInfo1").textbox("setText",remark);
    return true
    }
});

// 下载附件，通过提交表单的方式，因为jQuery的ajax没有流的返回类型，无法实现
// options:{
//     url:'', //下载地址
//     data:{name:value},  //要发送的数据
//     method:'post'
// }
function DownLoadFile(options){
    var config = $.extend(true, {method:"post"}, options);
    var $iframe = $('<iframe id="down-file-iframe" />');
    var $form = $('<form target="down-file-iframe" method="'+config.method+'" />');
    $form.attr('action', config.url);
    for(var key in config.data){
        $form.append('<input type="hidden" name="'+key+'"value="'+config.data[key]+'" />');
    }
    $iframe.append($form);
    $(document.body).append($iframe);
    $form[0].submit();
    $iframe.remove();
}


// 提交表单，查询路由资料
function submitForm(){
    $("#cc").showLoading();
    $('#ff').form('submit',{
        url:'otn/dispatch',
        onSubmit:function(){
            return $(this).form('enableValidation').form('validate');   // return false will stop the form submission
        },
        success:function(data){
            $('#output-box').textbox('setText',data);   //资源分配的输出框
            $("#cc").hideLoading();
        }
    });
}

// 点击提交资源分配所需的参数
function confirmDispatch(){
    $("#cc").showLoading();
    var index = $("#circuitName").textbox("getText");
    var remark1 = $("#remarkInfo1").textbox("getText");
    var remark2 = $("#remarkInfo2").textbox("getText");
    if(remark1){
        var remark = remark1+";"+remark2;
    }else{
        var remark = remark2;
    }
    
    var AInfo = $("#AInfo").textbox("getText");
    var ZInfo = $("#ZInfo").textbox("getText");
    var route = AInfo + $("#dispatchRoute").textbox("getText") + ZInfo;
    $.data(document.body, "source")["rows"][0]["index"] = index;
    $.data(document.body, "source")["rows"][0]["remark"] = remark;
    $.data(document.body, "dest")["rows"][0]["index"] = index;
    $.data(document.body, "dest")["rows"][0]["remark"] = remark;

    // 把电路编号及备注加入端口表
    
    var data = new Array();
    data.push($.data(document.body, "source")); //{vender:xx,tablename:yy,rows:[zz]}
    data.push($.data(document.body, "dest"));

    $("#dispatchDialog").dialog("close");    //关闭对话框
    $("#dispatchDialog>form").form("clear");    //清空表单

    var appendDispatchTable = function(){
        
        $("#tab2_table").datagrid("appendRow", {
            route: route,
            remark: remark2,
            AIndex: $.data(document.body, "source")["table"],
            ZIndex: $.data(document.body, "dest")["table"],
            Index: index
        });
        var AVender = $.data(document.body, "source")["vender"];
        var AJfname = $.data(document.body, "source")["tablename"];
        var ZVender = $.data(document.body, "dest")["vender"];
        var ZJfname = $.data(document.body, "dest")["tablename"];
        refreshPortDg(AVender, AJfname); // 刷新源端口表
        refreshPortDg(ZVender, ZJfname); // 刷新宿端口表
        $("#otn_resource_tabs").tabs("select",0); //切换至路由显示表
        $("#cc").hideLoading();
    };

    $.ajax({
        url:"otn/update", //可以共用
        data: { updatedata: JSON.stringify(data),
                action: "dispatch"},
        type: "POST",
        success: appendDispatchTable
    });
}


function clearForm(){
    $('#ff').form('clear');
}

function submit_otnform(){
    $('#otn_form').form('submit',{
        url:'otn/port',
        onSubmit:function(){
            return $(this).form('enableValidation').form('validate');   // return false will stop the form submission
        },
        success:function(data){
            $('#dg_otn').datagrid('loadData',JSON.parse(data));     //需要把json数据转为数组才能使用
        }
    });
}

var editIndex = undefined;
var tableObject = undefined;
function endEdit(){
    if(editIndex==undefined){return true}
    if(tableObject.datagrid('validateRow', editIndex)){
        tableObject.datagrid('endEdit', editIndex);
        storeAllChangedRows();
        // renderAllChangedRows();
        editIndex = undefined;
        return true;
    } else {
        return false;
    }
}
function edit(rowIndex, rowData){   // 编辑端口表
    if(editIndex!=rowIndex){
        if(endEdit()){
            tableObject.datagrid('selectRow',rowIndex)
                                    .datagrid('beginEdit',rowIndex);
            editIndex = rowIndex;
        } else {
            tableObject.datagrid('selectRow',editIndex);
        }
    }
}
function accept(){
    if(endEdit()){
        // $("#tab2_table").datagrid('acceptChanges');
        // var rows = tableObject.datagrid('getChanges');
        // alert(rows.length+' rows are changed!');
        // tableObject.datagrid('acceptChanges');
        return;
    }
}
function save(){
    var tablename = tableObject[0].id.split('___')[0]   //ToDo改
    var vender = tableObject[0].id.split('___')[1]
    var rows = undefined;
    if(endEdit()){
        rows = tableObject.datagrid('getChanges');
        if(rows.length>0){
            tableObject.datagrid('acceptChanges');
            // alert(rows.length+' rows are changed!');
            if(confirm(rows.length+' rows are changed!')){
                $("#cc").showLoading();
            }else{return;}
        } else {
            alert('还未编辑');
            return;
        }
    } else {return;}

    var data = [{vender:vender,tablename:tablename,rows:rows}];
    $.ajax({
        url: "otn/update",
        // data: {vender:vender,tablename:tablename,rows:JSON.stringify(rows)},
        data: { updatedata: JSON.stringify(data),
                action: "edit"},
        //需把rows转为字符串再传
        type: "POST",
        success: function(returnData) {
            if(returnData=="success"){
                $("#cc").hideLoading();
                alert("更新成功");
            } else {
                $("#cc").hideLoading();
                alert("更新失败");
            }
        },
        error:function(){
            $("#cc").hideLoading();
            alert("更新失败");
        }
    });
}
function undo(){
    if(endEdit()){
        tableObject.datagrid('rejectChanges');
    }
}

function storeAllChangedRows(){
    var portTabs = $.data($("#otnDispatchTab")[0], "portTabs");
    for(var key in portTabs){
        var $portTab = portTabs[key].el;
        var insertedRows = $.data($portTab[0], "datagrid").insertedRows;
        var deletedRows = $.data($portTab[0], "datagrid").deletedRows;
        var updatedRows = $.data($portTab[0], "datagrid").updatedRows;
        portTabs[key].changedRows = {"insertedRows":insertedRows,"deletedRows":deletedRows,"updatedRows":updatedRows};
        rederUpdatedRows($portTab, updatedRows);
    }

    function rederUpdatedRows(el, rows){
        var opts = el.datagrid("options");
        $.each(rows, function(i){
            var index = el.datagrid("getRowIndex", rows[i]);
            opts.finder.getTr(el[0], index).addClass("updatedRows");
        })
    }
}

function undoEdit(){

}

function saveConfirm(){
    var $saveDialog, $table, $tr, $td, options, portTabs, updatedRows, tableName;
    $saveDialog = $("#saveDialog");
    $saveDialog.empty();   // 清空所有子元素
    portTabs = $.data($("#otnDispatchTab")[0], "portTabs");
    options = {
        singleSelect:"true",
        nowrap:false,
        fitColumns:true,
        showHeader:false,
        columns:[[
                    {field:"no",title:"序号",width:5},
                    {field:"anode",title:"本端",width:13},
                    {field:"direction",title:"方向",width:13},
                    {field:"znode",title:"对端",width:13},
                    {field:"route",title:"波道路由",width:25},
                    {field:"wavelength",title:"波长编号",width:10},
                    {field:"neident",title:"网元标识",width:10},
                    {field:"lineport",title:"线路端口",width:15},
                    {field:"port",title:"支路端口",width:15},
                    {field:"index",title:"电路编号",width:20},
                    {field:"remark",title:"备注",width:20},
                    {field:"system",title:"所属系统",width:5,hidden:true},
                    {field:"jijiano",title:"机架编号",width:5,hidden:true},
                    {field:"kuangno",title:"框编号",width:5,hidden:true},
                    {field:"boardname",title:"单板名称",width:5,hidden:true},
                    {field:"portindex",title:"端口编号",width:5,hidden:true},
                    {field:"linetype",title:"电路类型",width:5,hidden:true},
                    {field:"rtx",title:"收/发",width:5,hidden:true},
                    {field:"odf",title:"ODF",width:5,hidden:true}
                ]],
        onRowContextMenu:function(e,index,row){ //datagrid页面中右键触发，不是tab标题
            e.preventDefault(); //阻止浏览器捕获右键事件
            $(this).datagrid("clearSelections"); //取消所有选中项
            $(this).datagrid("selectRow", index); //根据索引选中该行

            $.data(document.body, "row", row);  //将右键选中的行加入全局缓存
            $('#tab1_port_table_menu').menu('show', {
                //显示右键菜单
                left: e.pageX,//在鼠标点击处显示菜单
                top: e.pageY
            });
        }
    }
    for(var key in portTabs){
        tableName = portTabs[key]["tableName"];
        updatedRows = portTabs[key]["changedRows"]["updatedRows"];
        $table = $("<table></table>");
        $saveDialog.append("<p>"+tableName+"</p>");
        $saveDialog.append($table[0]);
        $table.datagrid(options);
        $table.datagrid("loadData", updatedRows);
    }
    $saveDialog.dialog("open");
}

function saveb(){
    var portTabs, tablename, vender, rows;
    var data = new Array();
    portTabs = $.data($("#otnDispatchTab")[0], "portTabs");
    $("#saveDialog").dialog("close");
    $("#cc").showLoading();

    $.each(portTabs, function(key){
        tablename = key.split("___")[0];
        vender = key.split("___")[1];
        rows = portTabs[key]['changedRows']['updatedRows']; //当前只处理更新的行，待实现增加与删除
        data.push({vender:vender,tablename:tablename,rows:rows})
    })
    // var tablename = tableObject[0].id.split('___')[0]   //ToDo改
    // var vender = tableObject[0].id.split('___')[1]
    // var rows = undefined;
    // if(endEdit()){
    //     rows = tableObject.datagrid('getChanges');
    //     if(rows.length>0){
    //         tableObject.datagrid('acceptChanges');
    //         // alert(rows.length+' rows are changed!');
    //         if(confirm(rows.length+' rows are changed!')){
    //             $("#cc").showLoading();
    //         }else{return;}
    //     } else {
    //         alert('还未编辑');
    //         return;
    //     }
    // } else {return;}

    // var data = [{vender:vender,tablename:tablename,rows:rows}];
    $.ajax({
        url: "otn/update",
        // data: {vender:vender,tablename:tablename,rows:JSON.stringify(rows)},
        data: { updatedata: JSON.stringify(data),
                action: "edit"},
        //需把rows转为字符串再传
        type: "POST",
        success: function(returnData) {
            if(returnData=="success"){
                $("#cc").hideLoading();
                alert("更新成功");
            } else {
                $("#cc").hideLoading();
                alert("更新失败");
            }
        },
        error:function(){
            $("#cc").hideLoading();
            alert("更新失败");
        }
    });
}
