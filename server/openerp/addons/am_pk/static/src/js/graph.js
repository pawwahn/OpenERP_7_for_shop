function openerp_credit_graph(instance, module) {
    /*Project Management v2.0 screens*/

    var QWeb = instance.web.qweb;
    /*Release Plan Screen Form view*/
    module.GraphForm = module.CreditBaseWidget.extend({
    	
    	
    	events: {
            'click #releasePlanSave': 'save_release_plan',
            'click .label' : 'update_status',
            'click #searchBtn': 'get_data',
        },



        init: function(parent, dataset, view_id, options) {
            this._super(parent, options);
            //this.id = dataset.id;
            //this.project=parent.project;
        },
        start: function() {
        	var self = this;
            self.$el.empty();
            self.$el.append(QWeb.render('pgmt.cb.pop'));
            
            var renderedElements = QWeb.render('project.graph');
            $('#home').append(renderedElements);
            
            //createBarChart(amount,month);
            //createChart2();
			//createBarChart();
            $(".date_class").datepicker({
                dateFormat: 'dd/mm/yy',
                changeMonth: true,
                changeYear: true,
                showButtonPanel: true,
                buttonImage: "/project_htc_v2/static/src/img/calendar.png",
                buttonImageOnly: true,
                buttonText: "dd/mm/yy"
            }).val();
        },
        
        get_data: function(){
        	var self = this;
            //self.$el.empty();
            var start_date = self.$el.find("#db_from_date").val();
            var end_date = self.$el.find("#db_to_date").val();
            var model = new instance.web.Model('credit.customer.bill');
  		    model.call("get_data",[start_date,end_date]).then(function(result){
  		    createBarChart(result);	
  		    });
			var new_model = new instance.web.Model('credit.customer.bill');
			new_model.call("get_state_wise_data",[start_date,end_date]).then(function(state_result){
  		    console.log("====================================== state result");
			console.log(state_result);
  		    createStateChart(state_result);	
  		    });
            
        	
        },
        
       
    });

}
