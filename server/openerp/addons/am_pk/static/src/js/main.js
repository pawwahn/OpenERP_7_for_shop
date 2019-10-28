openerp.am_pk = function(instance) {
	/*Autor Pavan Kumar Kota
	 * 2/6/2016
	 * Main page
	 * Import all necessary files
	 * */
	
    instance.am_pk = {};
    var module = instance.am_pk;
	
    // import base_widget.js
    openerp_credit_basewidget(instance,module);
	
    // import task.js
    openerp_credit_graph(instance,module);
	
    instance.web.client_actions.add('pgmt.cb.pop', 'instance.am_pk.GraphForm');
};