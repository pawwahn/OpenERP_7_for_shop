/*!
 * Project Dashboard
 * @author Pavan Kota
 * @date Sep 2015
 */

function createBarChart(result){
	console.log(result[0]);
	console.log(result[1]);
	//console.log(month);
	console.log("result of function =======================");
	$.jqplot.config.enablePlugins = true;
    //var s1 = [2, 6, 7, 10, 15, 8, 11,];
    //var ticks = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
	var s1 = result[1];
	var ticks = result[0];
	console.log("in chart ==============================");
    console.log(s1);
    console.log(ticks);	
    plot1 = $.jqplot('teamWiseProjectBar', [s1], {
        // Only animate if we're not using excanvas (not in IE 7 or IE 8)..
        animate: !$.jqplot.use_excanvas,
        seriesDefaults:{
            renderer:$.jqplot.BarRenderer,
            pointLabels: { show: true }
        },
        axes: {
            xaxis: {
                renderer: $.jqplot.CategoryAxisRenderer,
                ticks: ticks
            }
        },
        highlighter: { show: false }
    });
	
	$('#teamWiseProjectBar').bind('jqplotDataClick', 
            function (ev, seriesIndex, pointIndex, data) {
                $('#info1').html('series: '+seriesIndex+', point: '+pointIndex+', data: '+data);
            }
        );
	
} 
/*function createBarChart(){
$.jqplot.config.enablePlugins = true;
        var s1 = [2, 6, 7, 10];
        var ticks = ['a', 'b', 'c', 'd'];
         
        plot1 = $.jqplot('teamWiseProjectBar', [s1], {
            // Only animate if we're not using excanvas (not in IE 7 or IE 8)..
            animate: !$.jqplot.use_excanvas,
            seriesDefaults:{
                renderer:$.jqplot.BarRenderer,
                pointLabels: { show: true }
            },
            axes: {
                xaxis: {
                    renderer: $.jqplot.CategoryAxisRenderer,
                    ticks: ticks
                }
            },
            highlighter: { show: false }
        });
	
}*/


