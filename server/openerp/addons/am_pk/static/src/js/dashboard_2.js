function createStateChart(state_result){
	console.log("inside -----------------");
	console.log(state_result);
    //var line1 = [['Nissan', 4],['Porche', 6],['Acura', 2],['Aston Martin', 5],['Rolls Royce', 6]];
    var line1 = state_result
    $('#chart2').jqplot([line1], {
        title:'Bar Chart with Varying Colors',
        seriesDefaults:{
            renderer:$.jqplot.BarRenderer,
            rendererOptions: {
                // Set the varyBarColor option to true to use different colors for each bar.
                // The default series colors are used.
                varyBarColor: true
            }
        },
        axes:{
            xaxis:{
                renderer: $.jqplot.CategoryAxisRenderer
            }
        }
    })
}