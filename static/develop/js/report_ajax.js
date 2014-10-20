//  报表搜索查询操作
function reportCallback(obj){
    var url = $(obj).attr("action");
    jQuery.ajax({
	type: 'POST',
	url: url,
	data:$(obj).serializeArray(),
	success: report_success,
	error:error,
	dataType:'html',
	async:false
     });
     return false;
}

function report_success(data){
	$(".report_chart").remove();
	$("#content").append(data);
	$(".pie_chart").each(function(){drawPieChart(this);});
}

// 时间选择的快捷方式
function show_span_click(){
	var show_type = $(this).attr('show_type');
	//alert(show_type);
	var span_array = {'1':60*60*24, '2':60*60*24*7, '3':60*60*24*30};
	var endTime = new Date().getTime(); // 单位毫秒
	var startTime = endTime - span_array[show_type]*1000;
	$("#start_time").val(new Date(startTime).format('yyyy-MM-dd'));
	$("#end_time").val(new Date(endTime).format('yyyy-MM-dd'));
}

