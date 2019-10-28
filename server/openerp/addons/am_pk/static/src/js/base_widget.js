function openerp_credit_basewidget(instance, module){
	var QWeb = instance.web.qweb;
	
	module.CreditBaseWidget = instance.web.Widget.extend({
		init:function(parent,options){
            this._super(parent);
            this.project={};  
           
		},
	});
}