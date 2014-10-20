var previousLabel = null


//多数据源饼图
function drawPieChart(obj){
	//1. 数据
	var keys_data = $(obj).attr("keys_data");
	chart_data = keys_data.split(',');
	
	//2. 标签
	var keys_desc = $(obj).attr("keys_desc");
	chart_labels = keys_desc.split(',');


	var label_data = [];
	for(var i=0;i<chart_labels.length;i++){
		var item={};
		item['label'] = chart_labels[i];
		item['data'] = parseInt(chart_data[i]);
		label_data.push(item);
	}
	$.plot($(obj), label_data,
		{
			series: {
				pie: {
					show: true,
					label: {
                    				show: true
					}
				}
			},
			grid: {
				hoverable: true,
				autoHighlight:true
			},
			legend: {
				show: true
			}
		});
	
	$(obj).bind("plothover", pie_hover);

}

// 饼图浮动提示 tooltip
function pie_hover(event, pos, item){
	if (item){
		if(previousLabel!=item.series.label){
			previousLabel = item.series.label;
			$("#tooltip").remove();
			var color = item.series.color;
			//var value = $.formatNumber(item.series.data[0][1], { format: "#,###", locale: "us" });
			showTooltip(pos.pageX,pos.pageY,color, "此部分的值为" + item.series.data[0][1]);
		}

	}else{
		$("#tooltip").remove();
		previousPoint = null;
	}
}

function showTooltip(x, y, color, contents) {
    $('<div id="tooltip">' + contents + '</div>').css({
        position: 'absolute',
        display: 'none',
        top: y - 40,
        left: x - 120,
        border: '2px solid ' + color,
        padding: '3px',
        'font-size': '9px',
        'border-radius': '5px',
        'background-color': '#fff',
        'font-family': 'Verdana, Arial, Helvetica, Tahoma, sans-serif',
        opacity: 0.9
    }).appendTo("body").fadeIn(200);
}
